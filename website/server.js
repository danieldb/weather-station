const express = require("express");
const { readFileSync } = require("fs");
const app = express();
const http = require("http");
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/index.html");
});

app.get("/node_modules/socket.io/client-dist/socket.io.js", (req, res) => {
  res.sendFile(__dirname + "/node_modules/socket.io/client-dist/socket.io.js");
});
app.get("/d3.v7.min.js", (req, res) => {
  res.sendFile(__dirname + "/d3.v7.min.js");
});

io.on("connection", (socket) => {
  console.log("a user connected");
  let disconnected = false;
  setInterval(() => {
    let data = readFileSync("../new_data.csv").toString();
    socket.emit("data", data);
    console.log(data);
  }, 200);

  socket.on("disconnect", () => {
    disconnected = true;
    clearInterval();
  });
});

server.listen(3000, () => {
  console.log("listening on *:3000");
});
