import json

DEFAULT_SEARCH_LIMIT = 5

def load_movies():
    with open("data/movies.json") as f:
        return json.load(f)["movies"]

def load_stop_words():
    with open("data/stopwords.txt") as f:
        return f.read().splitlines()
