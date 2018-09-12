class Message():
    def __init__(self):
        self.public_key = ""
        self.message = ""
        self.signature = ""

class NodesRequest():
    def __init__(self):
        self.node_id = ""

class StateUpdate():
    def __init__(self):
        self.node_id = ""
        self.timestamp = 0
        self.new_state = ""

class NodesInfo():
    def __init__(self):
        self.node_ids_to_ports = {}
        self.node_ids_to_states = {}

class NewActiveNode():
    def __init__(self):
        self.node_id = ""
        self.timestamp = 0
        self.state = ""

class NodeExit():
    def __init__(self):
        self.node_id = ""
