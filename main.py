from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('1.1.1.1', port=53)
query = DNSQuery('ping.eu', q_type='A')

response, res_dic = handler.send_single_request(query)
handler.send_multi_requests('./csv_template.csv', './csv_result.csv')
print(res_dic)
