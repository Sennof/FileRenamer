#!/usr/bin/env python3
"""
Пакетное переименование файлов в директории.

Режимы:
  1 - по числам:  1, 2, 3, 4 ...
  2 - по буквам:  a, b, c ... z, aa, ab, ac ...

Расширения файлов сохраняются. Подпапки и скрытые файлы не затрагиваются.
"""

import os
import re
import uuid


def natural_key(name: str):
    """Естественная сортировка: file2 идёт перед file10."""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", name)]


def number_to_letters(n: int) -> str:
    """1 -> a, 26 -> z, 27 -> aa, 28 -> ab, ..."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(ord("a") + remainder) + result
    return result


def ask_directory() -> str:
    while True:
        path = input("\nВведите путь к директории: ").strip().strip('"').strip("'")
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            return path
        print("Такой директории не существует, попробуйте ещё раз.")


def ask_mode() -> int:
    print("\nВыберите вариант переименования:")
    print("  1 - по числам  (1, 2, 3, 4 ...)")
    print("  2 - по буквам  (a, b, c ... z, aa, ab, ac ...)")
    while True:
        choice = input("Ваш выбор (1/2): ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Введите 1 или 2.")


def get_files(directory: str) -> list[str]:
    files = [
        f
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and not f.startswith(".")
    ]
    return sorted(files, key=natural_key)


def build_plan(files: list[str], mode: int) -> list[tuple[str, str]]:
    plan = []
    for index, old_name in enumerate(files, start=1):
        _, ext = os.path.splitext(old_name)
        label = str(index) if mode == 1 else number_to_letters(index)
        plan.append((old_name, label + ext))
    return plan


def apply_plan(directory: str, plan: list[tuple[str, str]]) -> None:
    """
    Переименование в два этапа (через временные имена), чтобы новые имена
    не перезаписали существующие файлы, например при переименовании 2.txt -> 1.txt
    и 1.txt -> 2.txt.
    """
    temp_names = []

    # Этап 1: старое имя -> временное
    for old_name, new_name in plan:
        temp_name = f".tmp_{uuid.uuid4().hex}"
        os.rename(os.path.join(directory, old_name), os.path.join(directory, temp_name))
        temp_names.append((temp_name, old_name, new_name))

    # Этап 2: временное -> итоговое
    for temp_name, old_name, new_name in temp_names:
        os.rename(os.path.join(directory, temp_name), os.path.join(directory, new_name))


def run_once() -> None:
    directory = ask_directory()
    mode = ask_mode()

    files = get_files(directory)
    if not files:
        print("\nВ директории нет файлов для переименования.")
        return

    plan = build_plan(files, mode)

    print(f"\nНайдено файлов: {len(plan)}. Примеры переименования:")
    for old_name, new_name in plan[:5]:
        print(f"  {old_name}  ->  {new_name}")
    if len(plan) > 5:
        print("  ...")

    confirm = input("\nПродолжить? (y/n): ").strip().lower()
    if confirm not in ("y", "yes", "д", "да"):
        print("Отменено, файлы не тронуты.")
        return

    try:
        apply_plan(directory, plan)
    except OSError as e:
        print(f"\nОшибка при переименовании: {e}")
        print("Часть файлов могла получить временные имена вида .tmp_... — проверьте директорию.")
        return

    print(f"\nГотово! Переименовано файлов: {len(plan)}.")


def main() -> None:
    while True:
        run_once()

        print("\nЧто дальше?")
        print("  1 - начать заново")
        print("  2 - закончить")
        while True:
            choice = input("Ваш выбор (1/2): ").strip()
            if choice in ("1", "2"):
                break
            print("Введите 1 или 2.")

        if choice == "2":
            print("Работа завершена.")
            break


if __name__ == "__main__":
    main()