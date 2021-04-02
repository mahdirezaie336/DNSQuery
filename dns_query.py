import socket
import binascii
# from main import decode_message


class DNSQuery:

    def __init__(self, address, q_type='A', q_class=1, query_id='eeee'):
        self.header_fields = [
            '{:04x}'.format(int(query_id, 16)),           # ID
            '{:04x}'.format(int(''.join((
                '0',                                # QR
                '0000',                             # OPCODE
                '0',                                # AA
                '0',                                # TC
                '1',                                # RD
                '0',                                # RA
                '000',                              # Z
                '0000'                              # RCODE
            )), 2)),
            '{:04x}'.format(1),                    # QDCOUNT
            '{:04x}'.format(0),                    # ANCOUNT
            '{:04x}'.format(0),                    # NSCOUNT
            '{:04x}'.format(0)                     # ARCOUNT
        ]
        self.question_fields = (
            address,                                    # QNAME
            DNSQuery.get_record_type_value(q_type),       # QTYPE
            q_class                                     # QCLASS
        )

    def generate_message(self) -> str:
        """ Generates query message based on given fields into a string of hexadecimals. """
        message = ''.join(self.header_fields)

        # Adding address to the message
        address_parts = self.question_fields[0].split(".")
        for part in address_parts:
            address_len = "{:02x}".format(len(part))
            address_part = binascii.hexlify(part.encode())
            message += address_len
            message += address_part.decode()

        # Terminating bits for QNAME
        message += '00'

        # Adding QTYPE and QCLASS
        message += '{:04x}'.format(self.question_fields[1])
        message += '{:04x}'.format(self.question_fields[2])

        return message

    def __str__(self):
        return self.generate_message()

    @staticmethod
    def get_record_type_value(record_type):
        types = ["ERROR", "A", "NS", "MD", "MF", "CNAME", "SOA", "MB", "MG", "MR", "NULL", "WKS", "PTS", "HINFO",
                 "MINFO", "MX", "TXT"]

        return types.index(record_type) if isinstance(record_type, str) else types[record_type]


class DNSQueryHandler:

    def __init__(self, server_address = '1.1.1.1'):
        self.server_address = server_address
        self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, query: DNSQuery):
        self.dns_socket.sendto(binascii.unhexlify(str(message)), (self.server_address, 53))

    def get_response(self) -> :

dns_server = '1.1.1.1'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = DNSQuery('ping.eu').generate_message()
print('message is:', message)
s.sendto(binascii.unhexlify(message), (dns_server, 53))
data, _ = s.recvfrom(4096)
