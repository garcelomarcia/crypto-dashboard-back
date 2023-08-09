import socketIO from "socket.io";
import http from "http";

let socketInstance: socketIO.Server | null = null;

export const getSocketInstance = (server: http.Server): socketIO.Server => {
  if (!socketInstance) {
    socketInstance = new socketIO.Server(server, {
      cors: {
        origin: "http://localhost:3000",
        methods: ["GET", "POST"],
        allowedHeaders: ["Content-Type"],
        credentials: true,
      },
    });
  }
  return socketInstance;
};
