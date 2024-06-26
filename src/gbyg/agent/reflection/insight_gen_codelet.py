from __future__ import annotations

from typing import List

import cst_python as cst

from .insight_gen_tool import InsightGenerator

class InsightGeneratorCodelet(cst.Codelet):
    def __init__(self, 
                 statements: str | None = None, 
                 generated_insights_name: str | None = None) -> None:
        super().__init__()

        if statements is None:
            statements = "Statements"
        if generated_insights_name is None:
            generated_insights_name = "GeneratedInsights"

        self._statements = statements
        self._generated_insights_name = generated_insights_name

        self._insight_generator = InsightGenerator()

    def access_memory_objects(self) -> None:
        self._statements_mo = self.get_input(name=self._statements)
        self._generated_insights_mo = self.get_output(name=self._generated_insights_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        statements: List[str] = self._statements_mo.get_info()
        # descriptions = [m["description"] for m in statements]
        # statements = "\n".join(descriptions)
        query = {"statements": statements}
        result, _ = self._insight_generator._execute(query, context="")
        insights = result["insights"]

        self._generated_insights_mo.set_info(insights)