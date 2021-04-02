import socket
import binascii
import main


class DNSQuery:

    def __init__(self, address, type='A', query_id='eeee'):
        self.id = query_id
        self.fields = ['0',  # QR
                       '0000',  # OPCODE
                       '0',  # AA
                       '0',  # TC
                       '1',  # RD
                       '0',  # RA
                       '000',  # Z
                       '0000'  # RCODE
        ]
        self.counts = [
            1,  # QDCOUNT
            0,  # ANCOUNT
            0,  # NSCOUNT
            0  # ARCOUNT
        ]
        self.question_field = [
            address,                                    # QNAME
            DNSQuery.get_record_type_value(type),       # QTYPE
            1                                           # QCLASS
        ]

    def get_message(self):
        pass

    @staticmethod
    def get_record_type_value(record_type):
        types = ["ERROR", "A", "NS", "MD", "MF", "CNAME", "SOA", "MB", "MG", "MR", "NULL", "WKS", "PTS", "HINFO",
                 "MINFO", "MX", "TXT"]

        return types.index(record_type) if isinstance(record_type, str) else types[record_type]


dns_server = '1.1.1.1'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(binascii.unhexlify('aaaa010000010000000000000667697468756203636f6d0000010001'), (dns_server, 53))
data, _ = s.recvfrom(4096)
print(main.decode_message(binascii.hexlify(data).decode('utf-8')))
