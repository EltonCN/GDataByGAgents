from collections import deque

import cst_python as cst

from .memory_input import memory_input_constructor
from .summary import summary_description_generator_constructor
from .retrieval import RetrievalCodelet

def agent_constructor(mind:cst.Mind) -> None:
    memories_input = mind.create_memory_object("MemoriesInput", deque())
    memory_stream = mind.create_memory_object("MemoryStream", [])
    agent_summary_description = mind.create_memory_object("AgentSummaryDescription", "")
    agent_info = mind.create_memory_object("AgentInfo", {"name":"", "age":0, "traits":""})
    agent_time = mind.create_memory_object("AgentTime", 0)

    memory_input_constructor(mind, memories_input, memory_stream)
    summary_description_generator_constructor(mind, memory_stream, agent_info, 
                                              agent_time, agent_summary_description, 
                                              n_to_retrieve=2)
    
    #For test only (will be removed)
    query_memory = mind.create_memory_object("QueryMemory")
    retrieved_memories = mind.create_memory_object("RetrievedMemories")
    retrieval_codelet = RetrievalCodelet(query_memory.get_name(), 
                                         memory_stream.get_name(), 
                                         retrieved_memories.get_name(), 
                                         n_to_retrieve=2)
    
    retrieval_codelet.add_input(query_memory)
    retrieval_codelet.add_input(memory_stream)
    retrieval_codelet.add_output(retrieved_memories)
    
    mind.insert_codelet(retrieval_codelet)