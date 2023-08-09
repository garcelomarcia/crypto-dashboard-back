CREATE DATABASE big_orders;
\c big_orders

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    pair VARCHAR(255) NOT NULL,
    side VARCHAR(4) CHECK (side IN ('buy', 'sell')) NOT NULL,
    strength INT NOT NULL,
    price FLOAT NOT NULL,
    distance FLOAT NOT NULL,
    time INT NOT NULL
);
