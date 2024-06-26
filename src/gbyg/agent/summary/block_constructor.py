from __future__ import annotations

import cst_python as cst

from .summary_codelet import SummaryFunctionCodelet
from .summary_trigger_codelet import SummaryTriggerCodelet
from gbyg.agent.concat import TextConcatCodelet
from gbyg.agent.retrieval import RetrievalCodelet
from gbyg.agent.memory_stream import MemoryStream

def summary_description_generator_constructor(mind:cst.Mind, 
                            memory_stream:cst.MemoryObject|None=None,
                            agent_info:cst.MemoryObject|None=None,
                            agent_time:cst.MemoryObject|None=None,
                            agent_summary_description:cst.MemoryObject|None=None,
                            interval:float|None=None,
                            model_name:str|None=None,
                            n_to_retrieve:int|None=None,
                            decay_factor:float|None=None,
                            embedder_model:str|None=None) -> None:
    
    if memory_stream is None:
        memory_stream = mind.create_memory_object("MemoryStream", MemoryStream())
    if agent_info is None:
        agent_info = mind.create_memory_object("AgentInfo", {"name":"", "age":0, "traits":""})
    if agent_summary_description is None:
        agent_summary_description = mind.create_memory_object("AgentSummaryDescription", "")
    if agent_time is None:
        agent_time = mind.create_memory_object("AgentTime", 0)

    dimensions = ["Characteristics", "DailyOccupation", "ProgressFeeling"]
    query_memories = {}
    retrieved_memories = {}
    summary_memories = {}

    for dimension in dimensions:
        query_memory = mind.create_memory_object(dimension+"Query")
        retrieved_memory = mind.create_memory_object(dimension+"Memories", [])
        summary_memory = mind.create_memory_object(dimension+"Summary")

        query_memories[dimension] = query_memory
        retrieved_memories[dimension] = retrieved_memory
        summary_memories[dimension] = summary_memory

    trigger_codelet = SummaryTriggerCodelet(agent_info.get_name(),
                                            agent_time.get_name(),
                                            memory_stream.get_name(),
                                            query_memories["Characteristics"].get_name(),
                                            query_memories["DailyOccupation"].get_name(),
                                            query_memories["ProgressFeeling"].get_name(),
                                            interval)
    trigger_codelet.add_input(agent_info)
    trigger_codelet.add_input(agent_time)
    trigger_codelet.add_input(memory_stream)
    for dimension in dimensions:
        trigger_codelet.add_output(query_memories[dimension])
    
    retrieval_codelets = {}
    summary_codelets = {}
    for dimension in dimensions:

        retrieval_codelet = RetrievalCodelet(query_memories[dimension].get_name(),
                                             memory_stream.get_name(),
                                             agent_time.get_name(),
                                             retrieved_memories[dimension].get_name(),
                                             n_to_retrieve,
                                             decay_factor,
                                             embedder_model)
        retrieval_codelet.add_input(query_memories[dimension])
        retrieval_codelet.add_input(memory_stream)
        retrieval_codelet.add_input(agent_time)
        retrieval_codelet.add_output(retrieved_memories[dimension])

        summary_codelet = SummaryFunctionCodelet(query_memories[dimension].get_name(), 
                                                 retrieved_memories[dimension].get_name(),
                                                 summary_memories[dimension].get_name(),
                                                 model_name)
        summary_codelet.add_input(query_memories[dimension])
        summary_codelet.add_input(retrieved_memories[dimension])
        summary_codelet.add_output(summary_memories[dimension])

        retrieval_codelets[dimension] = retrieval_codelet
        summary_codelets[dimension] = summary_codelet


    memories_to_concat = [agent_info]

    for dimension in dimensions:
        memories_to_concat.append(summary_memories[dimension])

    concat_codelet = TextConcatCodelet(agent_summary_description.get_name(), "\n")
    concat_codelet.add_output(agent_summary_description)
    for memory in memories_to_concat:
        concat_codelet.add_input(memory)

    group_name = "SummaryDescriptionGenerator"
    mind.create_codelet_group(group_name)

    mind.insert_codelet(trigger_codelet, group_name)
    mind.insert_codelet(concat_codelet, group_name)
    
    for dimension in dimensions:
        mind.insert_codelet(retrieval_codelets[dimension], group_name)
        mind.insert_codelet(summary_codelets[dimension], group_name)