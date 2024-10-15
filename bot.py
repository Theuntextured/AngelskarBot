import discord
from discord.ext import commands
import bot_settings
import os

IS_ADMIN_COMMAND = "admin_command"

class Team:
    def __init__(self, name:str, symbol:str = "", category:discord.CategoryChannel = None) -> None:
        self.members = []
        self.tryouts = []
        self.standins = []
        self.captain = None
        self.vice_captain = None
        self.coach = None
        self.guest_count = 0

        self.name = name.title()
        self.symbol = symbol

        self.channel_category = category

        for self.schedule_channel in category.text_channels:
            if "schedule" in self.schedule_channel.name:
                break

    def is_valid_team(self):
        return len(self.members) > 0 and self.captain != None

    def __str__(self):
        return self.name 

    def get_info_string(self) -> str:
        out = f"# {self.symbol} | {self.name}"

        if not self.is_valid_team():
            return out

        out = f"{out}\n* {self.captain.display_name} **(Captain)**"
        if self.vice_captain != None:
            out = f"{out}\n* {self.vice_captain.display_name} **(Vice-Captain)**"

        for m in self.members:
            if m == self.captain or m == self.vice_captain:
                continue
            out = f"{out}\n* {m.display_name}"

        out = out + "\n"

        if len (self.tryouts) > 0:
            out = f"{out}\n **Tryouts:**"
            for m in self.tryouts:
                out = f"{out}\n* {m.display_name}"
            out = out + "\n"

        if len(self.standins) > 0:
            out = f"{out}\n **Stand-ins:**"
            for m in self.standins:
                out = f"{out}\n* {m.display_name}"
            out = out + "\n"

        if self.guest_count > 0:
            if self.guest_count > 1:
                g = "Guests"
            else:
                g = "Guest"
            out = f"{out}\n{self.guest_count} {g}\n"

        return out

    def update_members(self) -> None:
        self.captain = None
        self.vice_captain = None
        self.coach = None

        try:
            m = discord.utils.get(bot.angelskar_guild.roles, name=self.name + " Captain").members
            self.captain = m[0]
        except:
            pass
        try:
            m = discord.utils.get(bot.angelskar_guild.roles, name=self.name + " Vice-Captain").members
            self.vice_captain = m[0]
        except:
            pass
        try:
            m = discord.utils.get(bot.angelskar_guild.roles, name=self.name + " Coach").members
            self.coach = m[0]
        except:
            pass
        try:
            self.members = sorted(discord.utils.get(bot.angelskar_guild.roles, name= "AngelSkar " + self.name).members, key = lambda item : item.display_name)
        except:
            self.members = []
        try:
            self.standins = sorted(discord.utils.get(bot.angelskar_guild.roles, name= self.name + " Stand-in").members.copy(), key = lambda item : item.display_name)
        except:
            self.standins = []
        try:
            self.tryouts = sorted(discord.utils.get(bot.angelskar_guild.roles, name= self.name + " Tryout").members.copy(), key = lambda item : item.display_name)
        except:
            self.tryouts = []

        try:
            self.guest_count = len(discord.utils.get(bot.angelskar_guild.roles, name= self.name + " Guest").members)
        except:
            self.guest_count = 0

class Bot(commands.Bot):
    angelskar_guild:discord.Guild = None
    teams:dict[str, Team] = dict()
    #used to return value from get_last_message since the function returns coro
    target_message = None

    async def get_last_message(self, channel:discord.TextChannel):
        l = [message async for message in channel.history(limit=5)]
        for i in l:
            if i.author == self.user:
                self.target_message = i
        self.target_message = None

    def start_bot(self):
        bot_settings.bot = self
        self.bot_settings = bot_settings.load()
        try:
            with open("token.txt") as file:
                token = file.read()
        except:
            try:
                token = os.environ["TOKEN"]
            except:
                return
        self.run(token)

    async def update_roster_channel(self):
        channel: discord.TextChannel = self.bot_settings.get_roster_channel()

        if channel == None:
            return

        await self.get_last_message(channel)
        last_message = self.target_message

        to_send = "# **__ROSTERS__**\n\n"

        for t in sorted(self.teams.values(), key = lambda e : e.name):
            if t.is_valid_team():
                to_send = to_send + t.get_info_string() + "\n"

        if last_message and last_message.author == self.user:
            await last_message.edit(to_send)
        else:
            await channel.purge(limit=10, check=lambda m: m.author == bot.user)
            await channel.send(to_send)

    async def update_staff_channel(self):
        channel: discord.TextChannel = self.bot_settings.get_staff_channel()

        if channel == None:
            return

        to_send = "# **__STAFF__**"

        roles_to_display = ["Owner", "Co-owner", "Head Admin", "Admin", "Head Moderator", "Moderator", "Twitch Moderator", "Caster", "Developer", "Editor"]

        staff = {}
        roles:dict[str, list[discord.Member]] = {}

        for r in roles_to_display:
            role_obj = discord.utils.get(self.angelskar_guild.roles, name = r)
            for u in role_obj.members:
                if u not in staff:
                    staff[u] = [r]
                    if r in roles:
                        roles[r].append(u)
                    else:
                        roles[r] = [u]
                else:
                    staff[u].append(r)

        for r in roles_to_display:
            if r not in roles:
                continue
            if len(roles[r]) == 0:
                continue
            to_send = f"{to_send}\n# {r}"
            for u in roles[r]:
                to_send = f"{to_send}\n* {u.display_name}"

                if len(staff[u]) > 1:
                    to_send = to_send + " _(Also "
                    for i in range(1, len(staff[u])):
                        to_send = to_send + staff[u][i] + ", "
                    to_send = to_send[:-2] + ")_"

        await self.get_last_message(channel)
        last_message = self.target_message

        if last_message and last_message.author == self.user:
            last_message.edit(to_send)
        else:
            await channel.purge(limit=10, check=lambda m: m.author == bot.user)
            await channel.send(to_send)

    async def log_message(self, message:str) -> bool:
        if len(message) == 0:
            return False
        print(message)
        channel:discord.TextChannel = self.bot_settings.get_log_channel()
        if channel == None:
            return False
        await channel.send(message)
        return True

    async def update_teams(self) -> None:
        # old_team_names = set(self.teams.keys())
        team_names = set()

        for r in self.angelskar_guild.roles:
            if r.name.lower().endswith(" captain"):
                team_names.add(r.name.lower()[:-8])

        # if old_team_names == set(self.teams.keys()):
        #    return

        self.teams.clear()

        for i in team_names:
            i = i.lower()
            for c in self.angelskar_guild.voice_channels:
                if i in c.name.lower():
                    emote = c.name[0]
                    new_team = Team(i, emote, c.category)
                    self.teams[i] = new_team
                    new_team.update_members()
                    break

        await self.update_roster_channel()

bot = Bot(intents=discord.Intents.all(), command_prefix="/")

@bot.tree.command(name="help",description="Prints some information about the bot and available commands.")
async def help(interaction:discord.Interaction):
    out = "# AngelSkar Bot Help\n[Source Code](<https://github.com/Theuntextured/AngelskarBot>)\n"
    out = out + "## Available Commands:\n"
    for c in bot.tree.get_commands():
        if (interaction.permissions.manage_guild) or (IS_ADMIN_COMMAND not in c.extras):
            out = out + f"* `/{c.name}`: {c.description}\n"
    await interaction.response.send_message(out)

@bot.tree.command(name="logchannel", description="Displays or sets the log channel to use", extras={IS_ADMIN_COMMAND: True})
async def log_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        c = bot.bot_settings.get_log_channel()
        if c == None:
            await interaction.response.send_message("The log channel is currently not linked.")
        else:
            await interaction.response.send_message(f"The log channel is currently linked to {c.mention}")
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("Insufficient permissions to run the command.")
            return
        bot.bot_settings.set_log_channel(channel)

        message = f"Linked the log to channel {channel.mention}"
        await interaction.response.send_message(message)
        await channel.send(message)

@bot.tree.command(name="rosterchannel", description="Displays the roster channel to use. If you have the required permissions, you can set it.")
async def roster_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        c = bot.bot_settings.get_roster_channel()
        if c == None:
            await interaction.response.send_message("The roster channel is currently not linked.")
        else:
            await interaction.response.send_message(f"The roster channel is currently linked to {c.mention}")
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("Insufficient permissions to run the command.")
            return

        bot.bot_settings.set_roster_channel(channel)
        await bot.update_roster_channel()

        message = f"Linked the roster to channel {channel.mention}"
        await interaction.response.send_message(message)

@bot.tree.command(name="staffchannel", description="Displays the staff channel to use. If you have the required permissions, you can set it.")
async def staff_channel(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel == None:
        c = bot.bot_settings.get_staff_channel()
        if c == None:
            await interaction.response.send_message("The staff channel is currently not linked.")
        else:
            await interaction.response.send_message(f"The staff channel is currently linked to {c.mention}")
    else:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("Insufficient permissions to run the command.")
            return

        bot.bot_settings.set_staff_channel(channel)
        await bot.update_staff_channel()

        message = f"Linked the staff to channel {channel.mention}"
        await interaction.response.send_message(message)

@bot.tree.command(name="createprac", description="Creates a new practice schedule")
async def create_prac(interaction:discord.Interaction, channel:discord.TextChannel = None):
    if channel:
        await interaction.response.send_message("New prac awaiting to be scheduled")
    else:
        await interaction.response.send_message("Unable to locate channel")

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.log_message("Bot started!")
    bot.angelskar_guild = discord.utils.get(bot.guilds, id=1049126797465362523)

    await bot.update_teams()
    await bot.update_staff_channel()

@bot.event
async def on_member_update(before:discord.Member, after:discord.Member):
    # inefficient but fuck you
    if before.roles == after.roles:
        return
    for t in bot.teams.values():
        t.update_members()
    await bot.update_roster_channel()
    await bot.update_staff_channel()

@bot.event
async def on_member_remove(member:discord.Member):
    for t in bot.teams.values():
        t.update_members()
    await bot.update_roster_channel()
    await bot.update_staff_channel()

@bot.event
async def on_guild_update(before:discord.Guild, after:discord.Guild):
    #inefficient but fuck you
    #voice channels are used to determine the symbol of the team
    if before.roles == after.roles and before.voice_channels == after.voice_channels:
        return
    await bot.update_teams()
    await bot.update_staff_channel()
