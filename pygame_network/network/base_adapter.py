import re
import logging
from weakref import proxy
from functools import partial
from .. import message
from .. import event
from ..handler import Handler

__all__ = ('Connection', 'State')
_logger = logging.getLogger(__name__)


class Connection(object):
    """Class allowing to send messages

    It's created by by Client or Server, shouldn't be created manually.

    Sending is possible in two ways:
    * using net_<message_name> methods, where <message_name>
      is name of message registered in MessageFactory
    * using send method with message as argument

    Attributes:
        parent - proxy to Client / Server instance
        address - connection address
        connected - True if connected
        data_sent - amount of data sent
        data_received - amount of data received
        messages_sent - amount of messages sent
        messages_received - amount of messages received
    """

    def __init__(self, parent, message_factory, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.parent = proxy(parent)
        self.message_factory = message_factory
        self.message_factory.reset_context(self)
        self.handlers = []
        self.data_sent = 0
        self.data_received = 0
        self.messages_sent = 0
        self.messages_received = 0

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if (len(parts) == 2 and parts[0] == 'net' and
                parts[1] in self.message_factory._message_names):
            p = partial(self._send_message, self.message_factory.get_by_name(parts[1]))
            p.__doc__ = "Send %s message to remote host\n\nHost.net_%s" % (
                parts[1],
                self.message_factory._message_names[parts[1]].__doc__
            )
            # add new method so __getattr__ is no longer needed
            setattr(self, name, p)
            return p
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, name))

    def send(self, message, *args, **kwargs):
        """Send message to remote host

        Connection.send(message, *args, **kwargs): return int

        message - class created by MessageFactory.register or message name

        args and kwargs are used to initialize message object.
        Returns message id which can be used to retrieve response from
        Pygame event queue if sending was successful.
        """
        if isinstance(message, basestring):
            message = self.message_factory.get_by_name(message)
        self._send_message(message, *args, **kwargs)

    def _send_message(self, message, *args, **kwargs):
        name = message.__name__
        params = self.message_factory.get_params(message)[1]
        try:
            message_ = message(*args, **kwargs)
        except TypeError, e:
            e, f = re.findall(r'\d', e.message)
            raise TypeError('%s takes exactly %d arguments (%d given)' %
                (message.__doc__, int(e) - 1, int(f) - 1))
        data = self.message_factory.pack(message_)
        _logger.info('Sent %s message to %s:%s', name, *self.address)
        self.data_sent += len(data)
        self.messages_sent += 1
        return self._send_data(data, **params)

    def _receive(self, data, **kwargs):
        for message in self.message_factory.unpack_all(data, self):
            name = message.__class__.__name__
            _logger.info('Received %s message from %s:%s', name, *self.address)
            event.received(self, message)
            for h in self.handlers:
                getattr(h, 'net_' + name, h.on_recive)(message, **kwargs)

    def _connect(self):
        _logger.info('Connected to %s:%s', *self.address)
        event.connected(self)
        for h in self.handlers:
            h.on_connect()

    def _disconnect(self):
        _logger.info('Disconnected from %s:%s', *self.address)
        event.disconnected(self)
        for h in self.handlers:
            h.on_disconnect()

    def disconnect(self, *args):
        """Request a disconnection."""
        pass

    def add_handler(self, handler):
        """Add new Handler to handle messages.

        Connection.add_handler(handler)

        handler - instance of Receiver subclass
        """
        self.handlers.append(handler)
        handler.connection = proxy(self)

    @property
    def address(self):
        """Connection address."""
        return None, None


class Server(object):
    message_factory = message.message_factory
    handler = None
    connection = Connection

    def __init__(self, address='', port=0, conn_limit=4, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        _logger.info('Server created %s:%d, connections limit: %d', address, port, conn_limit)
        self.message_factory.set_frozen()
        self.conn_map = {}

    def update(self, timeout=0):
        pass

    def _accept(self, mf_hash, socket, c_id, address):
        if mf_hash == self.message_factory.get_hash():
            _logger.info('Connection with %s accepted', address)
            connection = self.connection(self, socket, self.message_factory)
            if self.handler is not None and issubclass(self.handler, Handler):
                handler = self.handler()
                handler.server = proxy(self)
                connection.add_handler(handler)
            self.conn_map[c_id] = connection
            event.accepted(self)
            connection._connect()
            return True
        else:
            _logger.info('Connection with %s refused, MessageFactory'\
                            ' hash incorrect', address)
            return False

    def _disconnect(self, c_id):
        self.conn_map[c_id]._disconnect()
        del self.conn_map[c_id]

    def _receive(self, c_id, data, **kwargs):
        self.conn_map[c_id]._receive(data, **kwargs)

    def connections(self, exclude=None):
        if exclude is None:
            return self.conn_map.itervalues()
        else:
            return (c for c in self.conn_map.itervalues() if c not in exclude)

    def handlers(self, exclude=None):
        if exclude is None:
            return (c.handlers[0] for c in self.conn_map.itervalues())
        else:
            return (c.handlers[0] for c in self.conn_map.itervalues() if c not in exclude)


class Client(object):
    """Class representing network client

    Example:
        client = pygame_network.client.Client()
        connection = client.connect("localhost", 10000)
        while True:
            client.update()
    """
    message_factory = message.message_factory

    def __init__(self, conn_limit=1, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.conn_map = {}
        _logger.info('Client created, connections limit: %d', conn_limit)

    def connect(self, address, port, message_factory=None, **kwargs):
        if message_factory is None:
            message_factory = self.message_factory
        _logger.info('Connecting to %s:%d', address, port)
        message_factory.set_frozen()
        socket, c_id = self._create_connection(address, port, message_factory.get_hash(), **kwargs)
        conn = self.connection(self, socket, message_factory)
        self.conn_map[c_id] = conn
        return conn

    def update(self, timeout=0):
        pass

    def _connect(self, c_id):
        self.conn_map[c_id]._connect()

    def _disconnect(self, c_id):
        self.conn_map[c_id]._disconnect()
        del self.conn_map[c_id]

    def _receive(self, c_id, data, **kwargs):
        self.conn_map[c_id]._receive(data, **kwargs)
