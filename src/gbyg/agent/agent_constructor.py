from __future__ import annotations

from collections import deque

import cst_python as cst

from .memory_input import memory_input_constructor
from .summary import summary_description_generator_constructor
from .reflection import reflection_constructor
from .memory_stream import MemoryStream

from .plan_reaction import EntityInfererCodelet

def agent_constructor(mind:cst.Mind, importance_threshould:float|None=None) -> None:
    memories_input = mind.create_memory_object("MemoriesInput", deque())
    memory_stream = mind.create_memory_object("MemoryStream", MemoryStream())
    agent_summary_description = mind.create_memory_object("AgentSummaryDescription", "")
    agent_info = mind.create_memory_object("AgentInfo", {"name":"", "age":0, "traits":""})
    agent_time = mind.create_memory_object("AgentTime", 0)
    actual_place = mind.create_memory_object("ActualPlace", "")


    memory_input_constructor(mind, memories_input, memory_stream)
    summary_description_generator_constructor(mind, memory_stream, agent_info, 
                                              agent_time, agent_summary_description, 
                                              n_to_retrieve=2)
    reflection_constructor(mind, memories_input, memory_stream, agent_time, importance_threshould)
    

    infered_entities = mind.create_memory_object("InferedEntities", [])
    entity_inferer_codelet = EntityInfererCodelet(memory_stream.get_name(),
                                                  infered_entities.get_name())
    entity_inferer_codelet.add_input(memory_stream)
    entity_inferer_codelet.add_output(infered_entities)
    mind.insert_codelet(entity_inferer_codelet) 
