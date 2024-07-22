import requests

def get_airport(location):
    url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport"

    querystring = {"query":location,"locale":"en-US"}

    headers = {
        "x-rapidapi-key": "7e763f9b31msh9ef6b7764a09cf9p11b068jsn02e91daac3e8",
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
    }   

    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    # print(response.json()['data'][0]['skyId'])

    return response.json()['data'][0]['skyId']