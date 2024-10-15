import discord
from discord.ext import commands
import bot_settings
import bot



@bot.command(name="createprac", description="Creates a new practice schedule")
async def create_prac(ctx,interaction:discord.Interaction, channel:discord.TextChannel = None):
    category_name = 'Shankz'  # Replace with the actual category name
    channel_name = 'schedule'   # Replace with the actual channel name
    # Invoke the findchannel command
    schedchannel = await ctx.invoke(bot.get_command('findchannel'), category_name, channel_name)
    if channel:
        await channel.send("New prac awaiting to be scheduled")
    else:
        await ctx.send("Unable to locate channel")

