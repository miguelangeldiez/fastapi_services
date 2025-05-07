const socket = new WebSocket("ws://localhost:8000/ws/notifications");

socket.onmessage = (event) => {
    console.log("Notificación recibida:", event.data);
};