from __future__ import annotations

import toolpy as tp

class SummaryFunction(tp.BasicTool):
    _description = "Summarizes statements to describe something."
    
    _input_description = {"query_statement":"the statement that will be described", "statements":"statements to summarize"}
    _return_description = {'description':'summarize description of the query'}

    _system_message = '''You are a statement summarizer, summarizing to describe something.
The JSON must use the schema: {'description':'str'}. 

Please use a valid JSON format.'''

    _base_prompt = '''How would you describe {query_statement} given the following statements?

{statements}'''

    def __init__(self,  model_name: str | None = None) -> None:
        super().__init__(self._description, 
                         self._input_description, 
                         self._base_prompt, 
                         self._return_description, 
                         self._system_message, model_name, True)