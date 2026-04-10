import os

# Denial-of-Wallet (DoW) Defense Configuration
DOW_INVOCATION_COST_CEILING = int(os.getenv("DOW_INVOCATION_COST_CEILING", "5000"))
DOW_BUDGET_LIMIT_PER_PERIOD = int(os.getenv("DOW_BUDGET_LIMIT_PER_PERIOD", "100"))
DOW_BUDGET_PERIOD_SECONDS = int(os.getenv("DOW_BUDGET_PERIOD_SECONDS", "3600"))

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
