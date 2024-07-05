import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = '6505300772:AAHs9iuwSwHwmA_BfBpIJxAoFWiD3Ml0HYE'
ADMIN_USER_ID = '1250100261'  # Замените на user_id администратора
CHANNEL_LINK = 'https://t.me/+d5KJl1imPT1mNTAy'  # Замените на ссылку на закрытый канал
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


# Определение состояний
class Form(StatesGroup):
    name = State()
    age = State()
    city = State()
    spiritual_help = State()
    directions = State()
    power_source = State()


blocked_users = set()


# Начало диалога
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    if message.from_user.id in blocked_users:
        await bot.send_message(message.from_user.id, "Вы уже прошли тестирование и не подходите по интересам и "
                                                     "профилю для участия в сообществе.")
        return

    await Form.name.set()
    await bot.send_message(message.from_user.id,
                           "Для вступления в сообщество Проводников Света ответьте, пожалуйста, на несколько вопросов.")
    await bot.send_message(message.from_user.id, "Как вас зовут?")


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    keyboard = back_button_keyboard()
    await bot.send_message(message.from_user.id, "Сколько вам лет?", reply_markup=keyboard)


@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await Form.previous()
        await bot.send_message(message.from_user.id, "Как вас зовут?", reply_markup=back_button_keyboard())
        return

    async with state.proxy() as data:
        data['age'] = message.text
    await Form.next()
    keyboard = back_button_keyboard()
    await bot.send_message(message.from_user.id, "Из какого вы города?", reply_markup=keyboard)


@dp.message_handler(state=Form.city)
async def process_city(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await Form.previous()
        await bot.send_message(message.from_user.id, "Сколько вам лет?", reply_markup=back_button_keyboard())
        return

    async with state.proxy() as data:
        data['city'] = message.text
    await Form.next()
    keyboard = yes_no_keyboard()
    await bot.send_message(message.from_user.id, "Оказываете ли вы духовную помощь людям?", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data in ['Да', 'Нет'], state=Form.spiritual_help)
async def process_spiritual_help_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    await state.update_data(spiritual_help=data)

    if data == "Нет":
        await bot.edit_message_text("К сожалению, вы не подходите по интересам и профилю для участия в сообществе "
                                    "Проводников Света. Благодарим за уделенное время!",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        blocked_users.add(callback_query.from_user.id)
        await state.finish()
        return

    await Form.next()
    keyboard = directions_keyboard()  # Изменяем клавиатуру для следующего вопроса
    await bot.edit_message_text("В каком направлении вы работаете?",
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=keyboard)



@dp.callback_query_handler(
    lambda c: c.data in ['Ченнелинг', 'Энергопрактики', 'Целительство', 'Йога', 'Космоэнергетика', 'Ясновидение',
                         'Осознанные сновидения', 'Гипноз', 'Не указано мое направление'],
    state=Form.directions)
async def process_directions_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    await state.update_data(directions=data)

    if data == "Не указано мое направление":
        await bot.edit_message_text("К сожалению, вы не подходите по интересам и профилю для участия в сообществе "
                                    "Проводников Света. Благодарим за уделенное время!",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        blocked_users.add(callback_query.from_user.id)
        await state.finish()
        return

    await Form.next()
    keyboard = power_source_keyboard()
    await bot.edit_message_text("Кто или что является источником вашей силы?",
                                chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data in ['Бог (Абсолют)', 'Собственный дух', 'Любовь (Божественный Свет)',
                                                'Не указан источник моей силы'],
                           state=Form.power_source)
async def process_power_source_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    await state.update_data(power_source=data)

    if data == "Не указан источник моей силы":
        await bot.edit_message_text("К сожалению, вы не подходите по интересам и профилю для участия в сообществе Проводников Света. Благодарим за уделенное время!",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id)
        blocked_users.add(callback_query.from_user.id)
        await state.finish()
        return

    async with state.proxy() as data:
        user_data = {
            "username": callback_query.from_user.username,
            "name": data['name'],
            "age": data['age'],
            "city": data['city'],
            "spiritual_help": data['spiritual_help'],
            "directions": data['directions'],
            "power_source": data['power_source']
        }

        await bot.send_message(ADMIN_USER_ID, format_user_data(user_data))

        join_button = types.InlineKeyboardButton(text="Вступить в сообщество", url=CHANNEL_LINK)
        join_keyboard = types.InlineKeyboardMarkup().add(join_button)

        await bot.edit_message_text(f"{data['name']}, поздравляем! Теперь вы можете стать участником сообщества "
                                    f"Проводников Света.",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=join_keyboard)

    await state.finish()



# Регистрация обработчика "Назад" для каждого состояния
@dp.callback_query_handler(lambda c: c.data == 'Назад', state=Form.age)
@dp.callback_query_handler(lambda c: c.data == 'Назад', state=Form.city)
@dp.callback_query_handler(lambda c: c.data == 'Назад', state=Form.spiritual_help)
@dp.callback_query_handler(lambda c: c.data == 'Назад', state=Form.directions)
@dp.callback_query_handler(lambda c: c.data == 'Назад', state=Form.power_source)
async def process_back_button_callback(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == 'Form:age':
        await Form.previous()
        await bot.edit_message_text("Как вас зовут?",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup())
    elif current_state == 'Form:city':
        await Form.previous()
        await bot.edit_message_text("Сколько вам лет?",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=back_button_keyboard())
    elif current_state == 'Form:spiritual_help':
        await Form.previous()
        await bot.edit_message_text("Из какого вы города?",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=back_button_keyboard())
    elif current_state == 'Form:directions':
        await Form.previous()
        await bot.edit_message_text("Оказываете ли вы духовную помощь людям?",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=yes_no_keyboard())
    elif current_state == 'Form:power_source':
        await Form.previous()
        await bot.edit_message_text("В каком направлении вы работаете?",
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=directions_keyboard())
    else:
        await bot.send_message(callback_query.from_user.id,
                               "Вы находитесь в начале опроса. Нажмите 'Старт', чтобы начать заново.")


# Клавиатуры
def back_button_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="Назад"))
    return keyboard


def yes_no_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Да", callback_data="Да"),
        types.InlineKeyboardButton(text="Нет", callback_data="Нет"),
        types.InlineKeyboardButton(text="Назад", callback_data="Назад")
    ]

    for button in buttons:
        keyboard.add(button)

    return keyboard


def directions_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Ченнелинг", callback_data="Ченнелинг"),
        types.InlineKeyboardButton(text="Энергопрактики", callback_data="Энергопрактики"),
        types.InlineKeyboardButton(text="Целительство", callback_data="Целительство"),
        types.InlineKeyboardButton(text="Йога", callback_data="Йога"),
        types.InlineKeyboardButton(text="Космоэнергетика", callback_data="Космоэнергетика"),
        types.InlineKeyboardButton(text="Ясновидение", callback_data="Ясновидение"),
        types.InlineKeyboardButton(text="Осознанные сновидения", callback_data="Осознанные сновидения"),
        types.InlineKeyboardButton(text="Гипноз", callback_data="Гипноз"),
        types.InlineKeyboardButton(text="Не указано мое направление", callback_data="Не указано мое направление")
    ]

    for button in buttons:
        keyboard.add(button)
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="Назад"))
    return keyboard


def power_source_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Бог (Абсолют)", callback_data="Бог (Абсолют)"),
        types.InlineKeyboardButton(text="Собственный дух", callback_data="Собственный дух"),
        types.InlineKeyboardButton(text="Любовь (Божественный Свет)", callback_data="Любовь (Божественный Свет)"),
        types.InlineKeyboardButton(text="Не указан источник моей силы", callback_data="Не указан источник моей силы")
    ]

    for button in buttons:
        keyboard.add(button)
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="Назад"))
    return keyboard


# Форматирование данных пользователя для отправки администратору
def format_user_data(user_data):
    return (f"Новый пользователь:\n"
            f"Username: {user_data['username']}\n"
            f"Имя: {user_data['name']}\n"
            f"Возраст: {user_data['age']}\n"
            f"Город: {user_data['city']}\n"
            f"Духовная помощь: {user_data['spiritual_help']}\n"
            f"Направление: {user_data['directions']}\n"
            f"Источник силы: {user_data['power_source']}")


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_chat_members(message: types.Message):
    for member in message.new_chat_members:
        user_name = member.username if member.username else member.first_name
        welcome_message = (
            f"@{user_name}, приветствуем вас в сообществе Проводников Света ❤️\n"
            "Пожалуйста, напишите несколько слов о себе и дайте ссылку на свой сайт 🙏🏻"
        )
        await bot.send_message(message.chat.id, welcome_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
