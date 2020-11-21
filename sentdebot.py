import os

from modules.background_tasks import start_all_background_tasks
from modules.bot import bot

if __name__ == "__main__":
    token_path = os.path.abspath(os.path.join('sentdebot', 'token.txt'))
    token = open(f"{token_path}", "r").read().split('\n')[0]

    start_all_background_tasks()
    bot.run(token)
