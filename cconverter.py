import json
import requests
import os.path
#  url sample
url = f'http://www.floatrates.com/daily/'

#  check cache function
def cache_(in_value, out_value, amount):
    u = requests.get(f'{url}usd.json')
    e = requests.get(f'{url}eur.json')
    with open('cache_usd.json', 'w') as data:
        u_str = json.dump(u.json(), data, indent=2)
    with open('cache_eur.json', 'w') as data:
        e_str = json.dump(e.json(), data, indent=2)
    if os.path.exists(f'cache_{in_value}.json'):
        with open(f'cache_{in_value}.json', 'r') as cache_file:
            cache_try = json.load(cache_file)
            return float(cache_try[f'{out_value}']['rate']) * amount
    elif os.path.exists(f'cache_{out_value}.json'):
        with open(f'cache_{out_value}.json', 'r') as cache_file:
            cache_try = json.load(cache_file)
            return float(cache_try[f'{in_value}']['inverseRate']) * amount
    else:
        return 0

#  converting values
def convert(in_value):
    while True:
        out_value = 'rub'
        if out_value == "":
            break
        else:
            amount = 1
    #  checking answer from cache_ function
            cache_try = cache_(in_value, out_value, amount)
    #  loading and processing data
            if cache_try == 0:
                # print('Sorry, but it is not in the cache!')
                r = requests.get(f'{url}{in_value}.json')
                with open('data.json', 'w') as data:
                    r_str = json.dump(r.json(), data, indent=2)
                with open('data.json', 'r') as data:
                    result_str = json.load(data)
                    result = float(result_str[f'{out_value}']['rate'])*amount
                    return (f'{round(result,2)} {out_value}.')

    #  adding info in cache file


                    with open(f'cache_{in_value}.json', 'a') as cache:

                        json.dump(result_str, cache, indent = 2)

            else:
                return (f'{round(cache_try,2)} {out_value}.')