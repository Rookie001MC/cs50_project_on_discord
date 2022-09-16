import random

import hikari
import lightbulb
import xkcd

xkcd_plugin = lightbulb.Plugin("Weather")


@xkcd_plugin.command
@lightbulb.command("xkcd", "Gets a webcomic from XKCD.com")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def xkcd_group():
    pass


@xkcd_group.child
@lightbulb.command("latest", "Gets the latest comic from XKCD.com")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def xkcd_latest(ctx):
    comic_object = xkcd.getLatestComic()
    comic_number = xkcd.getLatestComicNum()
    comic_info = info_getter(comic_object)
    comic_url = f"https://xkcd.com/{comic_number}"
    embed = hikari.Embed(
        color=0x32A852, title=comic_info[0], description=comic_info[1]
    ).set_image(comic_info[2])
    embed.add_field("Comic number", comic_number, inline=True)
    embed.add_field("Comic URL", comic_url, inline=True)
    await ctx.respond(embed)


@xkcd_group.child
@lightbulb.command("random", "Gets a random comic from XKCD.com")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def xkcd_random(ctx):
    random.seed()
    comic_number = random.randint(1, xkcd.getLatestComicNum())
    comic_object = xkcd.getComic(number=comic_number)
    comic_info = info_getter(comic_object)
    comic_url = f"https://xkcd.com/{comic_number}"
    embed = hikari.Embed(
        color=0x32A852, title=comic_info[0], description=comic_info[1]
    ).set_image(comic_info[2])
    embed.add_field("Comic number", comic_number, inline=True)
    embed.add_field("Comic URL", comic_url, inline=True)
    await ctx.respond(embed)


@xkcd_group.child
@lightbulb.option("comic_num", "Comic number", type=int)
@lightbulb.command("specific", "Gets a specific comic from XKCD.com")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def xkcd_specific(ctx):
    comic_number = ctx.options.comic_num
    if 1 <= comic_number <= xkcd.getLatestComicNum():
        comic_object = xkcd.getComic(number=comic_number)
        comic_info = info_getter(comic_object)
        comic_url = f"https://xkcd.com/{comic_number}"
        embed = hikari.Embed(
            color=0x32A852, title=comic_info[0], description=comic_info[1]
        ).set_image(comic_info[2])
        embed.add_field("Comic number", comic_number, inline=True)
        embed.add_field("Comic URL", comic_url, inline=True)
        await ctx.respond(embed)
    else:
        await ctx.respond(
            "**Error**: This comic does not exist!", flags=hikari.MessageFlag.EPHEMERAL
        )


def info_getter(comic):
    """Gets the alt_text and image_url of the provided comic object.

    Args:
        comic (Object): A Comic object based on user's input

    Returns:
        list: Containing alt_text and image_url of the comic.
    """
    title = comic.getTitle()
    alt_text = comic.getAltText()
    image_url = comic.getImageLink()
    return [title, alt_text, image_url]


def load(bot):
    """Loads this file as a Hikari-Lightbulb extension."""
    bot.add_plugin(xkcd_plugin)
