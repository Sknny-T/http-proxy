from netfilterqueue import NetfilterQueue
from scapy.all import *
from http.client import HTTPMessage
from io import StringIO
from flask import *
import gzip
import zlib
import subprocess
import sql

iprule = subprocess.Popen(["iptables", "-t", "mangle", "-A", "POSTROUTING", "-p", "tcp", "--dport", "80",
                           "-j", "NFQUEUE"], stdout=subprocess.PIPE)
iprule_rst = subprocess.Popen(["iptables", "-A", "OUTPUT", "-p", "tcp", "--tcp-flags", "RST", "RST",
                               "-j", "DROP"], stdout=subprocess.PIPE)

class Proxy:

    in_list = None
    page_list = ["/home.html", "/bla"]

    def get_http_path(self, pkt):
        load_layer("http")
        packet = IP(pkt.get_payload())
        if HTTPRequest in packet:
            path = ((packet[HTTP].Path).decode("utf-8"))
            return(path)

    def check_path(self, pkt):
        if self.get_http_path(pkt) in self.page_list:
            self.in_list = True
            return True
        else:
            return False

    def check_source(self, pkt):
        pkt1 = IP(pkt.get_payload())
        if pkt1.src == "192.168.56.1":
            print("Server")
            return True
        else:
            return False

    def accept_or_drop(self, pkt):
        #sql.connect()
        self.check_path(pkt)
        if self.check_source(pkt) and self.in_list:
            print("------------------WORKING----------------------")
            # pkt_tst = IP(pkt.get_payload())
            # pkt_tst.src = "192.168.1.1"
            # pkt.set_payload(b'pkt_tst')
            # print(pkt_tst.show())
            # self.in_list = False
            pkt.accept()
        else:
            pkt.accept()

    def print_and_accept(self, pkt):
        load_layer("http")
        packet = IP(pkt.get_payload())
        packet.show()
        pkt.accept()

    def http_encoding(self,pkt):
        load_layer("http")
        pkt_temp = IP(pkt.get_payload())
        if HTTPRequest in pkt_temp:
            print("Request")
            pkt_request = IP(pkt.get_payload())
            pkt.drop()
            send(pkt_request)
        else:
            pkt.accept()

    def build_packet(self,server, client, site):
        pkt = IP()
        pkt.src = "192.168.53.215"
        pkt.dst = client



prox = Proxy()
nfqueue = NetfilterQueue()


nfqueue.bind(0, prox.accept_or_drop)
try:
    print("waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    print("")
nfqueue.unbind()
removeIpTables= subprocess.Popen(["iptables", "-t", "mangle", "-F"])
removeIpTables_out = subprocess.Popen(["iptables", "-F", "OUTPUT"])
