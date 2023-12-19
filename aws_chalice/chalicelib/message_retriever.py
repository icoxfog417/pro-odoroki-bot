import html
import re
import urllib.request
from typing import Optional

from bs4 import BeautifulSoup


def exclude_mentions(message: str) -> str:
    return re.sub(r"<@.*?> ", "", message).strip()


def retrieve_description(url: str) -> Optional[str]:
    description = None

    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                html_content = response.read().decode("utf-8")
                soup = BeautifulSoup(html_content, "html.parser")
                tag = soup.find("meta", attrs={"name": "description"})
                description = (
                    html.unescape(tag.get("content")) if tag is not None else None
                )

    except Exception as ex:
        print(ex)

    return description
