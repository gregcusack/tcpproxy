from Connection import Connection
from scapy.all import *


class ConnectionTracker:
    def __init__(self):
        # self.connections = set()
        self.connections = {}


    def add_connection(self, pkt):
        connection = Connection(pkt)
        if connection:
            self.connections[connection.five_tuple] = connection
        else:
            print("Error failed to add connection: " + str(connection))

    def get_connection(self, connection):
        return self.connections[connection.five_tuple]

    def connection_exists(self, pkt):
        print("does connection exist??")
        connection = Connection(pkt)
        if connection:
            return connection.five_tuple in self.connections
        elif connection == False:
            return False
        else:
            print("Error failed to check if connection exists: " + str(connection))
            return None


    def update_connection(self, pkt):
        tmp_connection = Connection(pkt)
        if tmp_connection:
            five_tuple = tmp_connection.five_tuple
            connection = self.connections[five_tuple]
            connection.incoming_packet_update(pkt)
            self.connections[five_tuple] = connection
        else:
            print("Error failed to update connection: " + str(connection))

    def drop_packet(self, pkt):
        ret = self.connection_exists(pkt)
        if ret:
            self.drop_packet_in_active_connection(pkt)
        elif ret == False:
            self.drop_packet_in_new_connection(pkt)
        else:
            print("ERROR. dropping packet in unknown state")

    def drop_packet_in_active_connection(self, pkt):
        print("dropping packet in active connection")
        

    def drop_packet_in_new_connection(self, pkt):
        print("dropping packet in new connection")


