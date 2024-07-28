import random
import re
from collections import defaultdict

import cmudict

cmudict = cmudict.dict()
inverted_cmudict = defaultdict(list)
for word, pronunciations in cmudict.items():
    for pronunciation in pronunciations:
        inverted_cmudict[tuple(pronunciation)].append(word)


def homophone(text: str) -> str:
    """Transform a word into a random homophone."""
    if text not in cmudict:
        return text

    pronunciation = cmudict[text]
    selected_pronunciation = random.choice(pronunciation)
    alternates = inverted_cmudict[tuple(selected_pronunciation)]
    return random.choice(alternates)


def homophonify(text: str) -> str:
    """Process a paragraph by converting each word into homophones."""
    return re.sub(r"\w+", lambda word: homophone(word.group(0)), text).capitalize()


def uwufy(text: str) -> str:
    """Uwufy the sentence."""
    uwufied = ""
    for index, value in enumerate(text):
        caps = value.isupper()
        if value in ("L", "l", "R", "r"):
            uwufied += "W" if caps else "w"
        elif value.lower() == "o" and text[index - 1] in ("N", "n", "M", "m") and index > 0:
            uwufied += "yo"
        else:
            uwufied += value
    return uwufied
