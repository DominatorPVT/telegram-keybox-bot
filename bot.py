from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os, json, glob

TOKEN = os.getenv("BOT_TOKEN")  # GitHub Secrets
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Load pass status JSON
def load_pass_status():
    with open("keybox_store/keybox-pass-check.json", "r") as f:
        return json.load(f)

# Find any XML file inside keybox_store/keybox/
def get_keybox_file():
    files = glob.glob("keybox_store/keybox/*.xml")
    return files[0] if files else None

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_name = message.from_user.first_name
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔑 Keybox", callback_data="keybox"))
    keyboard.add(types.InlineKeyboardButton("✅ Pass Check", callback_data="passcheck"))
    keyboard.add(types.InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/skyLabsUpdates"))
    
    start_text = (
        f"👋 Welcome, {user_name}!\n"
        f"You are now connected to the Telegram Keybox Bot.\n\n"
        f"🔹 Key Features:\n"
        f"🔑 Secure Keybox file access\n"
        f"✅ Play Integrity Pass Check (Basic, Device, Strong)\n"
        f"👨‍💻 Direct contact with the Developer\n\n"
        f"Please select an option below to continue."
    )
    await message.answer(start_text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "keybox")
async def send_keybox(callback_query: types.CallbackQuery):
    keybox_file = get_keybox_file()
    if keybox_file:
        await bot.send_document(callback_query.from_user.id, open(keybox_file, "rb"))
    else:
        await bot.send_message(callback_query.from_user.id, "⚠️ No keybox file found in keybox_store/keybox/.")

@dp.callback_query_handler(lambda c: c.data == "passcheck")
async def pass_check(callback_query: types.CallbackQuery):
    status = load_pass_status()
    result = (
        f"KEYBOX STATUS\n\n"
        f"Basic  : {status['Basic']}\n"
        f"Device : {status['Device']}\n"
        f"Strong : {status['Strong']}"
    )
    await bot.send_message(callback_query.from_user.id, result)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
