from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('1.1.1.1', port=53)
query = DNSQuery('ping.eu', q_type='A')

response, res_dic = handler.send_single_request(query)
print(res_dic)
