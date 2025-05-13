import abc
from typing import List, Dict, Any
from datetime import datetime

RawItem = Dict[str, Any]

class BaseFetcher(abc.ABC):
    def __init__(self, source_id: str, url: str):
        self.source_id = source_id
        self.url = url

    @abc.abstractmethod
    async def fetch(self) -> List[RawItem]:
        ...
