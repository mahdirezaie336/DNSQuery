import socket
import binascii


class DNSQuery:

    def __init__(self, address, q_type='A', q_class=1, query_id='eeee'):
        self.header_fields = [
            '{:04x}'.format(int(query_id, 16)),  # ID
            '{:04x}'.format(int(''.join((
                '0',  # QR
                '0000',  # OPCODE
                '0',  # AA
                '0',  # TC
                '1',  # RD
                '0',  # RA
                '000',  # Z
                '0000'  # RCODE
            )), 2)),
            '{:04x}'.format(1),  # QDCOUNT
            '{:04x}'.format(0),  # ANCOUNT
            '{:04x}'.format(0),  # NSCOUNT
            '{:04x}'.format(0)  # ARCOUNT
        ]
        self.question_fields = (
            address,  # QNAME
            DNSQuery.get_record_type_value(q_type),  # QTYPE
            q_class  # QCLASS
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

    def __init__(self, server_address='1.1.1.1', port=53):
        self.server_address = (server_address, port)
        self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response = None
        self.msg_len = 0

    def send_message(self, query: DNSQuery):
        msg = query.generate_message()
        msg = msg.replace(" ", "").replace("\n", "")
        self.msg_len = len(msg)
        self.dns_socket.sendto(binascii.unhexlify(msg), self.server_address)

        data, _ = self.dns_socket.recvfrom(4096)
        self.response = binascii.hexlify(data).decode('utf-8')

    def print_response(self):
        if self.response is None:
            print('You have not still send a request.')
            return
        message = self.response
        res = []

        ID = message[0:4]
        query_params = message[4:8]
        qd_count = message[8:12]
        an_count = message[12:16]
        ns_count = message[16:20]
        ar_count = message[20:24]

        # Answer section
        ANSWER_SECTION_STARTS = self.msg_len

        num_answers = max([int(an_count, 16), int(ns_count, 16), int(ar_count, 16)])
        if num_answers > 0:
            res.append("\n# ANSWER SECTION")

            for ANSWER_COUNT in range(num_answers):
                if ANSWER_SECTION_STARTS < len(message):
                    a_name = message[ANSWER_SECTION_STARTS:ANSWER_SECTION_STARTS + 4]  # Refers to Question
                    a_type = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]
                    a_class = message[ANSWER_SECTION_STARTS + 8:ANSWER_SECTION_STARTS + 12]
                    TTL = int(message[ANSWER_SECTION_STARTS + 12:ANSWER_SECTION_STARTS + 20], 16)
                    rd_length = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                    r_data = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (rd_length * 2)]

                    if int(a_type, 16) == DNSQuery.get_record_type_value("A"):
                        octets = [r_data[i:i + 2] for i in range(0, len(r_data), 2)]
                        RDDATA_decoded = ".".join(list(map(lambda x: str(int(x, 16)), octets)))
                    else:
                        RDDATA_decoded = ".".join(
                            map(lambda p: binascii.unhexlify(p).decode('iso8859-1'),
                                DNSQueryHandler.parse_parts(r_data, 0, [])))

                    ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (rd_length * 2)

                try:
                    a_type
                except NameError:
                    None
                else:
                    res.append("# ANSWER " + str(ANSWER_COUNT + 1))
                    res.append("QDCOUNT: " + str(int(qd_count, 16)))
                    res.append("ANCOUNT: " + str(int(an_count, 16)))
                    res.append("NSCOUNT: " + str(int(ns_count, 16)))
                    res.append("ARCOUNT: " + str(int(ar_count, 16)))

                    res.append("ANAME: " + a_name)
                    res.append("ATYPE: " + a_type + " (\"" + DNSQuery.get_record_type_value(int(a_type, 16)) + "\")")
                    res.append("ACLASS: " + a_class)

                    res.append("\nTTL: " + str(TTL))
                    res.append("RDLENGTH: " + str(rd_length))
                    res.append("RDDATA: " + r_data)
                    res.append("RDDATA decoded (result): " + RDDATA_decoded + "\n")

        print("\n".join(res))

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
