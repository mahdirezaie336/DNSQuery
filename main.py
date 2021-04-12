from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('1.1.1.1', port=53)
query = DNSQuery('ping.eu', q_type='A')
handler.send_single_request(query)
print(handler.decode_message())
print(handler.response)
