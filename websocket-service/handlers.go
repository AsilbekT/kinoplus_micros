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
var (
	upgrader = websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
		CheckOrigin: func(r *http.Request) bool {
			// Ensure origin validation in production
			return true
		},
	}
	clients = make(map[string]*websocket.Conn)
	mutex   sync.Mutex
)

// HandleConnections upgrades HTTP to WebSocket and handles WebSocket connections
func HandleConnections(w http.ResponseWriter, r *http.Request, sessionID string) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		http.Error(w, "Could not open WebSocket connection", http.StatusBadRequest)
		return
	}
	defer ws.Close()

	// Add the connection to the clients map
	registerClient(sessionID, ws)
	defer unregisterClient(sessionID)

	log.Printf("WebSocket connected with session ID %s", sessionID)

	// Send a welcome message to the client
	sendMessageToClient(sessionID, `{"message": "connected"}`)

	// Read and echo messages from the WebSocket connection
	for {
		mt, message, err := ws.ReadMessage()
		if err != nil {
			log.Printf("Error reading message from session %s: %v", sessionID, err)
			break
		}
		log.Printf("Received message from session %s: %s", sessionID, string(message))

		// Echo the message back to the client
		if err := ws.WriteMessage(mt, message); err != nil {
			log.Printf("Error writing message to session %s: %v", sessionID, err)
			break
		}
	}

	log.Printf("WebSocket disconnected with session ID %s", sessionID)
}

// HandleMessage processes incoming HTTP POST requests and sends messages to the WebSocket client
func HandleMessage(w http.ResponseWriter, r *http.Request, sessionID string) {
	var tokenData struct {
		Token string `json:"token"`
	}

	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		log.Printf("Error reading request body: %v", err)
		http.Error(w, "Bad request: "+err.Error(), http.StatusBadRequest)
		return
	}
	log.Printf("Raw body received: %s", string(bodyBytes))

	// Parse the body as JSON or treat as raw token
	if err := json.Unmarshal(bodyBytes, &tokenData); err != nil {
		log.Printf("Failed to parse JSON, treating input as raw token")
		tokenData.Token = string(bodyBytes)
	}
	log.Printf("Processed token for session %s: %s", sessionID, tokenData.Token)

	// Retrieve WebSocket connection for the session
	conn, ok := getClient(sessionID)
	if !ok {
		log.Printf("No connection found for session ID %s", sessionID)
		http.Error(w, "WebSocket session not found", http.StatusNotFound)
		return
	}

	// Send the token to the WebSocket client
	message := map[string]string{"token": tokenData.Token}
	if err := sendJSONToClient(conn, message); err != nil {
		log.Printf("Error sending token to session %s: %v", sessionID, err)
		http.Error(w, "Failed to deliver message", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	log.Printf("Token sent to WebSocket client for session %s", sessionID)
}

// Utility functions

// registerClient adds a WebSocket connection to the clients map
func registerClient(sessionID string, conn *websocket.Conn) {
	mutex.Lock()
	defer mutex.Unlock()
	clients[sessionID] = conn
}

// unregisterClient removes a WebSocket connection from the clients map
func unregisterClient(sessionID string) {
	mutex.Lock()
	defer mutex.Unlock()
	delete(clients, sessionID)
}

// getClient retrieves a WebSocket connection from the clients map
func getClient(sessionID string) (*websocket.Conn, bool) {
	mutex.Lock()
	defer mutex.Unlock()
	conn, ok := clients[sessionID]
	return conn, ok
}

// sendMessageToClient sends a raw message to a WebSocket client
func sendMessageToClient(sessionID, message string) {
	conn, ok := getClient(sessionID)
	if ok {
		if err := conn.WriteMessage(websocket.TextMessage, []byte(message)); err != nil {
			log.Printf("Error sending message to session %s: %v", sessionID, err)
		} else {
			log.Printf("Message sent to session %s: %s", sessionID, message)
		}
	}
}

// sendJSONToClient sends a JSON-encoded message to a WebSocket client
func sendJSONToClient(conn *websocket.Conn, data interface{}) error {
	messageBytes, err := json.Marshal(data)
	if err != nil {
		return err
	}
	return conn.WriteMessage(websocket.TextMessage, messageBytes)
}
