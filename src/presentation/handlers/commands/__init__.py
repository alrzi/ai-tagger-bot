"""Командные хендлеры бота."""

from src.presentation.handlers.commands.start import router as start_router
from src.presentation.handlers.commands.help import router as help_router
from src.presentation.handlers.commands.status import router as status_router
from src.presentation.handlers.commands.list import router as list_router
from src.presentation.handlers.commands.search import router as search_router
from src.presentation.handlers.commands.categories import router as categories_router
from src.presentation.handlers.commands.stats import router as stats_router

__all__ = [
    "start_router",
    "help_router",
    "status_router",
    "list_router",
    "search_router",
    "categories_router",
    "stats_router",
]
