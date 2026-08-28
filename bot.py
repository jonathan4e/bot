import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import random
from google import genai
import aiohttp
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is connected")

@bot.tree.command(name="ping", description="Ping the bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention} to the server! :wave:")

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@bot.tree.command(name="ai", description="Ask AI a question")
async def ai_command(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None, 
        lambda: gemini_client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
    )

    text = response.text
    if len(text) > 1990:
        text = text[:1990] + "..."

    await interaction.followup.send(text)

@bot.hybrid_command(name="joke", description="Tells a joke")
async def joke(ctx: commands.Context):
    await ctx.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
            data = await resp.json()
    await ctx.send(f"{data['setup']} - {data['punchline']}")

@bot.hybrid_command(name="rps", description="Play Rock Paper Scissors")
@app_commands.choices(choice=[
    app_commands.Choice(name="Rock", value="rock"),
    app_commands.Choice(name="Paper", value="paper"),
    app_commands.Choice(name="Scissors", value="scissors")
])
async def rps(ctx: commands.Context, choice: str):
    user = choice.value.lower() if hasattr(choice, 'value') else choice.lower()
    botchoice = random.choice(["rock", "paper", "scissors"])
    
    if user == botchoice:
        await ctx.send(f"It's a tie! Both of us chose {user}.")
    elif (user == "rock" and botchoice == "scissors") or \
         (user == "paper" and botchoice == "rock") or \
         (user == "scissors" and botchoice == "paper"):
        await ctx.send(f"You win! You chose {user} and I chose {botchoice}.")
    else:
        await ctx.send(f"You lose! You chose {user} and I chose {botchoice}.")


bot.run(TOKEN)