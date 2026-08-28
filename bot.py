import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import random
from google import genai
import aiohttp
import asyncio
import time

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is connected to Discord!")

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
            model="gemini-3.6-lite", 
            contents    =prompt
        )
    )

    text = response.text
    if len(text) > 1995:
        text = text[:1995] + "..."

    await interaction.followup.send(text)

@bot.hybrid_command(name="joke", description="Tells a joke")
async def joke(ctx: commands.Context):
    await ctx.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://official-joke-api.appspot.com/random_joke") as response:
            data = await response.json()
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


@bot.hybrid_command(name="coinflip", description="Flip a coin")
async def coinflip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"The coin landed on {result}")


@bot.hybrid_command(name="diceroll", description="Roll a dice")
async def diceroll(ctx):
    await ctx.send(f"You rolled the number {random.randint(1, 6)}") 

@bot.hybrid_command(name="quote", description="Tells a quote"   )
async def quote(ctx):
    await ctx.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.quotable.io/random") as response:
            data = await response.json()
            await ctx.send(f"{data['content']} - {data['author']}")

@bot.hybrid_command(name="reminder", description="Set a reminder")
async def reminder(ctx, time:int, message:str):
    await ctx.send(f"Reminder set for {time} minutes from now.")
    await asyncio.sleep(time * 60)
    await ctx.send(f"Reminder: {message} ({ctx.author.mention})")


@bot.hybrid_command(name="weather", description="Get live weather")
async def weather(ctx, city:str):
    url = f"https://wttr.in/{city}?format=3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    await ctx.send(f"Weather in {city} : {data}")
                else:
                    await ctx.send("Couldn't fetch weather data")

@bot.hybrid_command(name="serverinfo", description="Get server info")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.blue())
    embed.add_field(name="Sercer Name", value=guild.name, inline=False)
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Member Count", value=guild.member_count, inline=False)
    embed.add_field(name="Owner", value=guild.owner, inline=False)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Boost Count", value=guild.premium_subscription_count, inline=False)
    embed.set_footer(text=f"For {ctx.author}")
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="time", description="Gets the current time")
async def time(ctx):
    await ctx.send(f"The current time is: {time.ctime()}")


@bot.hybrid_command(name="whoami", description="Who am I?")
async def whoami(ctx):
    await ctx.send(f"You are {ctx.author.name}")

@bot.hybrid_command(name="whoareu", description="Who are you?")
async def whoareu(ctx):
    await ctx.send(f"I am AllBot, your all-in-one Discord bot")


bot.run(TOKEN)

