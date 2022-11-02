from functools import total_ordering
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
        self.total_packets = 0
        self.total_packets_lock = threading.Lock()

        self.peer_surplus = 0
        self.our_surplus = 0

    def __hash__(self):
        return hash(self.five_tuple)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.five_tuple == other.five_tuple

    def __repr__(self):
        return f"<Connection five_tuple:{self.five_tuple}>"

    def is_modified(self):
        return (self.peer_surplus or self.our_surplus)

    def incr_total_packets(self):
        self.total_packets_lock.acquire()
        self.total_packets += 1
        self.total_packets_lock.release()

    def get_total_packets(self):
        self.total_packets_lock.acquire()
        val = self.total_packets
        self.total_packets_lock.release()
        return val

    def packet_update(self, m_pkt):
        pkt = m_pkt.packet()
        five_tuple = FiveTuple.from_pkt(m_pkt.packet())
        print("packet_update. flow direction: " + str(five_tuple.direction))

        if five_tuple.direction == FlowDirection.outbound:
            if not self.out_flow:
                self.out_flow = Flow(pkt[TCP].seq, pkt[TCP].ack, FlowDirection.outbound)
            else:
                self.update_outbound_flow(m_pkt)
        elif five_tuple.direction == FlowDirection.inbound:
            if not self.in_flow:
                self.in_flow = Flow(pkt[TCP].seq, pkt[TCP].ack, FlowDirection.inbound)
            else:
                self.update_inbound_flow(m_pkt)
        else:
            print('error packet is not inbound or outbound')        

    def update_outbound_flow(self, m_pkt):
        self.out_flow.update_packet_count()
        if m_pkt.is_modified():
            print("outbound packet modified. update seq/ack")
            if m_pkt.payload_len_diff() > 0:
                self.our_surplus += m_pkt.payload_len_diff()
        else:
            if self.peer_surplus > 0: #deleted content received from peer, and we are responding
                print("updating ack outbound")
                m_pkt.incr_ack(self.peer_surplus)
            self.out_flow.update_sequence_numbers(m_pkt.seq())
            self.out_flow.update_ack_numbers(m_pkt.ack())
    
    def update_inbound_flow(self, m_pkt):
        self.in_flow.update_packet_count()
        if m_pkt.is_modified():
            print("packet modified inbound. update seq/ack")
            if m_pkt.payload_len_diff() > 0: # packet has been reduced in size
                print("inbound payload len diff > 0: " + str(m_pkt.payload_len_diff()))
                self.peer_surplus += m_pkt.payload_len_diff()
        else:
            if self.peer_surplus > 0: #deleted content received from peer, and we are responding
                print("updating ack inbound")
                m_pkt.incr_ack(self.peer_surplus)
            self.in_flow.update_sequence_numbers(m_pkt.seq())
            self.in_flow.update_ack_numbers(m_pkt.ack())


    def update_total_packets(self):
        self.total_packets_lock.acquire()
        self.total_packets += 1
        val = self.total_packets
        self.total_packets_lock.release()
        print("total packets in connection: " + str(val))



    