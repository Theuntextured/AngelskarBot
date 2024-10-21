from bot import *


@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.log_message("Bot started!")
    bot.angelskar_guild = discord.utils.get(bot.guilds, id=1049126797465362523)
    util.setup_rank_emojis(bot)
    await bot.update_teams()
    await bot.update_staff_channel()


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):

    # inefficient but fuck you
    if before.roles == after.roles:
        return
    for t in bot.teams.values():
        t.update_members()
    await bot.update_roster_channel()
    await bot.update_staff_channel()


@bot.event
async def on_member_remove(member: discord.Member):
    for t in bot.teams.values():
        t.update_members()
    await bot.update_roster_channel()
    await bot.update_staff_channel()


@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    # inefficient but fuck you
    # voice channels are used to determine the symbol of the team
    if before.roles == after.roles and before.voice_channels == after.voice_channels:
        return
    await bot.update_teams()
    await bot.update_staff_channel()
