# from aiogram import Bot, Dispatcher, types
# from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
# from aiogram.utils import executor
# from django.conf import settings
# from django.core.management.base import BaseCommand
# import logging
# import time
#
#
# # Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)
# # Объект бота
# bot = Bot(token=settings.TELEGRAMBOT_API_TOKEN)
# # Диспетчер - нужен чтобы реагировать на определенные события ( @dp.message_handler )
# dp = Dispatcher(bot)
#
#
# # название кнопки-клавиатуры в чат-боте
# button = KeyboardButton('Some Button')
# # инициализируем появление клавиатуры в чате, resize_keyboard - форматирование размера,
# # one_time_keyboard - исчезает после нажатия
# price_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
# # добавляем кнопку в клавиатуру
# price_keyboard.add(button)
#
#
# # реагируем на команды "/help" и "/start".
# @dp.message_handler(commands=["help", "start"])
# async def command_help(message: types.Message):
#     # ответ бота, reply_markup отображает выбранную клавиатуру
#     await message.answer("Input Some Message", parse_mode="HTML", reply_markup=price_keyboard)
#
#
# # реакция на нажатие кнопки
# @dp.message_handler(lambda message: message.text == "Some Button")
# async def certain_message(msg: types.Message):
#     # Ответ бота. Импортируем файл price_parser и вызываем функцию price_parser()
#     msg_to_answer = 'Some msg'
#     await bot.send_message(msg.from_user.id, msg_to_answer)
#
#
# # реакция на ввод текста
# @dp.message_handler()
# async def query_telegram(msg: types.Message):
#     print(msg.text)
#
#     await bot.send_message(msg.chat.id, 'understandable, have a nice day')
#
#
# class Command(BaseCommand):
#     help = 'Implemented to Django application telegram bot setup command'
#
#     def handle(self, *args, **kwargs):
#         executor.start_polling(dp)



from django.conf import settings
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from ...models import Category, Producer
import logging


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAMBOT_API_TOKEN)

dp = Dispatcher(bot)

button = KeyboardButton('Categories')

button_producers = KeyboardButton('Producers')

# инициализируем появление клавиатуры в чате, resize_keyboard - форматирование размера,
# one_time_keyboard - исчезает после нажатия
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
# добавляем кнопку в клавиатуру
keyboard.add(button)
keyboard.add(button_producers)

keyboard_producers_only = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
keyboard_producers_only.add(button_producers)


# реагируем на команды "/help" и "/start".
@dp.message_handler(commands=["help", "start"])
async def command_help(message: types.Message):
    # ответ бота, reply_markup отображает выбранную клавиатуру
    await message.answer("Input Some Message", reply_markup=keyboard)


@sync_to_async()
def get_categories():
    return list(Category.objects.all())


# реакция на нажатие кнопки
@dp.message_handler(lambda message: message.text == "Categories")
async def certain_message(msg: types.Message):
    categories = await get_categories()

    msg_to_answer = ''
    for cat in categories:
        msg_to_answer += f"Category: {cat.name}\n{cat.description}\n"
    await bot.send_message(msg.from_user.id, msg_to_answer, reply_markup=keyboard_producers_only)


@sync_to_async()
def get_producers():
    return list(Producer.objects.all())


@dp.message_handler(lambda message: message.text == "Producers")
async def producers_callback(msg: types.Message):
    producers = await get_producers()

    msg_to_answer = ''
    for prod in producers:
        msg_to_answer += f"Producer: {prod.name}\n"

    await bot.send_message(msg.from_user.id, msg_to_answer)



# реакция на ввод текста
@dp.message_handler()
async def query_telegram(msg: types.Message):
    print(msg.text)
    await bot.send_message(msg.chat.id, 'understandable, have a nice day')


class Command(BaseCommand):
    help = 'Test TG Bot'

    def handle(self, *args, **options):
        executor.start_polling(dp)











