import discord
from discord import app_commands
from discord.ext import commands
import requests
import docx
import logging
import os

# Enable basic logging
logging.basicConfig(level=logging.INFO)

# API keys and token
API_KEY = "your_deepinfra_api_key"
DISCORD_TOKEN = "your_discord_bot_token"

# Load knowledge from .docx file
def load_knowledge_from_docx(path):
    if not os.path.isfile(path):
        logging.error(f"File not found: {path}")
        return "No knowledge available (file missing)."
    
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

# Load knowledge once at startup
custom_knowledge = load_knowledge_from_docx("knowledge.docx")

# Set up bot with message content intent
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Define a cog with the slash command
class MyBotClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="question",
        description="Ask the AI a question using the custom knowledge base."
    )
    async def question(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer(thinking=True)

        url = "https://api.deepinfra.com/v1/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [
                {"role": "system", "content": f"Answer only using the following context:\n\n{custom_knowledge}"},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]

            if len(reply) > 2000:
                reply = reply[:1997] + "..."

            await interaction.followup.send(reply)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

# Register the cog and sync slash commands
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced globally: {len(synced)}")
    except Exception as e:
        print(f"Error during command sync: {e}")

    await bot.add_cog(MyBotClient(bot))

# Run the bot
bot.run(DISCORD_TOKEN)
