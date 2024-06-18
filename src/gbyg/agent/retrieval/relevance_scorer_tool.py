from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import sentence_transformers
import toolpy as tp
from toolpy.tool.tool import TextLike

class MemoryRelevanceScorer(tp.Tool):
    _description = "Scores the contextual relevance of memories"
    _input_description = {"query_memory":"single memory defining the context", "embeddings":"list of memories embeddings"}
    _return_description = {"scores":"list of generated scores"}

    def __init__(self, embedder_model: str | None = None) -> None:
        super().__init__(self._description, self._input_description)

        if embedder_model is None:
            embedder_model = "all-MiniLM-L6-v2"

        self._embedder = sentence_transformers.SentenceTransformer(embedder_model)
    
    def _execute(self, query: Dict[str, str] | None, context: str | None) -> Tuple[Dict[str, TextLike], Dict[str, str]]:
        query_memory = query["query_memory"]
        embeddings = query["embeddings"]

        query_embedding = self._embedder.encode(query_memory)

        scores = sentence_transformers.util.cos_sim(query_embedding, embeddings)
        scores = scores.numpy()[0]

        result = {"scores":scores}

        return result, self._return_description