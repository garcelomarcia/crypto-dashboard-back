# Your Server App

Welcome to Your Server App! This repository contains the server-side code for your application, including a Node.js and Express server with Socket.IO setup, as well as a Python script (`order_fetcher.py`) to fetch data from the Binance API.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Node.js and npm (Node Package Manager): [Download Node.js](https://nodejs.org/)
- Python and pip: [Download Python](https://www.python.org/downloads/)

## Installation

### Node.js and Express Server

1. Clone this repository to your local machine.

2. Open a terminal and navigate to the `server` directory:

   ```bash
   cd path/to/your-server-app/server

3. Install Node.js dependencies:
    npm install.

### Python Dependencies

1. (Optional) Create a Python virtual environment (recommended):
    python -m venv venv

2. Activate the virtual environment:
    -On Windows:
        venv\Scripts\activate
    -On macOS/Linux:
        source venv/bin/activate
3. Navigate to the 'server' directory:
    cd path/to/your-server-app/server

4. pip install -r requirements.txt

## Configuration

### Environment variables

The Node.js server and the Python script use environment variables for sensitive information, such as API keys and secrets. Follow the instructions below to configure the .env file:

1. Duplicate the .env.example file in the server directory and rename it to .env.
    cp .env.example .env

2. Open the '.env' file in atext editor and fill in the required information.

3. Replace the placeholder values with your actual API keys and secrets:
    BINANCE_API_KEY=YOUR_BINANCE_API_KEY
    BINANCE_API_SECRET=YOUR_BINANCE_API_SECRET
Ensure there are no spaces between the equal sign and the values. Replace YOUR_BINANCE_API_KEY and YOUR_BINANCE_API_SECRET with your Binance API credentials.

### Running the Server
1. To start the Node.js server, open a terminal, navigate to the 'server' directory, and run:
    npm run dev
The server will be accessible at 'http://localhost:3001'
2. The Python script will run concurrently with the server and fetch data from the Binance API. The fetched data will be emitted via WebSocket to the client-side (Next.js app) using Socket.IO.

That's it! You have successfully set up the Node.js server and Python script for your application.