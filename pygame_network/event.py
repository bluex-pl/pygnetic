from weakref import proxy
import pygame
from pygame.event import Event
from pygame.locals import USEREVENT
import connection

NETWORK = USEREVENT + 1
NET_CONNECTED = 0
NET_DISCONNECTED = 1
NET_RECEIVED = 2
NET_RESPONSE = 3  # TODO: response !!


def conf_newtwork_event(val=1):
    global NETWORK
    NETWORK = USEREVENT + val


def _connected_event(connection):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_CONNECTED,
        #'connection': proxy(connection)
        'connection': connection
    }))
connection._connected_event = _connected_event


def _disconnected_event(connection):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_DISCONNECTED,
        #'connection': proxy(connection)
        'connection': connection
    }))
connection._disconnected_event = _disconnected_event


def _received_event(connection, channel, packet, packet_id):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_RECEIVED,
        #'connection': proxy(connection),
        'connection': connection,
        'channel': channel,
        'packet': packet,
        'p_id': packet_id,
        'p_type': packet.__class__
    }))
connection._received_event = _received_event


def _response_event(connection, channel, packet, packet_id):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_RESPONSE,
        #'connection': proxy(connection),
        'connection': connection,
        'channel': channel,
        'packet': packet,
        'p_id': packet_id,
        'p_type': packet.__class__
    }))
connection._response_event = _response_event
