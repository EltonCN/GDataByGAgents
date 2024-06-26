from __future__ import annotations

import toolpy as tp

class DetectObjectMovement(tp.BasicTool):
    _description = '''Detects if some object in moving in the environment'''

    _system_message = '''You are object movement detector that outputs in JSON.
The JSON object must use the schema: {'objects':[{'name':'str', 'reasoning':'str', 'origin_place':'str', 'target_place', 'str', 'movement duration':'float'}]}

Where reasoning is the reason why the object is beeing moved.

Please use a valid JSON format.
'''

    _base_prompt = '''{environment_tree}
    
Considering the environment hierarchy above, detects if any object in moving to another place.

The state or action of the object must clearly give a reason for it being moved. DO NOT ASSUME any motives and movements that are not in the provided environment.

If no objects are being moved, return the 'objects' list as empty. 
'''
    
    _input_description = {'environment_tree':'tree of elements in the environment'}

    _return_description = {'objects':'objects beeing moved, with name, origin place, target place and movement duration'}

    def __init__(self, model_name:str | None = None) -> None:

        super().__init__(self._description, self._input_description, self._base_prompt, 
                         self._return_description, self._system_message,  model_name,
                         json_mode=True)
