from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class InsightGenerator(tp.BasicTool):
    _description = "Generates high-level insights from a list of memory descriptions"
    _input_description = {"statements": "a list of statements/memory descriptions about the agent"}

    _system_message = '''You are an insight generator that outputs in JSON.
The JSON must use the schema: {'insights': [{'insight':'str', 'because_of':['int', 'int']}, {'insight':'str', 'because_of':['int', 'int']}, ...]}. 

Where 'insight' is the generated insight, and 'because_of' are the indexes of the statements used to generate the insight.

Please use a valid JSON format.'''

    _base_prompt = '''
Statements about the agent:
{statements}

What 5 high-level insights can you infer from the above statements?'''

    _return_description = {'insights': 'a list of five high-level insights'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description,
                         input_description=self._input_description,
                         prompt_template=self._base_prompt,
                         return_description=self._return_description,
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)