from __future__ import annotations

from typing import Dict, Tuple

import sentence_transformers

import toolpy as tp
from toolpy.tool.tool import TextLike

class Embedder(tp.Tool):
    _description = "Creates text embeddings"
    _input_description = {"texts":"list of texts to embed"}
    _return_description = {"embeddings":"list of generated embeddings"}

    def __init__(self, embedder_model: str | None = None) -> None:
        super().__init__(self._description, self._input_description)

        if embedder_model is None:
            embedder_model = "all-MiniLM-L6-v2"

        self._embedder = sentence_transformers.SentenceTransformer(embedder_model)
    
    def _execute(self, query: Dict[str, str] | None, context: str | None) -> Tuple[Dict[str, TextLike], Dict[str, str]]:
        texts = query["texts"]
        embeddings = self._embedder.encode(texts)

        result = {"embeddings":embeddings}

        return result, self._return_description