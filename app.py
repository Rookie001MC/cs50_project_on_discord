import os

import hikari
import lightbulb
from dotenv import load_dotenv

load_dotenv()
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN", None)
server_to_register_command = (1019969561954635837,)

bot = lightbulb.BotApp(
    token=discord_bot_token, default_enabled_guilds=server_to_register_command
)

bot.load_extensions("scripts.weather")
bot.run()
