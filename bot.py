import os
import requests
import base64
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

def download_photo(file_id):
    tg_file = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile",
        params={"file_id": file_id}
    ).json()

    file_path = tg_file["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    return requests.get(file_url).content

def generate_marketplace_image(image_bytes):
    url = "https://api.openai.com/v1/images/edits"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    prompt = (
        "Фотореалистичный интерьер уровня маркетплейса. "
        "Современная светлая гостиная, минимализм, дневной свет. "
        "Ковер аккуратно вписан в интерьер, центр композиции. "
        "Каталожное качество, без текста, без водяных знаков."
    )

    files = {
        "image": ("rug.jpg", image_bytes, "image/jpeg")
    }

    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024"
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()

    img_base64 = response.json()["data"][0]["b64_json"]
    return base64.b64decode(img_base64)

@dp.message(F.photo)
async def handle_photo(message: Message):
    await message.answer("Принял фото. Делаю карточку 🔥")

    file_id = message.photo[-1].file_id
    image_bytes = download_photo(file_id)
    result_image = generate_marketplace_image(image_bytes)

    await bot.send_photo(message.chat.id, result_image, caption="Готово ✅")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
