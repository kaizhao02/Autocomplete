import sys
import os
import heapq
import re

class Node:

    def __init__(self, data = None):
        self.data = data
        self.is_word = False
        self.score = 0
        self.completions = [] # Stores the top 10 words the start with the prefix this node represents

        self.left = None
        self.right = None
        self.middle = None
    
    def add_completion(self, word, score):
        """ Adds a word to this nodes completion list, maintaining the top 10 words with
            the highest score

            Args:
                word: the word to be added
                score: the score of the word
                
        """
        heapq.heappush(self.completions, (score, word))
        if len(self.completions) > 10:
            heapq.heappop(self.completions)

class QueryServer:
    """ A class to provide query serving.
        The underlying structure is a Ternary Search Tree

    """
    
    def __init__(self):
        self.root = Node()
        
    
    def insert_node(self, root, node):
        """ Inserts a node into the TST rooted by root

            Args:
                root: the root of the TST we are inserting into
                node: the node to be inserted
                
            Returns:
                returns the root
   
        """
        if not root:
            return node
        elif root.data < node.data:
            root.right = self.insert_node(root.right, node)
        elif root.data > node.data:
            root.left = self.insert_node(root.left, node)
        else:
            root.middle = self.insert_node(root.middle, node)

        return root
    
    def insert(self, word, score):
        """ Inserts a word into this TST, as well as inserting the word
            into all of the respective prefixes. 

            Args:
                word: the word to be inserted
                score: the score of word
   
        """
        ptr = self.root
        ptr.add_completion(word, score)
        self.insert_completion(word, word, score)

        for i, c in enumerate(word):

            if c == "_":
                self.insert_completion(word[i+1:], word, score)

            node = self.search_char(ptr.middle, c)
            
            if not node:
                node = Node(c)
                ptr.middle = self.insert_node(ptr.middle, node)

            ptr = node

        ptr.is_word = True
        ptr.score = score

    def insert_completion(self, prefix, word, score):
        """ Inserts word into the completions of all the prefix nodes of prefix
            
            Args:
                prefix: the prefix we are inserting into
                word: the word we are inserting
                score: the score of word
   
        """
        ptr = self.root
        
        for c in prefix:
            node = self.search_char(ptr.middle, c)
            
            if not node:
                node = Node(c)
                ptr.middle = self.insert_node(ptr.middle, node)

            ptr = node
            ptr.add_completion(word, score)

    def search_char(self, root, char):
        """ Searches root for the node where data equals char
            
            Args:
                root: the root of the tree to be searched
                char: the char we are looking for

            Returns:
                returns the node where the char is found or None if it
                is not found
   
        """

        while root:
            if root.data == char:
                return root
            elif root.data < char:
                root = root.right
            else:
                root = root.left

        return None

    def search(self, word):
        """ Searches this TST for a word
            
            Args:
                word: the word to be searched

            Returns:
                returns the node where the word is found or None if the word 
                doesn't exist in the TST
   
        """
        ptr = self.root

        for c in word:
            ptr = self.search_char(ptr.middle, c)
            if not ptr:
                break

        return ptr

    def get_completions(self, prefix):
        """ Returns:
                returns a list of the top 10 words starting with prefix
   
        """
        pre = self.search(prefix)
        if not pre:
            return []
        pre.completions.sort(reverse = True)
        return [completion[1] for completion in pre.completions]

    def build_from_strings(self, pairs):
        """ Builds this QueryServer from a list of strings of "(name, score)"" 
               
            Args:
                pairs: list of "(name, score)" strings
   
        """
        for pair in pairs:
            pair = pair.split(",")
            self.insert(pair[0].strip(), int(pair[1].strip()))
            # self.insert(pair[0], random.randint(0, 1000000))

    def build_from_tuples(self, pairs):
        """ Builds this QueryServer from a list of tuples of (name, score) 
               
            Args:
                pairs: list of (name, score) tuples
   
        """
        for pair in pairs:
            self.insert(pair[0], pair[1])

    def serialize(self):
        """ Serializes this QueryServer into a unique string representation which can be saved to a file
            and loaded at a later time
            
        Returns:
            returns the serialization of this QueryServer as a string
   
        """
        encoding = []

        def encode(node):
            if not node:
                encoding.append(':')
                return

            encoding.append((node.data if node.data else ":") + "," 
                            + str(node.is_word) + ","
                            + str(node.score) + ","
                            + ",".join(str(pair[0]) + "," + pair[1] for pair in node.completions))

            encode(node.left)
            encode(node.middle)
            encode(node.right)

        encode(self.root)

        return ' '.join(encoding)            

    def deserialize(self, encoding):
        """ Takes a serialized QueryServer and deserializes it, setting the root of this 
            tree to the deserialized QueryServer
               
            Args:
                encoding: the serialized QueryServer as a string 
   
        """

        def decode(encoding_iter):
            encoded_node = next(encoding_iter)

            if encoded_node == ":":
                return None 

            encoded_node = encoded_node.split(",")
            data = encoded_node[0]
            is_word = encoded_node[1] == str(True)
            score = int(encoded_node[2])
            i = 3

            if data == ":":
                node = Node()
            else:
                node = Node(data)

            node.is_word = is_word
            node.score = score

            while i < len(encoded_node):
                node.completions.append((int(encoded_node[i]), encoded_node[i + 1]))
                i += 2

            node.left = decode(encoding_iter)
            node.middle = decode(encoding_iter)
            node.right = decode(encoding_iter)

            return node

        encoding_iter = iter(encoding.split())

        self.root = decode(encoding_iter)

def load_QueryServer(pairs = None, names_input_filename = None, encoding_input_filename = None):
    """ Loads a QueryServer from either a list of (name, score) pairs, 
        an input file containing (name, score) pairs, or 
        an input file containing a serialized QueryServer.
           
        Args:
            pairs: list of (name, score) pairs
            names_input_filename: input file containing (name, score) pairs
            encoding_input_filename: input file containing a serialized QueryServer
            
        Returns:
            returns a new QueryServer with the loaded data
   
    """
    query_server = QueryServer()

    if pairs:
        query_server.build_from_tuples(pairs)
    
    elif names_input_filename:
        with open(names_input_filename, "r") as file:
            read_pairs = re.findall('\(([^)]+)', file.read())
        query_server.build_from_strings(read_pairs)
    
    elif encoding_input_filename:
        with open(encoding_input_filename, "r") as file:
            serialization = file.read()

        query_server.deserialize(serialization)

    return query_server

def dump_QueryServer(query_server, output_filename):
    """ Writes the serialization of a QueryServer to an output file 
           
        Args:
            query_server: the QueryServer to be serialized 
            output_filename: the file to be written to
           
    """
    with open(output_filename, "w") as file:
        file.write(query_server.serialize())

def print_options():
    print('Usage : ', os.path.basename(sys.argv[0]), ' [options]\n')
    print('Where   options not given         : builds new Query Server')
    print('        options = -n input        : loads Query Server from input via inserting names')
    print('        options = -s input        : loads Query Server from input via deserialization') 

def main(argv):
    output_filename = ""

    if len(sys.argv) == 1:
        query_server = QueryServer()
    elif len(sys.argv) == 3:
        if sys.argv[1] == "-s":
            print("\nLoading Query Server from serialization in " + sys.argv[2])
            query_server = load_QueryServer(encoding_input_filename = sys.argv[2])
        elif sys.argv[1] == "-n":
            print("\nLoading Query Server from names in " + sys.argv[2])
            query_server = load_QueryServer(names_input_filename = sys.argv[2])
        else:
            print_options()       
            return 
    else:
        print_options()
        return 

    # Allows users to insert names, query for names, or write the QueryServer to a file
    while True:
        user_input = input("\nPress 1 to add, 2 to query, 3 to dump data, any other key to quit: ")

        if user_input == "1":
            name = input("\nName: ")
            score = input("Score: ")
            try:
                query_server.insert(name, int(score))
            except:
                print("Invalid name or score")

        elif user_input == "2":
            prefix = input("\nPrefix: ")
            print(query_server.get_completions(prefix))
        elif user_input == "3":
            file = input("\nFile to dump to: ")
            print("Dumping data to " + file)
            dump_QueryServer(query_server, file)
        else:
            break

if __name__ == "__main__":
    main(sys.argv)


