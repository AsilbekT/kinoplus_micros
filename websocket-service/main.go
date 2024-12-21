package main

import (
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func main() {
	r := mux.NewRouter()

	// Route for establishing WebSocket connections
	r.HandleFunc("/ws/{sessionID}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		sessionID := vars["sessionID"]
		HandleConnections(w, r, sessionID) // Assumes a function that handles WebSocket connections
	})

	// Route for handling notifications
	r.HandleFunc("/notify/{sessionID}", func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		sessionID := vars["sessionID"]
		HandleMessage(w, r, sessionID) // Assumes a function that handles incoming notifications
	})

	// Set the router as the HTTP handler
	http.Handle("/", r)

	// Log the starting of the server
	log.Println("Server started on :7070")

	// Start the server on port 7070
	if err := http.ListenAndServe(":7070", nil); err != nil {
		log.Fatal("ListenAndServe:", err)
	}
}
