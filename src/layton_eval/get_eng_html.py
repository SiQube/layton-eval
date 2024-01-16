import os
import typing as t
from io import BytesIO
from logging import getLogger

import numpy as np
import requests
from bs4 import BeautifulSoup
from constants import ROOT_DIR
from PIL import Image
from tqdm import tqdm

log = getLogger(__name__)


def get_all_links(url: str) -> t.List[str]:
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")
    links = []
    for link in soup.find_all("a"):  # find all links
        if link.has_attr("href"):
            href = link["href"]
            if href and not href.startswith("#") and href.startswith("/wiki/Puzzle:") and href not in links:
                links.append(href)
    next_button = soup.select_one(".category-page__pagination-next")
    return links, next_button


def get_puzzle_images(soup: BeautifulSoup) -> Image:
    """
    Returns the game frame associated to a puzzle and its answer (when applicable).
    """
    if soup.select_one(".image.image-thumbnail") is not None:
        img = Image.open(BytesIO(requests.get(soup.select_one(".image.image-thumbnail").attrs["href"]).content))
        answer_img = soup.select_one(f"""[alt="{soup.select_one(".image.image-thumbnail").attrs["title"] + "S"}"]""")
        if answer_img is not None:
            link = answer_img.attrs.get("data-src", answer_img.attrs.get("src"))
            answer_img = Image.open(BytesIO(requests.get(link).content))
        return img, answer_img
    else:
        return None, None


if __name__ == "__main__":
    riddle_urls = []
    url = "https://layton.fandom.com/wiki/Category:All_Puzzles"
    keep_going = True
    while keep_going:
        riddle_links, next_button = get_all_links(url)
        riddle_urls.extend(riddle_links)
        keep_going = next_button is not None
        if keep_going:
            url = next_button.attrs["href"]
    riddle_urls = list(np.unique(riddle_urls))
    log.info(f"Extracted {len(riddle_urls)} riddles.")
    riddle_urls = [f"https://layton.fandom.com{url}" for url in riddle_urls]
    os.makedirs(f"{ROOT_DIR}/layton-data", exist_ok=True)
    os.makedirs(f"{ROOT_DIR}/layton-data/htmls", exist_ok=True)
    os.makedirs(f"{ROOT_DIR}/layton-data/images", exist_ok=True)
    os.makedirs(f"{ROOT_DIR}/layton-data/answer_images", exist_ok=True)
    for url in tqdm(riddle_urls):
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')
            img, answer_img = get_puzzle_images(soup)
            puzzle_name = url.split("Puzzle:")[-1].replace("/", "_")
            with open(f"{ROOT_DIR}/layton-data/htmls/{puzzle_name}.html", "wb") as f:
                f.write(content)
            if img is not None:
                img.convert("RGB").save(f"{ROOT_DIR}/layton-data/images/{puzzle_name}.jpg")
            else:
                log.info(f"No img found for puzzle at: {url}")
            if answer_img is not None:
                answer_img.convert("RGB").save(f"{ROOT_DIR}/layton-data/answer_images/{puzzle_name}.jpg")
            else:
                log.info(f"No answer_img found for puzzle at: {url}")
        else:
            log.info(f"Encountered error while navigating to {url}")
