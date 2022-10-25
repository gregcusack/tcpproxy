from netfilterqueue import NetfilterQueue
from scapy.all import *
from scapy.layers.http import HTTPRequest
import os
from Count import Count
from ConnectionTracker import ConnectionTracker
from Connection import Connection

load_contrib('bgp') #scapy does not automatically load items from Contrib. Must call function and module name to load.

count = Count()
connections = ConnectionTracker()

def setup():
    QUEUE_NUM = 1 
    # insert the iptables FORWARD rule
    os.system("iptables -I INPUT -p tcp --dport 5000 -j NFQUEUE --queue-num {}".format(QUEUE_NUM))

def new_packet(packet):
    pkt = IP(packet.get_payload())
    if Raw in pkt:# or BGPHeader in pkt:
        print("new packet!")
        if connections.connection_exists(pkt):
            connections.update_connection(pkt)
        else:
            print("connection does not exist. add")
            connections.add_connection(pkt)

        print(pkt.show())
        # print(str(pkt.summary()))
        count.incr_count()
        current_count = count.get_count()
        print("packet count: " + str(current_count))

        if b"drop-header: true" in pkt[Raw].load:
            print("drop header == true. Dropping packet")
            connections.drop_packet(pkt)
            packet.drop()
        else:
            packet.accept()

        # if current_count % 5 == 0:
        #     print("dopping packet. request multiple of 5: " + str(current_count))
        #     packet.drop()
        # else:
        #     packet.accept()
    else:
        packet.accept()



def main():
    setup()
    # count = Count()
    nfqueue = NetfilterQueue()
    nfqueue.bind(1, new_packet)
    print("waiting for nfqueue packets in queue...")
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        print('')

    nfqueue.unbind()


if __name__ == "__main__":
    main()