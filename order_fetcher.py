import os
from dotenv import load_dotenv
import time
import threading
from datetime import datetime
from binance import Client
import websocket
import json


# Replace YOUR_API_KEY and YOUR_API_SECRET with your Binance API credentials
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

# Initialize the Binance client
client = Client(api_key, api_secret)

def get_average_hourly_volume(pair):
    # Get the timestamp for one week ago
    start_time = int((time.time() - 7 * 24 * 3600) * 1000)
    
    # Get the klines (candlestick data) for the past week with 1-hour interval
    klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, start_time)

    # Calculate the total volume for the past week
    total_volume = sum(float(kline[5]) for kline in klines)

    # Calculate the average hourly volume for the past week
    average_hourly_volume = total_volume / (7 * 24)  # 7 days * 24 hours/day
    
    return average_hourly_volume

def check_orderbook_change(pair, price, initial_price, initial_time, average_hourly_volume):
    # Check if the price is within +/- 0.5% of the initial limit order price
    if (price >= 1.005 * initial_price) or (price <= 0.995 * initial_price):
        # Check if the order has been on the order book for at least one hour
        if (time.time() - initial_time) >= 3600:
            # Check if the order size is at least 1/6 of the average hourly volume
            order_size = 1 / 6 * average_hourly_volume
            if float(orders['asks'][0][1]) >= order_size:
                print(f"{datetime.now()} - Pair: {pair}, Price: {price} USDT")

def on_message(ws, message):
    # print(message)
    try:
        data = json.loads(message)
        print(data)
        if 'stream' in data:
            # Extract the symbol and update event data
            pair = data['stream'].split('@')[0]
            update_data = data['data']

            # Check if the update is on the order book and get the first ask price
            if update_data['e'] == 'depthUpdate' and update_data['a']:
                price = float(update_data['a'][0][0])
                index = top_30_usdt_pairs.index(pair)
                initial_limit_order_price = closing_prices[index]
                average_hourly_volume = get_average_hourly_volume(pair)
                check_orderbook_change(pair, price, initial_limit_order_price, initial_limit_order_time, average_hourly_volume)

    except Exception as e:
        print(f"Error occurred: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Function to handle WebSocket connection close
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

# Function to handle WebSocket connection open
def on_open(ws):
    print(f"WebSocket opened for Pair: {ws.pair}")
    
    # Send the subscribe string after the connection is open
    payload = {
        "method": "SUBSCRIBE",
        "params": [f'{ws.pair}@depth5'],
        "id": 1
    }
    ws.send(json.dumps(payload))

def ws_thread(pair):
    # Websocket URL for the trading pair's order book
    ws_url = f"wss://stream.binance.com:9443/ws/{pair}@depth5"

    # Establish websocket connection
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_open=on_open,  # Use lambda to pass the pair to on_open
                                on_close=on_close)

     # Store the pair information in the WebSocketApp object
    ws.pair = pair

    # Start listening to the websocket messages
    ws.run_forever()


if __name__ == "__main__":
    try:
        top_30_usdt_pairs = ['btcusdt', 'ethusdt', 'bnbusdt']

        for pair in top_30_usdt_pairs:
            thread = threading.Thread(target=ws_thread, args=(pair,), daemon=True)
            thread.start()

        # Rest of your main code...
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Script stopped by the user.")
