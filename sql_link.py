import mysql.connector
import json
import os

class SQLLink:
    def __init__(self):
        self.is_initialized = False

        self.settings = {}

        print("Initializing SQLLink")
        try:
            with open("database_settings.json", "r") as file:
                for i in json.load(file):
                    self.settings[i["name"]] = i["value"]
                print("Retrieved database settings via file.")
        except FileNotFoundError:
            try:
                settings = [
  {
    "name": "MYSQL_ADDON_DB",
    "value": os.environ["MYSQL_ADDON_DB"]
  },
  {
    "name": "MYSQL_ADDON_HOST",
    "value": os.environ["MYSQL_ADDON_HOST"]
  },
  {
    "name": "MYSQL_ADDON_PASSWORD",
    "value": os.environ["MYSQL_ADDON_PASSWORD"]
  },
  {
    "name": "MYSQL_ADDON_PORT",
    "value": os.environ["MYSQL_ADDON_PORT"]
  },
  {
    "name": "MYSQL_ADDON_URI",
    "value": os.environ["MYSQL_ADDON_URI"]
  },
  {
    "name": "MYSQL_ADDON_USER",
    "value": os.environ["MYSQL_ADDON_USER"]
  },
  {
    "name": "MYSQL_ADDON_VERSION",
    "value": os.environ["MYSQL_ADDON_VERSION"]
  }
]
                for s in settings:
                    self.settings[s["name"]] = s["value"]
                print("Retreived database settings via environment variables.")
            except Exception as E:
                print(E)
                print("Some environment variables were missing or incorrect. The database could not be linked.")
                return

        try:
            self.database = mysql.connector.connect(
                host=self.settings["MYSQL_ADDON_HOST"],
                user=self.settings["MYSQL_ADDON_USER"],
                password=self.settings["MYSQL_ADDON_PASSWORD"]
            )
            print("Database successfully connected.")
        except Exception as e:
            print(e)
            print("Could not connect to the database.")
            return

        self.cursor = self.database.cursor()

        self.cursor.execute("USE bzrthya0vj19yk6mpuf2")

        self.is_initialized = True

try:
    link = SQLLink()
except Exception as e:
    print(e)
    print("STOPPING")
    quit()