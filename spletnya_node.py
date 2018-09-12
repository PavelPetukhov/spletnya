import time
import socket
import json
import pickle
import uuid
import random

from threading import Thread

from spletnya.books import Books

from spletnya.molva import messages
from spletnya.authentication import Authentication

import logging
logger = logging.getLogger(__name__)

def generate_id():
    return str(uuid.uuid4())

def generate_timestamp():
    return int(round(time.time()))

class SpletnyaNode():
    def __init__(self, cfg):
        self._cfg = cfg

        self_auth = Authentication(self._cfg)

        self._books = Books()

        self._node = socket.socket(type=socket.SOCK_DGRAM)
        self._hostname = socket.gethostname()
        self._port = self._cfg.connection.port
        self._node_id = generate_id()

        self._num_of_nodes_to_notify = self._cfg.connection.num_of_nodes_to_notify

        self._node.bind((self._hostname, self._port))

        self._timestamp = generate_timestamp()
        self._state = self._books.get_random_book()
        self._node_ids_to_states = {}
        self._node_ids_to_ports = {}

        self._info_requested = False
        self._info_received = False

    def send_msg(self, msg, port):
        logger.info("Msg= {} sent to port={}".format(msg, port))
        self._node.sendto(msg, (self._hostname, port))

    def receive_msg(self):
        return self._node.recvfrom(1024)

    def notify_all(self, msg):
        for node_port in self._node_ids_to_ports:
            self.send_msg(msg, self._node_ids_to_ports[node_port])

    def select_nodes_and_notify(self, msg):
        nodes_num = self._num_of_nodes_to_notify
        if nodes_num > len(self._node_ids_to_ports.values()):
            nodes_num = len(self._node_ids_to_ports.values())

        ports_as_is = [self._node_ids_to_ports[k] for k in self._node_ids_to_ports]
        random.shuffle(ports_as_is)
        ports = ports_as_is[:nodes_num]
        for port in ports:
            self.send_msg(msg, port)

    def send_state(self):
        while True:
            time.sleep(5)

            if self._info_requested is False:
                self._info_requested = True

                req = messages.NodesRequest()
                msg = pickle.dumps(req)
                for node_port in self._cfg.connection.connected_nodes:
                    self.send_msg(msg, node_port)
            elif self._info_received is True:
                self._state = self._books.get_random_book()
                self._timestamp = generate_timestamp()
                logger.info("new state generated = {}, timestamp = {}, node_id={}".format(self._state, self._timestamp, self._node_id))
                msg = messages.StateUpdate()
                msg.node_id = self._node_id
                msg.timestamp = self._timestamp
                msg.new_state = self._state
                msg = pickle.dumps(msg)

                self.select_nodes_and_notify(msg)

    def log_states(self):
        all_states = {**self._node_ids_to_states, **{self._node_id : (self._timestamp, self._state)}}
        logger.info("Current states: {}".format(json.dumps(all_states)))

    def receive_message(self):
        while True:
            time.sleep(0.1)

            raw_msg, address = self.receive_msg()
            logger.info("Msg= {} received from={}".format(raw_msg, address))

            port = address[1]
            msg = pickle.loads(raw_msg)

            if isinstance(msg, messages.StateUpdate):
                state = self._node_ids_to_states.get(msg.node_id)
                if state is None or msg.timestamp > state[0]:
                    self._node_ids_to_states[msg.node_id] = (msg.timestamp, msg.new_state)
                    if self._info_received is True:
                        msg = pickle.dumps(msg)
                        self.select_nodes_and_notify(msg)
            elif isinstance(msg, messages.NodesRequest):
                info = messages.NodesInfo()
                info.node_ids_to_ports = {**self._node_ids_to_ports, **{self._node_id : self._port}}
                info.node_ids_to_states = {**self._node_ids_to_states, **{self._node_id : (self._timestamp, self._state)}}
                msg = pickle.dumps(info)
                self.send_msg(msg, port)
            elif isinstance(msg, messages.NodesInfo) and self._info_received is False:

                #TODO add sequence number check to get the freshest state
                self._info_received = True
                self._node_ids_to_ports = msg.node_ids_to_ports
                self._node_ids_to_states = msg.node_ids_to_states

                msg = messages.NewActiveNode()
                msg.node_id = self._node_id
                msg.state = self._state
                self._timestamp = generate_timestamp()
                msg.timestamp = self._timestamp
                msg = pickle.dumps(msg)
                self.notify_all(msg)
            elif isinstance(msg, messages.NewActiveNode):
                self._node_ids_to_ports[msg.node_id] = port
                self._node_ids_to_states[msg.node_id] = (msg.timestamp, msg.state)

            self.log_states()

    def run(self):
        logger.info("Spletnya node started")

        Thread(target=self.send_state).start()
        Thread(target=self.receive_message).start()

