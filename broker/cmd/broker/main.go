package main

import (
	"broker/internal"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func main() {
	// Connect to Users Service
	usersClient, err := internal.NewUsersClient("localhost:50051")
	if err != nil {
		log.Fatalf("Failed to connect to Users Service: %v", err)
	}

	// Connect to Auth Service
	authClient, err := internal.NewAuthClient("localhost:50052")
	if err != nil {
		log.Fatalf("Failed to connect to Auth Service: %v", err)
	}

	// Initialize HTTP handler
	usersHandler := internal.NewHandler(usersClient)
	authHandler := internal.NewHandler(authClient)

	// Initialize new mux router
	r := mux.NewRouter()

	// Setup HTTP server with mux for better routing
	r.HandleFunc("/createuser", usersHandler.CreateUser).Methods("POST")
	r.HandleFunc("/getuser", usersHandler.GetUser).Methods("GET")
	r.HandleFunc("/auth/send-otp", authHandler.SendOTP).Methods("POST")
	r.HandleFunc("/auth/verify-otp", authHandler.VerifyOTP).Methods("POST")
	r.HandleFunc("/auth/add-qr-user", authHandler.QRAuth).Methods("POST")

	// Listen and serve on HTTP port with mux router
	log.Println("Broker service is running on port 8080...")
	if err := http.ListenAndServe(":8080", r); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}
