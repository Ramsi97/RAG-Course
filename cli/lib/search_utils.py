import json
import os

DEFAULT_SEARCH_LIMIT = 5
CACHE_DIR   = os.path.join(os.getcwd(), "cache")

def load_movies():
    with open("data/movies.json") as f:
        return json.load(f)["movies"]

def load_stop_words():
    with open("data/stopwords.txt") as f:
        return f.read().splitlines()
# load method for inverted index
