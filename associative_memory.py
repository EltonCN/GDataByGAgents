import sys
import json
import datetime
from typing import Dict, List, Tuple, Set, Optional, Any

sys.path.append('../../')

class ConceptNode:
    """
    Represents a conceptual entity in a knowledge graph or memory system.
    
    Attributes:
        node_id (str): Unique identifier for the node.
        node_count (int): Total number of nodes in the memory.
        type_count (int): Count of nodes of the same type (either 'event' or 'thought').
        node_type (str): Type of the node, either 'thought' or 'event'.
        depth (int): Depth of the node in the thought hierarchy.
        created (datetime.datetime): Timestamp of when the node was created.
        expiration (Optional[datetime.datetime]): Timestamp of when the node expires, if applicable.
        last_accessed (datetime.datetime): Last accessed time, initially set to creation time.
        subject (str): Subject of the node.
        predicate (str): Predicate of the node.
        object (str): Object of the node.
        description (str): Description of the node.
        embedding_key (str): Key for the node's embedding in the embeddings dictionary.
        importance (float): importance (importance) score of the node.
        keywords (Set[str]): Keywords associated with the node.
        filling (List[str]): Additional context or references for the node.
    """

    def __init__(self, node_id: str, node_count: int, type_count: int, node_type: str, depth: int,
                 created: datetime.datetime, expiration: Optional[datetime.datetime], s: str, p: str, o: str, 
                 description: str, embedding_key: str, importance: float, keywords: Set[str], filling: List[str]):
        """
        Initializes a ConceptNode instance with the specified attributes.
        
        Args:
            node_id (str): Unique identifier for the node.
            node_count (int): Total number of nodes in the memory.
            type_count (int): Count of nodes of the same type.
            node_type (str): Type of the node.
            depth (int): Depth of the node in the hierarchy.
            created (datetime.datetime): Creation time of the node.
            expiration (Optional[datetime.datetime]): Expiration time of the node.
            s (str): Subject of the node.
            p (str): Predicate of the node.
            o (str): Object of the node.
            description (str): Description of the node.
            embedding_key (str): Key for the node's embedding.
            importance (float): importance score of the node.
            keywords (Set[str]): Keywords associated with the node.
            filling (List[str]): Additional context or references.
        """
        self.node_id: str = node_id
        self.node_count: int = node_count
        self.type_count: int = type_count
        self.type: str = node_type
        self.depth: int = depth
        self.created: datetime.datetime = created
        self.expiration: Optional[datetime.datetime] = expiration
        self.last_accessed: datetime.datetime = self.created
        self.subject: str = s
        self.predicate: str = p
        self.object: str = o
        self.description: str = description
        self.embedding_key: str = embedding_key
        self.importance: float = importance
        self.keywords: Set[str] = keywords
        self.filling: List[str] = filling

    def spo_summary(self) -> Tuple[str, str, str]:
        """
        Returns a summary of the node's subject, predicate, and object.
        
        Returns:
            Tuple[str, str, str]: A tuple containing (subject, predicate, object).
        """
        return (self.subject, self.predicate, self.object)


class AssociativeMemory:
    """
    Manages a collection of ConceptNode instances, allowing for addition, retrieval, 
    and saving of nodes, along with their associated metadata and relationships.
    
    Attributes:
        id_to_node (Dict[str, ConceptNode]): Maps node IDs to ConceptNode instances.
        seq_event (List[ConceptNode]): List of event nodes in order.
        seq_thought (List[ConceptNode]): List of thought nodes in order.
        kw_to_event (Dict[str, List[ConceptNode]]): Maps keywords to lists of event nodes.
        kw_to_thought (Dict[str, List[ConceptNode]]): Maps keywords to lists of thought nodes.
        kw_strength_event (Dict[str, int]): Tracks keyword strength (frequency) in event nodes.
        kw_strength_thought (Dict[str, int]): Tracks keyword strength (frequency) in thought nodes.
        embeddings (Dict[str, Any]): Precomputed embeddings loaded from a JSON file.
    """
    
    def __init__(self, f_saved: str):
        """
        Initializes an AssociativeMemory instance by loading data from JSON files.
        
        Args:
            f_saved (str): Path to the directory containing saved JSON files.
        """
        self.id_to_node: Dict[str, ConceptNode] = dict()
        self.seq_event: List[ConceptNode] = []
        self.seq_thought: List[ConceptNode] = []
        self.kw_to_event: Dict[str, List[ConceptNode]] = dict()
        self.kw_to_thought: Dict[str, List[ConceptNode]] = dict()
        self.kw_strength_event: Dict[str, int] = dict()
        self.kw_strength_thought: Dict[str, int] = dict()

        # Load embeddings from a JSON file
        self.embeddings: Dict[str, Any] = json.load(open(f_saved + "/embeddings.json"))

        # Load nodes from a JSON file
        nodes_load: Dict[str, Dict[str, Any]] = json.load(open(f_saved + "/nodes.json"))

        # Load keyword strengths from a JSON file
        kw_strength_load: Dict[str, Dict[str, int]] = json.load(open(f_saved + "/kw_strength.json"))

        for count in range(len(nodes_load.keys())):
            node_id: str = f"node_{str(count + 1)}"
            node_details: Dict[str, Any] = nodes_load[node_id]

            node_count: int = node_details["node_count"]
            type_count: int = node_details["type_count"]
            node_type: str = node_details["type"]
            depth: int = node_details["depth"]

            created: datetime.datetime = datetime.datetime.strptime(node_details["created"], '%Y-%m-%d %H:%M:%S')
            expiration: Optional[datetime.datetime] = None
            if node_details["expiration"]:
                expiration = datetime.datetime.strptime(node_details["expiration"], '%Y-%m-%d %H:%M:%S')

            s: str = node_details["subject"]
            p: str = node_details["predicate"]
            o: str = node_details["object"]

            description: str = node_details["description"]
            embedding_pair: Tuple[str, Any] = (node_details["embedding_key"], self.embeddings[node_details["embedding_key"]])
            importance: float = node_details["importance"]
            keywords: Set[str] = set(node_details["keywords"])
            filling: List[str] = node_details["filling"]

            # Add nodes based on their type
            if node_type == "event":
                self.add_event(created, expiration, s, p, o, description, keywords, importance, embedding_pair, filling)
            elif node_type == "thought":
                self.add_thought(created, expiration, s, p, o, description, keywords, importance, embedding_pair, filling)

        if kw_strength_load["kw_strength_event"]:
            self.kw_strength_event = kw_strength_load["kw_strength_event"]
        if kw_strength_load["kw_strength_thought"]:
            self.kw_strength_thought = kw_strength_load["kw_strength_thought"]

    def save(self, out_json: str) -> None:
        """
        Saves the current state of nodes, keyword strengths, and embeddings to JSON files.
        
        Args:
            out_json (str): Path to the directory where the JSON files will be saved.
        """
        # Prepare nodes data for saving
        r: Dict[str, Dict[str, Any]] = dict()
        for count in range(len(self.id_to_node.keys()), 0, -1):
            node_id: str = f"node_{str(count)}"
            node: ConceptNode = self.id_to_node[node_id]

            r[node_id] = dict()
            r[node_id]["node_count"] = node.node_count
            r[node_id]["type_count"] = node.type_count
            r[node_id]["type"] = node.type
            r[node_id]["depth"] = node.depth

            r[node_id]["created"] = node.created.strftime('%Y-%m-%d %H:%M:%S')
            r[node_id]["expiration"] = None
            if node.expiration:
                r[node_id]["expiration"] = node.expiration.strftime('%Y-%m-%d %H:%M:%S')

            r[node_id]["subject"] = node.subject
            r[node_id]["predicate"] = node.predicate
            r[node_id]["object"] = node.object

            r[node_id]["description"] = node.description
            r[node_id]["embedding_key"] = node.embedding_key
            r[node_id]["importance"] = node.importance
            r[node_id]["keywords"] = list(node.keywords)
            r[node_id]["filling"] = node.filling

        # Save nodes data to JSON file
        with open(out_json + "/nodes.json", "w") as outfile:
            json.dump(r, outfile)

        # Save keyword strengths to JSON file
        kw_strengths: Dict[str, Dict[str, int]] = dict()
        kw_strengths["kw_strength_event"] = self.kw_strength_event
        kw_strengths["kw_strength_thought"] = self.kw_strength_thought

        with open(out_json + "/kw_strength.json", "w") as outfile:
            json.dump(kw_strengths, outfile)

        # Save embeddings to JSON file
        with open(out_json + "/embeddings.json", "w") as outfile:
            json.dump(self.embeddings, outfile)

    def add_event(self, created: datetime.datetime, expiration: Optional[datetime.datetime], s: str, p: str, o: str, 
                  description: str, keywords: Set[str], importance: float, embedding_pair: Tuple[str, Any], filling: List[str]) -> ConceptNode:
        """
        Adds an event node to the memory.
        
        Args:
            created (datetime.datetime): Creation time of the event.
            expiration (Optional[datetime.datetime]): Expiration time of the event, if applicable.
            s (str): Subject of the event.
            p (str): Predicate of the event.
            o (str): Object of the event.
            description (str): Description of the event.
            keywords (Set[str]): Keywords associated with the event.
            importance (float): importance score of the event.
            embedding_pair (Tuple[str, Any]): A tuple containing the embedding key and the embedding itself.
            filling (List[str]): Additional context or references.
        
        Returns:
            ConceptNode: The created event node.
        """
        # Convert string datetime to datetime object if necessary
        if isinstance(created, str):
            created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
        if expiration and isinstance(expiration, str):
            expiration = datetime.datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')

        # Generate node metadata
        node_count: int = len(self.id_to_node.keys()) + 1
        type_count: int = len(self.seq_event) + 1
        node_type: str = "event"
        node_id: str = f"node_{str(node_count)}"
        depth: int = 0

        # Adjust description if it contains special characters
        if "(" in description:
            description = (" ".join(description.split()[:3]) + " " + description.split("(")[-1][:-1])

        # Create a new event node
        node: ConceptNode = ConceptNode(
                                node_id,
                                node_count,
                                type_count,
                                node_type,
                                depth,
                                created,
                                expiration,
                                s,
                                p,
                                o,
                                description,
                                embedding_pair[0],
                                importance,
                                keywords,
                                filling
                            )

        # Insert the node at the beginning of the event sequence
        self.seq_event[0:0] = [node]
        keywords = {kw.lower() for kw in keywords}
        
        # Map keywords to events
        for kw in keywords:
            if kw in self.kw_to_event:
                self.kw_to_event[kw][0:0] = [node]
            else:
                self.kw_to_event[kw] = [node]
        
        self.id_to_node[node_id] = node

        # Update keyword strength if the event is significant
        if f"{p} {o}" != "is idle":
            for kw in keywords:
                if kw in self.kw_strength_event:
                    self.kw_strength_event[kw] += 1
                else:
                    self.kw_strength_event[kw] = 1

        # Store the embedding
        self.embeddings[embedding_pair[0]] = embedding_pair[1]

        return node

    def add_thought(self, created: datetime.datetime, expiration: Optional[datetime.datetime], s: str, p: str, o: str, 
                    description: str, keywords: Set[str], importance: float, embedding_pair: Tuple[str, Any], filling: List[str]) -> ConceptNode:
        """
        Adds a thought node to the memory.
        
        Args:
            created (datetime.datetime): Creation time of the thought.
            expiration (Optional[datetime.datetime]): Expiration time of the thought, if applicable.
            s (str): Subject of the thought.
            p (str): Predicate of the thought.
            o (str): Object of the thought.
            description (str): Description of the thought.
            keywords (Set[str]): Keywords associated with the thought.
            importance (float): importance score of the thought.
            embedding_pair (Tuple[str, Any]): A tuple containing the embedding key and the embedding itself.
            filling (List[str]): Additional context or references.
        
        Returns:
            ConceptNode: The created thought node.
        """
        # Convert string datetime to datetime object if necessary
        if isinstance(created, str):
            created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
        if expiration and isinstance(expiration, str):
            expiration = datetime.datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')

        # Generate node metadata
        node_count: int = len(self.id_to_node.keys()) + 1
        type_count: int = len(self.seq_thought) + 1
        node_type: str = "thought"
        node_id: str = f"node_{str(node_count)}"
        depth: int = 1
        
        # Adjust depth based on filling nodes
        if filling:
            depth += max([self.id_to_node[i].depth for i in filling])

        # Create a new thought node
        node: ConceptNode = ConceptNode(
                                node_id,
                                node_count,
                                type_count,
                                node_type,
                                depth,
                                created,
                                expiration,
                                s,
                                p,
                                o,
                                description,
                                embedding_pair[0],
                                importance,
                                keywords,
                                filling
                            )

        # Insert the node at the beginning of the thought sequence
        self.seq_thought[0:0] = [node]
        keywords = {kw.lower() for kw in keywords}
        
        # Map keywords to thoughts
        for kw in keywords:
            if kw in self.kw_to_thought:
                self.kw_to_thought[kw][0:0] = [node]
            else:
                self.kw_to_thought[kw] = [node]
        
        self.id_to_node[node_id] = node

        # Update keyword strength if the thought is significant
        if f"{p} {o}" != "is idle":
            for kw in keywords:
                if kw in self.kw_strength_thought:
                    self.kw_strength_thought[kw] += 1
                else:
                    self.kw_strength_thought[kw] = 1

        # Store the embedding
        self.embeddings[embedding_pair[0]] = embedding_pair[1]

        return node

    def get_summarized_latest_events(self, retention: int) -> Set[Tuple[str, str, str]]:
        """
        Retrieves a summary of the latest events based on the retention limit.
        
        Args:
            retention (int): Number of latest events to summarize.
        
        Returns:
            Set[Tuple[str, str, str]]: A set of tuples containing (subject, predicate, object) for the latest events.
        """
        ret_set: Set[Tuple[str, str, str]] = set()
        
        # Collect summaries for the latest events
        for e_node in self.seq_event[:retention]:
            ret_set.add(e_node.spo_summary())
        
        return ret_set

    def get_str_seq_events(self) -> str:
        """
        Returns a string representation of the sequence of events.
        
        Returns:
            str: A string detailing the sequence of events.
        """
        ret_str: str = ""
        
        # Build a string representation of the event sequence
        for count, event in enumerate(self.seq_event):
            ret_str += f'{"Event", len(self.seq_event) - count, ": ", event.spo_summary(), " -- ", event.description}\n'
        
        return ret_str

    def get_str_seq_thoughts(self) -> str:
        """
        Returns a string representation of the sequence of thoughts.
        
        Returns:
            str: A string detailing the sequence of thoughts.
        """
        ret_str: str = ""
        
        # Build a string representation of the thought sequence
        for count, event in enumerate(self.seq_thought):
            ret_str += f'{"Thought", len(self.seq_thought) - count, ": ", event.spo_summary(), " -- ", event.description}\n'
        
        return ret_str

    def retrieve_relevant_thoughts(self, s_content: str, p_content: str, o_content: str) -> Set[ConceptNode]:
        """
        Retrieves thoughts relevant to the given subject, predicate, or object content.
        
        Args:
            s_content (str): Subject content to search for.
            p_content (str): Predicate content to search for.
            o_content (str): Object content to search for.
        
        Returns:
            Set[ConceptNode]: A set of relevant thought nodes.
        """
        contents: List[str] = [s_content, p_content, o_content]
        ret: List[ConceptNode] = []
        
        # Collect relevant thoughts based on the provided content
        for content in contents:
            if content.lower() in self.kw_to_thought:
                ret += self.kw_to_thought[content.lower()]

        return set(ret)

    def retrieve_relevant_events(self, s_content: str, p_content: str, o_content: str) -> Set[ConceptNode]:
        """
        Retrieves events relevant to the given subject, predicate, or object content.
        
        Args:
            s_content (str): Subject content to search for.
            p_content (str): Predicate content to search for.
            o_content (str): Object content to search for.
        
        Returns:
            set: A set of relevant event nodes.
        """
        contents = [s_content, p_content, o_content]
        ret: List[ConceptNode] = []
        
        # Collect relevant events based on the provided content
        for content in contents:
            if content.lower() in self.kw_to_event:
                ret += self.kw_to_event[content.lower()]

        ret = set(ret)
        return ret