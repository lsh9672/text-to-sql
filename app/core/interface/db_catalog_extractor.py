from abc import ABC, abstractmethod
## 타입 명시를 위해 import
from typing import Dict, Any

class DBCatalogExtractor(ABC):
    
    @abstractmethod
    def extractCatalog(self) -> Dict[str, Any]:
        pass
    
    