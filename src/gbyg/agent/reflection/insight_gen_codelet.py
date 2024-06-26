from __future__ import annotations

import datetime
from typing import List

import cst_python as cst

from .insight_gen_tool import InsightGenerator

class InsightGeneratorCodelet(cst.Codelet):
    def __init__(self, 
                 statements_name: str | None = None, 
                 memories_input_name: str | None = None,
                 agent_time_name : str | None = None) -> None:
        super().__init__()

        if statements_name is None:
            statements_name = "Statements"
        if memories_input_name is None:
            memories_input_name = "GeneratedInsights"
        if agent_time_name is None:
            agent_time_name = "AgentTime"

        self._statements_name = statements_name
        self._memories_input_name = memories_input_name
        self._agent_time_name = agent_time_name

        self._last_proc = 0

        self._insight_generator = InsightGenerator()

    def access_memory_objects(self) -> None:
        self._statements_mo = self.get_input(name=self._statements_name)
        self._memories_input_mo = self.get_output(name=self._memories_input_name)
        self._agent_time_mo = self.get_input(name=self._agent_time_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        statements: List[str] = self._statements_mo.get_info()
        
        if statements is None or statements == "":
            return
        if len(statements) == 0:
            return
        if self._statements_mo.get_timestamp() <= self._last_proc:
            return
        self._last_proc = self._statements_mo.get_timestamp()
        
        descriptions = [m["description"] for m in statements]
        indexes = [m["index"] for m in statements]

        statements = ["Statement "+str(indexes[i])+": "+descriptions[i] for i in range(len(indexes))]
        statements = "\n".join(statements)

        query = {"statements": statements}
        result, _ = self._insight_generator._execute(query, context="")
        insights = result["insights"]

        #Send memories to input

        memories_input = self._memories_input_mo.get_info()
        agent_time = self._agent_time_mo.get_info()

        for insight in insights:
            memory = {}
            memory["type"] = "reflection"
            memory["description"] = insight["insight"]
            memory["created"] = agent_time
            memory["last_acessed"] = agent_time
            memory["because_of"] = insight["because_of"]

            memories_input.append(memory)

        
        self._memories_input_mo.set_info(memories_input)