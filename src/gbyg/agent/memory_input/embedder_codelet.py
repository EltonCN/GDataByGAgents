from __future__ import annotations

from collections import deque

import cst_python as cst

from .embedder_tool import Embedder

class EmbedderCodelet(cst.Codelet):
    def __init__(self, embedder_model:str|None=None, 
                 memories_to_embed_name:str|None=None,
                 memories_output_name:str|None=None) -> None:
        super().__init__()

        self._embedder = Embedder(embedder_model)
        self._last_process = 0

        if memories_to_embed_name is None:
            memories_to_embed_name = "MemoriesToEmbed"
        if memories_output_name is None:
            memories_output_name = "EmbeddedMemories"

        self._memories_to_embed_name = memories_to_embed_name
        self._memories_output_name = memories_output_name

    def access_memory_objects(self) -> None:
        self._to_process_mo : cst.MemoryObject = self.get_input(name=self._memories_to_embed_name)
        self._output_mo : cst.MemoryObject = self.get_output(name=self._memories_output_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        memories_to_embbed : deque = self._to_process_mo.get_info()
        n = len(memories_to_embbed)

        if n == 0:
            return

        memories = []
        for _ in range(n):
            memory = memories_to_embbed.popleft()
            memories.append(memory)

        descriptions = [m['description'] for m in memories]
        query = {"texts":descriptions}
        result, _ = self._embedder(query)
        embeddings = result["embeddings"]
        
        to_score_queue : deque = self._output_mo.get_info()
        for i in range(n):
            memories[i]["embedding"] = embeddings[i]
            to_score_queue.append(memories[i])

        #Just to update timestamp
        self._output_mo.set_info(to_score_queue)
        