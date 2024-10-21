import json
import discord
from pytz import all_timezones

from datetime import datetime, timedelta, timezone
import re


def translate_to_datetime(text:str):
    # Regular expression to match the input like "10 days", "10 seconds", or "5 minutes"
    match = re.match(r"(\d+)\s*(seconds?|minutes?|hours?|days?)", text.strip().lower())
    if match:
        value = int(match.group(1))  # Extract the numeric value
        unit = match.group(2)  # Extract the unit (seconds, minutes, hours, days)

        # Determine the appropriate timedelta
        if "second" in unit:
            delta = timedelta(seconds=value)
        elif "minute" in unit:
            delta = timedelta(minutes=value)
        elif "hour" in unit:
            delta = timedelta(hours=value)
        elif "day" in unit:
            delta = timedelta(days=value)
        else:
            raise ValueError("Unsupported time unit")

        # Combine with current datetime
        return datetime.now(timezone.utc) + delta
    else:
        raise ValueError("Invalid input format")

capitals = {}

with open("country-by-capital-city.json", "r", encoding="utf-8") as file:
    for i in json.loads(file.read()):
        if i["city"] is None:
            continue
        capitals[i["country"]] = i["city"]

premier_ranks = {
    "Premier 30.000+": "Tier7",
    "Premier 25.000 - 29.999": "Tier6",
    "Premier 20.000 - 24.999": "Tier5",
    "Premier 15.000 - 19.999": "Tier4",
    "Premier 10.000 - 14.999": "Tier3",
    "Premier 5.000 - 9.999": "Tier2",
    "Premier 0 - 4.999": "Tier1",
}
faceit_ranks = {
    "Level 1": "Level1",
    "Level 2": "Level2",
    "Level 3": "Level3",
    "Level 4": "Level4",
    "Level 5": "Level5",
    "Level 6": "Level6",
    "Level 7": "Level7",
    "Level 8": "Level8",
    "Level 9": "Level9",
    "Level 10": "Level10",
}
UNKNOWN_RANK = "<:Level0:1234465815672262677>"

def setup_rank_emojis(bot:discord.Client):
    for key, value in premier_ranks.items():
        for e in bot.emojis:
            if e.name != value:
                continue
            premier_ranks[key] = f"<:{value}:{e.id}>"

    for key, value in faceit_ranks.items():
        for e in bot.emojis:
            if e.name != value:
                continue
            faceit_ranks[key] = f"<:{value}:{e.id}>"

def get_emoji_id_from_name(bot: discord.Client, name: str) -> (int | None):
    name = name.lower()
    for e in bot.emojis:
        if e.name != name and e.name != name.title():
            continue
        return e.id
    return None

def get_emoji_from_name(bot: discord.Client, name: str) -> (str | None):
    name = name.lower()
    for e in bot.emojis:
        if e.name != name and e.name != name.title():
            continue
        return f"<:{name}:{e.id}>"
    return None

country_emojis = {}

with open("country_emojis.json", "r", encoding="utf-8")  as file:
    for i in json.loads(file.read()):
        country_emojis[i["name"]] = f":flag_{i["code"].lower()}:"

def get_member_country_emoji(member: discord.Member) -> str:
    for i in member.roles:
        if i.name not in country_emojis:
            continue
        return country_emojis[i.name]
    return "🇪🇺"

def get_member_faceit_emoji(member: discord.Member) -> str:
    for r in member.roles:
        if r.name not in faceit_ranks:
            continue
        return faceit_ranks[r.name]
    return UNKNOWN_RANK

def get_member_premier_emoji(member: discord.Member) -> str:
    for r in member.roles:
        if r.name not in premier_ranks:
            continue
        return premier_ranks[r.name]
    return UNKNOWN_RANK

def get_member_display_rank_flag(member: discord.Member) -> str:
    return f"{get_member_country_emoji(member)} | {get_member_faceit_emoji(member)} | {get_member_premier_emoji(member)} | {member.display_name}"


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
