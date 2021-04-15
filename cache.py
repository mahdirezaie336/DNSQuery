cache_mem = {}


def my_cache(f):
    def g(self, query) -> (str, dict):
        data = cache_mem.get(str(query), 0)
        if isinstance(data, int):  # When data is not cached
            # Sending query to server
            response, res_dic = f(self, query)
            cache_mem[str(query)] = data + 1

            # More than 3 times
            if data >= 3:
                cache_mem[str(query)] = res_dic['Response RAW']

            return response, res_dic

        else:  # When data is cached
            res_dic = self.decode_message(data)

            # Extracting RDDATA
            try:
                rd_data = res_dic['Answer'][0]['RDDATA_DECODED']
            except IndexError:
                rd_data = 'No answer'

            return rd_data, res_dic
    return g
