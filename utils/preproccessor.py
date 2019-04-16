import re

from bs4 import BeautifulSoup


def cleanMe(soup):
    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text


def bytes_to_html(content):
    """
    Converts bytes content html to html content
    :param content: <bytes> html response
    :return: <str> html content
    """
    # ToDo: logging all errors
    try:
        return str(BeautifulSoup(content, features="html.parser"))
    except UnboundLocalError:
        return ''


def bytes_html_to_text(content):
    """
    Converts bytes content html to just text from HTML-content
    :param content: <bytes> html response
    :return: <str> text content
    """
    soup = BeautifulSoup(content, features="html.parser")
    return cleanMe(soup)


def scrap_mail_from_text(content: str) -> str or None:
    """
    Scrapes with the email pattern from the received content
    Returns first email which was found or None if nothing matches
    """
    res = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}",
        content
    )
    return res[0] if res else None


def replace_email_symbols(text: str) -> str:
    """
    Replace specific for email symbols
    """
    # ToDo: find all of those symbols
    # ToDo: create a logic which can use those symbols in the app frontend view
    symbols = ['=20', '=A0', '=0A', '=0D']
    for sym in symbols:
        text = text.replace(sym, '')
    return text
