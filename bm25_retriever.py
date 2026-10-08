# ============================================================
# Mariano LegRAG IA - Búsqueda léxica BM25
# ============================================================

import re
import unicodedata
from typing import List, Tuple
import numpy as np
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, chunks_texts: List[str]):
        self.chunks_texts = chunks_texts
        self.tokenized_corpus = [self._tokenize(text) for text in chunks_texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        # Normalizar unicode, quitar tildes
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii").lower()

        # Extraer palabras y números (con punto decimal opcional)
        tokens = re.findall(r"\b[a-z]+(?:\.[a-z]+)?\b|\d+(?:\.\d+)*", text)
        return tokens

    def retrieve(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        top_indices = np.argsort(scores)[-k:][::-1]
        results = []
        for idx in top_indices:
            results.append((self.chunks_texts[idx], float(scores[idx])))

        return results