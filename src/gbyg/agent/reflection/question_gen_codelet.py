from __future__ import annotations

from typing import List

import cst_python as cst

from .question_gen_tool import QuestionGenerator
from gbyg.agent.memory_stream import MemoryStream

class QuestionGeneratorCodelet(cst.Codelet):
    def __init__(self, 
                 memories_description: str | None = None, 
                 agent_time_name : str | None = None,
                 generated_questions_name: str | None = None,
                 importance_threshould:float|None=None) -> None:
        super().__init__()

        if memories_description is None:
            memories_description = "Memories"
        if generated_questions_name is None:
            generated_questions_name = "GeneratedQuestions"
        if importance_threshould is None:
            importance_threshould = 10
        if agent_time_name is None:
            agent_time_name = "AgentTime"

        self._memories_description = memories_description
        self._generated_questions_name = generated_questions_name
        self._importance_threshould = importance_threshould
        self._agent_time_name = agent_time_name

        self._last_process = 0
        self._last_created = 0

        self._question_generator = QuestionGenerator()

    def access_memory_objects(self) -> None:
        self._memories_mo = self.get_input(name=self._memories_description)
        self._generated_questions_mo = self.get_output(name=self._generated_questions_name)
        self._agent_time_mo = self.get_input(name=self._agent_time_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self,) -> None:
        memories: MemoryStream = self._memories_mo.get_info()

        if memories is None or memories == "":
            return
        if self._memories_mo.get_timestamp() <= self._last_process:
            return
        
        self._last_process = self._memories_mo.get_timestamp()

        last_150 = memories.get_last_created(150, self._last_created)
        cumulative_importance = sum([m["importance"] for m in last_150])

        if cumulative_importance < self._importance_threshould:
            return

        memories = memories.get_last_created(100)

        descriptions = [m["description"] for m in memories]
        statements = "\n".join(descriptions)
        query = {"memories": statements}
        result, _ = self._question_generator(query, context="")
        questions = result["questions"]

        agent_time = self._agent_time_mo.get_info()
        self._last_created = agent_time

        self._generated_questions_mo.set_info(questions)