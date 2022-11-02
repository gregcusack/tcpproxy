from dataclasses import replace
from scapy.all import *

class MutablePacket:
    def __init__(self, pkt):
        self.pkt = pkt
        self.orig_IP_len = pkt[IP].len

        if Raw in pkt:
            self.orig_load_len = len(pkt[Raw].load)
        else:
            self.orig_load_len = 0

        self.ack_num = pkt[TCP].ack
        self.seq_num = pkt[TCP].seq

        self.been_modified = False
        self.diff = 0
        self.new_IP_len = 0

        self.replacement_load_eq_len = b"GET /mirror/greg/bruh HTTP/1.1\r\nHost: 192.168.1.211:8000\r\nUser-Agent: curl/7.79.1\r\nAccept: */*\r\nmodify-header: true\r\n\r\n"
        self.replacement_load_diff_len = b"GET /mirror/g/b HTTP/1.1\r\nHost: 192.168.1.211:8000\r\nUser-Agent: curl/7.58.0\r\nAccept: */*\r\nmodify-header: shrink\r\n\r\n"
        # self.replacement_load_eq_len = b"GET /mirror/greg/bruh HTTP/1.1\r\nHost: 192.168.1.211:8000\r\nUser-Agent: curl/7.79.1\r\nAccept: */*\r\nmodify-header: true\r\n\r\n"
        # self.replacement_load_diff_len = b"GET /mirror/greg/bob HTTP/1.1\r\nHost: 192.168.1.23:8000\r\nUser-Agent: curl/7.58.0\r\nAccept: */*\r\nmodify-header: shrink\r\n\r\n"
        # self.replacement_load_diff_len = b"GET /mirror/g/b HTTP/1.1\r\nHost: 192.168.1.211:8000\r\nUser-Agent: curl/7.58.0\r\nAccept: */*\r\nmodify-header: shrink\r\n\r\n"

    def is_modified(self):
        return self.been_modified

    def set_modified(self):
        self.been_modified = True

    def ack(self):
        return self.ack_num
    
    def seq(self):
        return self.seq_num

    def packet(self):
        return self.pkt

    def payload_len_diff(self):
        return self.diff

    def incr_ack(self, amnt):
        self.set_modified()
        self.ack_num += amnt
        self.pkt[TCP].ack = self.ack_num

    def decr_ack(self, amnt):
        self.set_modified()
        self.ack_num -= amnt
        self.pkt[TCP].seq = self.seq_num

    def edit_payload(self, maintain_length): # pass in dict of invalid routes via **kwargs
        # print("modifying packet")
        replacement_load = self.replacement_load_eq_len
        if not maintain_length:
            replacement_load = self.replacement_load_diff_len

        load = self.pkt[Raw].load
        print(load)
        self.pkt[Raw].load = replacement_load
        print("new load")
        print(self.pkt[Raw].load)
        new_load_len = len(replacement_load)

        print("old, new load lens: " + str(self.orig_load_len) + ", " + str(new_load_len))

        if self.orig_load_len > new_load_len:
            self.diff = self.orig_load_len - new_load_len
            self.pkt[IP].len -= self.diff
        elif self.orig_load_len < new_load_len:
            self.diff = new_load_len - self.orig_load_len
            self.pkt[IP].len += self.diff

        print("Packets differ by " + str(self.diff) + " bytes")
        
        self.new_IP_len = self.pkt[IP].len

        del self.pkt[IP].chksum
        del self.pkt[TCP].chksum
        
        print(self.pkt.show())
        print("pkt post payload/len mod")
        self.set_modified()
