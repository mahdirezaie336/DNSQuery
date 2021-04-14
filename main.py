from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('1.1.1.1', port=53)
query = DNSQuery('time.ir', q_type='PTR', rd='1')

response, res_dic = handler.send_single_request(query)
for key in res_dic:
    print(key, ': ', res_dic[key])
