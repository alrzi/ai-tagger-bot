.PHONY: check lint typecheck run install verify check-di test

# Установка зависимостей
install:
	source .venv/bin/activate && pip install -r requirements.txt

# Проверка кода (аналог swift build)
check:
	source .venv/bin/activate && ruff check src/ config/ main.py

# Проверка типов (аналог swift build — строгая проверка)
typecheck:
	source .venv/bin/activate && mypy src/ config/ main.py

# Автоисправление
fix:
	source .venv/bin/activate && ruff check --fix src/ config/ main.py

# Запуск бота
run:
	source .venv/bin/activate && python main.py

# Проверка DI контейнера
check-di:
	source .venv/bin/activate && python scripts/check_di.py

# Запуск всех тестов
test:
	source .venv/bin/activate && pytest tests/ -x

# Полная проверка
verify: check typecheck check-di test

# Подключение к консоли PostgreSQL
db-shell:
	docker compose exec postgres psql -U ai_tagger ai_tagger
