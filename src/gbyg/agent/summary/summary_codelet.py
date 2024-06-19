from __future__ import annotations

import time

import cst_python as cst

from .summary_tool import SummaryFunction




class SummaryFunctionCodelet(cst.Codelet):
    def __init__(self, query_memory_name:str | None=None, 
                 memories_memory_name:str | None=None, 
                 summary_memory_name:str | None=None,
                 model_name:str|None=None) -> None:
        super().__init__()

        if query_memory_name is None:
            query_memory_name = "QueryMemory"
        if memories_memory_name is None:
            memories_memory_name = "Memories"
        if summary_memory_name is None:
            summary_memory_name = "Summary"

        self._query_memory_name = query_memory_name
        self._memories_memory_name = memories_memory_name
        self._summary_memory_name = summary_memory_name

        self._summary_function = SummaryFunction(model_name)

        self._last_process = 0

    def access_memory_objects(self) -> None:
        self._query_memory_mo = self.get_input(name=self._query_memory_name)
        self._memories_mo = self.get_input(name=self._memories_memory_name)
        self._summary_mo = self.get_output(name=self._summary_memory_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        query_memory = self._query_memory_mo.get_info()
        memories = self._memories_mo.get_info() 

        if query_memory is None or query_memory == "":
            return
        if self._query_memory_mo.get_timestamp() <= self._last_process:
            return
        
        if memories is None or memories == "" or len(memories) == 0:
            return
        if self._memories_mo.get_timestamp() <= self._last_process:
            return
        
        self._last_process = time.time()

        if isinstance(query_memory, str):
            query_statement = query_memory
        else:
            query_statement = query_memory["description"]

        if isinstance(memories, str):
            statements = memories
        elif isinstance(memories, list):
            if isinstance(memories[0], str):
                statements = "\n".join(memories)
            else:
                descriptions = [m["description"] for m in memories]
                statements = "\n".join(descriptions)

        query = {"query_statement":query_statement, "statements":statements}

        result, _ = self._summary_function(query)

        summary = result["description"]

        self._summary_mo.set_info(summary)