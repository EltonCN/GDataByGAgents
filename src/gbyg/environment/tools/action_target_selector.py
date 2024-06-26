from __future__ import annotations

import toolpy as tp

class ActionTargetSelector(tp.BasicTool):
    _description = '''Selects the objects that an action is changing'''

    _system_message = '''You are object selector that outputs in JSON.
The JSON object must use the schema: {'objects':['str', 'str', ...]}

Please use a valid JSON format.
'''

    _base_prompt = '''{environment_tree}
    
Considering the environment hierarchy above, select the objects that the following action is affecting, if any. The actor can affect itself state. 

Actor: {actor}
Place: {place}
Action: {action}
'''
    
    _input_description = {'environment_tree':'tree of elements in the environment',
                          'actor':'actor that is doing the action',
                          'place':'place where the actor is',
                          'action':'action that is beeing made in the environment'
    }

    _return_description = {'objects':'list of affected objects'}

    def __init__(self, model_name:str | None = None) -> None:

        super().__init__(self._description, self._input_description, self._base_prompt, 
                         self._return_description, self._system_message,  model_name,
                         json_mode=True)
