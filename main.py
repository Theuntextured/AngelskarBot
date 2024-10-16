from bot import bot
import webserver

if __name__ == "__main__":
    print("Starting...")
    webserver.keep_alive()
    bot.start_bot()
