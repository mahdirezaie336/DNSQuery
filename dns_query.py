import socket
import binascii
import csv


class DNSQuery:
    types = ["ERROR", "A", "NS", "MD", "MF", "CNAME", "SOA", "MB", "MG", "MR", "NULL", "WKS", "PTR", "HINFO",
             "MINFO", "MX", "TXT", 'RP', 'AFSDB', 'X25', 'ISDN', 'RT', 'NSAP', 'NSAP-PTR', 'SIG', 'KEY', 'PX',
             'GPOS', 'AAAA']  # From Wikipedia

    def __init__(self, address, q_type='A', q_class=1, query_id='eeee', rd='0'):
        self.header_fields = [
            '{:04x}'.format(int(query_id, 16)),  # ID
            '{:04x}'.format(int(''.join((
                '0',  # QR
                '0000',  # OPCODE
                '0',  # AA
                '0',  # TC
                rd,  # RD
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

        return message.replace(" ", "").replace("\n", "")

    def __str__(self):
        return self.generate_message()

    @staticmethod
    def get_record_type_value(record_type):
        return DNSQuery.types.index(record_type) if isinstance(record_type, str) else DNSQuery.types[record_type]


class DNSQueryHandler:

    def __init__(self, server_address='1.1.1.1', port=53):
        self.server_address = (server_address, port)
        self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_single_request(self, query: DNSQuery) -> (str, dict):
        """ Sends a single dns query.
            :returns response as a dictionary and RDData as a string.
            :param query A DNSQuery object to send to DNS server.
            """

        response = self.send_udp_message(query.generate_message())
        response_dict = self.decode_message(response)

        # Extracting RDDATA
        try:
            rd_data = response_dict['Answer'][0]['RDDATA_DECODED']
        except IndexError:
            rd_data = 'No answer'

        return rd_data, response_dict

    def send_iterative_query(self, query: DNSQuery) -> (str, dict):
        """ Sends an iterative query. """

        temp = self.server_address
        # query.header_fields[6] = '0'  # set RD to 0
        response, res_dict = self.send_single_request(query)

        # Searching for host ip
        try:
            while res_dict['ANCOUNT'] == 0 and res_dict['ARCOUNT'] != 0:
                print('Here')
                for additional_item in res_dict['Additional']:
                    if additional_item['A_TYPE'] == 'A':
                        self.server_address = (additional_item['RDDATA_DECODED'], 53)
                        response, res_dict = self.send_single_request(query)
                        break
        finally:
            self.server_address = temp

        # When not found
        if res_dict['ANCOUNT'] == 0:
            raise Exception('Can not resolve address', res_dict['QNAME'])

        return response, res_dict

    def send_multi_requests(self, source_file_address: str, destination_file_address: str) -> None:
        """ Reads source csv file and sends queries to DNS server.
            The csv file columns must be like this:

                No.     Destination Address     Type    DNS Server

            e.g: 1,ping.eu,A,1.1.1.1
            """

        result = [("No.", "AType", "TTL", "RDData")]

        # Reading queries from source csv file
        with open(source_file_address, 'r') as csv_in:
            for row in csv.reader(csv_in):
                if row[0] == "No.":
                    continue
                query = DNSQuery(row[1], q_type=row[2], query_id=row[0])
                _, res_dic = self.send_single_request(query)
                result.append((row[0], res_dic['ATYPE'], res_dic['TTL'], res_dic['RDDATA_DECODED']))

        # Saving queries result into destination address
        with open(destination_file_address, 'w') as csv_out:
            obj = csv.writer(csv_out, )
            for item in result:
                obj.writerow(item)

    def send_udp_message(self, msg: str) -> str:
        """ Sends a udp message which is in hexadecimal format inside a string.
            :returns udp response in hexadecimal format inside a string
            """

        self.dns_socket.sendto(binascii.unhexlify(msg), self.server_address)
        data, _ = self.dns_socket.recvfrom(4096)

        return binascii.hexlify(data).decode('utf-8')

    def decode_message(self, message: str) -> dict:
        """ Decodes a dns query inside a string in hexadecimal format.
            :returns Decoded message in a dictionary
            """

        # Decoding header section
        result = {'Response RAW': message,
                  'ID': (ID := message[0:4]) + ': ' + str(int(message[0:4], 16)),
                  'QUERY_PARAMS': '{:016b}'.format(int(message[4:8], 16)),
                  'QDCOUNT': (qd_count := int(message[8:12], 16)),
                  'ANCOUNT': (an_count := int(message[12:16], 16)),
                  'NSCOUNT': (ns_count := int(message[16:20], 16)),
                  'ARCOUNT': (ar_count := int(message[20:24], 16))}

        # Decoding question section
        q_name_parts = DNSQueryHandler.parse_parts(message, 24, [])
        offset = 26 + (len("".join(q_name_parts))) + (len(q_name_parts) * 2)
        q_type = message[offset: (offset := offset + 4)]
        q_class = message[offset: (offset := offset + 4)]

        result['QNAME'] = q_name_parts
        result['QNAME_DECODED'] = '.'.join([binascii.unhexlify(x).decode() for x in q_name_parts])
        result['QTYPE'] = DNSQuery.get_record_type_value(int(q_type, 16))
        result['QCLASS'] = int(q_class, 16)

        # Decoding answer section
        for section in (sections := {'Answer': an_count, 'Authority': ns_count, 'Additional': ar_count}):

            result[section] = []
            if sections[section] > 0:

                for i in range(sections[section]):

                    res = {}

                    if offset < len(message):

                        a_name = message[offset: (offset := offset + 4)]
                        a_type = message[offset: (offset := offset + 4)]
                        a_class = message[offset: (offset := offset + 4)]
                        TTL = int(message[offset: (offset := offset + 8)], 16)
                        rd_length = int(message[offset: (offset := offset + 4)], 16)
                        rd_data = message[offset: (offset := offset + (rd_length * 2))]

                        if int(a_type, 16) == DNSQuery.get_record_type_value('A'):
                            octets = [rd_data[i:i + 2] for i in range(0, len(rd_data), 2)]
                            RDDATA_decoded = '.'.join(str(int(x, 16)) for x in octets)
                        else:
                            RDDATA_decoded = '.'.join(binascii.unhexlify(p).decode('iso8859-1') for p in
                                                      self.parse_parts(rd_data, 0, []))

                        # print(int(a_type, 16), rd_length, rd_data, RDDATA_decoded)
                        res['A_NAME'] = a_name
                        res['A_TYPE'] = DNSQuery.get_record_type_value(int(a_type, 16))
                        res['A_CLASS'] = a_class

                        res['TTL'] = str(TTL)
                        res['RDLENGTH'] = str(rd_length)
                        res['RDDATA'] = rd_data
                        res['RDDATA_DECODED'] = RDDATA_decoded

                    result[section].append(res)

        return result

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
