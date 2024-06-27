from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class ActionTool(tp.BasicTool):
    _description = "Selects the next agent action"
    _input_description = {"know_world_tree": "know places and objects in the world, in a tree structure",
                          "name": "agent name",
                          "state": "current agent state",
                          "observation": "current agent observation",
                          "place": "current agent location",
                          "planned_action": "action the agent planned to do now",
                          "action": "actual current action",
                          "next_action": "next_planned_action",
                          "time": "current time"}

    _system_message = '''You are a action generator that outputs in JSON.
The JSON must use the schema: {'action':'str'}. 

The action must start with the person name.

Please use a valid JSON format.'''

    _base_prompt = '''Know world tree: {know_world_tree}

Considering the above know world, and the bellow information, what should be {name} action?
Prefer to stay in the current area if the activity can be done there.

Current state: {state}
Current observation: {observation}
Current place: {place}
Current planned action: {planned_action}
Current actual action: {action}
Next planned action: {next_action}
Current time: {time}
'''

    _return_description = {'action':'action for the agent perform'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description, 
                         input_description=self._input_description, 
                         prompt_template=self._base_prompt, 
                         return_description=self._return_description, 
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)
        