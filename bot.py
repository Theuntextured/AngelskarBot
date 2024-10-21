import discord
from discord.ext import commands
import bot_settings
import os
from datetime import datetime
import util
from practice import Practice


months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

class Team:
    def __init__(
        self, name: str, symbol: str = "", category: discord.CategoryChannel = None
    ) -> None:
        self.members = []
        self.tryouts = []
        self.standins = []
        self.captain = None
        self.vice_captain = None
        self.coach = None
        self.guest_count = 0

        self.name = name.title()
        self.symbol = symbol

        self.stand_in_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"{self.name} Stand-in"
        )
        self.tryout_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"{self.name} Tryout"
        )
        self.captain_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"{self.name} Captain"
        )
        self.vice_captain_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"{self.name} Vice-Captain"
        )
        self.guest_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"{self.name} Guest"
        )
        self.coach_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"{self.name} Coach"
        )
        self.player_role = discord.utils.get(
            bot.angelskar_guild.roles, name=f"AngelSkar {self.name}"
        )

        self.roles = {
            "player": self.player_role,
            "captain": self.captain_role,
            "vice-captain": self.vice_captain_role,
            "stand-in": self.vice_captain_role,
            "tryout": self.tryout_role,
            "coach": self.coach_role,
            "guest": self.guest_role,
        }

        self.channel_category = category

        for self.schedule_channel in category.text_channels:
            if "schedule" in self.schedule_channel.name:
                break

        self.practices = []

    def is_valid_team(self):
        return len(self.members) > 0 and self.captain != None

    def __str__(self):
        return self.name

    def get_info_string(self) -> str:
        out = f"# {self.symbol} | {self.name}"

        if not self.is_valid_team():
            return out

        out = f"{out}\n* {util.get_member_display_rank_flag(self.captain)} **(Captain)**"
        if self.vice_captain != None:
            out = f"{out}\n* {util.get_member_display_rank_flag(self.vice_captain)} **(Vice-Captain)**"

        for m in self.members:
            if m == self.captain or m == self.vice_captain:
                continue
            out = f"{out}\n* {util.get_member_display_rank_flag(m)}"

        out = out + "\n"

        if len(self.tryouts) > 0:
            out = f"{out}\n **Tryouts:**"
            for m in self.tryouts:
                out = f"{out}\n* {util.get_member_display_rank_flag(m)}"
            out = out + "\n"

        if len(self.standins) > 0:
            out = f"{out}\n **Stand-ins:**"
            for m in self.standins:
                out = f"{out}\n* {util.get_member_display_rank_flag(m)}"
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
            m = self.captain_role.members
            self.captain = m[0]
        except:
            pass
        try:
            m = self.vice_captain_role.members
            self.vice_captain = m[0]
        except:
            pass
        try:
            m = self.coach_role.members
            self.coach = m[0]
        except:
            pass
        try:
            self.members = sorted(
                self.player_role.members, key=lambda item: item.display_name
            )
        except:
            self.members = []
        try:
            self.standins = sorted(
                self.stand_in_role.members.copy(), key=lambda item: item.display_name
            )
        except:
            self.standins = []
        try:
            self.tryouts = sorted(
                self.tryout_role.members.copy(), key=lambda item: item.display_name
            )
        except:
            self.tryouts = []

        try:
            self.guest_count = len(self.guest_role.members)
        except:
            self.guest_count = 0

    def get_mention(self, include_stand_ins=False) -> str:
        out = ""
        out = out + self.player_role.mention
        if len(self.tryout_role.members) > 0:
            out = out + " " + self.tryout_role.mention

        if include_stand_ins:
            if len(self.stand_in_role.members) > 0:
                out = out + " " + self.tryout_role.mention

        return out

class Bot(commands.Bot):
    angelskar_guild: discord.Guild = None
    teams: dict[str, Team] = dict()
    # used to return value from get_last_message since the function returns coro
    target_message = None

    async def get_last_message(self, channel: discord.TextChannel):
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

        to_send = "# **__ROSTERS__**\n\n"

        await channel.purge(limit=10, check=lambda m: m.author == bot.user)
        for t in sorted(self.teams.values(), key=lambda e: e.name):
            if t.is_valid_team():
                to_send = to_send + t.get_info_string() + "\n"

        current_iteration = ""
        for s in to_send.split("\n"):
            if len(current_iteration) + len(s) > 2000:
                await channel.send(current_iteration)
                current_iteration = s
                continue

            current_iteration = current_iteration + "\n" + s

        if current_iteration != "":
            await channel.send(current_iteration)

    async def update_staff_channel(self):
        channel: discord.TextChannel = self.bot_settings.get_staff_channel()

        if channel == None:
            return

        to_send = "# **__STAFF__**"

        roles_to_display = [
            "Owner",
            "Co-owner",
            "Head Admin",
            "Admin",
            "Head Moderator",
            "Moderator",
            "Twitch Moderator",
            "Caster",
            "Developer",
            "Editor",
        ]

        staff = {}
        roles: dict[str, list[discord.Member]] = {}

        for r in roles_to_display:
            role_obj = discord.utils.get(self.angelskar_guild.roles, name=r)
            for u in role_obj.members:
                if u == self.user:
                    continue
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

    async def log_message(self, message: str) -> bool:
        if len(message) == 0:
            return False
        print(message)
        channel: discord.TextChannel = self.bot_settings.get_log_channel()
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
                    emote = util.get_emoji_from_name(self, i)
                    if emote is None:
                        emote = c.name[0]
                    new_team = Team(i, emote, c.category)
                    self.teams[i] = new_team
                    new_team.update_members()
                    break

        await self.update_roster_channel()

bot = Bot(intents=discord.Intents.all(), command_prefix="/")

def get_team_from_user(user: discord.Member) -> (Team | None):

    for i in ["player", "coach", "stand-in", "tryout"]:
        for t in bot.teams.values():
            if t.roles[i] in user.roles:
                return t

    return None
