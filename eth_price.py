import requests

def get_ethereum_price_in_usdc():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDC"
    response = requests.get(url)
    if response.status_code <= 200:
        price = response.json().get("price")
        return float(price)
    else:
        print("Ошибка при получении данных")
        return None

price = get_ethereum_price_in_usdc()
