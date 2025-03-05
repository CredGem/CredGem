from typing import Any, Dict


def get_context_filter(context: Dict[str, Any]) -> str:
    """Convert context dict to filter string."""
    return f"[{','.join([f'{k}={v}' for k, v in context.items()])}]"
