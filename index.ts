const express = require("express");
const http = require("http");
const dotenv = require("dotenv");
const cors = require("cors");
import db from "./db";
import { Order, Liquidation } from "./models";
import { getSocketInstance } from "./socket";
// const db = require("./db")
// const Order = require("./models")

dotenv.config();

const app = express();
app.use(
  cors({
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type"],
  })
);
const server = http.createServer(app);

const io = getSocketInstance(server);

const port = process.env.PORT || 3000;

app.get("/", (req: any, res: any) => {
  res.send("Hello World");
});

db.sync({ force: true }).then(() => {
  server.listen(port, () => {
    console.log(`Server listening on port 3001`);
  });
});

// Handle WebSocket connections
io.on("connection", async (socket: any) => {
  console.log("Client connected:", socket.id);
  // Listen for database change events from Python script
  socket.on("databaseChange", async (changeData: any) => {
    try {
      const result = await Order.findAll();
      // Broadcast the change to all connected clients
      io.emit("databaseChange", result);
    } catch (error) {
      console.error("Error fetching data from the database:", error);
    }
  });

  socket.on("liquidationsChange", async (changeData: any) => {
    try {
      const result = await Liquidation.findAll({
        order:[['id', 'DESC']],
        limit:5
      });
      // Broadcast the change to all connected clients
      io.emit("liquidationsChange", result);
    } catch (error) {
      console.error("Error fetching data from the database:", error);
    }
  });

  // Fetch data from the database
  let initialOrders;
  try {
    const result = await Order.findAll();
    initialOrders = result;
  } catch (error) {
    console.error("Error fetching data from the database:", error);
  }

  // Emit the initial database data to the connected client
  if (initialOrders) {
    socket.emit("databaseChange", initialOrders);
  }

  // Fetch data from the database
  let initialLiquidations;
  try {
    const result = await Liquidation.findAll({
      order:[['id', 'DESC']],
      limit:5
    });
    initialLiquidations = result;
  } catch (error) {
    console.error("Error fetching data from the database:", error);
  }

  // Emit the initial database data to the connected client
  if (initialLiquidations) {
    socket.emit("liquidationsChange", initialLiquidations);
  }

  // Handle client disconnection
  socket.on("disconnect", () => {
    console.log("Client disconnected:", socket.id);
  });
});
