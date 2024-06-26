from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class QuestionGenerator(tp.BasicTool):
    _description = "Generates questions from a list of memories"
    _input_description = {"memories": "a list of memory descriptions"}

    _system_message = '''You are a question generator that outputs in JSON.
The JSON must use the schema: {'questions': ['str', 'str', 'str']}. 

Please use a valid JSON format.'''

    _base_prompt = '''
Given the following list of memories:
{memories}

What are 3 most salient high-level questions we can answer about the subjects in these memories?'''

    _return_description = {'questions': 'a list of three high-level questions'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description,
                         input_description=self._input_description,
                         prompt_template=self._base_prompt,
                         return_description=self._return_description,
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)