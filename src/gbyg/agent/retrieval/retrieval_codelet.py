from __future__ import annotations

import datetime
import time
from collections import deque

import numpy as np
import cst_python as cst

from .recency_scorer_tool import MemoryRelativeRecencyScorer
from .relevance_scorer_tool import MemoryRelevanceScorer


class RetrievalCodelet(cst.Codelet):
    def __init__(self, 
                 query_memory_name:str|None=None, 
                 memory_stream_name:str|None=None,
                 agent_time_name:str|None=None,
                 retrieved_memories_name:str|None=None, 
                 n_to_retrieve:int=100,
                 decay_factor:float|None=None, embedder_model:str|None = None) -> None:
        super().__init__()

        if query_memory_name is None:
            query_memory_name = "QueryMemory"
        if memory_stream_name is None:
            memory_stream_name = "MemoryStream"
        if retrieved_memories_name is None:
            retrieved_memories_name = "RetrievedMemories"
        if agent_time_name is None:
            agent_time_name = "AgentTime"
        

        self._query_memory_name = query_memory_name
        self._retrieved_memories_name = retrieved_memories_name
        self._memory_stream_name = memory_stream_name
        self._agent_time_name = agent_time_name

        self._n = n_to_retrieve
        self._last_process = 0

        self._recency_scorer = MemoryRelativeRecencyScorer(decay_factor)
        self._relevance_scorer = MemoryRelevanceScorer(embedder_model)

    def access_memory_objects(self) -> None:
        self._query_memory_mo = self.get_input(name=self._query_memory_name)
        self._memory_stream_mo = self.get_input(name=self._memory_stream_name)
        self._retrieved_memories_mo = self.get_output(name=self._retrieved_memories_name)
        self._agent_time_mo = self.get_input(name=self._agent_time_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        all_queries = self._query_memory_mo.get_info()

        if all_queries is None or all_queries == "":
            return
        if self._query_memory_mo.get_timestamp() <= self._last_process:
            return

        if not isinstance(all_queries, list):
            all_queries = [all_queries]
        
        retrieved_memories = []
        retrieved_indexes = set()
        for query_memory in all_queries:
        
            if query_memory is None or query_memory == "":
                return
            

            self._last_process = time.time()

            memory_stream : deque = self._memory_stream_mo.get_info()
            
            importances = []
            timestamps = []
            embeddings = []

            for memory in memory_stream:
                importances.append(memory["importance"])
                timestamps.append(memory["last_acessed"])
                embeddings.append(memory["embedding"])

            importances = np.array(importances)

            query = {"timestamps":timestamps}
            result, _ = self._recency_scorer(query)
            recencies = result["scores"]
    
            if isinstance(query_memory, str):
                query_description = query_memory
            else:
                query_description = query_memory["description"]

            query = {"query_memory":query_description, "embeddings":embeddings}
            result, _ = self._relevance_scorer(query)
            relevances = result["scores"]

            scores = importances + recencies + relevances
            indexes = np.argpartition(scores, -self._n)[-self._n:]
            
            for i in indexes:
                memory = memory_stream[i]

                if memory["index"] in retrieved_indexes:
                    continue
                    
                retrieved_indexes.add(memory["index"])
                retrieved_memories.append(memory)

        current_time = self._agent_time_mo.get_info()
        for m in retrieved_memories:
            m["last_acessed"] = current_time

        self._retrieved_memories_mo.set_info(retrieved_memories)
