from __future__ import annotations

from collections import deque

import cst_python as cst

from .embedder_codelet import EmbedderCodelet
from .importance_scorer_codelet import MemoryImportanceScorerCodelet

def memory_input_constructor(mind:cst.Mind, 
                            memories_input:cst.MemoryObject|None=None, 
                            memory_stream:cst.MemoryObject|None=None,
                            embedder_model:str|None=None,
                            model_name:str|None=None) -> None:
    
    if memories_input is None:
        memories_input = mind.create_memory_object("MemoriesInput", deque())
    if memory_stream is None:
        memory_stream = mind.create_memory_object("MemoryStream", [])

    memories_to_score = mind.create_memory_object("MemoriesToScore", deque())

    embedder_codelet = EmbedderCodelet(embedder_model, memories_input.get_name(), memories_to_score.get_name())
    embedder_codelet.add_input(memories_input)
    embedder_codelet.add_output(memories_to_score)

    importance_codelet = MemoryImportanceScorerCodelet(model_name, memories_to_score.get_name(), memory_stream.get_name())
    importance_codelet.add_input(memories_to_score)
    importance_codelet.add_output(memory_stream)

    mind.create_codelet_group("MemoryInput")
    mind.insert_codelet(embedder_codelet, "MemoryInput")
    mind.insert_codelet(importance_codelet, "MemoryInput")