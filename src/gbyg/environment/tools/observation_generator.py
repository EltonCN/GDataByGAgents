from __future__ import annotations

import toolpy as tp

class ObservationGenerator(tp.BasicTool):
    _description = '''Generates the observation of a agent'''

    _system_message = '''You are observation generator that outputs in JSON.
The JSON object must use the schema: {'observation':'str'}

Please use a valid JSON format.
'''

    _base_prompt = '''{environment_tree}
    
Considering the environment hierarchy above, generates the observation for the following agent:

Agent name: {agent}
Agent state: {state}
Agent place: {place}
Agent action: {action}

The observation must describe what the agent can see, hear and feel sensorially. Use the third person singular.
'''
    
    _input_description = {'environment_tree':'tree of elements in the environment',
                          'agent':'actor that is doing the action',
                          'state':'current agent state',
                          'place':'place where the agent is',
                          'action':'action that the agent is doing'
    }

    _return_description = {'observation':'agent observation'}

    def __init__(self, model_name:str | None = None) -> None:

        super().__init__(self._description, self._input_description, self._base_prompt, 
                         self._return_description, self._system_message,  model_name,
                         json_mode=True)
