"""API functionality for Reservoir"""

import os
import sys
import requests




RESERVOIR_HOSTED_ENDPOINT = "https://api.reservoir.tools/"

RESERVOIR_API_KEY = os.environ["RES_API_KEY"]

def make_singular_call_to_asks_endpoint(collection_address, session_object, continuation_token=None):
    """Used to make continuous calls to fetch asll assets of a collection.
       No continuation token is used on the first call; only subsequent calls.
    """

    asks_endpoint = "orders/asks/v2"
    full_url = RESERVOIR_HOSTED_ENDPOINT + asks_endpoint

    payload = {
        "contracts" : collection_address,
        "includePrivate" : False,
        "sortBy" : "createdAt",
        "limit" : 1000
    }

    if continuation_token:
        payload.update({"continuation" : continuation_token})

    #Make Call
    r = session_object.get(full_url, params=payload)

    if r.status_code == 200:
        print("Good call in call to 'make_singular_call_to_asks_endpoint'")
        return r.json()

    else:
        print("Bad return code in call to 'make_singular_call_to_asks_endpoint'")
        print(f"Code returned: {r.status_code}")
        print(f"Data returned: {r.json()}")
        return None

def find_token_id_from_token_set_id(token_set_id):
    text_split = token_set_id.split(':')
    token_id = text_split[-1]
    return token_id

def unpack_asks_call_result_and_return_continuation_token(response_data, pricing_data_dict):
    temp_dict = {}

    response_orders = response_data["orders"]

    for order in response_orders:
        order_price = order["price"]
        #try:
        #    token_id = order["rawData"]["offer"]["identifierOrCriteria"]

        #except KeyError:
        token_id = find_token_id_from_token_set_id(order["tokenSetId"])

        temp_dict[token_id] = order_price

    pricing_data_dict.update(temp_dict)

    continuation_token = response_data["continuation"]

    return continuation_token
    
def fetch_asks_for_collection(collection_address, session_object):
    pricing_data = {}

    first_call = make_singular_call_to_asks_endpoint(collection_address, session_object)

    c_token = unpack_asks_call_result_and_return_continuation_token(first_call, pricing_data)

    print(f"Continuation_token: {c_token}")

    end_of_collection_found = False

    while not end_of_collection_found:
        next_call = make_singular_call_to_asks_endpoint(collection_address, session_object, continuation_token=c_token)
        c_token = unpack_asks_call_result_and_return_continuation_token(next_call, pricing_data)

        print(f"Continuation_token: {c_token}")

        if c_token is None:
            end_of_collection_found = True
            print("All collection data retrieved")

    #Sort dict
    #sorted_asks = {key:value for key, value in sorted(pricing_data.items(), key=lambda item:item[1])}
    #return sorted_asks

    return pricing_data

def test_return_asset_by_token(collection_address, token_id, session_object):
    asks_endpoint = "orders/asks/v2"
    full_url = RESERVOIR_HOSTED_ENDPOINT + asks_endpoint

    payload = {
        "token" : collection_address + ':' + token_id,
        "includePrivate" : False,
        "sortBy" : "createdAt",
        "limit" : 1000
    }

    #Make Call
    r = session_object.get(full_url, params=payload)

    if r.status_code == 200:
        print("Good call in call to 'make_singular_call_to_asks_endpoint'")
        return r.json()

    else:
        print("Bad return code in call to 'make_singular_call_to_asks_endpoint'")
        print(f"Code returned: {r.status_code}")
        print(f"Data returned: {r.json()}")
        return None


if __name__ == "__main__":
    session = requests.Session()
    session.headers = {"x-api-key" : RESERVOIR_API_KEY}

    if len(sys.argv) < 2:
        print("No argument provided for 'collection_address'.  Use 'python reservoir.py <collection_address>'")
        sys.exit(0)

    else:
        collection_address = sys.argv[1]

    
    pricing_data = fetch_asks_for_collection(collection_address, session)
    print(pricing_data['1136'])
    

    #token_id = '1136'
    #r = test_return_asset_by_token(collection_address, token_id, session)
    #print(r)
