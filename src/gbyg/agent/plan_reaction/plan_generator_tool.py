from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class PlanGenerator(tp.BasicTool):
    _description = "Generates a day plan for a agent"
    _input_description = {"summary_description":"agent summary description",
                          "previous_day_summary":"agent summary of previous day",
                          "today_date":"today date, with weekday, month and day",
                          "agent_name":"name of the agent"}

    _system_message = '''You are a plan generator that outputs in JSON.
The JSON must use the schema: {'plan':[{'hour':'int', 'action':'str'}, {'hour':'int', 'action':'str'}, ...]}. 

The hour must be in a 24 hour format (0, 1, ..., 23), and is the action start time.

Please use a valid JSON format.'''

    _base_prompt = '''{summary_description}

{previous_day_summary}

Today is {today_date}, here is {agent_name} for today in broad strokes:
'''

    _return_description = {'plan':'generated agent plan with actions and hours'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description, 
                         input_description=self._input_description, 
                         prompt_template=self._base_prompt, 
                         return_description=self._return_description, 
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)
        