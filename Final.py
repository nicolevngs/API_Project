import requests
import secretos
import json
import sqlite3
from flask import Flask, render_template, request
app = Flask(__name__)

url = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/latest_stat_by_country.php"

headers = {'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com", 'x-rapidapi-key': "c027f6b238mshf6faaba00bcfb90p13274ejsn74e851405f27"}

API_KEY = 'D_F-jRYIOvFGuFFxVafOhhn59sofG5Xq3uMCu2L5VJjrbiUCreVOh6B-XOn1NSPirVP9-MawRte-MriRX810e_QeNGXL4L_ZgR7FH4tv0PEKxezngWWMBNoSwIaDXnYx'
base_url = 'https://api.yelp.com/v3/businesses/search'
base_url2 = 'https://api.yelp.com/v3/transactions/delivery/search'
headers1 = {'Authorization': f"Bearer {API_KEY}"}
FIB_CACHE = {}
CACHE_FILENAME = "cache.json"


@app.route('/Products')
def handle_products():
    conn = sqlite3.connect('final.db')
    cur = conn.cursor()

    cur.execute('SELECT * from Products as p JOIN Stores as s on p.Available_at=s.Id')

    product_list= []

    for row in cur:
        product_list.append(f'Product: {row[1]} Use for: {row[3]} Available at: {row[6]},{row[7]}')

    conn.close()

    return render_template('Products.html', product_list=product_list)


def make_request_corona(string_country):
    ''' Makes call to API
           Parameters:
           A string
           ----------
           Returns
           json from API call
           -------

           '''
    querystring = {"country": string_country}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    return response


def clean_corona(response_corona):
    ''' Cleans data from Coronavirus API call (json)
     Parameters:
     A dictionary
     ----------
     Returns
    A dict
     -------

     '''
    corona_dict = {}
    dict_from_call = response_corona['latest_stat_by_country'][0]
    corona_dict['Country'] = dict_from_call['country_name']
    corona_dict['Total Cases'] = dict_from_call['total_cases']
    corona_dict['Active Cases'] = dict_from_call['active_cases']
    corona_dict['Deaths'] = dict_from_call['total_deaths']
    corona_dict['Recovered'] = dict_from_call['total_recovered']
    return corona_dict


@app.route('/')
def index():
    return render_template('covid.html')


@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    country_name = request.form["country"]
    results = clean_corona(make_request_corona(country_name))
    return render_template('covid.html', results=results)


def handle_the_form():
    return "Form was processed"


def make_request_yelp_hospitals(string_zipcode):
    ''' Checks if url is in cache, if it isn´t it makes the API call and saves url in cache for call
        (through function)
            Parameters:
            A string (zipcode)
            ----------
            Returns
            -------
            json from Yelp API call
            '''
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
    ''' Cleans the list of dicts to extract the desired information only
            Parameters:
            A list of dicts
            ----------
            Returns:
            A list
            -------

            '''
    hospitals_list = []
    print(response_hospitals)
    for hospitals_dict in response_hospitals['businesses']:
        dict_hosp = {}
        dict_hosp['Hospital'] = hospitals_dict['name']
        dict_hosp['Website'] = hospitals_dict['url']
        dict_hosp['Phone'] = hospitals_dict['display_phone']
        dict_hosp['Address'] = hospitals_dict["location"]['display_address'][0]
        hospitals_list.append(dict_hosp)
    return hospitals_list


def make_request_yelp_stayhome(string_zipcode):
    ''' Checks if url is in cache, if it isn´t it makes the API call and saves url in cache for call
    (through function)
        Parameters:
        A string (zipcode)
        ----------
        Returns
        -------
        json from Yelp API call
        '''
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
    ''' Cleans the list of dicts to extract the desired information only
        Parameters:
        A list of dicts
        ----------
        Returns:
        A list
        -------

        '''
    restaurant_list = []
    for restaurant_dict in response_stayhome['businesses'][:10]:
        dict_rest = {}
        dict_rest['Name'] = restaurant_dict['name']
        dict_rest['Website'] = restaurant_dict['url']
        dict_rest['Phone Number'] = restaurant_dict['display_phone']
        restaurant_list.append(dict_rest)
    return restaurant_list


@app.route('/symptoms')
def symptoms():
    return render_template('symptoms.html')


@app.route('/handle_symptoms', methods=['POST'])
def handle_symptoms():
    answer = request.form["choice"]
    return render_template('symptoms.html', answer=answer)


@app.route('/handle_restaurants', methods=['POST'])
def handle_restaurants():
    zipcode = request.form["zipcoderes"]
    results_res = clean_restaurants(make_request_yelp_stayhome(zipcode))
    return render_template('restaurants.html', results_res=results_res)


@app.route('/handle_hospitals', methods=['POST'])
def handle_hospitals():
    zipcode_hospital = request.form["zipcodehosp"]
    results_hos = clean_hospitals(make_request_yelp_hospitals(zipcode_hospital))
    return render_template('hospitals.html', results_hos=results_hos)


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
    app.run(debug=True)

