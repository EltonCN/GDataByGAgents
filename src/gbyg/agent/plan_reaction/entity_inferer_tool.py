from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class EntityInferer(tp.BasicTool):
    _description = "Infer the observed entity and its action status from an observation."
    _input_description = {"observation": "the observation description"}

    _system_message = '''You are an entity inferer that outputs in JSON.
The JSON must use the schema: {"entity": [{"observed_entity": "str", "action_status": "str"}]}.
Please use a valid JSON format.'''

    _base_prompt = _base_prompt = '''Given an observation, identify the central/main entity that the subject is observing/noticing/perceiving. Then, extract relevant and detailed information about the entity's current state or actions.

Observation:{observation}'''

    _return_description = {"entity": [{"observed_entity": "entity", "action_status": "status"}]}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description, 
                         input_description=self._input_description, 
                         prompt_template=self._base_prompt, 
                         return_description=self._return_description, 
                         system_message=self._system_message, 
                         model_name=model_name, 
                         json_mode=True)

    def _execute(self, query: Dict[str, str], context: str) -> Tuple[Dict[str, TextLike], Dict[str, str]]:
        result, return_description = super()._execute(query, context)

        entities = result.get("entity", [])

        queries = []
        for entity in entities:
            observed_entity = entity["observed_entity"]
            action_status = entity["action_status"]
            queries.append({
                "query_1": f"What is Alex's relationship with the {observed_entity}?",
                "query_2": f"The {observed_entity} is {action_status}."
            })

        return {"queries": queries}, return_description