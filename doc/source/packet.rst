:mod:`packet` Module
====================

.. module:: packet
   :synopsis: Packet manager and predefined packets.


.. class:: PacketManager

   Class allowing to register new packet types and send them.
   
   It is used by :class:`Client` and :class:`Server`.
   
   Example::
   
       chat_msg = PacketManager.register('chat_msg', ('player', 'msg'), enet.PACKET_FLAG_RELIABLE)
       PacketManager.send(peer, 0, chat_msg('Tom', 'Test message'))
   
   
   .. classmethod:: PacketManager.get_packet(name)
   
      Returns packet class with given name
   
      :param name: name of packet
      :return: packet (namedtuple)
      
   
   .. classmethod:: PacketManager.register(name, field_names[, flags])
   
      Register new packet type and return class
      
      :param name: name of packet class
      :param field_names: list of names of packet fields
      :param flags: 
         enet flags used when sending packet
         (default :const:`enet.PACKET_FLAG_RELIABLE`)
      :return: packet (namedtuple)
      

Predefined packets
------------------

.. class:: chat_msg(player, msg)

   :param player: player name
   :param msg: message


.. class:: update_remoteobject(type_id, obj_id, variables)

   Packet used by :class:`syncobject.SyncObjectManager` to update state of
   :class:`syncobject.RemoteObject`.

   :param type_id: identifier of object type
   :param obj_id: identifier of object instance
   :param variables: list of changed object variables

