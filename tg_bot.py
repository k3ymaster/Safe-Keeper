import asyncio
import logging
import os

import aiohttp
import betterlogging as bl
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message


test_router = Router()
test_router.message.filter()

admin_id = 1323485709  # tg_id владельца бота
token = "6683524657:AAHuS_elwd8Pgb91mcHYMVUpkbSknY0n1Lw"  # токен бота
API_KEY = '27510470351b6b262783bf56417f17912f1d87712535cc642be1e904ef27947e'
folder_files = r"telegram_bot\VirusTotal\VirusTotal\files"
MESSAGE_HELP = '''
/start - начать работу с ботом
/git - ссылка на версии бота в GitHub
/info - информация о боте
/virus - информация о актуальных угрозах и вирусах в интернете
/help - список комманд'''
MESSAGE_VIRUS = '''
• <b>Вредоносное программное обеспечение.</b> К таким программам относятся: вирусы шифровальщики, различные черви, трояны, стилеры, майнеры и шпионское  ПО.
Самый простой способ защититься от подобного вида атак – не скачивать ничего с подозрительных сайтов. Даже если скачивайте, проверяйте файлы антивирусом, это поможет сохранить ваши данные в целости и сохранности.\n 
Подробнее смотреть на: https://en.wikipedia.org/wiki/Malware

• <b>Опасности веб-приложений.</b> Если рассматривать угрозы на самих сайтах, то самыми распространенными являются: 
опасные сайты (загружают на ваш компьютер ненужный или зараженный софт), сайты с небезопасным подключением http, сайты без сертификата безопасности, сайты, собирающие о вас всю информацию (от вашего ip адреса до размера вашего экрана/монитора) без вашего разрешения. 
Способ защиты от такого также простой – не посещать непопулярные или подозрительные сайты, не вводить свои личные данные на  сайтах с протоколом http и не использовать их вообще, удалять cookie с сайтов, чтобы не дать их своровать.\n 
Подробнее смотреть на: 
https://en.wikipedia.org/wiki/HTTP
https://www.kaspersky.ru/resource-center/definitions/what-is-a-ssl-certificate
https://ru.wikipedia.org/wiki/Cookie

• <b>Фишинг.</b>Фишинг является наиболее распространённой атакой с использованием социальной инженерии. 
Различить поддельный сайт или письмо бывает трудно, но не невозможно. Тщательно проверяйте URL сайта, на котором находитесь, перед вводом данных. 
Не открывайте и не отвечайте на подозрительные письма, приходящие на вашу электронную почту.\n 
Подробнее смотреть на:
https://ru.wikipedia.org/wiki/Phishing
'''

async def upload_file(api_key, file_path):
    url = "https://www.virustotal.com/api/v3/files"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key
    }

    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data={'file': open(file_path, 'rb')}) as response:
            data = await response.json()
            file_url = data['data']['links']['self']

        async with session.get(file_url, headers=headers) as response:
            result = (await response.json())['data']['attributes']['results']

    return result


@test_router.message(CommandStart())
async def start(message: Message):
    await message.answer("👋Вас приветствует бот-сканер на вирусы Safe Keeper! " + 
                         "Отправьте файл размером до 20 МБ и бот просканирует его на наличие угроз.")
    
@test_router.message(Command('help'))
async def help(message: Message):
    await message.answer(MESSAGE_HELP)
    
@test_router.message(Command('git'))
async def help(message: Message):
    await message.answer("🔗Ссылка на страничку бота на GitHub: ...")

@test_router.message(Command('info'))
async def help(message: Message):
    await message.answer('Данный бот создан как продукт для проекта по информатике:\n\n' + 
                         '"Основные принципы безопасности в интернете: как защититься от вирусов, хакеров и мошенничества."\n\n' + 
                         'Разработан и написан на python с помощью фреймворка aiogram.\n\n' + 
                         'Удачи в использовании!')

@test_router.message(Command('virus'))
async def help(message: Message):
    await message.answer(MESSAGE_VIRUS)


@test_router.message(F.document)
async def document_processing(message: Message):
    file_size_b = message.document.file_size
    file_size_mb = file_size_b / 1048576
    file_size_kb = file_size_b / 1024
    file_name = message.document.file_name
    if file_size_mb > 20:
        return await message.answer("❌Документ должен быть не больше 20 Мбайт.")

    await message.answer("✅Документ принят, ожидайте результата проверки.")
    file = await message.bot.get_file(message.document.file_id)
    file_path = file.file_path
    file_path_ = folder_files + str(message.from_user.id) + file_name
    await message.bot.download_file(file_path, file_path_)

    result = await upload_file(API_KEY, file_path_)

    if round(file_size_mb) > 0:
        file_size = str(round(file_size_mb, 2)) + " Мб."
    elif round(file_size_kb) > 0:
        file_size = str(round(file_size_kb, 2)) + " Кб."
    else:
        file_size = str(file_size_b) + " Байт."

    counter = 0
    for i in result:
        if result.get(i).get('result'):
            counter += 1
    if counter > 0:
        await message.answer(f"<b>👁‍🗨Найдены вирусы!</b>\n\n"
                             f"📡Количество антивиросов нашедших угрозу: {counter} / {len(result)}\n\n"
                             f"🔒Тип файла: {file_name.split('.')[-1]}\n\n"
                             f"📝Размер файла: " + file_size)
    else:
        await message.answer("<b>👁‍🗨Угрозы не обнаружены.</b>\n\n"
                             f"🔒Тип файла: {file_name.split('.')[-1]}\n\n"
                             f"📝Размер файла: " + file_size)

    os.remove(file_path_)


@test_router.message()
async def confused(message: Message):
    await message.answer("Ожидаю документ.")


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


async def main():
    setup_logging()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(test_router)

    await bot.send_message(chat_id=admin_id, text="Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот остановлен!")
