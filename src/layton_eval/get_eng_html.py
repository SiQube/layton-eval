import os
import typing as t
from logging import getLogger

import numpy as np
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import ROOT_DIR

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


if __name__ == "__main__":
    riddle_urls = []
    url = "https://layton.fandom.com/wiki/Category:All_Puzzles"
    keep_going = True
    while keep_going:
        riddle_links, next_button = get_all_links(url)
        riddle_urls.extend(riddle_urls)
        keep_going = next_button is None
        if keep_going:
            url = next_button.attrs["href"]
    riddle_urls = list(np.unique(riddle_urls))
    log.info(f"Extracted {len(riddle_urls)} riddles.")
    riddle_urls = [f"https://layton.fandom.com{url}" for url in riddle_urls]
    os.makedirs(f"{ROOT_DIR}/layton-data", exist_ok=True)
    for url in tqdm(riddle_urls):
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content
            puzzle_name = url.split("Puzzle:")[-1].replace("/", "_")
            with open(f"{ROOT_DIR}/layton-data/{puzzle_name}.html", "wb") as f:
                f.write(content)
        else:
            log.info(f"Encountered error while navigating to {url}")
