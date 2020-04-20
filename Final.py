import requests
import secretos
import json

url = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/latest_stat_by_country.php"

headers = {'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com", 'x-rapidapi-key': "c027f6b238mshf6faaba00bcfb90p13274ejsn74e851405f27"}

API_KEY = 'D_F-jRYIOvFGuFFxVafOhhn59sofG5Xq3uMCu2L5VJjrbiUCreVOh6B-XOn1NSPirVP9-MawRte-MriRX810e_QeNGXL4L_ZgR7FH4tv0PEKxezngWWMBNoSwIaDXnYx'
base_url = 'https://api.yelp.com/v3/businesses/search'
base_url2 = 'https://api.yelp.com/v3/transactions/delivery/search'
headers1 = {'Authorization': f"Bearer {API_KEY}"}
FIB_CACHE = {}
CACHE_FILENAME = "cache.json"


def country_name():
    response1 = input("Write the name of the country you wish to get information on: ")
    return response1


def tellme_zipcode():
    response1 = input("We'll find restaurants near you who deliver. Tell us your zipcode: ")
    return response1


def make_request_corona(string_country):
    querystring = {"country": string_country}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    return response

def clean_corona(response_corona):
    corona_dict = {}
    dict_from_call = response_corona['latest_stat_by_country'][0]
    corona_dict['Country'] = dict_from_call['country_name']
    corona_dict['Total Cases'] = dict_from_call['total_cases']
    corona_dict['Active Cases'] = dict_from_call['active_cases']
    corona_dict['Deaths'] = dict_from_call['total_deaths']
    corona_dict['Recovered'] = dict_from_call['total_recovered']
    return corona_dict


def make_request_yelp_hospitals(string_zipcode):
    params = {
        "term": "hospitals",
        "limit": "5",
        "location": string_zipcode,
    }
    url_hospitals = requests.Request('GET', base_url, headers=headers1, params=params).prepare().url

    if url in FIB_CACHE:
        response = FIB_CACHE[url_hospitals]
    else:
        response = requests.get(base_url, headers=headers1, params=params).json()
        FIB_CACHE[url_hospitals] = response
    return response


def clean_hospitals(response_hospitals):
    hospitals_list = []
    for hospitals_dict in response_hospitals['business']:
        dict_hosp = {}
        dict_hosp['Hospital'] = hospitals_dict['name']
        dict_hosp['Website'] = hospitals_dict['url']
        dict_hosp['Phone'] = hospitals_dict['display_phone']
        dict_hosp['Address'] = hospitals_dict['display_address'][0]
        hospitals_list.append(dict_hosp)
    return hospitals_list


def make_request_yelp_stayhome(string_zipcode):
    params = {
        "location": string_zipcode,
    }
    url_stayhome = requests.Request('GET', base_url2, headers=headers1, params=params).prepare().url
    if url in FIB_CACHE:
        response = FIB_CACHE[url_stayhome]
    else:
        response = requests.get(base_url2, headers=headers1, params=params).json()
        FIB_CACHE[url_stayhome] = response
    return response


def clean_restaurants(response_stayhome):
    restaurant_list =[]
    for restaurant_dict in response_stayhome['businesses'][:10]:
        dict_rest = {}
        dict_rest['Name'] = restaurant_dict['name']
        dict_rest['Website'] = restaurant_dict['url']
        dict_rest['Phone Number'] = restaurant_dict['display_phone']
        restaurant_list.append(dict_rest)
    return restaurant_list


def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the FIB_CACHE dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()



if __name__ == "__main__":

    user_input = country_name()
    print(make_request_corona(user_input))

    user_zipcode = tellme_zipcode()
    print(make_request_yelp_stayhome(user_zipcode))

    print(make_request_yelp_hospitals(user_zipcode))


