from dns_query import DNSQuery, DNSQueryHandler


handler = DNSQueryHandler('198.41.0.4', port=53)
query = DNSQuery('aut.ac.ir', q_type='A', rd='0')

response, res_dic = handler.send_single_request(query)

for key in res_dic:
    print(key, ': ', res_dic[key])
