from __future__ import annotations

import toolpy as tp

class ObjectStateUpdater(tp.BasicTool):
    _description = '''Updates a object state'''

    _system_message = '''You are a object state updater that outputs in JSON.
The JSON object must use the schema: {'new_state':'str'}

Please use a valid JSON format.
'''

    _base_prompt = '''Update the following object state:

Object name: {name}
Object place: {place}
Object description: {description}
Object current state: {state}
Actor: {actor}
Action on the object: {action}

The new state must describe only the object, not where it is or what is around it.
'''
    
    _input_description = {'name':'object name',
                          'place':'place where the object current are',
                          'description':'object description',
                          'state':'object current state',
                          'actor':'actor acting on the object',
                          'action':'action on the object'}

    _return_description = {'new_state':'new_state for the object'}

    def __init__(self, model_name:str | None = None) -> None:

        super().__init__(self._description, self._input_description, self._base_prompt, 
                         self._return_description, self._system_message,  model_name,
                         json_mode=True)
