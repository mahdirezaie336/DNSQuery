from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('localhost', port=16800)
query = DNSQuery('ping.eu')
handler.send_message(query)
handler.print_response()
print(handler.response)
