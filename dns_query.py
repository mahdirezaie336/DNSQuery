import socket
import binascii
import main


class DNSQuery:

    def __init__(self, address, query_id = b'\xee\xee'):
        self.address = address
        self.id = query_id
        self.fields = ['0',         # QR
                       '0000',      # OPCODE
                       '0',         # AA
                       '0',         # TC
                       '1',         # RD
                       '0',         # RA
                       '000',       # Z
                       '0000'       # RCODE
                       ]

    def get_message(self):



dns_server = '1.1.1.1'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(binascii.unhexlify('aaaa010000010000000000000667697468756203636f6d0000010001'), (dns_server, 53))
data, _ = s.recvfrom(4096)
print(main.decode_message(binascii.hexlify(data).decode('utf-8')))
