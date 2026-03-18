import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# ===================== INTENTS =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===================== DATABASE =====================
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"sell": [], "coins": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ===================== READY =====================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

# ===================== AUTO MODERATION =====================
BAD_WORDS = ["scam", "hack", "fraud"]

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    for word in BAD_WORDS:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention} Watch your language!")
            return
    await bot.process_commands(message)

# ===================== PRICE SYSTEM =====================
PRICE_DB = {
    "roger": 5000,
    "shanks": 4500,
    "luffy": 3000
}

def get_price(ex):
    return PRICE_DB.get(ex.lower(), 1000)

# ===================== SLASH COMMANDS =====================
@bot.tree.command(name="sell", description="List your account")
@app_commands.describe(ex="EX character")
async def sell(interaction: discord.Interaction, ex: str):
    data["sell"].append({"user": interaction.user.id, "ex": ex})
    save_data()
    price = get_price(ex)
    await interaction.response.send_message(f"🛒 Listed {ex}\n💸 Suggested Price: {price}")

@bot.tree.command(name="buy", description="Find an account to buy")
@app_commands.describe(ex="EX character")
async def buy(interaction: discord.Interaction, ex: str):
    for s in data["sell"]:
        if s["ex"].lower() == ex.lower():
            seller = await bot.fetch_user(s["user"])
            await interaction.response.send_message(f"🔥 Match Found!\n{interaction.user.mention} 🤝 {seller.mention}")
            return
    await interaction.response.send_message(f"No match found for {ex}.")

# ===================== RUN BOT =====================
# Load token from Railway environment variable
token = os.getenv("TOKEN")
if not token:
    print("❌ TOKEN not found! Add it in Railway Variables.")
else:
    bot.run(token)
