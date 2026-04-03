# AI Tagger Bot

Telegram-бот для сохранения и анализа контента с помощью ИИ.

## Функции

- 📝 Сохранение текстов и ссылок
- 🤖 Автоматический анализ через Ollama (теги, резюме)
- 🔍 Семантический поиск по смыслу
- 📊 Статистика по категориям (`/stats`)
- 🏷 Управление категориями (`/categories`)

## Запуск через Docker

### Требования

- Docker и Docker Compose
- Ollama, запущенный на локальной машине (http://localhost:11434)

### Шаги

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd ai-tagger-bot
```

2. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактировать .env:
# - BOT_TOKEN: токен от @BotFather
# - POSTGRES_USER/PASSWORD/DB: настройки БД
# - OLLAMA_MODEL: модель Ollama (по умолчанию llama3)
```

3. Запустить:
```bash
docker-compose up -d
```

4. Проверить статус:
```bash
docker-compose ps
docker-compose logs bot
```

### Ollama

Бот использует Ollama для AI-анализа. Ollama должна быть запущена на хост-машине:

```bash
# Установить Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Запустить модель
ollama run llama3
```

Docker подключается к Ollama через `host.docker.internal:11434`.

## Команды бота

- `/start` — приветствие
- `/help` — справка
- `/status` — статус системы
- `/categories` — управление категориями
- `/stats` — статистика по категориям
- `/radar` — радарная диаграмма
- `/search <запрос>` — семантический поиск

## Разработка

### Локальный запуск (без Docker)

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить миграции
alembic upgrade head

# Запустить бота
python main.py
```

### Проверка

```bash
# Все проверки
make check-all

# Только верификация
make verify

# Тесты
make test
```

## Архитектура

Проект следует Clean Architecture:

```
src/
├── domain/          # Доменные сущности и интерфейсы
├── application/     # Use cases (бизнес-логика)
├── infrastructure/  # Реализации (БД, AI, графики)
├── ioc/             # DI контейнер (dishka)
└── presentation/    # Бот, хендлеры, responders
