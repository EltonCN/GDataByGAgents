from __future__ import annotations

from collections import deque

import cst_python as cst

from gbyg.agent.memory_stream import MemoryStream
from gbyg.agent.retrieval import RetrievalCodelet
from . import QuestionGeneratorCodelet, InsightGeneratorCodelet


def reflection_constructor(mind:cst.Mind, 
        memories_input:cst.MemoryObject|None=None, 
        memory_stream:cst.MemoryObject|None=None,
        agent_time:cst.MemoryObject|None=None,
        importance_threshould:float|None=None,
        embedder_model:str|None=None,
        model_name:str|None=None) -> None:
    
    if memories_input is None:
        memories_input = mind.create_memory_object("MemoriesInput", deque())
    if memory_stream is None:
        memory_stream = mind.create_memory_object("MemoryStream", MemoryStream())
    if agent_time is None:
        agent_time = mind.create_memory_object("AgentTime", 0)

    # Create memory objects for questions and insights
    generated_questions = mind.create_memory_object("GeneratedQuestions", [])
    statements = mind.create_memory_object("Statements", [])

    # Create and insert QuestionGeneratorCodelet
    question_generator_codelet = QuestionGeneratorCodelet(memory_stream.get_name(),
                                                          agent_time.get_name(),
                                                          generated_questions.get_name(),
                                                          importance_threshould)
    question_generator_codelet.add_input(memory_stream)
    question_generator_codelet.add_input(agent_time)
    question_generator_codelet.add_output(generated_questions)

    retrieval_codelet = RetrievalCodelet(generated_questions.get_name(),
                                        memory_stream.get_name(),
                                        agent_time.get_name(),
                                        statements.get_name())
    retrieval_codelet.add_input(generated_questions)
    retrieval_codelet.add_input(memory_stream)
    retrieval_codelet.add_input(agent_time)
    retrieval_codelet.add_output(statements)

    # Create and insert InsightGeneratorCodelet
    insight_generator_codelet = InsightGeneratorCodelet(statements.get_name(),
                                                        memories_input.get_name(),
                                                        agent_time.get_name())
    insight_generator_codelet.add_input(statements)
    insight_generator_codelet.add_input(agent_time)
    insight_generator_codelet.add_output(memories_input)
    

    mind.create_codelet_group("Reflection")
    mind.insert_codelet(insight_generator_codelet, "Reflection")
    mind.insert_codelet(retrieval_codelet, "Reflection")
    mind.insert_codelet(question_generator_codelet, "Reflection")