import time
import socket
import json

from threading import Thread

from spletnya.books import Books

import logging
logger = logging.getLogger(__name__)

class SpletnyaNode():
    def __init__(self, cfg):
        self._cfg = cfg

        self._node = socket.socket(type=socket.SOCK_DGRAM)
        self._hostname = socket.gethostname()
        self._port = self._cfg.connection.port

        self._node.bind((self._hostname, self._port))
        self._connected_nodes_ports = self._cfg.connection.connected_nodes

        self._state = ""

        self._books = Books()

        self._states = {}


    def send_msg(self, msg, port):
        logger.info("Msg= {} sent to port={}".format(msg, port))
        self._node.sendto(msg, (self._hostname, port))

    def send_state(self):
        while True:
            time.sleep(5)

            self._state = self._books.get_random_book()
            encoded_msg = self._state.encode('ascii')
            for node_port in self._connected_nodes_ports:
                self.send_msg(encoded_msg, node_port)

            self.log_states()

    def log_states(self):
        all_states = {**self._states, **{self._port : self._state}}
        logger.info("Current states: {}".format(json.dumps(all_states)))

    def get_state(self):
        while True:
            time.sleep(0.1)

            msg, address = self._node.recvfrom(1024)
            logger.info("Msg= {} received from={}".format(msg, address))

            self._states[address[1]] = msg.decode()

            #encoded_msg = self._state.encode('ascii')
            #for node_port in self.connected_nodes_ports:
            #    self.send_msg(encoded_msg, node_port)

    def run(self):
        logger.info("Spletnya node started")

        Thread(target=self.send_state).start()
        Thread(target=self.get_state).start()

