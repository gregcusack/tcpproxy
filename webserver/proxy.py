from dataclasses import replace
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

"""
1) We can modify the packet if we maintain the same length and everything works as expected
2) IF we modify the length of the TCP packet, then it fails despite updating the IP.len field
3) I believe this is because the ACK that comes back is wrong. ACK that comes back will
have old seq/ack numbers that are off by the length of the change we made.
4) Steps
    a) add in iptables to catch packets coming back from the server (aka ACKS)
    b) match streams by direction -> client->server needs to be connected to server->client
    c) Maintain ACKs/seq numbers

"""

def modify_packet(pkt):
    # print("modifying packet")
    load = pkt[Raw].load
    print(load)
    replacement_load = b"GET /mirror/greg/bruh HTTP/1.1\r\nHost: 192.168.5.92:8000\r\nUser-Agent: curl/7.79.1\r\nAccept: */*\r\nmodify-header: true\r\n\r\n"
    pkt[Raw].load = replacement_load
    print("new load")
    print(pkt[Raw].load)

    len_old_load = len(load)
    len_new_load = len(replacement_load)

    diff = 0
    if len_old_load > len_new_load:
        diff = len_old_load - len_new_load
        pkt[IP].len -= diff
    elif len_old_load < len_new_load:
        diff = len_new_load - len_old_load
        pkt[IP].len += diff

    print(pkt.show())
    print("pkt post payload/len mod")

    return pkt


def setup():
    QUEUE_NUM = 1 
    # insert the iptables FORWARD rule
    os.system("iptables -I INPUT -p tcp --dport 5000 -j NFQUEUE --queue-num {}".format(QUEUE_NUM))
    # os.system("iptables -I OUTPUT -p tcp --sport 5000 -j NFQUEUE --queue-num {}".format(QUEUE_NUM))

def new_packet(packet):
    pkt = IP(packet.get_payload())
    if Raw in pkt:# or BGPHeader in pkt:
        print("new packet!")
        if connections.connection_exists(pkt):
            print("connection exists. updating stream")
            connections.update_connection(pkt)
        else:
            print("connection does not exist. add")
            connections.add_connection(pkt)

        print(pkt.show())
        # print(str(pkt.summary()))
        count.incr_count()
        current_count = count.get_count()
        print("packet count: " + str(current_count))

        # packet.accept()
        if b"drop-header: true" in pkt[Raw].load:
            print("drop header == true. Dropping packet")
            connections.drop_packet(pkt)
            packet.drop()
        elif b"modify-header: true" in pkt[Raw].load:
            print("modify packet!")
            new_pkt = modify_packet(pkt)
            del new_pkt[IP].chksum
            del new_pkt[TCP].chksum
            packet.set_payload(bytes(new_pkt))
            packet.accept()
        else:
            packet.accept()
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