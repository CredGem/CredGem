from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass(frozen=True)
class Balance:
    credit_type_id: str
    available: float
    held: float
    spent: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Balance':
        return cls(
            credit_type_id=data['credit_type_id'],
            available=float(data['available']),
            held=float(data['held']),
            spent=float(data['spent'])
        )


@dataclass(kw_only=True)
class WalletResponse:
    id: str
    name: str
    created_at: str
    updated_at: str
    description: Optional[str] = field(default=None)
    context: Dict = field(default_factory=dict)
    balances: List[Balance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WalletResponse':
        # Handle optional fields with defaults
        balances_data = data.get('balances', [])
        balances = [Balance.from_dict(b) if isinstance(b, dict) else b for b in balances_data]
        
        return cls(
            id=data['id'],
            name=data['name'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            description=data.get('description'),
            context=data.get('context', {}),
            balances=balances
        )

    def __post_init__(self):
        if self.balances and isinstance(self.balances[0], dict):
            object.__setattr__(self, 'balances', [Balance.from_dict(b) if isinstance(b, dict) else b for b in self.balances])


@dataclass(kw_only=True)
class CreditTypeResponse:
    id: str
    name: str
    created_at: str
    updated_at: str
    description: Optional[str] = field(default=None)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreditTypeResponse':
        return cls(
            id=data['id'],
            name=data['name'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            description=data.get('description')
        )


@dataclass(kw_only=True)
class TransactionResponse:
    id: str
    type: str
    credit_type_id: str
    wallet_id: str
    amount: float = field(default=0.0)
    description: Optional[str] = field(default=None)
    issuer: str = field(default="")
    context: Dict = field(default_factory=dict)
    created_at: str
    status: Optional[str] = field(default=None)
    hold_status: Optional[str] = field(default=None)
    payload: Optional[Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionResponse':
        # Extract amount from payload if present
        payload = data.get('payload', {})
        amount = float(payload.get('amount', 0)) if isinstance(payload, dict) else 0.0
        
        return cls(
            id=data['id'],
            type=data.get('type', ''),
            credit_type_id=data['credit_type_id'],
            wallet_id=data.get('wallet_id', ''),
            amount=amount,
            description=data.get('description'),
            issuer=data.get('issuer', ''),
            context=data.get('context', {}),
            created_at=data['created_at'],
            status=data.get('status'),
            hold_status=data.get('hold_status'),
            payload=payload
        ) 