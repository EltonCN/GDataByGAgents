from __future__ import annotations

from collections import deque
from typing import List

import cst_python as cst

from .importance_scorer_tool import MemoryImportanceScorer

class MemoryImportanceScorerCodelet(cst.Codelet):
    def __init__(self, model_name:str|None=None, 
                memories_to_score_name:str|None=None, 
                scored_memories_name:str|None=None) -> None:
        super().__init__()

        if memories_to_score_name is None:
            memories_to_score_name = "MemoriesToScore"
        if scored_memories_name is None:
            scored_memories_name = "ScoredMemories"

        self._memories_to_score_name = memories_to_score_name
        self._scored_memories_name = scored_memories_name

        self._importance_scorer = MemoryImportanceScorer(model_name)
    
    def access_memory_objects(self) -> None:
        self._to_score_mo = self.get_input(name=self._memories_to_score_name)
        self._memory_stream_mo = self.get_output(name=self._scored_memories_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        memories_to_score : deque = self._to_score_mo.get_info()
        memory_stream : List = self._memory_stream_mo.get_info()
        n = len(memories_to_score)

        for _ in range(n):
            memory = memories_to_score.popleft()
            query = {"memory":memory["description"]}
            result, _ = self._importance_scorer(query)
            memory["importance"] = result["score"]

            memory_stream.append(memory)

        #Just to update timestamp
        self._memory_stream_mo.set_info(memory_stream)
