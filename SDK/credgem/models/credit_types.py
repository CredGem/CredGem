from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(kw_only=True)
class CreditTypeRequest:
    name: str
    description: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class CreditTypeUpdateRequest:
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class CreditTypeResponse:
    id: str
    name: str
    created_at: str
    updated_at: str
    description: Optional[str] = field(default=None)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreditTypeResponse":
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            description=data.get("description"),
        )
