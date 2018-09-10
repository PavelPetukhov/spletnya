import time
import socket
from threading import Thread

from spletnya.books import Books

import logging
logger = logging.getLogger(__name__)

class SpletnyaNode():
    def __init__(self, cfg):
        self.cfg = cfg

        self.node = socket.socket(type=socket.SOCK_DGRAM)
        self.hostname = socket.gethostname()
        self.port = self.cfg.connection.port

        self.node.bind((self.hostname, self.port))
        self.connected_nodes_ports = self.cfg.connection.connected_nodes

        self._books = Books()


    def send_state(self):
        while True:
            time.sleep(5)

            msg = self._books.get_random_book()
            encoded_msg = msg.encode('ascii')
            for node_port in self.connected_nodes_ports:
                logger.info("Msg= {} sent to port={}".format(msg, node_port))
                self.node.sendto(encoded_msg, (self.hostname, node_port))

    def get_state(self):
        while True:
            time.sleep(0.1)

            msg, address = self.node.recvfrom(1024)
            logger.info("Msg= {} received from={}".format(msg, address))


    def run(self):
        logger.info("Spletnya node started")

        Thread(target=self.send_state).start()
        Thread(target=self.get_state).start()

