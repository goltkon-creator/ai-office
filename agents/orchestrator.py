from typing import Callable, Awaitable
from agents import copywriter, structurer, finalizer


async def run_orchestrator(
    task: str,
    send_update: Callable[[str, str, str], Awaitable[None]]
) -> str:
    """
    Главный агент — Ксенон.
    Принимает задачу, координирует работу команды, возвращает результат.
    """

    # Шаг 1: Копирайтер пишет текст
    await send_update("copywriter", "working", "Пишу текст для лендинга...")
    copy_text = await copywriter.run(task)
    await send_update("copywriter", "done", "Текст готов")

    # Шаг 2: Структуратор раскладывает по блокам Tilda
    await send_update("structurer", "working", "Разбиваю на блоки Tilda...")
    structure = await structurer.run(task, copy_text)
    await send_update("structurer", "done", "Структура готова")

    # Шаг 3: Финализатор собирает итоговый документ
    await send_update("finalizer", "working", "Собираю финальный результат...")
    result = await finalizer.run(task, copy_text, structure)
    await send_update("finalizer", "done", "Готово!")

    await send_update("xenon", "done", "Задача выполнена")

    return result
