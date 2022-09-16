import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse


def price_get():
    """Gets the price of Vietnam's common used fuel types.
    This does a few things before actually sending the message to user:
    - Calls get_page() to get the page data
    - Makes a BeautifulSoup from the page, then gets the fuel price table.
    - Pass the table to table_parsing() to get the fuel data as a dictionary.
    - Process the resulting dictionary then returns the final message.

    Returns:
        dict: Containing the message to be sent to FB.
    """
    page_data = get_page()
    if page_data is False:
        response_object = create_response_object(False)
    else:
        soup = BeautifulSoup(page_data, "html.parser")

        # Thank god I only need to deal with 1 table 🥲
        table = soup.find("table", class_="table")
        fuel_data = table_parsing(table)

        response_object = create_response_object(fuel_data)
    return response_object


def get_page():
    """Fetches the HTML markup of the page containing the fuel prices.

    Returns:
        str: The entire page in the form of a string.
        Returns False if there is any problem during page fetching (lost of internet, page error,....)
    """
    try:
        url = "https://www.pvoil.com.vn/truyen-thong/tin-gia-xang-dau"
        data = requests.get(url).text
    except BaseException as err:
        data = False
        print(f"Error in fetching data: {err}")
    return data


def table_parsing(table):
    """Parses the table, as processed from the price_get() function, to get the relevant data.

    Args:
        table (str): The fuel prices table.

    Returns:
        dict: Containing the product name, current price, and how much the price changed compared to last adjustment.
    """
    list_of_heads = table.thead.find_all("strong")
    last_updated_head = list_of_heads[2].text.strip()
    last_updated_time = parse(last_updated_head, fuzzy=True)

    result = {"last_updated": last_updated_time.strftime("%d/%m/%Y, %H:%M")}
    product = []
    price = []
    offset = []
    for row in table.tbody.find_all("tr"):
        columns = row.find_all("td")

        if columns != []:
            product.append(translate_fuel_names(columns[1].text.strip()))
            price.append(int(columns[2].text.strip().replace(".", "")))
            offset.append(int(columns[3].text.strip().replace(".", "")))

    df = pd.DataFrame(
        {"product": product, "price": price, "offset_by_previous": offset}
    )

    data = df.to_dict("records")
    result["data"] = data
    return result


def translate_fuel_names(product):
    """Translate the product name to English.

    Args:
        product (str): Name of the product in Vietnamese.

    Returns:
        str: Name of the product in English.
    """
    TRANSLATIONS = {
        "Xăng RON 95-III": "E5 RON 95-III",
        "Xăng E5 RON 92-II": "E5 RON 92-II",
        "Dầu DO 0,05S-II": "Diesel Oil DO 0.05S",
        "Dầu KO": "Kerosene",
    }

    if product in TRANSLATIONS:
        return TRANSLATIONS[product]


def offset_price_emoji(offset_price):
    """Adds an emoji, indicating the price difference compared to last adjustment.
    This is used purely for more nicer looking message.

    Args:
        offset_price (int): The fuel price of current product, unformatted.

    Returns:
        str: The fuel price of current product, with added emojis.
        Returns "no change" if there is no change in price.
    """
    if offset_price == 0:
        return "no change"
    elif offset_price < 0:
        offset_with_icon = f"⬇️ down {abs(offset_price)} dong/liter"
    else:
        offset_with_icon = f"⬆️ up {offset_price} dong/liter"
    return offset_with_icon


def create_response_object(data):
    """Generates a response dictionary to be used for sending the message.

    Args:
        data (dict): Data containing the current fuel price.

    Returns:
        dict: Represents the message to be sent to the user.
    """
    if data is False:
        response = {"text": "Something has gone wrong!"}
    else:
        last_updated = data["last_updated"]
        fuel_data = data["data"]
        data_string = ""

        for product in fuel_data:
            data_string += f"{product['product']}: {product['price']} dong/liter - {offset_price_emoji(product['offset_by_previous'])} compared to last adjustment.\n"

        response = {
            "text": f"""Showing current Vietnam fuel prices:
Last adjustment: {last_updated}

{data_string}
Source:
https://www.pvoil.com.vn/truyen-thong/tin-gia-xang-dau"""
        }
    return response


# Yes, this script can be run, but for local debug only
if __name__ == "__main__":
    price_get()
