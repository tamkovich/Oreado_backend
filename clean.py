from bs4 import BeautifulSoup

from bs4.element import NavigableString


def rec_tag(ind, element, tags):
    childs = element.findChild()

    if childs is None:
        return

    childs = list(childs)

    close_tag = str(element).find('>')
    tag_name = str(element)[:close_tag].strip('<')
    tags[ind].append(tag_name)

    for child in childs:
        try:
            new_child = BeautifulSoup(str(child), 'html.parser')
            rec_tag(ind, new_child, tags)
        except:
            pass


def delete_extra_text(elements):
    data = []
    for element in elements:
        data.append(element.split()[0].strip('/'))
    return data


def delete_displayed_text(element):
    new_children = []
    for child in element.contents:
        if not isinstance(child, NavigableString):
            new_children.append(delete_displayed_text(child))
    element.contents = new_children
    return element


def clean_text_main(element):
    soup = BeautifulSoup(element, 'html.parser')
    soup = delete_displayed_text(soup)

    str_soup = str(soup)

    start_body = str_soup.find('body')
    without_body = str_soup[start_body + 4:]
    close_tag = without_body.find('>')

    without_body = without_body[close_tag + 1:]

    end_body = without_body[::-1].find('ydob')
    without_body = without_body[:len(without_body) - end_body - 6]

    soup = BeautifulSoup(without_body, 'html.parser')
    [s.extract() for s in soup(['script', 'style'])]

    return str(soup)
