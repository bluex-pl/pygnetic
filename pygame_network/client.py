import logging
import enet
from message import MessageFactory
from connection import Connection

_logger = logging.getLogger(__name__)


class Client(object):
    """Class representing network client

    Example:
        client = pygame_network.client.Client()
        connection = client.connect("localhost", 10000)
        while True:
            client.step()
    """
    def __init__(self, connections_limit=1, channel_limit=0, in_bandwidth=0, out_bandwidth=0):
        self.host = enet.Host(None, connections_limit, channel_limit, in_bandwidth, out_bandwidth)
        self._peers = {}
        self._peer_cnt = 0

    def connect(self, address, port, channels=2, message_factory=MessageFactory):
        peer_id = self._peer_cnt = self._peer_cnt + 1
        peer_id = str(peer_id)
        # Can't register messages after connection
        message_factory._frozen = True
        address = enet.Address(address, port)
        peer = self.host.connect(address, channels, message_factory.get_hash())
        peer.data = peer_id
        connection = Connection(self, peer, message_factory)
        self._peers[peer_id] = connection
        return connection

    def step(self, timeout=0):
        if len(self._peers) == 0:
            return
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                _logger.info('Connected to %s', event.peer.address)
                self._peers[event.peer.data]._connect()
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                _logger.info('Disconnected from %s', event.peer.address)
                self._peers[event.peer.data]._disconnect()
                del self._peers[event.peer.data]
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                _logger.info('Received data from %s', event.peer.address)
                self._peers[event.peer.data]._receive(event.packet.data, event.channelID)
            event = host.check_events()
