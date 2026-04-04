"""Application layer (Use Cases)."""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | [%(name)s] | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

# Logger categories
log_use_case = logging.getLogger("Use case")
log_ai = logging.getLogger("AI")
log_db = logging.getLogger("Database")
log_bot = logging.getLogger("Bot")
log_worker = logging.getLogger("Worker")
