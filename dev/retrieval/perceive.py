import sys
from typing import List, Dict, Union
from numpy import dot, ndarray
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

sys.path.append('../../')

def get_embedding(text: str, model_name: str = 'all-MiniLM-L6-v2') -> ndarray:
    """
    This function initializes a SentenceTransformer model and takes a string of 
    text as input to return a 1-D array object that represents the embedding of 
    the input text. The embedding is generated using the SentenceTransformer model.

    INPUT: 
        text: A string of text for which the embedding needs to be generated.
        model_name: A string representing the name of the model to be initialized.
                    Default is 'all-MiniLM-L6-v2'.
    OUTPUT: 
        A 1-D array object representing the embedding of the input text.
    
    Example input: 
        text = "How are you?"
    """
    model = SentenceTransformer(model_name)
    return model.encode(text)

def retrieve(persona, perceived: List) -> Dict[str, Dict[str, Union[List, object]]]:
    """
    This function takes the events that are perceived by the persona as input
    and returns a set of related events and thoughts that the persona would 
    need to consider as context when planning. 

    INPUT: 
        perceived: a list of event <ConceptNode>s that represent any of the events
                   that are happening around the persona. What is included in here
                   are controlled by the att_bandwidth and retention 
                   hyper-parameters.
    OUTPUT: 
        retrieved: a dictionary of dictionary. The first layer specifies an event, 
                   while the latter layer specifies the "curr_event", "events", 
                   and "thoughts" that are relevant.
    """
    retrieved: Dict[str, Dict[str, Union[List, object]]] = dict()
    for event in perceived:
        retrieved[event.description] = dict()
        retrieved[event.description]["curr_event"] = event
        
        relevant_events = persona.a_mem.retrieve_relevant_events(event.subject, event.predicate, event.object)
        retrieved[event.description]["events"] = list(relevant_events)

        relevant_thoughts = persona.a_mem.retrieve_relevant_thoughts(event.subject, event.predicate, event.object)
        retrieved[event.description]["thoughts"] = list(relevant_thoughts)
    
    return retrieved

def cos_sim(a: ndarray, b: ndarray) -> float:
    """
    This function calculates the cosine similarity between two input vectors 
    'a' and 'b'. Cosine similarity is a measure of similarity between two 
    non-zero vectors of an inner product space that measures the cosine 
    of the angle between them.

    INPUT: 
        a: 1-D array object 
        b: 1-D array object 
    OUTPUT: 
        A scalar value representing the cosine similarity between the input 
        vectors 'a' and 'b'.
    
    Example input: 
        a = [0.3, 0.2, 0.5]
        b = [0.2, 0.2, 0.5]
    """
    return dot(a, b) / (norm(a) * norm(b))

def normalize_dict_floats(d: Dict[str, float], target_min: float, target_max: float) -> Dict[str, float]:
    """
    This function normalizes the float values of a given dictionary 'd' between 
    a target minimum and maximum value. The normalization is done by scaling the
    values to the target range while maintaining the same relative proportions 
    between the original values.

    INPUT: 
        d: Dictionary. The input dictionary whose float values need to be 
           normalized.
        target_min: Integer or float. The minimum value to which the original 
                    values should be scaled.
        target_max: Integer or float. The maximum value to which the original 
                    values should be scaled.
    OUTPUT: 
        d: A new dictionary with the same keys as the input but with the float
           values normalized between the target_min and target_max.

    Example input: 
        d = {'a': 1.2, 'b': 3.4, 'c': 5.6, 'd': 7.8}
        target_min = -5
        target_max = 5
    """
    min_val = min(d.values())
    max_val = max(d.values())
    range_val = max_val - min_val

    normalized_d = {}
    if range_val == 0:
        for key in d:
            normalized_d[key] = (target_max - target_min) / 2
    else:
        for key, val in d.items():
            normalized_d[key] = ((val - min_val) * (target_max - target_min) / range_val + target_min)
    
    return normalized_d

def top_highest_x_values(d: Dict[str, float], x: int) -> Dict[str, float]:
    """
    This function takes a dictionary 'd' and an integer 'x' as input, and 
    returns a new dictionary containing the top 'x' key-value pairs from the 
    input dictionary 'd' with the highest values.

    INPUT: 
        d: Dictionary. The input dictionary from which the top 'x' key-value pairs 
           with the highest values are to be extracted.
        x: Integer. The number of top key-value pairs with the highest values to
           be extracted from the input dictionary.
    OUTPUT: 
        A new dictionary containing the top 'x' key-value pairs from the input 
        dictionary 'd' with the highest values.
    
    Example input: 
        d = {'a': 1.2, 'b': 3.4, 'c': 5.6, 'd': 7.8}
        x = 3
    """
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True)[:x])

def extract_recency(persona, nodes: List) -> Dict[str, float]:
    """
    Gets the current Persona object and a list of nodes that are in a 
    chronological order, and outputs a dictionary that has the recency score
    calculated.

    INPUT: 
        persona: Current persona whose memory we are retrieving. 
        nodes: A list of Node object in a chronological order. 
    OUTPUT: 
        recency_out: A dictionary whose keys are the node.node_id and whose values
                     are the float that represents the recency score. 
    """
    recency_vals = [persona.scratch.recency_decay ** i for i in range(len(nodes), 0, -1)]

    recency_out: Dict[str, float] = {}
    for count, node in enumerate(nodes):
        recency_out[node.node_id] = recency_vals[count]

    return recency_out

def extract_importance(persona, nodes: List) -> Dict[str, float]:
    """
    Gets the current Persona object and a list of nodes that are in a 
    chronological order, and outputs a dictionary that has the importance score
    calculated (importance is the importance of the memory node).

    INPUT: 
        persona: Current persona whose memory we are retrieving. 
        nodes: A list of Node object in a chronological order. 
    OUTPUT: 
        importance_out: A dictionary whose keys are the node.node_id and whose 
                        values are the float that represents the importance score.
    """
    importance_out: Dict[str, float] = {}
    for count, node in enumerate(nodes):
        importance_out[node.node_id] = node.importance

    return importance_out

def extract_relevance(persona, nodes: List, focal_pt: str) -> Dict[str, float]:
    """
    Gets the current Persona object, a list of nodes that are in a 
    chronological order, and the focal_pt string and outputs a dictionary 
    that has the relevance score calculated.

    INPUT: 
        persona: Current persona whose memory we are retrieving. 
        nodes: A list of Node object in a chronological order. 
        focal_pt: A string describing the current thought of revent of focus.  
    OUTPUT: 
        relevance_out: A dictionary whose keys are the node.node_id and whose values
                       are the float that represents the relevance score. 
    """
    focal_embedding = get_embedding(focal_pt)

    relevance_out: Dict[str, float] = {}
    for node in nodes:
        node_embedding = persona.a_mem.embeddings[node.embedding_key]
        relevance_out[node.node_id] = cos_sim(node_embedding, focal_embedding)

    return relevance_out

def new_retrieve(persona, focal_points, n_count=30, debug=False):
  """
  Given the current persona and focal points (focal points are events or 
  thoughts for which we are retrieving), we retrieve a set of nodes for each
  of the focal points and return a dictionary. 

  INPUT: 
    persona: The current persona object whose memory we are retrieving. 
    focal_points: A list of focal points (string description of the events or
                  thoughts that is the focus of current retrieval).
  OUTPUT: 
    retrieved: A dictionary whose keys are a string focal point, and whose 
               values are a list of Node object in the agent's associative 
               memory.

  Example input:
    persona = <persona> object 
    focal_points = ["How are you?", "Jane is swimming in the pond"]
  """
  # <retrieved> is the main dictionary that we are returning
  retrieved: Dict[str, List] = {} 
  for focal_pt in focal_points: 
    # Getting all nodes from the agent's memory (both thoughts and events) and
    # sorting them by the datetime of creation.
    # You could also imagine getting the raw conversation, but for now. 
    nodes = [[i.last_accessed, i] for i in persona.a_mem.seq_event + persona.a_mem.seq_thought if "idle" not in i.embedding_key]
    nodes = sorted(nodes, key=lambda x: x[0])
    nodes = [i for created, i in nodes]

    # Calculating the recency scores for each node.
    recency_out = extract_recency(persona, nodes)
    recency_out = normalize_dict_floats(recency_out, 0, 1)

    # Calculating the importance scores for each node.   
    importance_out = extract_importance(persona, nodes)
    importance_out = normalize_dict_floats(importance_out, 0, 1)  
    
    # Calculating the relevance scores for each node.
    relevance_out = extract_relevance(persona, nodes, focal_pt)
    relevance_out = normalize_dict_floats(relevance_out, 0, 1)

    # Computing the final scores that combines the component values. 
    # Note to self: test out different weights. [1, 1, 1] tends to work
    # decently, but in the future, these weights should likely be learned, 
    # perhaps through an RL-like process.
    # gw = [1, 1, 1]
    # gw = [1, 2, 1]
    gw = [1, 1, 1]
    master_out: Dict[str, float] = {}
    for key in recency_out.keys():
            master_out[key] = (
                persona.scratch.recency_w * recency_out[key] * gw[0]
                + persona.scratch.relevance_w * relevance_out[key] * gw[1]
                + persona.scratch.importance_w * importance_out[key] * gw[2]
            )

    # Extracting the highest x values.
    # <master_out> has the key of node.id and value of float. Once we get the 
    # highest x values, we want to translate the node.id into nodes and return
    # the list of nodes.
    master_out = top_highest_x_values(master_out, len(master_out.keys()))
    master_out = top_highest_x_values(master_out, n_count)
    master_nodes = [persona.a_mem.id_to_node[key] for key in list(master_out.keys())]

    # Debugging information
    if debug:
        print(f"Debug information for focal point: {focal_pt}")
        print("\nNode Creation Datetime and Recency Scores:")
        for node in nodes:
            print(f"Node ID: {node.node_id}, Last Accessed: {node.last_accessed}, Recency Score: {recency_out[node.node_id]:.4f}")

        print("\nImportance Scores:")
        for node in nodes:
            print(f"Node ID: {node.node_id}, Importance Score: {importance_out[node.node_id]:.4f}")

        print("\nRelevance Scores:")
        for node in nodes:
            print(f"Node ID: {node.node_id}, Relevance Score: {relevance_out[node.node_id]:.4f}")

        print("\nNode Scores Breakdown:")
        for key, val in master_out.items():
            node = persona.a_mem.id_to_node[key]
            recency_score = persona.scratch.recency_w * recency_out[key] * gw[0]
            relevance_score = persona.scratch.relevance_w * relevance_out[key] * gw[1]
            importance_score = persona.scratch.importance_w * importance_out[key] * gw[2]
            print(f"\nNode ID: {node.node_id}, Description: {node.description}")
            print(f"Combined Score: {val:.4f}")
            print(f"Recency Score: {recency_score:.4f}")
            print(f"Importance Score: {importance_score:.4f}")
            print(f"Relevance Score: {relevance_score:.4f}")
        
    for n in master_nodes:
        n.last_accessed = persona.scratch.curr_time
    
    retrieved[focal_pt] = master_nodes

  return retrieved