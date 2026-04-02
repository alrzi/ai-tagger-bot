# Cline Project Instructions

## Working Directory

**ALL terminal commands MUST be executed from the project directory:**

```bash
cd /Users/alrzi/Work/Projects/ai-tagger-bot && <command>
```

This rule is absolute — never run commands from any other directory.

## Git Branch

Always work on the `main` branch. Verify with:
```bash
cd /Users/alrzi/Work/Projects/ai-tagger-bot && git branch --show-current
```

## Virtual Environment

When installing packages or running scripts, always:
1. Navigate to project directory first
2. Then activate venv or run commands

**Correct example:**
```bash
cd /Users/alrzi/Work/Projects/ai-tagger-bot && source .venv/bin/activate && pip install dishka
```

**Wrong example (never do this):**
```bash
source .venv/bin/activate && pip install dishka  # Missing cd!
```

## Project Stack

- **Python** — основной язык
- **aiogram 3.x** — Telegram bot framework
- **Ollama** — AI анализ и эмбеддинги
- **SQLAlchemy 2.x + Alembic** — база данных и миграции
- **dishka** — DI контейнер
- **aiohttp** — HTTP клиент

## Project Structure

```
ai-tagger-bot/
├── config/              # Настройки приложения
├── migrations/          # Alembic миграции
├── src/
│   ├── domain/          # Доменные модели и репозитории
│   ├── infrastructure/  # AI, DB, web реализации
│   └── presentation/    # Bot handlers, keyboards
├── src/usecases/        # Бизнес-логика (use cases)
└── tests/               # Тесты
```

## Common Commands

```bash
# Run bot
cd /Users/alrzi/Work/Projects/ai-tagger-bot && python main.py

# Run tests
cd /Users/alrzi/Work/Projects/ai-tagger-bot && python -m pytest

# Run migrations
cd /Users/alrzi/Work/Projects/ai-tagger-bot && alembic upgrade head

# Install dependencies
cd /Users/alrzi/Work/Projects/ai-tagger-bot && pip install -r requirements.txt
