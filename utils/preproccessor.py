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
    return str(BeautifulSoup(content, features="html.parser"))


def bytes_html_to_text(content):
    """
    Converts bytes content html to just text from HTML-content
    :param content: <bytes> html response
    :return: <str> text content
    """
    soup = BeautifulSoup(content, features="html.parser")
    return cleanMe(soup)
