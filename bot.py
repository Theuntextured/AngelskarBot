import discord
from discord.ext import commands
import bot_settings

class Team:
    def __init__(self) -> None:
        self.members = []
        self.tryouts = []
        self.standins = []
        self.captain = None
        self.vice_captain = None

        self.name = ""
        self.symbol = ""
        

class Bot(commands.Bot):
    def start_bot(self):
        bot_settings.bot = self
        self.bot_settings = bot_settings.load()
        try:
            with open("token.txt") as file:
                token = file.read()
        except:
            return
        self.run(token)

    async def log_message(self, message:str) -> bool:
        print(message)
        channel:discord.TextChannel = self.bot_settings.get_log_channel()
        if channel == None:
            return False
        await channel.send(message)
        return True

bot = Bot(intents=discord.Intents.all(), command_prefix="/")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello world.")

@bot.tree.command(name="help",description="Prints some information about the bot and commands available.")
async def help(interaction:discord.Interaction):
    out = "# AngelSkar Bot Help\n"
    out = out + "## Available Commands:\n"
    for c in bot.tree.get_commands():
        out = out + f"* `/{c.name}`: {c.description}\n"
    await interaction.response.send_message(out)

@bot.tree.command(name="logchannel", description="Sets the log channel to use.", )
async def log_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        await interaction.response.send_message(f"The log channel is currently linked to {bot.bot_settings.get_log_channel().mention}")
    else:
        bot.bot_settings.set_log_channel(channel)

        message = f"Linked the log to channel {channel.mention}"
        await interaction.response.send_message(message)
        await channel.send(message)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.log_message("Bot started!")

@bot.event
async def on_member_update(before:discord.Member, after:discord.Member):
    global bot
    if before.roles == after.roles:
        return
    
    guild = after.guild

    for r in guild.roles:
        await bot.log_message(r.name)