from collections import defaultdict
import os
import string

from .search_utils import (
    DEFAULT_SEARCH_LIMIT,
    load_movies,
    load_stop_words,
    CACHE_DIR,
)
from nltk.stem import PorterStemmer
import pickle
Stop_Words = load_stop_words()
Stemmer = PorterStemmer()
def search_command(query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> list[dict]:
    idx = InvertedIndex()
    idx.load()
    seen, result = set(), []
    query_tokens = tokenize_text(query)
    for query_token in query_tokens:
        doc_ids = idx.get_documents(query_token)
        for doc_id in doc_ids:
            if doc_id not in seen:
                seen.add(doc_id)
                result.append(idx.docmap[doc_id])
                if len(result) >= DEFAULT_SEARCH_LIMIT:
                    return result
    return result

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def tokenize_text(text: str) -> list[str]:
    text =  preprocess_text(text)
    tokens = text.split()
    valid_tokens = [token for token in tokens if token]
    return stem_tokens(valid_tokens)

def remove_stop_words(tokens: list[str]) -> list[str]:
    stop_words = [preprocess_text(word) for word in Stop_Words]
    return [token for token in tokens if token not in stop_words]

def stem_tokens(tokens: list[str]) -> list[str]:
    tokens = remove_stop_words(tokens)
    return [Stemmer.stem(token) for token in tokens]

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(set)
        self.docmap: dict[int, dict] = {}
        self.index_path = os.path.join(CACHE_DIR, "index.pkl")
        self.docmap_path = os.path.join(CACHE_DIR, "docmap.pkl")
    def __add_document(self, doc_id: int, text: str) -> None:
        tokens = tokenize_text(text)
        tokens = stem_tokens(tokens)
        for token in tokens:
            self.index[token].add(doc_id)
            
    def get_documents(self, term: str) -> list[int]:
        doc_ids = self.index.get(term, set())
        return sorted(list(doc_ids))

    def build(self) -> None:
        movies = load_movies()
        for movie in movies:
            doc_id = movie["id"]
            doc_description = f"{movie['title']} {movie['description']}"
            self.docmap[doc_id] = movie
            self.__add_document(doc_id, doc_description)
    def save(self) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump(self.index, f)
        with open(self.docmap_path, "wb") as f:
            pickle.dump(self.docmap, f)
    def load(self) -> None:
        with open(self.index_path, "rb") as f:
            self.index = pickle.load(f)
        with open(self.docmap_path, "rb") as f:
            self.docmap = pickle.load(f)

def build_command() -> None:
    index = InvertedIndex()
    index.build()
    index.save()
    