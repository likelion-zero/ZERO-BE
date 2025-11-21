# create/api.py

from create.utils.gemini import get_meanings


def get_word_meanings(word: str):
    # 여기서 print 쓰면 안 됨
    return get_meanings(word, top_k=3)
