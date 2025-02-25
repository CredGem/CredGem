from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi import HTTPException, Query, Request
from pydantic import BaseModel

from src.models.base import PaginationRequest


async def get_pagination(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=10, ge=1, le=100, description="Number of items per page"
    ),
) -> PaginationRequest:
    return PaginationRequest(page=page, page_size=page_size)


def dict_parser(param_name: str = "context"):
    """
    Creates a dependency function that parses [key=value] pairs from query parameters.

    Args:
        param_name: The name of the query parameter to parse (default: "context")

    Usage:
        get_context = create_key_value_parser("context")
        get_filters = create_key_value_parser("filters")
    """

    async def parser(
        request: Request,
        param_value: Optional[str] = Query(
            None,
            alias=param_name,
            description=f"{param_name} parameter in format: [key=value,key=value]",
            examples=["[key1=value1]", "[key1=value1,key2=value2]"],
            pattern=r"\[([^=\[\]]+=[^=\[\],]+,)*([^=\[\]]+=[^=\[\],]+)\]",
        ),
    ) -> Dict[str, str]:
        result = {}
        if param_value:
            content = param_value.strip("[]")
            pairs = content.split(",")
            for pair in pairs:
                if not pair:
                    continue
                key, value = pair.split("=", 1)
                result[key] = value
        return result

    return parser


def parse_iso_date(param_name: str = "date"):
    """
    Creates a dependency function that parses ISO format dates from query parameters.
    Handles Z timezone indicator by converting to +00:00 format.

    Args:
        param_name: The name of the query parameter to parse (default: "date")

    Returns:
        datetime: The parsed datetime object

    Raises:
        ValueError: If date string is not in valid ISO format
    """

    async def parser(
        date_str: str = Query(
            ...,
            alias=param_name,
            description=(
                f"{param_name} parameter in ISO format (e.g. 2024-01-01T00:00:00Z)"
            ),
            example="2024-01-01T00:00:00Z",
        )
    ) -> datetime:
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid datetime format for {param_name}. "
                    "Use ISO format (e.g., 2024-01-01T00:00:00Z)"
                ),
            )

    return parser


class DateTimeRange(BaseModel):
    start_date: datetime
    end_date: datetime


def get_datetime_range(
    start_date: Optional[str] = Query(
        default=None, description="Start date in ISO format (e.g. 2024-01-01T00:00:00Z)"
    ),
    end_date: Optional[str] = Query(
        default=None, description="End date in ISO format (e.g. 2024-01-01T00:00:00Z)"
    ),
) -> DateTimeRange:
    # Make sure datetime.now() is timezone-aware
    current_time = datetime.now(timezone.utc)

    if not start_date and not end_date:
        normalized_start_date = current_time - timedelta(days=30)
        normalized_end_date = current_time

    elif not start_date and end_date:
        normalized_start_date = current_time - timedelta(days=30)
        normalized_end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    elif not end_date and start_date:
        normalized_start_date = datetime.fromisoformat(
            start_date.replace("Z", "+00:00")
        )
        normalized_end_date = current_time

    else:  # both start and end date are provided
        assert start_date and end_date
        normalized_start_date = datetime.fromisoformat(
            start_date.replace("Z", "+00:00")
        )
        normalized_end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    if normalized_start_date > normalized_end_date:
        raise HTTPException(
            status_code=422,
            detail="Start date must be before end date",
        )

    return DateTimeRange(start_date=normalized_start_date, end_date=normalized_end_date)
