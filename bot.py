# bot.py
import os
import time

from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import time

from redis_listener import RedisListener

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER = os.getenv("SERVER")
SERVER_ID = os.getenv("SERVER_ID")

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

redis_listener = RedisListener()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    
    for guild in bot.guilds:
        if guild.name == SERVER:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
    
    await bot.tree.sync(guild=discord.Object(id=guild.id))
    redis_listener.start_listener()
    check_loop.start()
    

@tasks.loop(seconds=2)
async def check_loop():
    servers = redis_listener.get_servers()
    print("Checking loop")
    for name, server in servers.items():
        cur_time = time.time()
        if cur_time * 1000 - server.last_update > 5000:
            redis_listener.update_online_status(name, False)
            print(f"Server {name} is offline")
            for guild in bot.guilds:
                if guild.name == SERVER:
                    break
            channel = discord.utils.get(guild.channels, name="general")
            await channel.send(f"Server {name} is offline")

@bot.tree.command(
    name="online",
    description="Check if a PVPCamp server is online",
    guild=discord.Object(SERVER_ID)
)
async def status_check(intrctn: discord.Interaction):
    name = "build"
    print("Checking if the server is online")
    servers = redis_listener.get_servers()
    if name not in servers:
        await intrctn.response.send_message("Server not found")
        return
    is_online = servers[name].currently_online
    res = f"Server {name} is " + (is_online * "online!") + (~is_online * "offline!")
    print(res)
    
    await intrctn.response.send_message(res)

bot.run(TOKEN)