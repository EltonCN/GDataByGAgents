import sys
sys.path.append('../../')

import json
import datetime

class ConceptNode: 
    def __init__(self, node_id, node_count, type_count, node_type, depth,
                 created, expiration, s, p, o, description, embedding_key, 
                 poignancy, keywords, filling): 
        self.node_id = node_id  # Unique identifier for the node
        self.node_count = node_count  # Node count in the entire memory
        self.type_count = type_count  # Node count in its type (event or thought)
        self.type = node_type  # Type of the node, either 'thought' or 'event'
        self.depth = depth  # Depth of the node in the thought hierarchy

        self.created = created  # Creation time of the node
        self.expiration = expiration  # Expiration time of the node, if any
        self.last_accessed = self.created  # Last accessed time, initially set to creation time

        self.subject = s  # Subject of the node
        self.predicate = p  # Predicate of the node
        self.object = o  # Object of the node

        self.description = description  # Description of the node
        self.embedding_key = embedding_key  # Key for the node's embedding in the embeddings dictionary
        self.poignancy = poignancy  # Poignancy (importance) score of the node
        self.keywords = keywords  # Keywords associated with the node
        self.filling = filling  # Filling (additional context or references) for the node

    def spo_summary(self): 
        return (self.subject, self.predicate, self.object)  # Returns a summary of the node's subject, predicate, and object

# AssociativeMemory class for managing a collection of ConceptNodes
class AssociativeMemory: 
  def __init__(self, f_saved):
    # Dictionary to map node IDs to ConceptNode instances
    self.id_to_node = dict()
    
    # Lists to keep track of event and thought nodes in order
    self.seq_event = []
    self.seq_thought = []

    # Dictionaries to map keywords to lists of event or thought nodes
    self.kw_to_event = dict()
    self.kw_to_thought = dict()

    # Dictionaries to track keyword strength (frequency) in event or thought nodes
    self.kw_strength_event = dict()
    self.kw_strength_thought = dict()

    # Load precomputed embeddings from a JSON file
    self.embeddings = json.load(open(f_saved + "/embeddings.json"))

    # Initialize the sentence-transformers model for generating embeddings
    # self.model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load nodes from a saved file
    nodes_load = json.load(open(f_saved + "/nodes.json"))
    for count in range(len(nodes_load.keys())): 
      node_id = f"node_{str(count+1)}"
      node_details = nodes_load[node_id]

      # Extract node details
      node_count = node_details["node_count"]
      type_count = node_details["type_count"]
      node_type = node_details["type"]
      depth = node_details["depth"]

      created = datetime.datetime.strptime(node_details["created"], 
                                           '%Y-%m-%d %H:%M:%S')
      expiration = None
      if node_details["expiration"]: 
        expiration = datetime.datetime.strptime(node_details["expiration"],
                                                '%Y-%m-%d %H:%M:%S')

      s = node_details["subject"]
      p = node_details["predicate"]
      o = node_details["object"]

      description = node_details["description"]
      embedding_pair = (node_details["embedding_key"], 
                        self.embeddings[node_details["embedding_key"]])
      poignancy =node_details["poignancy"]
      keywords = set(node_details["keywords"])
      filling = node_details["filling"]
      
      # Add the node to the appropriate sequence (event or thought)
      if node_type == "event": 
        self.add_event(created, expiration, s, p, o, 
                   description, keywords, poignancy, embedding_pair, filling)
      elif node_type == "thought": 
        self.add_thought(created, expiration, s, p, o, 
                   description, keywords, poignancy, embedding_pair, filling)

    # Load keyword strength data from a saved file
    kw_strength_load = json.load(open(f_saved + "/kw_strength.json"))
    if kw_strength_load["kw_strength_event"]: 
      self.kw_strength_event = kw_strength_load["kw_strength_event"]
    if kw_strength_load["kw_strength_thought"]: 
      self.kw_strength_thought = kw_strength_load["kw_strength_thought"]

  def save(self, out_json):
    # Save nodes to a JSON file 
    r = dict()
    for count in range(len(self.id_to_node.keys()), 0, -1): 
      node_id = f"node_{str(count)}"
      node = self.id_to_node[node_id]

      r[node_id] = dict()
      r[node_id]["node_count"] = node.node_count
      r[node_id]["type_count"] = node.type_count
      r[node_id]["type"] = node.type
      r[node_id]["depth"] = node.depth

      r[node_id]["created"] = node.created.strftime('%Y-%m-%d %H:%M:%S')
      r[node_id]["expiration"] = None
      if node.expiration: 
        r[node_id]["expiration"] = (node.expiration
                                        .strftime('%Y-%m-%d %H:%M:%S'))

      r[node_id]["subject"] = node.subject
      r[node_id]["predicate"] = node.predicate
      r[node_id]["object"] = node.object

      r[node_id]["description"] = node.description
      r[node_id]["embedding_key"] = node.embedding_key
      r[node_id]["poignancy"] = node.poignancy
      r[node_id]["keywords"] = list(node.keywords)
      r[node_id]["filling"] = node.filling

    with open(out_json+"/nodes.json", "w") as outfile:
      json.dump(r, outfile)

    # Save keyword strength data to a JSON file
    r = dict()
    r["kw_strength_event"] = self.kw_strength_event
    r["kw_strength_thought"] = self.kw_strength_thought
    with open(out_json+"/kw_strength.json", "w") as outfile:
      json.dump(r, outfile)

    # Save embeddings to a JSON file
    with open(out_json+"/embeddings.json", "w") as outfile:
      json.dump(self.embeddings, outfile)

  def add_event(self, created, expiration, s, p, o, 
                      description, keywords, poignancy, 
                      embedding_pair, filling):
    
    # Check if the created and expiration times are in the right format
    if type(created) == str:
      created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
    if expiration and type(expiration) == str:
      expiration = datetime.datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')
    
    # Setting up the node ID and counts.
    node_count = len(self.id_to_node.keys()) + 1
    type_count = len(self.seq_event) + 1
    node_type = "event"
    node_id = f"node_{str(node_count)}"
    depth = 0

    # Node type specific clean up. 
    if "(" in description: 
      description = (" ".join(description.split()[:3]) 
                     + " " 
                     +  description.split("(")[-1][:-1])

    # Creating the <ConceptNode> object.
    node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                       created, expiration, 
                       s, p, o, 
                       description, embedding_pair[0],
                       poignancy, keywords, filling)

    # Creating various dictionary cache for fast access. 
    self.seq_event[0:0] = [node]
    keywords = [i.lower() for i in keywords]
    for kw in keywords: 
      if kw in self.kw_to_event: 
        self.kw_to_event[kw][0:0] = [node]
      else: 
        self.kw_to_event[kw] = [node]
    self.id_to_node[node_id] = node 

    # Adding in the kw_strength
    if f"{p} {o}" != "is idle":  
      for kw in keywords: 
        if kw in self.kw_strength_event: 
          self.kw_strength_event[kw] += 1
        else: 
          self.kw_strength_event[kw] = 1

    self.embeddings[embedding_pair[0]] = embedding_pair[1]

    return node

  def add_thought(self, created, expiration, s, p, o, 
                        description, keywords, poignancy, 
                        embedding_pair, filling):
    
    # Check if the created and expiration times are in the right format
    if type(created) == str:
      created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
    if expiration and type(expiration) == str:
      expiration = datetime.datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')

    # Setting up the node ID and counts.
    node_count = len(self.id_to_node.keys()) + 1
    type_count = len(self.seq_thought) + 1
    node_type = "thought"
    node_id = f"node_{str(node_count)}"
    depth = 1 
    try: 
      if filling: 
        depth += max([self.id_to_node[i].depth for i in filling])
    except: 
      pass

    # Creating the <ConceptNode> object.
    node = ConceptNode(node_id, node_count, type_count, node_type, depth,
                       created, expiration, 
                       s, p, o, 
                       description, embedding_pair[0], poignancy, keywords, filling)

    # Creating various dictionary cache for fast access. 
    self.seq_thought[0:0] = [node]
    keywords = [i.lower() for i in keywords]
    for kw in keywords: 
      if kw in self.kw_to_thought: 
        self.kw_to_thought[kw][0:0] = [node]
      else: 
        self.kw_to_thought[kw] = [node]
    self.id_to_node[node_id] = node 

    # Adding in the kw_strength
    if f"{p} {o}" != "is idle":  
      for kw in keywords: 
        if kw in self.kw_strength_thought: 
          self.kw_strength_thought[kw] += 1
        else: 
          self.kw_strength_thought[kw] = 1

    self.embeddings[embedding_pair[0]] = embedding_pair[1]

    return node

  def get_summarized_latest_events(self, retention): 
    ret_set = set()
    for e_node in self.seq_event[:retention]: 
      ret_set.add(e_node.spo_summary())
    return ret_set


  def get_str_seq_events(self): 
    ret_str = ""
    for count, event in enumerate(self.seq_event): 
      ret_str += f'{"Event", len(self.seq_event) - count, ": ", event.spo_summary(), " -- ", event.description}\n'
    return ret_str


  def get_str_seq_thoughts(self): 
    ret_str = ""
    for count, event in enumerate(self.seq_thought): 
      ret_str += f'{"Thought", len(self.seq_thought) - count, ": ", event.spo_summary(), " -- ", event.description}\n'
    return ret_str

  def retrieve_relevant_thoughts(self, s_content, p_content, o_content): 
    contents = [s_content, p_content, o_content]

    ret = []
    for i in contents: 
      if i in self.kw_to_thought: 
        ret += self.kw_to_thought[i.lower()]

    ret = set(ret)
    return ret

  def retrieve_relevant_events(self, s_content, p_content, o_content): 
    contents = [s_content, p_content, o_content]

    ret = []
    for i in contents: 
      if i in self.kw_to_event: 
        ret += self.kw_to_event[i]

    ret = set(ret)
    return ret