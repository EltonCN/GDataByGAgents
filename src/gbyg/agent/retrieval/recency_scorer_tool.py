from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import toolpy as tp
from toolpy.tool.tool import TextLike

class MemoryRelativeRecencyScorer(tp.Tool):
    _description = "Scores the relative recency of memories"
    _input_description = {"timestamps":"memories last acess timestamps"}
    _return_description = {"scores":"list of generated scores"}

    def __init__(self, decay_factor: float | None = None) -> None:
        super().__init__(self._description, self._input_description)
    
        if decay_factor is None:
            decay_factor = 0.995

        self._decay_factor = decay_factor

    def _execute(self, query: Dict[str, str] | None, context: str | None) -> Tuple[Dict[str, TextLike], Dict[str, str]]:
        timestamps = np.array(query["timestamps"], dtype=np.float32)
        indexes = np.argsort(timestamps)
        indexes = indexes[::-1]

        scores = np.power(self._decay_factor, indexes)

        max_score = scores.max()
        min_score = scores.min()

        scores = (scores-min_score)/(max_score-min_score)

        result = {"scores":scores}

        return result, self._return_description