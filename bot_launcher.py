# this class should be written to handle the launch of the bot, I feel I need to make a flask class rather than a
# module, then I can decouple them, as atm the bot has to be ran within the dashboard and I don't like it,
# you crash the site you crash the bot, and I don't like that fragility

from bot_config_protocols import ReadOnlyConfig
from bot_main import Bot
from bot_dashboard import BotDashboard


def main():
    bot = Bot()
    dashboard = BotDashboard(bot)
    dashboard.start_dashboard()

    bot.run()

    dashboard.stop_dashboard()


if __name__ == '__main__':
    main()
