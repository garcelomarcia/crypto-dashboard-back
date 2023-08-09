import requests
import time
from sqlalchemy import create_engine, Column, Integer, String, Float, Time, Enum, MetaData, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
import json
import socketio

sio = socketio.Client()
# Create a database engine
engine = create_engine('postgresql://postgres:password@localhost:5432/big_orders')

# Create a base class for the declarative ORM models
Base = declarative_base()

# Define the ORM model for the orders table
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    pair = Column(String, nullable=False)
    side = Column(String, nullable=False)
    strength = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)

conn = psycopg2.connect(
        host="localhost",
        dbname="big_orders",
        user="postgres",
        password="password"
        )

# cur = conn.cursor()
# cur.execute("DROP TABLE IF EXISTS orders;")
# conn.commit()
# cur.close()
# conn.close()
# Base.metadata.create_all(engine)

@sio.event
def on_connect():
    print('Connected to server')

@sio.event
def on_disconnect():
    print('Disconnected from server')

@sio.event
def on_chat_message(data):
    print(f'Received message: {data}')

@sio.event
def on_connect_error(data):
    print(f'Connection error: {data}')


# Function to add a new entry to the table
def add_order(name, a2, raz, price, dal, tmin):
    session = sessionmaker(bind=engine)()
    side = 'buy' if a2 == 'bid' else 'sell'
    order = Order(pair=name, side=side, strength=raz, price=price, distance=dal, time=tmin)
    session.add(order)
    session.commit()
    session.close()

# Function to remove an entry from the table
def remove_order(name, a2):
    session = sessionmaker(bind=engine)()
    side = 'buy' if a2 == 'bid' else 'sell'
    order = session.query(Order).filter_by(pair=name, side=side).first()
    if order:
        session.delete(order)
        session.commit()
    session.close()

def update_order(name, a2, raz, price, dal, tmin):
    session = sessionmaker(bind=engine)()
    side = 'buy' if a2 == 'bid' else 'sell'
    try:

        order = session.query(Order).filter_by(pair=name, side=side).first()
        if order:
            order.pair = name
            order.side = side
            order.strength = raz
            order.price = price
            order.distance = dal
            order.time = tmin
            session.commit()
        else:
            print("Order not foud")
    except Exception as e:
        print("Error updating order:", e)
    finally:
        session.close()

def handle_response(response):
    return {order['id']: order for order in response if order['tmin'] > 60 and order['raz'] > 10 and order['dal'] < 1}

def make_get_request(url):
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

@sio.event
def send_message(data_array):
    # print(data_array)
    try:
        sio.connect("http://localhost:3001")
        sio.emit("databaseChange", data_array)
        print("message sent")
        time.sleep(3)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        sio.disconnect()

if __name__ == "__main__":
    url = "https://bitok.blog/screener_data_new.php"
    interval_seconds = 15  # Adjust this value based on the interval between requests

    previous_response_dict = {}

    try:

        while True:
            response_data = make_get_request(url)

            if response_data:
                current_response_dict = handle_response(response_data)
                current_response_array = list(current_response_dict.values())
                # print(current_response_array)

                if previous_response_dict:
                    # Find elements that were added and removed between the responses
                    elements_added = {id for id in current_response_dict if id not in previous_response_dict}
                    elements_removed = {id for id in previous_response_dict if id not in current_response_dict}
                    elements_same = {id for id in current_response_dict if id in previous_response_dict}

                    # Get the orders for the elements added and removed
                    added_orders = [current_response_dict[id] for id in elements_added]
                    removed_orders = [previous_response_dict[id] for id in elements_removed]
                    same_orders = [current_response_dict[id] for id in elements_same]

                    # Print the elements that were added and removed
                    # print("Elements Removed:")
                    for order in removed_orders:
                        print(f"Adding {order['id']}")
                        remove_order(name=order["name"], a2=order["a2"])

                    # print("Elements Added:")
                    for order in added_orders:
                        print(f"Removing {order['id']}")
                        add_order(name=order["name"], a2=order["a2"], raz=order["raz"], price=order["price"], dal=order["dal"], tmin=order["tmin"])

                    for order in same_orders:
                        update_order(name=order["name"], a2=order["a2"], raz=order["raz"], price=order["price"], dal=order["dal"], tmin=order["tmin"])

                    if (len(added_orders) + len(removed_orders)) > 0:
                        send_message(current_response_array)

                else:
                    for order in current_response_array:
                        add_order(name=order["name"], a2=order["a2"], raz=order["raz"], price=order["price"], dal=order["dal"], tmin=order["tmin"])
                    send_message(current_response_array)

                # Update the previous response dictionary with the current one
                previous_response_dict = current_response_dict

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("Script stopped by user.")
