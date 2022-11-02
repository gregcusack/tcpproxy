from dataclasses import replace
from netfilterqueue import NetfilterQueue
from scapy.all import *
from scapy.layers.http import HTTPRequest
import os
from Count import Count
from ConnectionTracker import ConnectionTracker
from MutablePacket import MutablePacket

load_contrib('bgp') #scapy does not automatically load items from Contrib. Must call function and module name to load.

count = Count()
connections = ConnectionTracker()

def setup():
    QUEUE_NUM = 1 
    # insert the iptables FORWARD rule
    os.system("iptables -I INPUT -p tcp --dport 5000 -j NFQUEUE --queue-num {}".format(QUEUE_NUM))
    os.system("iptables -I OUTPUT -p tcp --sport 5000 -j NFQUEUE --queue-num {}".format(QUEUE_NUM))

def new_packet(packet):
    # We need to track all packets not just ones with a payload!!
    print("##############################################")
    print("new packet")
    pkt = IP(packet.get_payload())
    m_pkt = MutablePacket(pkt)

    print(m_pkt.packet().show())
    count.incr_count()
    current_count = count.get_count()
    print("packet count: " + str(current_count))

    if Raw in pkt:# or BGPHeader in pkt:
        print("payload in packet")
        # m_pkt = MutablePacket(pkt)

        """
        Check for blockchain validation here.
        If packet need mnodification here, set flag
        """
        if b"modify-header: true" in m_pkt.packet()[Raw].load:
            print("modify packet! - blockchain check fails")
            invalid_routes = []
            invalid_routes.append("colorado")
            m_pkt.edit_payload(maintain_length=True)
        
        elif b"modify-header: shrink" in m_pkt.packet()[Raw].load:
            print("shrink packet! - blockchain check fails")
            invalid_routes = []
            invalid_routes.append("colorado")
            m_pkt.edit_payload(maintain_length=False)

        
    if not connections.connection_exists(m_pkt):
        connections.add_connection(m_pkt)
    connections.update_connection(m_pkt)

    if m_pkt.is_modified():
        packet.set_payload(bytes(m_pkt.packet()))
        print("packet after modification: ")
        print(m_pkt.packet().show())
    
    packet.accept()
        

        

        # if connections.connection_exists(pkt):
        #     print("connection exists. updating stream")
        #     connections.update_connection(pkt)
        # else:
        #     print("connection does not exist. add")
        #     connections.add_connection(pkt)

       
    # else:
    #     packet.accept()
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")




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
        # remove that rule we just inserted, going back to normal.
        os.system("iptables --flush")
        nfqueue.unbind()


if __name__ == "__main__":
    main()