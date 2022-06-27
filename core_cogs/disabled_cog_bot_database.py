import aiosqlite
from nextcord.ext import commands

from bot_config_manager import ReadOnlyConfig

config = ReadOnlyConfig()


# database cog
class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        path = config.get('database_path')
        await self.bot.wait_until_ready()
        async with aiosqlite.connect(path) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    'CREATE TABLE IF NOT EXISTS guild_users (name INTEGER, id INTEGER)'
                )
                await cursor.execute(
                    'CREATE TABLE IF NOT EXISTS guild_channels (name INTEGER, id INTEGER)'
                )
                await cursor.execute(
                    'CREATE TABLE IF NOT EXISTS messages (id INTEGER, channel_id INTEGER, author_id INTEGER, '
                    'timestamp INTEGER) '
                )
            await db.commit()

        # print the database table names
        async with aiosqlite.connect(path) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    'SELECT name FROM sqlite_master WHERE type = "table"'
                )
                print(await cursor.fetchall())

    async def add_user(self, user):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'INSERT INTO guild_users (name, id) VALUES (?, ?)',
                    (user.name, user.id)
                )

    async def remove_user(self, user):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'DELETE FROM guild_users WHERE id = ?',
                    (user.id,)
                )

    async def add_channel(self, channel):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'INSERT INTO guild_channels (name, id) VALUES (?, ?)',
                    (channel.name, channel.id)
                )

    async def remove_channel(self, channel):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'DELETE FROM guild_channels WHERE id = ?',
                    (channel.id,)
                )

    async def add_message(self, message):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'INSERT INTO messages (id, channel_id, author_id, timestamp) VALUES (?, ?, ?, ?)',
                    (message.id, message.channel.id, message.author.id, message.created_at.timestamp())
                )

    async def remove_message(self, message):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'DELETE FROM messages WHERE id = ?',
                    (message.id,)
                )

    async def get_users(self):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'SELECT * FROM guild_users'
                )
                return await cursor.fetchall()

    async def get_channels(self):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'SELECT * FROM guild_channels'
                )
                return await cursor.fetchall()

    async def get_messages(self):
        async with aiosqlite.connect(config.get('database_path')) as db:
            async with db.cursor as cursor:
                await cursor.execute(
                    'SELECT * FROM messages'
                )
                return await cursor.fetchall()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.add_message(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.add_user(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.remove_user(member)

    @commands.Cog.listener()
    async def on_channel_create(self, channel):
        await self.add_channel(channel)

    @commands.Cog.listener()
    async def on_channel_delete(self, channel):
        await self.remove_channel(channel)


def setup(bot):
    bot.add_cog(Database(bot))
