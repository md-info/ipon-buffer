"""Build a debug APK with Android SDK tools and the JDK, without Gradle dependencies."""

import os
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get("ANDROID_SDK_ROOT", ROOT.parents[1] / "work/android-sdk"))
JAVA = Path(os.environ.get("JAVA_HOME", "C:/Program Files/JetBrains/IntelliJ IDEA 2026.1.3/jbr"))
TOOLS = SDK / "build-tools/35.0.0"
PLATFORM = SDK / "platforms/android-35/android.jar"
BUILD = ROOT / "android/build"


def run(*args):
    subprocess.run([str(x) for x in args], check=True, cwd=ROOT)


def main():
    os.environ["JAVA_HOME"] = str(JAVA)
    os.environ["PATH"] = str(JAVA / "bin") + os.pathsep + os.environ["PATH"]
    BUILD.mkdir(exist_ok=True)
    classes = BUILD / "classes"
    classes.mkdir(exist_ok=True)
    run(
        TOOLS / "aapt2.exe", "compile", "--dir", ROOT / "android/res", "-o", BUILD / "resources.zip"
    )
    unsigned = BUILD / "unsigned.apk"
    run(
        TOOLS / "aapt2.exe",
        "link",
        "-I",
        PLATFORM,
        "--manifest",
        ROOT / "android/AndroidManifest.xml",
        "--min-sdk-version",
        "26",
        "--target-sdk-version",
        "35",
        "-o",
        unsigned,
        BUILD / "resources.zip",
    )
    run(
        JAVA / "bin/javac.exe",
        "--release",
        "8",
        "-classpath",
        PLATFORM,
        "-d",
        classes,
        ROOT / "android/src/com/iponbuffer/app/MainActivity.java",
    )
    run(
        TOOLS / "d8.bat",
        "--lib",
        PLATFORM,
        "--min-api",
        "26",
        "--output",
        BUILD,
        *classes.rglob("*.class"),
    )
    with zipfile.ZipFile(unsigned, "a", zipfile.ZIP_DEFLATED) as apk:
        apk.write(BUILD / "classes.dex", "classes.dex")
    aligned = BUILD / "aligned.apk"
    run(TOOLS / "zipalign.exe", "-f", "4", unsigned, aligned)
    key = BUILD / "debug.keystore"
    if not key.exists():
        run(
            JAVA / "bin/keytool.exe",
            "-genkeypair",
            "-keystore",
            key,
            "-storepass",
            "android",
            "-keypass",
            "android",
            "-alias",
            "androiddebugkey",
            "-dname",
            "CN=Ipon Demo,O=Development,C=CA",
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "10000",
        )
    output = BUILD / "Ipon-Buffer-demo.apk"
    run(
        TOOLS / "apksigner.bat",
        "sign",
        "--ks",
        key,
        "--ks-pass",
        "pass:android",
        "--out",
        output,
        aligned,
    )
    run(TOOLS / "apksigner.bat", "verify", "--verbose", output)
    run(TOOLS / "aapt2.exe", "dump", "badging", output)
    print(output)


if __name__ == "__main__":
    main()
