import os
import requests
import datetime
import telebot

# === ENVIRONMENT VARIABLES ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# === SETTINGS ===
DAILY_TIME = "07:00"  # 7 AM
MARKETS = ["1", "2", "12", "OV1.5"]
TARGET_ODDS = 10.0

# === API ENDPOINT ===
API_URL = "https://api-football-v1.p.rapidapi.com/v3/odds"

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}


def fetch_odds():
    """Fetch today's odds from API-Football"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    params = {"date": today, "bookmaker": "1"}  # bookmaker 1 = Pinnacle

    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        print("Error fetching odds:", e)
        return []


def build_ticket():
    """Filter markets and accumulate odds until target is reached"""
    matches = fetch_odds()
    ticket = []
    total_odds = 1.0

    for match in matches:
        try:
            teams = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
            for bookmaker in match.get("bookmakers", []):
                for bet in bookmaker.get("bets", []):
                    market_name = bet.get("name", "")
                    for value in bet.get("values", []):
                        label = value.get("value")
                        odd = float(value.get("odd", 0))

                        if label in MARKETS and 1.2 <= odd <= 1.8:
                            ticket.append(f"{teams} → {label} ({odd})")
                            total_odds *= odd
                            if total_odds >= TARGET_ODDS:
                                return ticket, round(total_odds, 2)
        except:
            continue

    return ticket, round(total_odds, 2)


def send_daily_ticket():
    """Send ticket to Telegram"""
    ticket, total_odds = build_ticket()
    if not ticket:
        message = "⚠️ No safe picks found today."
    else:
        message = "🔥 Today’s Safe Picks (Accumulated ~10 Odds) 🔥\n\n"
        for idx, pick in enumerate(ticket, start=1):
            message += f"{idx}. {pick}\n"
        message += f"\n✅ Total Odds: {total_odds}"

    bot.send_message(CHAT_ID, message)


# === MAIN LOOP ===
if __name__ == "__main__":
    import schedule
    import time

    schedule.every().day.at(DAILY_TIME).do(send_daily_ticket)

    print("🤖 Bot is running...")

    while True:
        schedule.run_pending()
        time.sleep(30)
