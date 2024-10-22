from bot import *
from typing import Callable
from discord.app_commands.errors import CheckFailure
from pytz import all_timezones
from util import capitals

class NotCaptain(CheckFailure):
    def __init__(self) -> None:
        message = (
            f"You are not a captain of any team, which is required to run this command."
        )
        super().__init__(message)


def is_captain(
    include_vice_captain: bool = False,
) -> Callable[[discord.app_commands.checks.T], discord.app_commands.checks.T]:

    def predicate(interaction: discord.Interaction) -> bool:
        team = get_team_from_user(interaction.user)
        if team is None:
            raise NotCaptain()
            return False
        if team.captain == interaction.user:
            return True
        if team.vice_captaincaptain == interaction.user and include_vice_captain:
            return True

        raise NotCaptain
        return False

    return discord.app_commands.commands.check(predicate)

async def command_list_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    current = current.lower().strip()
    out = []
    for c in bot.tree.get_commands():
        if current not in c.name:
            continue
        can_run = True
        for check in c.checks:
            try:
                check(interaction)
            except:
                can_run = False
                break
        if can_run:
            out.append(discord.app_commands.Choice(name=c.name, value=c.name))
    return out

async def time_zone_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:

    c = current.lower()
    out = []

    for i in all_timezones:
        if c in i.lower():
            out.append(discord.app_commands.Choice(name=i, value=i))
            if len(out) == 25:
                return out

    for country, capital in capitals.items():
        if c in country.lower():
            for k in all_timezones:
                if capital.lower() in k.lower():
                    out.append(discord.app_commands.Choice(name=k, value=k))
                    break

    return out

class NotDeveloper(CheckFailure):
    def __init__(self) -> None:
        message = (
            f"This command is not fully ready yet. Only users with the developer role can run this."
        )
        super().__init__(message)

def is_developer() -> Callable[[discord.app_commands.checks.T], discord.app_commands.checks.T]:

    def predicate(interaction: discord.Interaction) -> bool:
        dev_role = discord.utils.get(interaction.user.roles, name="Developer")

        if dev_role is None:
            raise NotCaptain
            return False
        
        return True

    return discord.app_commands.commands.check(predicate)