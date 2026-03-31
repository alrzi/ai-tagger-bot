.PHONY: check lint run install

# Установка зависимостей
install:
	source .venv/bin/activate && pip install -r requirements.txt

# Проверка кода (аналог swift build)
check:
	source .venv/bin/activate && ruff check src/ config/ main.py

# Автоисправление
fix:
	source .venv/bin/activate && ruff check --fix src/ config/ main.py

# Запуск бота
run:
	source .venv/bin/activate && python main.py
