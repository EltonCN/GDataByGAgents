from collections import deque

import cst_python as cst

from .memory_input import memory_input_constructor
from .summary import summary_description_generator_constructor
from .retrieval import RetrievalCodelet
from .reflection import QuestionGeneratorCodelet, InsightGeneratorCodelet

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

    ######################################################################################

    # Create memory objects for questions and insights
    generated_questions = mind.create_memory_object("GeneratedQuestions", [])
    generated_insights = mind.create_memory_object("GeneratedInsights", [])
    statements = mind.create_memory_object("Statements", [])

    # Create and insert QuestionGeneratorCodelet
    question_generator_codelet = QuestionGeneratorCodelet(memory_stream.get_name(),
                                                          generated_questions.get_name())
    question_generator_codelet.add_input(memory_stream)
    question_generator_codelet.add_output(generated_questions)
    mind.insert_codelet(question_generator_codelet)

    # Create and insert InsightGeneratorCodelet
    insight_generator_codelet = InsightGeneratorCodelet(statements.get_name(),
                                                        generated_insights.get_name())
    insight_generator_codelet.add_input(statements)
    insight_generator_codelet.add_output(generated_insights)
    mind.insert_codelet(insight_generator_codelet)   