import os
from dotenv import load_dotenv
import threading
import time
from datetime import datetime, timedelta
from binance.client import Client

load_dotenv()

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

def check_orderbook_change(pair):
    try:
        print(f"Checking order book for pair: {pair}")
        start_time = int(time.time()-24*3600*1000)
        order_list = client.get_all_orders(symbol=pair)
        last_price = float(client.get_symbol_ticker(symbol=pair)['price'])
        average_hourly_volume = get_average_hourly_volume(pair)
        top_price = last_price * 1.005
        lowest_price = last_price * 0.995
        highest_ask_qty = 0
        highest_bid_qty = 0
        highest_ask_order = None  # Initialize the variable
        highest_bid_order = None  # Initialize the variable

        print(len(order_list))

        for order in order_list:  # Changed 'i' to 'order' to avoid confusion
            if float(order['origQty']) > highest_ask_qty and order['side'] == "SELL" and float(order['price']) < top_price:
                highest_ask_qty = float(order['origQty'])
                highest_ask_order = order

            if float(order['origQty']) > highest_bid_qty and order['side'] == "BUY" and float(order['price']) > lowest_price:
                highest_bid_qty = float(order['origQty'])
                highest_bid_order = order

        if highest_ask_order:            
            print(highest_ask_order)
                      
            if highest_ask_qty >= average_hourly_volume:
                print(f"{datetime.now()} - Pair: {pair}, Side: ASK, Price: {highest_ask_order['price']}, "
                      f"Quantity: {highest_ask_qty}, Order ID: {highest_ask_order['orderId']}")

        if highest_bid_order:
           
            if highest_bid_qty >= average_hourly_volume:
                print(f"{datetime.now()} - Pair: {pair}, Side: BID, Price: {highest_bid_order['price']}, "
                      f"Quantity: {highest_bid_qty}, Order ID: {highest_bid_order['orderId']}")

    except Exception as e:
        print(f"Error occurred for {pair}: {e}")

def order_checker(pair):
    while True:
        check_orderbook_change(pair)
        time.sleep(60)

if __name__ == "__main__":
    try:
        # Get the top 30 USDT trading pairs
        # top_30_usdt_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        top_30_usdt_pairs = ['BTCUSDT']


        # Start the threads for each trading pair
        for pair in top_30_usdt_pairs:
            threading.Thread(target=order_checker, args=(pair,), daemon=True).start()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Script stopped by the user.")
