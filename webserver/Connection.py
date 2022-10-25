import threading
from scapy.all import *

class Connection:
    # def __init__(self, src_port, dst_port, src_ip, dst_ip):
    #     self.five_tuple = FiveTuple(proto="TCP", src_port=src_port, dst_port=dst_port, \
    #         src_ip=src_ip, dst_ip=dst_ip)

    def __init__(self, pkt):
        if TCP in pkt:
            print("creating connection")
            self.five_tuple = FiveTuple(proto="TCP", src_port=pkt[TCP].sport, dst_port=pkt[TCP].dport, \
                src_ip=pkt[IP].src, dst_ip=pkt[IP].dst)
        else:
            print("TCP not in packet. can't create connection object. returning None")
            return None

        self.true_sequence_number = pkt[TCP].seq
        self.proxy_sequence_number = pkt[TCP].seq

        self.true_ack_number = pkt[TCP].ack
        self.proxy_ack_number = pkt[TCP].ack
        self.num_packets = 1

        self.packet_count_lock = threading.Lock()
        self.sequence_number_lock = threading.Lock()
        self.ack_number_lock = threading.Lock()


    def incoming_packet_update(self, pkt):
        if TCP not in pkt:
            print("Error. should not get here. ")
        self.update_packet_count()
        self.update_sequence_numbers(pkt)
        self.update_ack_numbers(pkt)


    def update_packet_count(self):
        self.packet_count_lock.acquire()
        
        self.num_packets += 1
        val = self.num_packets
        
        self.packet_count_lock.release()
        print("incr packets: " + str(val))

    def update_sequence_numbers(self, pkt):
        self.sequence_number_lock.acquire()
        
        self.true_sequence_number = pkt[TCP].seq
        self.proxy_sequence_number = pkt[TCP].seq
        
        t_seq = self.true_sequence_number
        p_seq = self.proxy_sequence_number
        
        self.sequence_number_lock.release()
        print("seq num update (true, proxy): " + str(t_seq) + ", " + str(p_seq))

    def update_ack_numbers(self, pkt):
        self.ack_number_lock.acquire()
        
        self.true_ack_number = pkt[TCP].ack
        self.proxy_ack_number = pkt[TCP].ack
        
        t_ack = self.true_ack_number
        p_ack = self.proxy_ack_number
        
        self.ack_number_lock.release()
        print("ack num update (true, proxy): " + str(t_ack) + ", " + str(p_ack))

    
    

class FiveTuple:
    def __init__(self, proto, src_port, dst_port, src_ip, dst_ip):
        self.proto = proto
        self.src_port = src_port
        self.dst_port = dst_port
        self.src_ip = src_ip
        self.dst_ip = dst_ip

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.proto == other.proto and \
            self.dst_port == other.dst_port and \
            self.src_ip == other.src_ip and \
            self.dst_ip == other.dst_ip #and \
            # self.src_port == other.src_port


    def __hash__(self):
        return hash((self.proto, self.dst_port, self.src_ip, self.dst_ip)) #,  self.src_port))
