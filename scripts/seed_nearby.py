"""Populate fictional, photo-led community examples. Explicit and idempotent."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.db import Store  # noqa: E402
from app.nearby import meta, reactions, reports  # noqa: E402
from sqlalchemy import select  # noqa: E402


def seed(store):
    meta.create_all(store.engine)
    credits = json.loads((ROOT / "web/public/demo/credits.json").read_text())
    credit = {x["asset"].split(".")[0]: x for x in credits}
    examples = [
        (
            "rice",
            "Rice for the week",
            "1 kg, regular white rice",
            "Puregold — fictional demo branch",
            5800,
            "Mika · demo neighbor",
            (
                "Comparing staples before the weekly shop. Check the variety and "
                "pack size before comparing prices."
            ),
        ),
        (
            "eggs",
            "A dozen eggs for breakfast",
            "12 medium eggs",
            "Aling Nena’s sari-sari — fictional store",
            9600,
            "Sam · demo neighbor",
            (
                "A useful small-store find for the neighborhood. Sharing the "
                "dozen price so it is easier to compare."
            ),
        ),
        (
            "vegetables",
            "Tomatoes for tonight’s cooking",
            "1 kg tomatoes",
            "Community produce stall — fictional store",
            7000,
            "Lia · demo neighbor",
            "Local stalls belong here too. Freshness and travel cost matter alongside the price.",
        ),
        (
            "eggs",
            "Quick essentials stop",
            "6 medium eggs",
            "7-Eleven — fictional demo branch",
            6600,
            "Paolo · demo neighbor",
            (
                "Convenient on the way home. Compare the six-pack with a dozen "
                "rather than just the shelf price."
            ),
        ),
        (
            "rice",
            "Small grocery, everyday staple",
            "1 kg regular white rice",
            "Reyes Family Grocery — fictional store",
            5500,
            "Ana · demo neighbor",
            (
                "Adding a neighborhood grocery to the comparison. Please check "
                "availability before making a trip."
            ),
        ),
        (
            "vegetables",
            "Grocery produce comparison",
            "1 kg tomatoes",
            "Savemore — fictional demo branch",
            8500,
            "Joel · demo neighbor",
            (
                "Another option for the same shopping list. These are sample "
                "prices to demonstrate the experience."
            ),
        ),
    ]
    with store.lock, store.engine.begin() as conn:
        for i, (photo, item, quantity, shop, price, author, caption) in enumerate(examples):
            rid = f"sample-nearby-v1-{i}"
            if conn.execute(select(reports.c.id).where(reports.c.id == rid)).first():
                continue
            body = {
                "item": item,
                "quantity": quantity,
                "store": shop,
                "area": "Demo Central" if i != 5 else "Demo Riverside",
                "price_minor": price,
                "observed_at": int(time.time()) - (i + 1) * 900,
                "conditions": "Illustrative regular price. Not a current retailer quote.",
                "photo": f"/demo/{photo}.jpg",
                "demo": True,
                "author_name": author,
                "caption": caption,
                "photo_credit": credit[photo]["author"],
                "photo_source": credit[photo]["source"],
            }
            conn.execute(
                reports.insert().values(id=rid, owner=f"sample-author-{i}", body=json.dumps(body))
            )
            for j in range(2 + i % 3):
                conn.execute(
                    reactions.insert().values(
                        id=f"{rid}-thanks-{j}",
                        report=rid,
                        actor=f"sample-viewer-{j}",
                        kind="helpful",
                    )
                )
            if i % 2 == 0:
                conn.execute(
                    reactions.insert().values(
                        id=f"{rid}-confirm", report=rid, actor="sample-confirmer", kind="confirmed"
                    )
                )
    print("Six fictional photo posts available. Existing reports preserved.")


if __name__ == "__main__":
    seed(Store("sqlite:///" + str(ROOT / "ipon-demo.db")))
