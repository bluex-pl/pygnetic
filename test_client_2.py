import random
import logging
import pygame_network
from pygame_network import Receiver, Client


class EchoReceiver(Receiver):
    def __init__(self):
        self.connected = None
        self.counter = 10

    def net_echo(self, channel, packet_id, packet):
        print 'packet #%d @ch%d: %s' % (packet_id, channel, packet)

    def on_connect(self):
        self.connected = True

    def on_disconnect(self):
        self.connected = False

    def step(self):
        if self.counter > 0 and self.connected == True:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            print("%s: out: %r" % (self.connection.address, msg))
            self.connection.net_echo(msg)
            self.counter -= 1


def main():
    logging.basicConfig(level=logging.DEBUG)

    pygame_network.register('echo', ('msg',))
    print 'connecting'
    client = Client()
    connection = client.connect("localhost", 54301)
    receiver = EchoReceiver()
    connection.add_receiver(receiver)
    print 'client started'
    while receiver.connected != False:
        client.step()
        receiver.step()


if __name__ == '__main__':
    main()
