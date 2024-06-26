from __future__ import annotations

from collections import deque

import cst_python as cst

from .memory_input import memory_input_constructor
from .summary import summary_description_generator_constructor
from .reflection import reflection_constructor
from .memory_stream import MemoryStream

def agent_constructor(mind:cst.Mind, importance_threshould:float|None=None) -> None:
    memories_input = mind.create_memory_object("MemoriesInput", deque())
    memory_stream = mind.create_memory_object("MemoryStream", MemoryStream())
    agent_summary_description = mind.create_memory_object("AgentSummaryDescription", "")
    agent_info = mind.create_memory_object("AgentInfo", {"name":"", "age":0, "traits":""})
    agent_time = mind.create_memory_object("AgentTime", 0)

    memory_input_constructor(mind, memories_input, memory_stream)
    summary_description_generator_constructor(mind, memory_stream, agent_info, 
                                              agent_time, agent_summary_description, 
                                              n_to_retrieve=2)
    reflection_constructor(mind, memories_input, memory_stream, agent_time, importance_threshould)