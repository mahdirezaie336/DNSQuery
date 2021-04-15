from dns_query import DNSQuery, DNSQueryHandler
from cache import load_cache_from_file, save_cache_to_file

load_cache_from_file()
try:
    handler = DNSQueryHandler('198.41.0.4', port=53)
    query = DNSQuery('aut.ac.ir', q_type='A', rd='0')

    response, res_dic = handler.send_iterative_query(query)

    for key in res_dic:
        print(key, ': ', res_dic[key])
finally:
    save_cache_to_file()
