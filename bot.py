from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os, json, glob, subprocess

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8521407395  # fixed owner ID
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Admins list stored in memory (can be extended to file/db)
admins = set()

# Load pass status JSON
def load_pass_status():
    with open("keybox_store/keybox-pass-check.json", "r") as f:
        return json.load(f)

# Find any XML file inside keybox_store/keybox/
def get_keybox_file():
    files = glob.glob("keybox_store/keybox/*.xml")
    return files[0] if files else None

@dp.message_handler(commands=['help'])
async def help_cmd(message: types.Message):
    help_text = (
        "📖 Help Menu\n\n"
        "/start - Start bot\n"
        "/help - Show this help menu\n"
        "/addadmin <id> - Add admin (Owner only)\n"
        "/removeadmin <id> - Remove admin (Owner only)\n"
        "/adminlist - Show all admins\n"
        "/uploadkeybox - Upload new keybox file (Owner/Admin only)"
    )
    await message.answer(help_text)

@dp.message_handler(commands=['addadmin'])
async def add_admin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Only owner can add admins.")
    try:
        new_id = int(message.get_args())
        admins.add(new_id)
        await message.answer(f"✅ Admin {new_id} added successfully.")
    except:
        await message.answer("⚠️ Usage: /addadmin <user_id>")

@dp.message_handler(commands=['removeadmin'])
async def remove_admin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Only owner can remove admins.")
    try:
        rem_id = int(message.get_args())
        if rem_id in admins:
            admins.remove(rem_id)
            await message.answer(f"✅ Admin {rem_id} removed successfully.")
        else:
            await message.answer("⚠️ This ID is not an admin.")
    except:
        await message.answer("⚠️ Usage: /removeadmin <user_id>")

@dp.message_handler(commands=['adminlist'])
async def admin_list(message: types.Message):
    if not admins:
        await message.answer("ℹ️ No admins added yet.")
    else:
        admin_list_text = "👥 Current Admins:\n" + "\n".join([str(a) for a in admins])
        await message.answer(admin_list_text)

@dp.message_handler(commands=['uploadkeybox'])
async def upload_keybox(message: types.Message):
    if message.from_user.id != OWNER_ID and message.from_user.id not in admins:
        return await message.answer("❌ Only owner or admins can upload keybox.")
    if not message.document:
        return await message.answer("📂 Please send a .xml file with this command.")
    if not message.document.file_name.endswith(".xml"):
        return await message.answer("⚠️ Only .xml files are allowed.")
    
    file = await message.document.download(destination_file=f"keybox_store/keybox/{message.document.file_name}")
    await message.answer(f"✅ New keybox file {message.document.file_name} uploaded successfully.")

    # Commit to GitHub (branch master)
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"New keybox uploaded by {message.from_user.id}"], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        await message.answer("📤 Keybox file pushed to GitHub master branch.")
    except Exception as e:
        await message.answer(f"⚠️ GitHub push failed: {e}")

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
