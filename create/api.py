# create/api.py

from create.utils.gemini import get_meanings


def get_word_meanings(word: str):
    return get_meanings(word, top_k=3)

