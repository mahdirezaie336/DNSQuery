#!/usr/bin/env python3

from dns_query import DNSQuery, DNSQueryHandler
from cache import load_cache_from_file, save_cache_to_file
import sys


args = sys.argv
if len(args) > 1:
    name_address = args[1]
else:
    name_address = 'ping.eu'

if len(args) > 2:
    query_type = args[2]
else:
    query_type = 'A'

load_cache_from_file()
try:
    handler = DNSQueryHandler('1.1.1.1', port=53)
    query = DNSQuery(name_address, q_type=query_type, rd='1')

    # handler.send_multi_requests('./csv_template.csv', './csv_result.csv')
    response, res_dic = handler.send_query(query, is_iterative=False)

    for key in res_dic:
        print(key, ': ', res_dic[key])
finally:
    save_cache_to_file()

print('\n*******************\nResponse:', response)
