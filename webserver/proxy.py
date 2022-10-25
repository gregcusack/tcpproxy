from netfilterqueue import NetfilterQueue
from scapy.all import *
from scapy.layers.http import HTTPRequest
import os

def setup():
    QUEUE_NUM = 1 
    # insert the iptables FORWARD rule
    os.system("iptables -I INPUT -p tcp --dport 5000 -j NFQUEUE --queue-num {}".format(QUEUE_NUM))



def new_packet(packet):
    print("suhh")
    pkt = IP(packet.get_payload())
    print(pkt.show())
    packet.accept()



def main():
    setup()
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