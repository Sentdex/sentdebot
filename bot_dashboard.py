import os

from quart import Quart, render_template, redirect, url_for
from quart_nextcord import DiscordOAuth2Session, requires_authorization, Unauthorized
from bot_config_manager import ReadOnlyConfig

config = ReadOnlyConfig()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "true"

class BotDashboard(Quart):

    def __init__(self, bot):
        super().__init__(__name__)
        self.bot = bot
        self.secret_key = bytes.fromhex(config.get('management_panel_session'))

        self.config['DISCORD_CLIENT_ID'] = config.get('discord_client_id')
        self.config['DISCORD_CLIENT_SECRET'] = config.get('discord_client_secret')
        self.config['DISCORD_REDIRECT_URI'] = config.get('discord_redirect_uri')
        self.config['DISCORD_BOT_TOKEN'] = config.get('bot_token')

        self.oauth = DiscordOAuth2Session(self)

        @self.route('/login/')
        async def login():
            return await self.oauth.create_session()
    
        @self.route('/logout/')
        async def logout():
            await self.oauth.revoke()
            return redirect(url_for('login'))
    
        @self.route('/callback/')
        async def authorization_callback():
            try:
                await self.oauth.callback()
            except Unauthorized:
                return redirect(url_for('index'))
            return redirect(url_for('dashboard'))
    
        @self.route('/')
        async def index():
            if self.oauth.authorized:
                return redirect(url_for('dashboard'))
            return redirect(url_for('login'))

        @self.route('/dashboard/')
        @requires_authorization
        async def dashboard():
            return await render_template('dashboard.html', bot=self.bot)

        @self.route('/dashboard/bot_settings/')
        @requires_authorization
        async def bot_settings():
            return await render_template('bot_settings.html', bot=self.bot)

        @self.route('/dashboard/cog_settings/')
        @requires_authorization
        async def cog_settings():
            return await render_template('cog_settings.html', bot=self.bot)


    def start_dashboard(self):
        self.bot.client.loop.create_task(self.run_task(host="127.0.0.1", port=5000))

    def stop_dashboard(self):
        self.bot.client.loop.stop()