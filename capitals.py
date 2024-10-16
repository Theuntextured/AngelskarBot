import json

capitals = {}

with open("country-by-capital-city.json", "r", encoding="utf-8") as file:
    for i in json.loads(file.read()):
        if i["city"] is None:
            continue
        capitals[i["country"]] = i["city"]