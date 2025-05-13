from pathlib import Path
from pydantic import BaseModel, Field
import yaml

class SourceConfig(BaseModel):
    id: str
    type: str
    url: str
    interval: int
    lang: str = Field(default="en")
    weight: int = Field(default=1)
    active: bool = Field(default=True)

def load_sources(path: str | Path = Path(__file__).parents[2] / "sources.yml") -> list[SourceConfig]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [SourceConfig.model_validate(d) for d in data if d.get("active", True)]
