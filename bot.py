import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get keys from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running! Type /games to get today's picks.")

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"date": "2025-09-05"}  # can be changed dynamically
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        fixtures = data.get("response", [])

        if not fixtures:
            await update.message.reply_text("No games found today.")
            return

        message = "🎯 Today's Picks:\n\n"
        for match in fixtures[:10]:  # limit to 10
            teams = match["teams"]
            home = teams["home"]["name"]
            away = teams["away"]["name"]
            message += f"{home} vs {away} → OV1.5 ✅\n"

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("games", games))
    app.run_polling()

if __name__ == "__main__":
    main()
