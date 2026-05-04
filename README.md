# telegram-keybox-bot

A simple Telegram bot built with **Python + aiogram**, hosted on **GitHub Actions**.

### Features
- 🔑 Send Keybox file
- ✅ Show Pass Check (Basic, Device, Strong) from JSON
- 👨‍💻 Developer profile link

### Setup
1. Create a bot with [BotFather](https://t.me/BotFather) and get the token.
2. Fork/clone this repo.
3. Add `BOT_TOKEN` in GitHub Secrets:
   - Go to **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `BOT_TOKEN`
   - Value: `<your-telegram-bot-token>`
4. Edit `keybox-pass-check.json` to update status (✅ / ❌).
5. Push changes → GitHub Actions will run the bot.

### Run Locally
```bash
pip install -r requirements.txt
python bot.py
