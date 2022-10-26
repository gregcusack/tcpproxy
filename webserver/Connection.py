import threading
from scapy.all import *
from FiveTuple import FiveTuple
from Flow import Flow
from FlowDirection import FlowDirection

class Connection:

    def __init__(self, pkt):
        if TCP in pkt:
            print("creating connection")
            self.five_tuple = FiveTuple(proto="TCP", src_port=pkt[TCP].sport, dst_port=pkt[TCP].dport, \
                src_ip=pkt[IP].src, dst_ip=pkt[IP].dst)
        else:
            print("TCP not in packet. can't create connection object. returning None")
            return None

        self.out_flow = None
        self.in_flow = None 

        if self.five_tuple.direction == FlowDirection.outbound:
            self.out_flow = Flow(pkt[TCP].seq, pkt[TCP].ack, FlowDirection.outbound)
        elif self.five_tuple.direction == FlowDirection.inbound:
            self.in_flow = Flow(pkt[TCP].seq, pkt[TCP].ack, FlowDirection.inbound)
        else:
            print("ERROR. five tuple is neither in flow or outflow!") 

        self.total_packets = 1
        self.total_packets_lock = threading.Lock()

    def __hash__(self):
        return hash(self.five_tuple)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.five_tuple == other.five_tuple

    def __repr__(self):
        return f"<Connection five_tuple:{self.five_tuple}>"



    def packet_update(self, pkt):
        if TCP not in pkt:
            print("Error. should not get here. ")
        five_tuple = FiveTuple.from_pkt(pkt)
        print("packet_update. flow direction: " + str(five_tuple.direction))

        if five_tuple.direction == FlowDirection.outbound:
            if not self.out_flow:
                self.out_flow = Flow(pkt[TCP].seq, pkt[TCP].ack, FlowDirection.outbound)
            else:
                self.update_outbound_flow(pkt)
        elif five_tuple.direction == FlowDirection.inbound:
            if not self.in_flow:
                self.in_flow = Flow(pkt[TCP].seq, pkt[TCP].ack, FlowDirection.inbound)
            else:
                self.update_inbound_flow(pkt)
        else:
            print('error packet is not inbound or outbound')        

    def update_outbound_flow(self, pkt):
        self.out_flow.update_packet_count()
        self.out_flow.update_sequence_numbers(pkt[TCP].seq)
        self.out_flow.update_ack_numbers(pkt[TCP].ack)
    
    def update_inbound_flow(self, pkt):
        self.in_flow.update_packet_count()
        self.in_flow.update_sequence_numbers(pkt[TCP].seq)
        self.in_flow.update_ack_numbers(pkt[TCP].ack)


    def update_total_packets(self):
        self.total_packets_lock.acquire()
        self.total_packets += 1
        val = self.total_packets
        self.total_packets_lock.release()
        print("total packets in connection: " + str(val))



    