import anthropic

client = anthropic.AsyncAnthropic()

SYSTEM = """Ты эксперт по структуре лендингов на Tilda.
Твоя задача — взять готовый текст и разложить его по блокам Tilda.

Ты знаешь все типы блоков Tilda: Hero, Features, Testimonials, CTA, FAQ, Footer и т.д.
Для каждого блока указывай:
- Тип блока Tilda (например: BA610, BF9, T706 и т.д.)
- Содержимое блока из предоставленного текста
- Рекомендации по оформлению

Формат ответа — JSON-подобная структура, понятная для верстальщика."""

SYSTEM_TEXT = """Ты эксперт по структуре лендингов на Tilda.
Твоя задача — взять готовый текст и разложить его по блокам Tilda.

Для каждого блока указывай:
- Название блока (Hero, Features, About, Testimonials, CTA, FAQ, Footer)
- Текст, который туда идёт
- Рекомендуемые настройки (цвет фона, выравнивание)

Отвечай структурированно, по блокам."""


async def run(brief: str, copy_text: str) -> str:
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_TEXT,
        messages=[{
            "role": "user",
            "content": f"Бриф:\n{brief}\n\nГотовый текст от копирайтера:\n{copy_text}\n\nРаздели по блокам Tilda."
        }]
    )
    return message.content[0].text
