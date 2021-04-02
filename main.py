from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('1.1.1.1')
query = DNSQuery('ping.eu')
handler.send_message(query)
handler.print_response()
print(handler.response)
