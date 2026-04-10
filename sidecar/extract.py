import logging
import time
from typing import Dict, Any

import redis
from ipcha.config import (
    REDIS_HOST, REDIS_PORT,
    DOW_BUDGET_LIMIT_PER_PERIOD, DOW_BUDGET_PERIOD_SECONDS
)
from ipcha.models import User
from ipcha.exceptions import BudgetLimitExceededError

logger = logging.getLogger(__name__)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def _get_current_window_timestamp() -> int:
    """Calculates the start of the current time window."""
    now = int(time.time())
    return (now // DOW_BUDGET_PERIOD_SECONDS) * DOW_BUDGET_PERIOD_SECONDS

def check_and_update_budget(user: User):
    """
    Checks if the user is within their rolling budget and increments their usage.
    Uses Redis for atomic operations.

    Raises:
        BudgetLimitExceededError: If the user's budget for the period is exceeded.
    """
    window_ts = _get_current_window_timestamp()
    key = f"dow_budget:{user.id}:{window_ts}"

    # Use a pipeline for atomicity
    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    pipeline.expire(key, DOW_BUDGET_PERIOD_SECONDS)
    current_usage, _ = pipeline.execute()

    if int(current_usage) > DOW_BUDGET_LIMIT_PER_PERIOD:
        log_payload: Dict[str, Any] = {
            "event": "dow_rejection",
            "userID": user.id,
            "timestamp": time.time(),
            "rejectionType": "budget_limit",
            "observedValue": current_usage,
            "limitValue": DOW_BUDGET_LIMIT_PER_PERIOD,
        }
        logger.warning(log_payload)
        raise BudgetLimitExceededError(
            "User budget for the current period has been exceeded.",
            user_id=user.id,
            observed_value=current_usage,
            limit_value=DOW_BUDGET_LIMIT_PER_PERIOD
        )
