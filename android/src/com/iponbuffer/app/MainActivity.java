package com.iponbuffer.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Build;
import android.graphics.Insets;
import android.view.WindowInsets;
import android.widget.FrameLayout;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceError;

public final class MainActivity extends Activity {
    private static final String HOME = "http://127.0.0.1:5173/";
    private WebView web;
    private ValueCallback<Uri[]> photo;
    private boolean errorShown;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xfffafbf7);
        getWindow().setNavigationBarColor(0xfffafbf7);
        // Size the viewport itself: WebView padding does not protect CSS fixed elements.
        if (Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(false);
        getWindow().getDecorView().setSystemUiVisibility(0x2000 | 0x10 | 0x100 | 0x200 | 0x400);
        FrameLayout viewport = new FrameLayout(this);
        web = new WebView(this);
        viewport.addView(web, new FrameLayout.LayoutParams(-1, -1));
        setContentView(viewport);
        viewport.setOnApplyWindowInsetsListener((v, insets) -> {
            int left, top, right, bottom;
            if (Build.VERSION.SDK_INT >= 30) {
                Insets safe = insets.getInsets(WindowInsets.Type.systemBars()
                    | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                left = safe.left; top = safe.top; right = safe.right; bottom = safe.bottom;
            } else {
                left = insets.getSystemWindowInsetLeft(); top = insets.getSystemWindowInsetTop();
                right = insets.getSystemWindowInsetRight(); bottom = insets.getSystemWindowInsetBottom();
            }
            FrameLayout.LayoutParams bounds = (FrameLayout.LayoutParams) web.getLayoutParams();
            if (bounds.leftMargin != left || bounds.topMargin != top
                    || bounds.rightMargin != right || bounds.bottomMargin != bottom) {
                bounds.setMargins(left, top, right, bottom);
                web.setLayoutParams(bounds);
            }
            return Build.VERSION.SDK_INT >= 30 ? WindowInsets.CONSUMED : insets.consumeSystemWindowInsets();
        });
        viewport.requestApplyInsets();
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.getSettings().setAllowFileAccess(false);
        web.getSettings().setAllowContentAccess(true);
        web.getSettings().setMixedContentMode(0);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if ("http".equals(uri.getScheme()) && "127.0.0.1".equals(uri.getHost()) && uri.getPort() == 5173) return false;
                if ("https".equals(uri.getScheme())) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignored) { }
                }
                return true;
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (!request.isForMainFrame() || errorShown) return;
                errorShown = true;
                new AlertDialog.Builder(MainActivity.this).setTitle("Connect to your demo")
                    .setMessage("Start Ipon Buffer on your computer, connect this phone by USB, then run android/connect.ps1. The backend and AI run on your computer.")
                    .setPositiveButton("Retry", (d,w) -> { errorShown = false; web.loadUrl(HOME); })
                    .setNegativeButton("Close", (d,w) -> finish()).show();
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (photo != null) photo.onReceiveValue(null);
                photo = callback;
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.setType("image/*");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                try { startActivityForResult(intent, 7); } catch (Exception e) { photo.onReceiveValue(null); photo = null; }
                return true;
            }
        });
        // No native JavaScript bridge, wallet credentials, camera or location access.
        web.loadUrl(HOME);
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request == 7 && photo != null) {
            photo.onReceiveValue(result == RESULT_OK && data != null && data.getData() != null ? new Uri[]{data.getData()} : null);
            photo = null;
        }
    }
    @Override public void onBackPressed() {
        web.evaluateJavascript("(function(){var d=document.querySelector('[role=dialog]');if(!d)return false;var b=Array.from(d.querySelectorAll('button')).find(function(x){return /cancel|back to feed/i.test(x.textContent)});if(b){b.click();return true;}return false;})()", result -> {
            if (!"true".equals(result)) {
                if (web.canGoBack()) web.goBack(); else finish();
            }
        });
    }
    @Override protected void onDestroy() {
        if (photo != null) photo.onReceiveValue(null);
        web.destroy();
        super.onDestroy();
    }
}
