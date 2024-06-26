from __future__ import annotations

import toolpy as tp


class ActionDurationEstimator(tp.BasicTool):
    _description = '''Estimates the duration of a action.'''

    _system_message = '''You are action duration estimator that outputs in JSON.
The JSON object must use the schema: {'reasoning':'str', 'action_duration':'float '}

Where reasoning is the reason why the action takes this time. The action_duration must be in seconds.

Please use a valid JSON format.
'''

    _base_prompt = '''{environment_tree}   

Considering the above environment tree, estimate the following action duration. 

DO NOT ASSUME ANYTHING THAT IS NOT IN THE ENVIRONMENT OR AGENT ACTION.

Action agent: {agent}
Action: {action}
'''
    
    _input_description = {'agent':'who is doing the action',
                          'environment_tree': 'tree of elements in the environment',
                            'action':'agent action'}

    _return_description = {'reasoning':'why the action takes this time', 
                           'action_duration':'duration of the action in seconds'}

    def __init__(self, model_name:str | None = None) -> None:

        super().__init__(self._description, self._input_description, self._base_prompt, 
                         self._return_description, self._system_message,  model_name,
                         json_mode=True)
