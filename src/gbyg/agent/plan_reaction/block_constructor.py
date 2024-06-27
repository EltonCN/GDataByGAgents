from __future__ import annotations

import cst_python as cst

from gbyg.agent.memory_stream import MemoryStream
from .plan_generator_codelet import PlanGeneratorCodelet

def plan_reaction_generator_constructor(mind:cst.Mind, 
                            memory_stream:cst.MemoryObject|None=None,
                            agent_info:cst.MemoryObject|None=None,
                            agent_time:cst.MemoryObject|None=None,
                            agent_summary_description:cst.MemoryObject|None=None,
                            previous_day_summary:cst.MemoryObject|None=None,
                            model_name:str|None=None,) -> None:
    
    if memory_stream is None:
        memory_stream = mind.create_memory_object("MemoryStream", MemoryStream())
    if agent_info is None:
        agent_info = mind.create_memory_object("AgentInfo", {"name":"", "age":0, "traits":""})
    if agent_summary_description is None:
        agent_summary_description = mind.create_memory_object("AgentSummaryDescription", "")
    if agent_time is None:
        agent_time = mind.create_memory_object("AgentTime", 0)
    if previous_day_summary is None:
        previous_day_summary = mind.create_memory_object("PreviousDaySummary", "")

    plan_memory = mind.create_memory_object("Plan", "")

    plan_generator_codelet = PlanGeneratorCodelet(agent_info.get_name(),
                                                  agent_time.get_name(),
                                                  agent_summary_description.get_name(),
                                                  previous_day_summary.get_name(),
                                                  plan_memory.get_name(),
                                                  model_name)
    plan_generator_codelet.add_input(agent_info)
    plan_generator_codelet.add_input(agent_time)
    plan_generator_codelet.add_input(agent_summary_description)
    plan_generator_codelet.add_input(previous_day_summary)

    plan_generator_codelet.add_output(plan_memory)

    group_name = "PlanReact"
    mind.create_codelet_group(group_name)

    mind.insert_codelet(plan_generator_codelet, group_name)