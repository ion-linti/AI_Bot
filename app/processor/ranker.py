from datetime import datetime, timezone

def compute_score(stars: int, upvotes: int, weight: int, published) -> float:
    age_hours = 0
    if published:
        age_hours = (datetime.now(timezone.utc) - published.replace(tzinfo=timezone.utc)).total_seconds() / 3600
    return (stars + upvotes) + weight + max(0, 48 - age_hours)
