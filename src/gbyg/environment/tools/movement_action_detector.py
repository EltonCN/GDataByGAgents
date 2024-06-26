from __future__ import annotations

import toolpy as tp


class MovementActionDetector(tp.BasicTool):
    _description = '''Detects if a action is a movement.'''

    _system_message = '''You are movement action detector that outputs in JSON.
The JSON object must use the schema: {'reasoning':'str', 'is_movement':'bool', 'from':'str','to':'str','movement_duration':'float '}

Where reasoning is the reason why the object is beeing moved. The movement_duration must be in seconds.

Please use a valid JSON format.
'''

    _base_prompt = '''{environment_tree}   

Considering the above environment tree, detect if the following action is a movement of the agent. 
The action must clearly give a reason for it being a movement. The from and to places must be in the environment tree.

DO NOT ASSUME any motives and movements.

Action agent: {agent}
Action: {action}
'''
    
    _input_description = {'agent':'who is doing the action',
                          'environment_tree': 'tree of elements in the environment',
                            'action':'agent action'}

    _return_description = {'reasoning':'why this action is a movement', 
                           'is_movement':'bool indicating if the action is a movement', 
                           'from':'from where the object is coming',
                           'to':'to where the object is going',
                           'movement_duration':'duration of the movement in seconds'}

    def __init__(self, model_name:str | None = None) -> None:

        super().__init__(self._description, self._input_description, self._base_prompt, 
                         self._return_description, self._system_message,  model_name,
                         json_mode=True)
