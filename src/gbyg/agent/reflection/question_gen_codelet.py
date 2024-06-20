from __future__ import annotations

from typing import List

import cst_python as cst

from .question_gen_tool import QuestionGenerator

class QuestionGeneratorCodelet(cst.Codelet):
    def __init__(self, 
                 memories_description: str | None = None, 
                 generated_questions_name: str | None = None) -> None:
        super().__init__()

        if memories_description is None:
            memories_description = "Memories"
        if generated_questions_name is None:
            generated_questions_name = "GeneratedQuestions"

        self._memories_description = memories_description
        self._generated_questions_name = generated_questions_name

        self._question_generator = QuestionGenerator()

    def access_memory_objects(self) -> None:
        self._memories_mo = self.get_input(name=self._memories_description)
        self._generated_questions_mo = self.get_output(name=self._generated_questions_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self,) -> None:
        memories: List[str] = self._memories_mo.get_info()
        descriptions = [m["description"] for m in memories]
        statements = "\n".join(descriptions)
        query = {"memories": statements}
        result, _ = self._question_generator._execute(query, context="")
        questions = result["questions"]

        self._generated_questions_mo.set_info(questions)