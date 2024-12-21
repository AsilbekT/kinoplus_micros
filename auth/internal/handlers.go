package internal

import (
	authProto "auth/proto"
	user "auth/proto/users"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

type Handler struct {
	UserServiceClient user.UserServiceClient
}

func writeErrorResponse(w http.ResponseWriter, statusCode int, message string) {
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

func (app *App) RegisterHTTPRoutes(r *mux.Router) {
	r.HandleFunc("/auth/send-otp", app.HTTPHandleSendOTP).Methods("POST")
	r.HandleFunc("/auth/verify-otp", app.HTTPHandleVerifyOTP).Methods("POST")
	r.HandleFunc("/auth/add-qr-user", app.HTTPHandleQRAuth).Methods("POST")
}

func (app *App) HTTPHandleSendOTP(w http.ResponseWriter, r *http.Request) {
	log.Println("Received request for /auth/send-otp")
	var req struct {
		PhoneNumber string `json:"phone_number"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Printf("Error decoding request body: %v", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	log.Printf("Processing OTP for phone number: %s", req.PhoneNumber)
	grpcReq := &authProto.SendOTPRequest{PhoneNumber: req.PhoneNumber}

	resp, err := app.SendOTP(r.Context(), grpcReq)
	if err != nil {
		log.Printf("Error sending OTP: %v", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	log.Println("OTP sent successfully")
	json.NewEncoder(w).Encode(resp)
}

func (app *App) HTTPHandleVerifyOTP(w http.ResponseWriter, r *http.Request) {
	var req struct {
		PhoneNumber string `json:"phone_number"`
		OTP         string `json:"otp"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Construct the gRPC request
	grpcReq := &authProto.VerifyOTPRequest{
		PhoneNumber: req.PhoneNumber,
		Otp:         req.OTP,
	}

	// Call the VerifyOTP method
	resp, err := app.VerifyOTP(r.Context(), grpcReq)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Encode the response to JSON
	json.NewEncoder(w).Encode(resp)
}

func (app *App) HTTPHandleQRAuth(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SessionId string `json:"session_id"` // Adjust JSON tag to match the expected input
		UserId    int32  `json:"user_id"`
	}

	log.Println("Received request for /auth/qr-auth")
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		log.Printf("Error decoding request body: %v", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	log.Printf("Processing QR Authentication for SessionId: %s and UserId: %d", req.SessionId, req.UserId)

	grpcReq := &authProto.QRAuthRequest{
		SessionId: req.SessionId, // Use the correct field names from the generated Go code
		UserId:    req.UserId,
	}

	resp, err := app.QRAuth(r.Context(), grpcReq)
	if err != nil {
		log.Printf("Error during QR authentication: %v", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(resp)
}
