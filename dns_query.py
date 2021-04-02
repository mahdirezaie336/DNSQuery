import socket
import binascii
# from main import decode_message
from collections import OrderedDict


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
        self.response = None

    def send_message(self, query: DNSQuery):
        msg = query.generate_message()
        msg = msg.replace(" ", "").replace("\n", "")
        self.dns_socket.sendto(binascii.unhexlify(msg), (self.server_address, 53))
        self.response, _ = self.dns_socket.recvfrom(4096)

    def print_response(self):
        if self.response is None:
            print('You had not still send a request.')
            return
        message = binascii.unhexlify(self.response).decode('utf-8')
        res = []

        ID = message[0:4]
        query_params = message[4:8]
        QDCOUNT = message[8:12]
        ANCOUNT = message[12:16]
        NSCOUNT = message[16:20]
        ARCOUNT = message[20:24]

        params = "{:b}".format(int(query_params, 16)).zfill(16)
        QPARAMS = OrderedDict([
            ("QR", params[0:1]),
            ("OPCODE", params[1:5]),
            ("AA", params[5:6]),
            ("TC", params[6:7]),
            ("RD", params[7:8]),
            ("RA", params[8:9]),
            ("Z", params[9:12]),
            ("RCODE", params[12:16])
        ])

        # Question section
        QUESTION_SECTION_STARTS = 24
        question_parts = DNSQueryHandler.parse_parts(message, QUESTION_SECTION_STARTS, [])

        QNAME = ".".join(map(lambda p: binascii.unhexlify(p).decode(), question_parts))

        QTYPE_STARTS = QUESTION_SECTION_STARTS + (len("".join(question_parts))) + (len(question_parts) * 2) + 2
        QCLASS_STARTS = QTYPE_STARTS + 4

        QTYPE = message[QTYPE_STARTS:QCLASS_STARTS]
        QCLASS = message[QCLASS_STARTS:QCLASS_STARTS + 4]

        res.append("\n# HEADER")
        res.append("ID: " + ID)
        res.append("QUERYPARAMS: ")
        for qp in QPARAMS:
            res.append(" - " + qp + ": " + QPARAMS[qp])
        res.append("\n# QUESTION SECTION")
        res.append("QNAME: " + QNAME)
        res.append("QTYPE: " + QTYPE + " (\"" + DNSQuery.get_record_type_value(int(QTYPE, 16)) + "\")")
        res.append("QCLASS: " + QCLASS)

        # Answer section
        ANSWER_SECTION_STARTS = QCLASS_STARTS + 4

        NUM_ANSWERS = max([int(ANCOUNT, 16), int(NSCOUNT, 16), int(ARCOUNT, 16)])
        if NUM_ANSWERS > 0:
            res.append("\n# ANSWER SECTION")

            for ANSWER_COUNT in range(NUM_ANSWERS):
                if (ANSWER_SECTION_STARTS < len(message)):
                    ANAME = message[ANSWER_SECTION_STARTS:ANSWER_SECTION_STARTS + 4]  # Refers to Question
                    ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]
                    ACLASS = message[ANSWER_SECTION_STARTS + 8:ANSWER_SECTION_STARTS + 12]
                    TTL = int(message[ANSWER_SECTION_STARTS + 12:ANSWER_SECTION_STARTS + 20], 16)
                    RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                    RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]

                    if ATYPE == DNSQuery.get_record_type_value("A"):
                        octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]
                        RDDATA_decoded = ".".join(list(map(lambda x: str(int(x, 16)), octets)))
                    else:
                        RDDATA_decoded = ".".join(
                            map(lambda p: binascii.unhexlify(p).decode('iso8859-1'),
                                DNSQueryHandler.parse_parts(RDDATA, 0, [])))

                    ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)

                try:
                    ATYPE
                except NameError:
                    None
                else:
                    res.append("# ANSWER " + str(ANSWER_COUNT + 1))
                    res.append("QDCOUNT: " + str(int(QDCOUNT, 16)))
                    res.append("ANCOUNT: " + str(int(ANCOUNT, 16)))
                    res.append("NSCOUNT: " + str(int(NSCOUNT, 16)))
                    res.append("ARCOUNT: " + str(int(ARCOUNT, 16)))

                    res.append("ANAME: " + ANAME)
                    res.append("ATYPE: " + ATYPE + " (\"" + DNSQuery.get_record_type_value(int(ATYPE, 16)) + "\")")
                    res.append("ACLASS: " + ACLASS)

                    res.append("\nTTL: " + str(TTL))
                    res.append("RDLENGTH: " + str(RDLENGTH))
                    res.append("RDDATA: " + RDDATA)
                    res.append("RDDATA decoded (result): " + RDDATA_decoded + "\n")

        return "\n".join(res)

    @staticmethod
    def parse_parts(message, start, parts):
        part_start = start + 2
        part_len = message[start:part_start]

        if len(part_len) == 0:
            return parts

        part_end = part_start + (int(part_len, 16) * 2)
        parts.append(message[part_start:part_end])

        if message[part_end:part_end + 2] == "00" or part_end > len(message):
            return parts
        else:
            return DNSQueryHandler.parse_parts(message, part_end, parts)


dns_server = '1.1.1.1'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = DNSQuery('ping.eu').generate_message()
print('message is:', message)
s.sendto(binascii.unhexlify(message), (dns_server, 53))
data, _ = s.recvfrom(4096)
