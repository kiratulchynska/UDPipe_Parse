import re

class Node:
    """
    Represents a node in a CoNLL-U file.
    Attributes:
        str (str): The original line representing the node.
        id (str): The ID of the node.
        form (str): The form of the node.
        lemma (str): The lemma of the node.
        upos (str): The universal part-of-speech tag.
        xpos (str): The language-specific part-of-speech tag.
        feats (dict): A dictionary of features.
        head (str): The ID of the head node.
        deprel (str): The dependency relation to the head.
        deps (list): A list of enhanced dependencies.
        misc (dict): A dictionary of miscellaneous information.
        parent (Node): The head node object, set later when the head node is found.
        children (list): A list of child Node objects, set later when the children nodes are found.
    """
    def __init__(self, line):
        """
        Initialize a Node object from a line in a CoNLL-U file.
        Args:
            line (str): A line from a CoNLL-U file representing a node. For example:
                        "1\tThe\tthe\tDET\tDT\tDefinite=Def|PronType=Art\t4\tdet\t_\t_"
        """
        def extract_features(feats):
            """
            Extract features from a string and return them as a dictionary.
            Args:
                feats (str): A string of features in the format "key=value|key2=value2|...".
            Returns:
                dict: A dictionary where keys are feature names and values are feature values.
            """
            if feats == '_':
                return {}
            feats = feats.split('|')
            feats_dict = {}
            for feat in feats:
                key, value = feat.split('=')
                feats_dict[key.strip()] = value.strip()
            return feats_dict
        
        line = line.split('\t')
        self.id = line[0]
        self.form = line[1]
        self.lemma = line[2] if line[2] != '_' else ''
        self.upos = line[3] if line[3] != '_' else ''
        self.xpos = line[4] if line[4] != '_' else ''
        self.feats = extract_features(line[5])
        self.head = line[6] if line[6] != '_' else ''
        self.deprel = line[7] if line[7] != '_' else ''
        self.deps = line[8].split('|') if line[8] != '_' else []
        self.misc = extract_features(line[9])
        self.parent = None  # This will be set later when the head node is found
        self.children = []  # This will be set later when the children nodes are found
    
    def __str__(self):
        string = '\t'.join([
            self.id,
            self.form,
            self.lemma if self.lemma != '' else '_',
            self.upos if self.upos != '' else '_',
            self.xpos if self.xpos != '' else '_',
            '|'.join([f"{k}={v}" for k, v in self.feats.items()]) if self.feats else '_',
            self.head if self.head != '' else '_',
            self.deprel if self.deprel != '' else '_',
            '|'.join(self.deps) if self.deps else '_',
            '|'.join([f"{k}={v}" for k, v in self.misc.items()]) if self.misc else '_'
        ])
        return string
    
    def get_rels(self, nodes: list):
        """
        Get the relations of this node from a list of nodes.
        Args:
            nodes (list): A list of Node objects.
        """
        for node in nodes:
            if node.head == self.id:
                self.children.append(node)
            if node.id == self.head:
                self.parent = node
        if self.parent is None and self.head == '0':
            self.parent = Node('0\tROOT\t_\t_\t_\t_\t_\t_\t_\t_') 

class Sent:
    """
    Represents a sentence in a CoNLL-U file.
    Attributes:
        metadata (dict): A dictionary of metadata for the sentence.
        nodes (list): A list of Node objects representing the tokens in the sentence.

    """
    def __init__(self, text: str):
        """
        Initialize a Sent object from a CoNLL-U formatted string.
        Args:
            text (str): A CoNLL-U formatted string representing a sentence.
        """
        metadata = {}
        not_filled_nodes = []
        for line in text.strip().split('\n'):
            if line.startswith('#'):
                if ' = ' in line:
                    k, v = line[2:].split(' = ', 1)
                    metadata[k.strip()] = v.strip()
                else:
                    metadata[line[2:].strip()] = ''
            elif re.search(r'^\d+(\t[^\t]+){9}', line):
                node = Node(line)
                not_filled_nodes.append(node)
        self.metadata = metadata

        nodes = []
        for node in not_filled_nodes:
            node: Node
            node.get_rels(not_filled_nodes)
            nodes.append(node)
        self.nodes = nodes
    
    def __str__(self):
        string = ''
        for k, v in self.metadata.items():
            if v:
                string += f"# {k} = {v}\n"
            else:
                string += f"# {k}\n"
        for node in self.nodes:
            string += str(node) + '\n'
        return string
