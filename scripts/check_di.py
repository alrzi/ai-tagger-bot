#!/usr/bin/env python3
"""Проверяет DI контейнер."""

import sys
import os

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_di_container() -> bool:
    """Проверяет что DI контейнер создаётся без ошибок."""
    try:
        from src.ioc.container import make_container
        make_container()
        print("✅ DI контейнер создаётся")
        return True
    except Exception as e:
        print(f"❌ DI контейнер: {e}")
        return False


def main() -> None:
    if not check_di_container():
        sys.exit(1)
    print("✅ Все проверки пройдены")


if __name__ == "__main__":
    main()
