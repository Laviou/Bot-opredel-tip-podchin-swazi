import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

API_TOKEN = '8089364227:AAHCKBBivc5jhf2YQuWsdnwOM3_rTuqhcSc'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

ADJECTIVE_ENDINGS = ['ый', 'ий', 'ая', 'яя', 'ое', 'ее', 'ой', 'ей', 'ые', 'ие', 'их', 'ых', 'ому', 'ему', 'ою', 'ею']
VERB_ENDINGS = ['ть', 'ти', 'чь', 'ться', 'тся', 'л', 'ла', 'ло', 'ли', 'ем', 'ет', 'ете', 'ут', 'ют', 'им', 'ишь',
                'ите', 'ат', 'ят']
ADVERB_ENDINGS = ['о', 'е', 'и', 'у', 'ю', 'ой', 'ей']
NOUN_CASES = {
    'родительный': ['а', 'я', 'ы', 'и', 'ов', 'ев', 'ей', 'ок', 'ек', 'ь', 'ью', 'ии'],
    'дательный': ['у', 'ю', 'ам', 'ям'],
    'винительный': ['у', 'ю', 'а', 'я', 'о', 'е'],
    'творительный': ['ом', 'ем', 'ой', 'ей', 'ами', 'ями', 'ою', 'ею'],
    'предложный': ['е', 'и', 'ах', 'ях'],
    'именительный': ['', 'а', 'я', 'о', 'е', 'ы', 'и', 'й', 'ь']
}

ACCUSATIVE_VERBS = ['читать', 'видеть', 'любить', 'писать', 'знать', 'смотреть',
                    'понимать', 'желать', 'слышать', 'чувствовать', 'петь', 'рисовать',
                    'делать', 'строить', 'готовить', 'покупать', 'продавать', 'держать',
                    'нести', 'вести', 'вести', 'ждать', 'искать', 'находить']

GENITIVE_TRIGGERS = ['дом', 'книга', 'стакан', 'чашка', 'кусок', 'бутылка', 'пакет',
                     'коробка', 'тарелка', 'ложка', 'вилка', 'ножик', 'от', 'без',
                     'для', 'до', 'из', 'у', 'около', 'возле', 'вместо', 'после']

def get_part_of_speech(word):
    word_lower = word.lower()

    for ending in ADJECTIVE_ENDINGS:
        if word_lower.endswith(ending):
            return 'прилагательное'

    for ending in VERB_ENDINGS:
        if word_lower.endswith(ending):
            return 'глагол'

    for ending in ADVERB_ENDINGS:
        if word_lower.endswith(ending):
            return 'наречие'

    return 'существительное'

def get_case_simplified(word):
    word_lower = word.lower()

    for case in ['родительный', 'дательный', 'творительный', 'предложный', 'винительный', 'именительный']:
        for ending in NOUN_CASES[case]:
            if word_lower.endswith(ending):
                return case

    return 'именительный'

def determine_connection_type(phrase):
    """
    Определяет тип подчинительной связи в словосочетании.
    """
    phrase = phrase.strip()

    if not phrase:
        return None

    words = phrase.split()

    if len(words) < 2:
        return None

    word1 = words[0]
    word2 = words[1] if len(words) > 1 else ""

    pos1 = get_part_of_speech(word1)
    pos2 = get_part_of_speech(word2)

    case1 = get_case_simplified(word1) if pos1 == 'существительное' else None
    case2 = get_case_simplified(word2) if pos2 == 'существительное' else None

    if pos2 == 'существительное' and pos1 in ['прилагательное', 'числительное']:

        main_word = word2
        main_pos = pos2

        dependent_word = word1
        dependent_pos = pos1
        dependent_case = case1

    elif pos1 == 'глагол' and pos2 in ['существительное', 'наречие']:

        main_word = word1
        main_pos = pos1

        dependent_word = word2
        dependent_pos = pos2
        dependent_case = case2

    elif pos2 == 'глагол' and pos1 in ['существительное', 'наречие']:

        main_word = word2
        main_pos = pos2

        dependent_word = word1
        dependent_pos = pos1
        dependent_case = case1

    else:

        main_word = word2
        main_pos = pos2
        dependent_word = word1
        dependent_pos = pos1
        dependent_case = case1


    main_word_lower = main_word.lower()
    dependent_word_lower = dependent_word.lower()
    phrase_lower = phrase.lower()

    if dependent_pos == 'прилагательное' and main_pos == 'существительное':
        connection_type = "СОГЛАСОВАНИЕ"
        reason = f"Зависимое слово ({dependent_word.lower()}) согласуется с главным ({main_word.lower()}) в роде, числе и падеже."
        question = f"{main_word.lower()} (какой?) {dependent_word.lower()}"

    elif (main_pos == 'глагол' and dependent_pos == 'существительное' and
          main_word_lower in ACCUSATIVE_VERBS):
        connection_type = "УПРАВЛЕНИЕ"
        reason = f"Глагол '{main_word.lower()}' требует винительного падежа от зависимого слова."
        question = f"{main_word.lower()} (что?) {dependent_word.lower()}"

    elif (main_pos == 'существительное' and dependent_pos == 'существительное' and
          any(dependent_word_lower.endswith(end) for end in NOUN_CASES['родительный'])):
        connection_type = "УПРАВЛЕНИЕ"
        reason = f"Зависимое слово ({dependent_word.lower()}) стоит в родительном падеже."
        question = f"{main_word.lower()} (чего? чей?) {dependent_word.lower()}"

    elif any(prep in phrase_lower for prep in ['от ', 'без ', 'для ', 'до ', 'из ', 'у ', 'около ', 'возле ']):
        connection_type = "УПРАВЛЕНИЕ"
        reason = "Предлог требует родительного падежа."
        question = f"{main_word.lower()} (чего?) {dependent_word.lower()}"

    elif (dependent_pos == 'существительное' and dependent_case == 'дательный'):
        connection_type = "УПРАВЛЕНИЕ"
        reason = f"Зависимое слово ({dependent_word.lower()}) стоит в дательном падеже."
        question = f"{main_word.lower()} (кому? чему?) {dependent_word.lower()}"

    elif (dependent_pos == 'существительное' and dependent_case == 'творительный'):
        connection_type = "УПРАВЛЕНИЕ"
        reason = f"Зависимое слово ({dependent_word.lower()}) стоит в творительном падеже."
        question = f"{main_word.lower()} (кем? чем?) {dependent_word.lower()}"

    elif dependent_pos == 'наречие' and main_pos == 'глагол':
        connection_type = "ПРИМЫКАНИЕ"
        reason = f"Зависимое слово ({dependent_word.lower()}) связано с главным ({main_word.lower()}) только по смыслу, так как является неизменяемой частью речи."
        question = f"{main_word.lower()} (как?) {dependent_word.lower()}"

    elif dependent_pos == 'наречие' and main_pos == 'прилагательное':
        connection_type = "ПРИМЫКАНИЕ"
        reason = f"Зависимое слово ({dependent_word.lower()}) связано с главным ({main_word.lower()}) только по смыслу."
        question = f"{main_word.lower()} (насколько?) {dependent_word.lower()}"

    elif main_pos == 'глагол' and dependent_pos == 'существительное':
        connection_type = "УПРАВЛЕНИЕ"
        reason = f"Глагол '{main_word.lower()}' управляет падежом зависимого существительного."
        question = f"{main_word.lower()} (что?) {dependent_word.lower()}"

    else:
        if dependent_pos == 'прилагательное':
            connection_type = "СОГЛАСОВАНИЕ"
            reason = f"Зависимое слово ({dependent_word.lower()}) согласуется с главным ({main_word.lower()})."
            question = f"{main_word.lower()} (какой?) {dependent_word.lower()}"
        elif dependent_case and dependent_case != 'именительный':
            connection_type = "УПРАВЛЕНИЕ"
            reason = f"Зависимое слово ({dependent_word.lower()}) стоит в {dependent_case} падеже."

            questions_by_case = {
                'родительный': 'кого? чего?',
                'дательный': 'кому? чему?',
                'винительный': 'кого? что?',
                'творительный': 'кем? чем?',
                'предложный': 'о ком? о чём?'
            }
            q_word = questions_by_case.get(dependent_case, '?')
            question = f"{main_word.lower()} ({q_word}) {dependent_word.lower()}"
        else:
            connection_type = "ПРИМЫКАНИЕ"
            reason = f"Зависимое слово ({dependent_word.lower()}) связано с главным ({main_word.lower()}) по смыслу."
            question = f"{main_word.lower()} (как?) {dependent_word.lower()}"

    return {
        'type': connection_type,
        'reason': reason,
        'main': f"{main_word.lower()} ({main_pos})",
        'dependent': f"{dependent_word.lower()} ({dependent_pos})",
        'question': question
    }


@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = """⭐️ Здравствуйте! ⭐️

Это бот для определения типа подчинительной связи в словосочетании.

Чтобы начать работу введите *начать*, чтобы завершить работу введите *завершить*."""

    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.text)
async def handle_text(message: Message):
    user_text = message.text.strip()

    if user_text.lower() in ['начать', 'start']:
        await message.answer("🌟Введите словосочетание:")

    elif user_text.lower() in ['завершить', 'конец', 'стоп', 'stop', 'завершить']:
        await message.answer("💫 Спасибо за то что воспользовались нашим ботом!")

    else:
        result = determine_connection_type(user_text)

        if result is None:
            await message.answer("❌ Пожалуйста, введите корректное словосочетание (минимум два слова).")
            return

        response = f"""✏️*Словосочетание:* {user_text}

📍*Тип подчинительной связи:* {result['type']}

➡️*Признак связи:* {result['reason']}

📒*Синтаксический анализ:*

❓{result['question']}

○ *Главное слово:* {result['main']}
○ *Зависимое слово:* {result['dependent']}

Введите следующее словосочетание для анализа или *завершить* для выхода."""

        await message.answer(response, parse_mode="Markdown")

async def main():
    print("Бот запущен...")
    print("Примеры словосочетаний для проверки:")
    print("- красивый дом (согласование)")
    print("- читать книгу (управление)")
    print("- бежать быстро (примыкание)")
    print("- дом отца (управление)")
    print("- очень красивый (примыкание)")
    print("- говорить с другом (управление)")
    print("- писать карандашом (управление)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")