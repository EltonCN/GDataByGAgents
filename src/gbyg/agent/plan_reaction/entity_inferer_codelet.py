from __future__ import annotations

from typing import Dict, List

import cst_python as cst
from collections import deque

from .entity_inferer_tool import EntityInferer

class EntityInfererCodelet(cst.Codelet):
    def __init__(self,
                 memory_to_infer_name: str | None = None, 
                 inferred_entities_name: str | None = None) -> None:
        super().__init__()

        if memory_to_infer_name is None:
            memory_to_infer_name = "MemoryToInfer"
        if inferred_entities_name is None:
            inferred_entities_name = "InferredEntities"

        self._memory_to_infer_name = memory_to_infer_name
        self._inferred_entities_name = inferred_entities_name

        self._entity_inferer = EntityInferer()

    def access_memory_objects(self) -> None:
        self._to_infer = self.get_input(name=self._memory_to_infer_name)
        self._inferred_entities_mo = self.get_output(name=self._inferred_entities_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        memory_to_infer: List = self._to_infer.get_info()
        inferred_entities: List = self._inferred_entities_mo.get_info()

        for memory in memory_to_infer:
            if memory['type'] == 'observation' and not memory.get('queries_retrieved', False):
                query = {"observation": memory["description"]}
                result, _ = self._entity_inferer._execute(query, context="")
                inferred_entities.append(result["queries"])
                memory['queries_retrieved'] = True  

        self._inferred_entities_mo.set_info(inferred_entities)