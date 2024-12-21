package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

// Global variables and constants
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // Remember to secure this for production environments!
	},
}

var clients = make(map[string]*websocket.Conn)
var mutex sync.Mutex

// HandleConnections upgrades HTTP to WebSocket and handles incoming WebSocket connections
func HandleConnections(w http.ResponseWriter, r *http.Request, sessionID string) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		http.Error(w, "Could not open WebSocket connection", http.StatusBadRequest)
		return
	}
	defer ws.Close()

	mutex.Lock()
	clients[sessionID] = ws
	mutex.Unlock()

	log.Printf("WebSocket connected with session ID %s", sessionID)
	sendWelcomeMessage(sessionID, "connected")

	for {
		mt, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("read error: %v", err)
			break
		}
		log.Printf("Received message from %s: %v", sessionID, message)

		// Echo the message back to the client for demonstration purposes
		if err := ws.WriteMessage(mt, message); err != nil {
			log.Printf("write error: %v", err)
			break
		}
	}

	mutex.Lock()
	delete(clients, sessionID)
	mutex.Unlock()
	log.Printf("WebSocket disconnected with session ID %s", sessionID)
}

// sendWelcomeMessage sends a greeting message to the connected WebSocket client
func sendWelcomeMessage(sessionID, message string) {
	mutex.Lock()
	conn, ok := clients[sessionID]
	mutex.Unlock()

	if ok {
		if err := conn.WriteMessage(websocket.TextMessage, []byte(message)); err != nil {
			log.Printf("error: failed to send welcome message to %s: %v", sessionID, err)
		} else {
			log.Printf("Welcome message sent to %s", sessionID)
		}
	}
}

func HandleMessage(w http.ResponseWriter, r *http.Request, sessionID string) {
	var tokenData struct {
		Token string `json:"token"`
	}

	// Read the raw body
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		log.Printf("Error reading request body: %v", err)
		http.Error(w, "Bad request: "+err.Error(), http.StatusBadRequest)
		return
	}
	log.Printf("Raw body received: %s", string(bodyBytes))

	// Try to parse as JSON object
	if err := json.Unmarshal(bodyBytes, &tokenData); err != nil {
		log.Printf("Failed to decode JSON object, treating input as raw token")

		// Treat the input as a raw token string
		tokenData.Token = string(bodyBytes)
	}

	log.Printf("Processed token: %s", tokenData.Token)

	mutex.Lock()
	conn, ok := clients[sessionID]
	mutex.Unlock()

	if !ok {
		log.Printf("No connection found for session ID %s", sessionID)
		http.Error(w, "WebSocket session not found", http.StatusNotFound)
		return
	}

	// Send the token back to the WebSocket client
	if err := conn.WriteMessage(websocket.TextMessage, []byte(tokenData.Token)); err != nil {
		log.Printf("Error sending token to WebSocket client: %v", err)
		http.Error(w, "Failed to deliver message", http.StatusInternalServerError)
	} else {
		log.Printf("Token sent back to WebSocket client: %s", sessionID)
		w.WriteHeader(http.StatusOK)
	}
}
