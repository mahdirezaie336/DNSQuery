#!/usr/bin/env python3

from dns_query import DNSQuery, DNSQueryHandler
from cache import load_cache_from_file, save_cache_to_file
import sys


args = sys.argv
if len(args) > 1:
    name_address = args[1]
else:
    name_address = 'aut.ac.ir'

if len(args) > 2:
    port_number = int(args[2])
else:
    port_number = 53

load_cache_from_file()
try:
    handler = DNSQueryHandler('198.41.0.4', port=port_number)
    query = DNSQuery(name_address, q_type='A', rd='0')

    response, res_dic = handler.send_query(query, is_iterative=True)

    for key in res_dic:
        print(key, ': ', res_dic[key])
finally:
    save_cache_to_file()

print('\n*******************\nResponse:', response)
