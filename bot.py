import discord
from discord.ext import commands
import requests
import docx
import logging

logging.basicConfig(level=logging.INFO)


API_KEY = ""


DISCORD_TOKEN = ""


def lade_wissen_aus_docx(pfad):
    doc = docx.Document(pfad)
    return "\n".join([para.text for para in doc.paragraphs])

eigenes_wissen = lade_wissen_aus_docx("knowledge.docx")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")

@bot.command()
async def question(ctx, *, user_input):
    await ctx.send("🤖 Thinking...")

    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": f"Answer only using the following context:\n\n{eigenes_wissen}"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]

        if len(reply) > 2000:
            reply = reply[:1997] + "..."

        await ctx.send(reply)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

bot.run(DISCORD_TOKEN)
