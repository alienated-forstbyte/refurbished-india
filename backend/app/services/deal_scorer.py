import statistics
from collections import defaultdict

CPU_TIERS = {
    "high_end": {"i9", "core ultra 9", "ryzen 9", "threadripper"},
    "upper_mid": {"i7", "core ultra 7", "ryzen 7"},
    "mid_range": {"i5", "core ultra 5", "ryzen 5"},
    "entry": {"i3", "core ultra 3", "ryzen 3", "n100", "n95", "n3050", "pentium", "celeron", "athlon"},
}


def _cpu_tier(cpu_generation: str) -> str:
    gen = cpu_generation.lower()
    for tier, keywords in CPU_TIERS.items():
        if any(kw in gen for kw in keywords):
            return tier
    return "unknown"


def compute_deal_scores(rows: list[dict]) -> dict[int, float]:
    ram_groups: dict[int, list[float]] = defaultdict(list)
    cpu_tier_groups: dict[str, list[float]] = defaultdict(list)
    cpu_tier_by_id: dict[int, str] = {}

    for r in rows:
        price = r["price"]
        if price is None:
            continue
        if r.get("ram_gb") is not None:
            ram_groups[r["ram_gb"]].append(price)
        if r.get("cpu_generation"):
            tier = _cpu_tier(r["cpu_generation"])
            cpu_tier_groups[tier].append(price)
            cpu_tier_by_id[r["id"]] = tier

    ram_medians = {k: statistics.median(v) for k, v in ram_groups.items() if len(v) >= 3}
    cpu_tier_medians = {k: statistics.median(v) for k, v in cpu_tier_groups.items() if len(v) >= 3}

    scores: dict[int, float] = {}
    for r in rows:
        pid = r["id"]
        price = r["price"]
        if price is None or price <= 0:
            scores[pid] = 50.0
            continue

        components = 0
        weighted_z = 0.0

        ram_gb = r.get("ram_gb")
        if ram_gb is not None and ram_gb in ram_medians and ram_medians[ram_gb] > 0:
            weighted_z += (ram_medians[ram_gb] - price) / ram_medians[ram_gb]
            components += 1

        if pid in cpu_tier_by_id:
            tier = cpu_tier_by_id[pid]
            if tier in cpu_tier_medians and cpu_tier_medians[tier] > 0:
                cpu_score = (cpu_tier_medians[tier] - price) / cpu_tier_medians[tier]
                weighted_z += cpu_score * 2
                components += 2

        if components == 0:
            scores[pid] = 50.0
        else:
            raw = weighted_z / components
            raw = max(-0.5, min(0.5, raw))
            scores[pid] = round((raw + 0.5) * 100, 1)

    return scores


async def refresh_deal_scores(session):
    from sqlalchemy import select, update
    from app.models.product import Product

    result = await session.execute(
        select(
            Product.id,
            Product.price,
            Product.ram_gb,
            Product.cpu_generation,
        ).where(Product.stock_status == "in_stock", Product.price.isnot(None))
    )
    rows = [r._asdict() for r in result.all()]
    scores = compute_deal_scores(rows)

    for pid, score in scores.items():
        await session.execute(
            update(Product).where(Product.id == pid).values(deal_score=score)
        )

    out_of_stock_ids = await session.execute(
        select(Product.id).where(Product.stock_status != "in_stock")
    )
    for (pid,) in out_of_stock_ids:
        await session.execute(
            update(Product).where(Product.id == pid).values(deal_score=None)
        )

    await session.commit()
