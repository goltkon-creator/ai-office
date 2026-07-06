import anthropic

client = anthropic.AsyncAnthropic()

SYSTEM = """Ты профессиональный копирайтер для лендингов.
Твоя задача — написать продающий текст для каждого блока лендинга.

Ты пишешь ТОЛЬКО текст: заголовки, подзаголовки, описания, CTA-кнопки.
Формат ответа — чёткая структура с блоками.

Правила:
- Пиши конкретно, без воды
- Заголовки — короткие и цепляющие
- Описания — польза для клиента, не характеристики продукта
- CTA — призыв к действию с выгодой"""


async def run(brief: str) -> str:
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Напиши текст для лендинга по этому брифу:\n\n{brief}"
        }]
    )
    return message.content[0].text
