import websocket
from sqlalchemy import create_engine, Column, Integer, String, Float, Time, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from binance.client import Client
from datetime import datetime
import socketio
import os
import time

load_dotenv()

sio = socketio.Client()


api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")


client = Client(api_key, api_secret)

# Create a database engine
engine = create_engine('postgresql://postgres:password@localhost:5432/big_orders')

# Create a base class for the declarative ORM models
Base = declarative_base()

# Define the ORM model for the liquidations table
class Liquidation(Base):
    __tablename__ = 'liquidations'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)
    volume = Column(String, nullable=False)
    quantity = Column(String, nullable=False)
    time = Column(String, nullable=False)

class Liq:
    def __init__(self):
        self.socket = "wss://fstream.binance.com/ws/!forceOrder@arr"
        self.ws = websocket.WebSocketApp(self.socket, on_message=self.on_message, on_close=self.on_close)
        self.symbol: str = ""
        self.order_quantity = 0
        self.event_time: int = 0
        self.average_price: float = 0.0
        self.side = ""
        self.price: float = 0.0
        self.order_last_filled_quantity = 0.0
        self.order_filled_accumulated_quantity = 0
        self.order_trade_time: int = 0
        self.string: str= ""

    def print_result(self):
        amount = int(self.order_quantity * self.average_price)
        
        global base_url
        pair = self.symbol
        side=self.side
        quantity = self.order_quantity
        time_end = self.order_trade_time+18000000
        time_start = time_end-86400000
        time_end = str(time_end)
        time_start = str(time_start)
        bars = client.futures_historical_klines(symbol=pair , interval ='1m', start_str=time_start, end_str=time_end)
        volumes = []
        for i in range(len(bars)):
            volume = float(bars[i][5])
            h = float(bars[i][2])
            l = float(bars[i][3])
            p = abs(h+l)/2
            volume_usd = (p*volume)
            volumes.append(volume_usd)
        vol = sum(volumes)/len(volumes)
        # vol = vol/10
        order_time = str(datetime.fromtimestamp(self.order_trade_time/1000))
        # print(string)
        if amount >= vol:
            try:
                print(pair,side,amount,quantity,order_time)
                session = sessionmaker(bind=engine)()
                liquidation = Liquidation(symbol=pair, side=side, volume=amount, quantity=quantity, time=order_time)
                session.add(liquidation)
                session.commit()
                session.close()
            except Exception as e:
                print("Error occured: ", e)

            try:
                sio.connect("http://localhost:3001")
                sio.emit("liquidationsChange", "change")
                print("message sent")
                time.sleep(3)

            except Exception as e:
                print("An error occurred:", e)

            finally:
                sio.disconnect()

       
    def on_message(self, ws, message):
        """Fetch liquidation Order Streams.

        __ https://binance-docs.github.io/apidocs/futures/en/#liquidation-order-streams
        """
        for item in message.split(","):
            item = item.replace("}", "").replace("{", "").replace('"', "").replace("o:s:", "s:")
            if "forceOrder" not in item:
                _item = item.split(":")
                if _item[0] == "E":
                    self.event_time = int(_item[1])
                elif _item[0] == "s":
                    self.symbol = _item[1]
                elif _item[0] == "S":
                    self.side = _item[1]
                elif _item[0] == "q":
                    self.order_quantity = float(_item[1])
                elif _item[0] == "p":
                    self.price = _item[1]
                elif _item[0] == "ap":
                    self.average_price = float(_item[1])
                elif _item[0] == "l":
                    self.order_last_filled_quantity = _item[1]
                elif _item[0] == "z":
                    self.order_filled_accumulated_quantity = _item[1]
                elif _item[0] == "T":
                    self.order_trade_time = int(_item[1])

        self.print_result()


    def on_close(self):
        print("closed")


liq = Liq()
liq.ws.run_forever()