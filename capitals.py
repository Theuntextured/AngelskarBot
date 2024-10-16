import json
import discord
from pytz import all_timezones


capitals = {}

with open("country-by-capital-city.json", "r", encoding="utf-8") as file:
    for i in json.loads(file.read()):
        if i["city"] is None:
            continue
        capitals[i["country"]] = i["city"]


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
