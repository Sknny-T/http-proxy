import netfilterqueue
from scapy.all import *
import regex as re
import gzip
import io
import subprocess
import time
import os
import folder_search
import config
import psycopg2
import sql


iprule = subprocess.Popen(["iptables", "-t", "mangle", "-A", "POSTROUTING", "-p", "tcp", "--dport", "80",
                           "-j", "NFQUEUE"], stdout=subprocess.PIPE)
iprule = subprocess.Popen(["iptables", "-t", "mangle", "-A", "POSTROUTING", "-p", "tcp", "-s", config.server_IP,
                           "-j", "NFQUEUE"], stdout=subprocess.PIPE)
iprule_rst = subprocess.Popen(["iptables", "-A", "OUTPUT", "-p", "tcp", "--tcp-flags", "RST", "RST",
                               "-j", "DROP"], stdout=subprocess.PIPE)

iprule = subprocess.Popen(["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "DNAT",
                           "--to-destination", config.server_IP + ":80"])
iprule = subprocess.Popen(["iptables", "-t", "nat", "-A", "POSTROUTING", "-d", config.server_IP + "/32" ,"-p", "tcp",
                           "-m", "tcp", "--dport", "80", "-j", "SNAT", "--to-source", config.proxy_IP])

print('Connecting to the PostgreSQL database...')
conn = psycopg2.connect(
    host=config.sql_server_ip,
    database=config.sql_database,
    user=config.sql_user,
    password=config.sql_password)

cur = conn.cursor()


class Proxy:

    fake_ack = None
    in_list = []
    pkt_path = []


    def gzip_str(self, str):
        output = io.BytesIO()

        with gzip.GzipFile(fileobj= output, mode= "w") as fo:
            fo.write(str)

        bytes_obj = output.getvalue()
        return bytes_obj

    def get_http_path(self, pkt):
        load_layer("http")
        packet = IP(pkt.get_payload())
        if HTTPRequest in packet:
            path = ((packet[HTTP].Path).decode("utf-8"))
            path = path[1 : : ]
            return path

    def check_path(self, pkt):
        path = self.get_http_path(pkt)
        if path is not None:
            path = path.rsplit("/", 1)[-1]
        if any(path in sublist for sublist in config.page_list):
            self.in_list.append("1")
            self.pkt_path.append(self.get_http_path(pkt))
            return True
        else:
            return False

    def is_status_404(self, pkt):
        status_code = pkt[HTTP].Status_Code
        status_code = status_code.decode("utf-8")
        if status_code == "404":
            return True

    def send_ack_to_server(self, pkt):
        ack_to_server = IP(dst=config.server_IP) / TCP(seq=pkt.ack, ack=pkt.seq + 22, dport=pkt.sport, sport=pkt.dport,
                                                       flags='A')
        send(ack_to_server)

    def change_payload(self, pkt, load, content_type):
        if pkt.haslayer(Raw):
            pkt[Raw].load = load
        pkt[HTTP].Status_Code = '200'
        pkt[HTTP].Reason_Phrase = 'OK'
        pkt[HTTP].Content_Encoding = "gzip, deflate"
        del pkt[IP].flags
        del pkt[IP].src
        del pkt[IP].len
        del pkt[IP].chksum
        del pkt[TCP].chksum
        pkt[HTTP].Content_Length = str(len(load))
        pkt[HTTP].Content_Type = content_type
        return pkt

    def send_fin_ack_to_usr(self,clt_IP, pkt, new_packet):
        ip_total_len = len(new_packet[IP])
        ip_header_len = new_packet[IP].ihl * 32 // 8
        tcp_header_len = new_packet[TCP].dataofs * 32 // 8
        tcp_seg_len = ip_total_len - ip_header_len - tcp_header_len
        fin_ack_clt = IP(dst=clt_IP) / TCP(seq=pkt.seq + tcp_seg_len, ack=pkt.ack,
                                           dport=pkt.dport, sport=pkt.sport, flags='FA')
        time.sleep(0.05)
        send(fin_ack_clt)

    def check_creds(self, raw, clt_IP):
        if "Username=admin&Password=password" in raw:
            cur.execute("insert into Proxy_Log(packet_path, client_ip, module, note, type) Values('"
                        + self.pkt_path[0] + "'," + "'" + clt_IP + "'," + "'HTTP_Proxy',"
                        + "'Credentials: admin:password'," + "'Warning'" + ")")
            conn.commit()
            print("------------------------------ALERT--------------------------------")
            print("                 LEAKED CREDENTIALS WERE USED!")
            print("-------------------------------------------------------------------")

    def get_raw(self, pkt):
        http_packet = IP(pkt.get_payload())
        load = http_packet[Raw].load
        load = load.decode("utf-8")
        return load

    def send_new_packet(self, pkt, http_packet, clt_IP):
        self.send_ack_to_server(http_packet)
        pkt.drop()
        new_packet = self.build_new_packet(http_packet)
        send(new_packet)
        cur.execute("insert into Proxy_Log(packet_path, client_ip, module, note, type) Values('"
                    + self.pkt_path[0] + "'," + "'" + clt_IP + "'," + "'HTTP_Proxy',"
                    + "'Interaction with Proxy'," + "'Alert'" + ")")
        conn.commit()
        self.send_fin_ack_to_usr(clt_IP, http_packet, new_packet)
        del self.in_list[0]
        del self.pkt_path[0]

    def build_new_packet(self, pkt):
        if ".png" in self.pkt_path[0]:
            f = open(config.websites_path + self.pkt_path[0], "rb")
            injection_code = f.read()
        else:
            f = open(config.websites_path + self.pkt_path[0], "r")
            injection_code = f.read()
        if ".png" not in self.pkt_path[0]:
            injection_code = str.encode(injection_code)
        if "home.html" in self.pkt_path[0]:
            if pkt.haslayer(Raw):
                raw = pkt[Raw].load
                raw = raw.decode("utf-8")
                injection_code = raw.replace("</body>", "<!-- Login credentials for login.php only for debugging, please "
                                                        "remove before deployment: User: admin // Password: password "
                                                        "-->\n</body>")
                injection_code = str.encode(injection_code)
        gzip_load = self.gzip_str(injection_code)
        if ".png" in self.pkt_path[0]:
            new_packet = self.change_payload(pkt, gzip_load, "image/png")
        elif ".css" in self.pkt_path[0]:
            new_packet = self.change_payload(pkt, gzip_load, "text/css")
        else:
            new_packet = self.change_payload(pkt, gzip_load, "text/html")
        self.fake_ack = new_packet[IP].ack
        return new_packet

    def inject_code(self, pkt):
        load_layer("http")
        http_packet = IP(pkt.get_payload())
        clt_IP = http_packet[IP].dst
        if http_packet.haslayer(HTTPRequest):
            self.check_path(pkt)
        if http_packet.haslayer(HTTPResponse):
            #load = self.get_raw(pkt)
            if http_packet[IP].src == config.server_IP and self.in_list:
                self.send_new_packet(pkt, http_packet, clt_IP)
            else:
                pkt.accept()
        elif http_packet.haslayer(HTTPRequest) and http_packet.haslayer(Raw):
            self.check_creds(self.get_raw(pkt), http_packet[IP].src)
            pkt.accept()
        else:
            pkt.accept()
        return


try:
    prox = Proxy()
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, prox.inject_code)
    print("Proxy running")
    cur.execute("update module_status set http_proxy = 'on' where http_proxy like 'off' ")
    conn.commit()
    queue.run()

except KeyboardInterrupt:
    print("exit")
removeIpTables = subprocess.Popen(["iptables", "-t", "mangle", "-F"])
removeIpTables_out = subprocess.Popen(["iptables", "-F", "OUTPUT"])
removeIpTables_out = subprocess.Popen(["iptables", "-F"])
removeIpTables_out = subprocess.Popen(["iptables", "-t", "nat", "-F"])
cur.execute("update module_status set http_proxy = 'off' where http_proxy like 'on' ")
conn.commit()
cur.close()
conn.close()
