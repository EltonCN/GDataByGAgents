from __future__ import annotations

from typing import Dict, Tuple

import toolpy as tp
from toolpy.tool.tool import TextLike

class MemoryImportanceScorer(tp.BasicTool):
    _description = "Evaluates the intrinsic importance of a memory, distinguishing between core memories and mundane memories"
    _input_description = {"memory":"the memory description"}

    _system_message = '''You are a memory importance scorer that outputs in JSON.
The JSON must use the schema: {'score':'float'}. 

Please use a valid JSON format.'''

    _base_prompt = '''On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory.

Memory: {memory}'''

    _return_description = {'score':'the importance score for the memory'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description, 
                         input_description=self._input_description, 
                         prompt_template=self._base_prompt, 
                         return_description=self._return_description, 
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)
        
    def _execute(self, query: Dict[str, str], context: str) -> Tuple[Dict[str, TextLike], Dict[str, str]]:
        result, return_description =  super()._execute(query, context)
        
        score = result["score"]
        norm_score = (score-1)/9
        result["score"] = norm_score
    
        return result, return_description
        