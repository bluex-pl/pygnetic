:mod:`pygame_network` Package
=============================

.. toctree::
   :maxdepth: 1
   
   client
   packet
   syncobject
   
Events
------

Connected event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_CONNECTED`
   | ``event.connection`` `proxy`_ to connection

Disconnected event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_DISCONNECTED`
   | ``event.connection`` `proxy`_ to connection

Received event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_RECEIVED`
   | ``event.connection`` `proxy`_ to connection
   | ``event.channel`` channel of connection
   | ``event.packet`` received packet
   | ``event.p_id`` packet identifier
   | ``event.p_type`` packet type

Response event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_RESPONSE`
   | ``event.connection`` `proxy`_ to connection
   | ``event.channel`` channel of connection
   | ``event.packet`` received packet
   | ``event.p_id`` packet identifier
   | ``event.p_type`` packet type

Example::

   for e in pygame.event.get():
       if e.type == NETWORK:
           if e.net_type == NET_CONNECTED:
               print 'connected'
           elif e.net_type == NET_DISCONNECTED:
               print 'disconnected'
           elif e.net_type == NET_RECEIVED:
               if e.p_type == packet.chat_msg:
                   print '%s: %s' % (e.packet.player, e.packet.msg)
               else:
                   print 'received:', e.packet
           elif e.net_type == NET_RESPONSE:
               print 'response @%d: %s' % (e.p_id, e.packet)


Functions
---------

.. function:: register(name, field_names[, flags])
   
   Register new packet type and return class by calling 
   :meth:`packet.PacketManager.register` 
   
   :param name: name of packet class
   :param field_names: list of names of packet fields
   :param flags: 
      enet flags used when sending packet
      (default :const:`enet.PACKET_FLAG_RELIABLE`)
   :rtype: (named tuple) packet
   
.. _proxy: http://docs.python.org/library/weakref.html#weakref.proxy