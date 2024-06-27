from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class PlanDecomposer(tp.BasicTool):
    _description = "Decompose a plan action in finner grain actions"
    _input_description = {"original_plan":"original agent plan",
                            "minimum_minutes":"minumum minutes a action must have"}

    _system_message = '''You are a plan decomposer that outputs in JSON.
The JSON must use the schema: {'plan':[{'hour':'int', 'minute':'int', 'action':'str'}, {'hour':'int', 'minute':'int', 'action':'str'}, ...]}. 

The hour must be in 24 hour format (0, 1, ..., 23).
The hour and minute fields are the action start time. 

Please use a valid JSON format.'''

    _base_prompt = '''{original_plan}

Decompose the broad strokes plan above in actions of {minimum_minutes} or more minutes (a action can have more minutes).
'''

    _return_description = {'plan':'generated agent plan with actions, hours and minutes'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description, 
                         input_description=self._input_description, 
                         prompt_template=self._base_prompt, 
                         return_description=self._return_description, 
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)
        