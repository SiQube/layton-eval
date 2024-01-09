import os
import typing as t

import bs4
import pandas as pd
from bs4 import BeautifulSoup
from constants import ROOT_DIR
from PIL import Image
from tqdm import tqdm

type2color = {"1": "#E8E8B8", "2": "#C8E8C0", "3": "#C8F0E0", "Special": "#F0C7A7"}


def get_file_soup(path: str) -> BeautifulSoup:
    """
    get the soup from an html path
    """
    with open(path, "rb") as f:
        content = f.read()
    return BeautifulSoup(content, "html.parser")


def load_puzzle_image(puzzle_name: str):
    return Image.open(f"{ROOT_DIR}/layton-data/images/{puzzle_name}.jpg")


def get_puzzle_description(soup: BeautifulSoup) -> t.List[str] | str:
    """
    Get puzzle description from soup object.
    """
    puzzle_element = soup.find(id='Puzzle')
    hints_element = soup.find(id='Hints')
    solution_element = soup.find(id="Solution")

    # Collect everything between Puzzle and Hints
    nodes_between_elements = []
    if puzzle_element is None:  # Some RW Puzzles do not have a Puzzle section.
        return
    current_element = puzzle_element.find_next()

    has_images = False
    dl_encountered = 0
    while (current_element and current_element.find_next() not in [hints_element, solution_element]) and (
        dl_encountered < 2
    ):
        if str(current_element).startswith("<p>"):
            clean_content = ""
            for elem in current_element.contents:
                if str(elem).startswith('''<a class="image"'''):
                    nodes_between_elements.append(current_element)
                    has_images = True
                elif isinstance(elem, bs4.element.NavigableString):
                    clean_content += elem
                else:
                    for c in elem.contents:
                        if str(c) != "<br/>":
                            clean_content += c
            nodes_between_elements.append(clean_content)
        elif str(current_element).startswith("<dl>"):
            dl_encountered += 1
        current_element = current_element.find_next()
    if has_images:
        return nodes_between_elements[0]
    else:
        return "\n".join(nodes_between_elements)


def get_puzzle_category(soup: BeautifulSoup) -> str:
    """
    Returns the category of a puzzle.
    """
    if soup.select_one("[data-source='type'] a") is not None:
        return soup.select_one("[data-source='type'] a").attrs["title"].split(":").pop()


def get_puzzle_picarats(soup: BeautifulSoup) -> int:
    """
    Returns the number of picarats owned by a puzzle.
    """
    if tag := soup.select_one("[data-source='picarats'] .pi-data-value.pi-font"):
        return int(tag.contents[0])


def get_puzzle_id(soup: BeautifulSoup) -> str:
    """
    Return the puzzle id.
    """
    if soup.select_one("[data-source='number'] .pi-data-value.pi-font") is not None:
        return soup.select_one("[data-source='number'] .pi-data-value.pi-font").contents[0]


def get_puzzle_hint(soup: BeautifulSoup, type: t.Literal["1", "2", "3", "Special"]) -> str:
    """
    Given the hint type, returns the associated hint found in the puzzle.
    """
    background_color = type2color.get(type, None)
    base = f"[style='height:200px; overflow-y:auto; overflow-x:hidden; word-wrap:break-word; overflow: -moz-scrollbars-vertical; line-height:normal; border: 2px solid black; padding:3px; background:{background_color}; font-size:14px'] dl"
    hint = ""
    while (h := soup.select_one(f"{base}+p")) is not None:
        base += "+p"
        for c in h.contents:
            hint += str(c)
    if hint:
        return hint
    else:
        hint = soup.select(
            "[style='height:200px; overflow-y:auto; overflow-x:hidden; word-wrap:break-word; overflow: -moz-scrollbars-vertical; line-height:normal; border: 2px solid black; padding:3px; background:#E8E8B8; font-size:14px'] p"
        )
        clean_content = ""
        for h in hint:
            if isinstance(h, bs4.element.NavigableString):
                clean_content += h
            else:
                for c in h.contents:
                    if isinstance(c, bs4.element.NavigableString):
                        clean_content += c
                    elif str(c) == "<br/>":
                        clean_content += "\n"
                    elif str(c).startswith("<img"):
                        continue
                    else:
                        clean_content += c.contents[0]
        return clean_content


def get_puzzle_solution(soup: BeautifulSoup) -> str:
    """
    Get the unstructured solution of a puzzle.
    """
    correct_element = soup.find(id="Correct")
    navbox_element = soup.select_one(".navbox.mw-collapsible.mw-collapsed tbody")
    nodes_between_elements = []
    current_element = correct_element.find_next()
    dl_encountered = 0
    while (current_element and current_element.find_next() != navbox_element) and dl_encountered < 2:
        if str(current_element).startswith("<p>"):
            nodes_between_elements.append(current_element.contents[0])
        elif str(current_element).startswith("<dl>"):
            dl_encountered += 1
        current_element = current_element.find_next()
    return "\n".join(nodes_between_elements)


if __name__ == "__main__":
    df = {
        "id": [],
        "category": [],
        "description": [],
        "img": [],
        "picarats": [],
        "first_hint": [],
        "second_hint": [],
        "third_hint": [],
        "special_hint": [],
    }
    for puzzle_html_name in tqdm(os.listdir(f"{ROOT_DIR}/layton-data/htmls")[509 + 169 :]):
        puzzle_name = puzzle_html_name.replace(".html", "")
        img_path = f"{ROOT_DIR}/layton-data/images/{puzzle_name}.jpg"
        img = Image.open(img_path) if os.path.exists(img_path) else None
        soup = get_file_soup(f"{ROOT_DIR}/layton-data/htmls/{puzzle_name}.html")
        category = get_puzzle_category(soup)
        description = get_puzzle_description(soup)
        puzzle_id = get_puzzle_id(soup)
        picarats = get_puzzle_picarats(soup)
        first_hint = get_puzzle_hint(soup, "1")
        second_hint = get_puzzle_hint(soup, "2")
        third_hint = get_puzzle_hint(soup, "3")
        special_hint = get_puzzle_hint(soup, "Special")
        df["id"].append(puzzle_id)
        df["category"].append(category)
        df["description"].append(description)
        df["img"].append(img)
        df["picarats"].append(picarats)
        df["first_hint"].append(first_hint)
        df["second_hint"].append(second_hint)
        df["third_hint"].append(third_hint)
        df["special_hint"].append(special_hint)
    df = pd.DataFrame(df)
    df.to_excel(f"{ROOT_DIR}/layton-annotations.xlsx")
