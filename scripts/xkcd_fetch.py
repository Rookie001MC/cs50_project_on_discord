import xkcd


def fetcher(user_input):
    """Process the inputted command and fetches the requested comic.

    Args:
        user_input (str): the command as inputted by user.

    Returns:
        dict: a response object to be sent back to the `handle_message` function for processing and sending to FB.
    """
    commands = user_input.split(" ")
    found = True
    if len(commands) == 1:
        comic_object = xkcd.getLatestComic()
    elif len(commands) == 2:
        subcommand = commands[1]
        if subcommand == "latest":
            comic_object = xkcd.getLatestComic()

        elif subcommand == "random":
            comic_object = xkcd.getRandomComic()

        else:
            try:
                input_comic_num = int(subcommand)
            except ValueError:
                err_message = "Invalid comic number or subcommand!"
                found = False
            else:
                if 1 <= input_comic_num <= xkcd.getLatestComicNum():
                    comic_object = xkcd.getComic(input_comic_num)
                else:
                    err_message = f"Your requested comic, number {input_comic_num}, does not exist!"
                    found = False

    elif len(commands) > 2:
        err_message = "Too many arguments!"
        found = False

    if found is True:

        alt_text, image_url = info_getter(comic_object)
        response = [
            {"text": alt_text},
            {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": image_url,
                    },
                },
            },
        ]
    else:
        response = {
            "text": err_message,
        }

    return response


def info_getter(comic):
    """Gets the alt_text and image_url of the provided comic object.

    Args:
        comic (Object): A Comic object based on user's input

    Returns:
        list: Containing alt_text and image_url of the comic.
    """
    alt_text = comic.getAltText()
    image_url = comic.getImageLink()
    return [alt_text, image_url]
