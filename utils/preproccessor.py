from bs4 import BeautifulSoup


def bytes_to_html(content):
    """
    Converts bytes content html to html content
    :param content: <bytes> html response
    :return: <str> html content
    """
    soup = BeautifulSoup(content, features="html.parser")
    return str(soup)
