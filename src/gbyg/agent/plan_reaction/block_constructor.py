from __future__ import annotations

import cst_python as cst

from gbyg.agent.memory_stream import MemoryStream
from .plan_generator_codelet import PlanGeneratorCodelet
from .action_codelet import ActionCodelet

def plan_reaction_generator_constructor(mind:cst.Mind, 
                            memory_stream:cst.MemoryObject|None=None,
                            agent_info:cst.MemoryObject|None=None,
                            agent_time:cst.MemoryObject|None=None,
                            agent_summary_description:cst.MemoryObject|None=None,
                            previous_day_summary:cst.MemoryObject|None=None,
                            know_world:cst.MemoryObject|None=None,
                            actual_place:cst.MemoryObject|None=None,
                            model_name:str|None=None) -> None:
    
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
    if know_world is None:
        know_world = mind.create_memory_object("KnowWorld", {})
    if actual_place is None:
        actual_place = mind.create_memory_object("ActualPlace", "")

    
    plan_memory = mind.create_memory_object("Plan", "")

    #TODO Create outside
    current_observation = mind.create_memory_object("CurrentObservation", "")
    current_state = mind.create_memory_object("CurrentState", "")
    action_memory = mind.create_memory_object("Action", "")

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


    action_codelet = ActionCodelet(agent_info.get_name(),
                                   agent_time.get_name(),
                                   current_observation.get_name(),
                                   current_state.get_name(),
                                   plan_memory.get_name(),
                                   know_world.get_name(),
                                   actual_place.get_name(),
                                   action_memory.get_name(),
                                   model_name)
    action_codelet.add_input(agent_info)
    action_codelet.add_input(agent_time)
    action_codelet.add_input(current_observation)
    action_codelet.add_input(current_state)
    action_codelet.add_input(plan_memory)
    action_codelet.add_input(know_world)
    action_codelet.add_input(actual_place)
    action_codelet.add_output(action_memory)

    group_name = "PlanReact"
    mind.create_codelet_group(group_name)

    mind.insert_codelet(plan_generator_codelet, group_name)
    mind.insert_codelet(action_codelet, group_name)