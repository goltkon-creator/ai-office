import anthropic

client = anthropic.AsyncAnthropic()

SYSTEM = """Ты верстальщик лендингов. Твоя задача — собрать финальный результат.

На вход получаешь:
1. Бриф клиента
2. Текст от копирайтера
3. Структуру блоков от структуратора

Твой выход — готовый документ с:
1. КРАТКОЕ РЕЗЮМЕ — о чём лендинг, кому, какая цель
2. ИНСТРУКЦИЯ ДЛЯ TILDA — пошагово как собрать в Tilda (какие блоки, в каком порядке)
3. ГОТОВЫЙ ТЕКСТ ПО БЛОКАМ — скопируй и вставь в каждый блок
4. РЕКОМЕНДАЦИИ — цвета, шрифты, изображения

Пиши чётко, практично — клиент должен просто открыть Tilda и сделать всё по инструкции."""


async def run(brief: str, copy_text: str, structure: str) -> str:
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"БРИФ:\n{brief}\n\n"
                f"ТЕКСТ КОПИРАЙТЕРА:\n{copy_text}\n\n"
                f"СТРУКТУРА БЛОКОВ:\n{structure}\n\n"
                "Собери финальный результат для клиента."
            )
        }]
    )
    return message.content[0].text
