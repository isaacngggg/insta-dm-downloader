import requests


def get_price(originSkyId, destinationSkyId, fromDate, currency):
	url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/getPriceCalendar"

	querystring = {"originSkyId":originSkyId,"destinationSkyId":destinationSkyId,"fromDate":fromDate,"currency":currency}

	headers = {
		"x-rapidapi-key": "7e763f9b31msh9ef6b7764a09cf9p11b068jsn02e91daac3e8",
		"x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)

	# print(response.json())

	return response.json()['data']['flights']['days']