package internal

import (
	"encoding/json"
	"log"
	"net/http"
)

type Handler struct {
	Client interface{}
}

func NewHandler(client interface{}) *Handler {
	return &Handler{Client: client}
}

func writeErrorResponse(w http.ResponseWriter, statusCode int, message string) {
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

// GetUserClient performs type assertion once and can be reused, reducing duplication.
func (h *Handler) GetUserClient() (UserClient, bool) {
	client, ok := h.Client.(UserClient)
	return client, ok
}

// GetAuthClient performs type assertion once and can be reused, reducing duplication.
func (h *Handler) GetAuthClient() (AuthClient, bool) {
	client, ok := h.Client.(AuthClient)
	return client, ok
}

func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var payload struct {
		Email       string `json:"email"`
		PhoneNumber string `json:"phone_number"`
		Name        string `json:"name"`
	}

	client, ok := h.GetUserClient()
	if !ok {
		writeErrorResponse(w, http.StatusInternalServerError, "Client configuration error")
		return
	}

	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		log.Printf("Error decoding request body: %v", err)
		writeErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	res, err := client.CreateUser(r.Context(), payload.Email, payload.PhoneNumber, payload.Name)
	if err != nil {
		log.Printf("Error creating user: %v", err)
		writeErrorResponse(w, http.StatusInternalServerError, "Failed to create user: "+err.Error())
		return
	}

	json.NewEncoder(w).Encode(res)
}

func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
	client, ok := h.GetUserClient()
	if !ok {
		writeErrorResponse(w, http.StatusInternalServerError, "Users Client configuration error")
		return
	}

	userID := r.URL.Query().Get("user_id")
	if userID == "" {
		writeErrorResponse(w, http.StatusBadRequest, "Missing user_id")
		return
	}

	res, err := client.GetUser(r.Context(), userID)
	if err != nil {
		log.Printf("Error retrieving user: %v", err)
		writeErrorResponse(w, http.StatusInternalServerError, "Failed to get user: "+err.Error())
		return
	}

	json.NewEncoder(w).Encode(res)
}

func (h *Handler) SendOTP(w http.ResponseWriter, r *http.Request) {
	client, ok := h.GetAuthClient()
	if !ok {
		writeErrorResponse(w, http.StatusInternalServerError, "Auth Client configuration error")
		return
	}

	if r.Method != http.MethodPost {
		writeErrorResponse(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		PhoneNumber string `json:"phone_number"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	if req.PhoneNumber == "" {
		writeErrorResponse(w, http.StatusBadRequest, "Phone number is required")
		return
	}

	response, err := client.SendOTP(r.Context(), req.PhoneNumber)
	log.Println(response, err)
	if err != nil {
		writeErrorResponse(w, http.StatusInternalServerError, "Failed to send OTP: "+err.Error())
		return
	}

	json.NewEncoder(w).Encode(response)
}

func (h *Handler) VerifyOTP(w http.ResponseWriter, r *http.Request) {
	client, ok := h.GetAuthClient()
	if !ok {
		writeErrorResponse(w, http.StatusInternalServerError, "Auth Client configuration error")
		return
	}

	if r.Method != http.MethodPost {
		writeErrorResponse(w, http.StatusMethodNotAllowed, "Method not allowed")
		return
	}

	var req struct {
		PhoneNumber string `json:"phone_number"`
		OTP         string `json:"otp"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	if req.PhoneNumber == "" || req.OTP == "" {
		writeErrorResponse(w, http.StatusBadRequest, "Phone number and OTP are required")
		return
	}

	response, err := client.VerifyOTP(r.Context(), req.PhoneNumber, req.OTP)
	if err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Failed to verify OTP: "+err.Error())
		return
	}
	log.Println(response)
	json.NewEncoder(w).Encode(response)
}

// func (h *Handler) QRAuth(w http.ResponseWriter, r *http.Request) {
// 	log.Println(r)
// 	var req struct {
// 		SessionId string `json:"session_id"`
// 		UserId    int32  `json:"user_id"`
// 	}
// 	log.Println("session_id -> ", req.SessionId, req.UserId)

// 	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
// 		http.Error(w, `{"error": "Invalid request body"}`, http.StatusBadRequest)
// 		return
// 	}

// 	client, ok := h.GetAuthClient()
// 	if !ok {
// 		http.Error(w, `{"error": "Auth client not configured"}`, http.StatusInternalServerError)
// 		return
// 	}

// 	resp, err := client.QRAuth(r.Context(), req.SessionId, req.UserId)
// 	log.Println(resp, err)
// 	if err != nil {
// 		http.Error(w, `{"error": "Failed to process QR authentication"}`, http.StatusInternalServerError)
// 		return
// 	}

// 	json.NewEncoder(w).Encode(resp)
// }

func (h *Handler) QRAuth(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SessionId string `json:"session_id"`
		UserId    int32  `json:"user_id"`
	}

	log.Println("in handler -> ", req)
	// Parse request body
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		log.Printf("Error decoding request body: %v", err)
		return
	}

	// Validate input
	if req.SessionId == "" {
		writeErrorResponse(w, http.StatusBadRequest, "SessionId is required")
		return
	}
	if req.UserId <= 0 {
		writeErrorResponse(w, http.StatusBadRequest, "Invalid UserId")
		return
	}

	// Get AuthClient
	client, ok := h.GetAuthClient()
	if !ok {
		writeErrorResponse(w, http.StatusInternalServerError, "Auth client not configured")
		return
	}

	// Forward the request to the auth service
	resp, err := client.QRAuth(r.Context(), req.SessionId, req.UserId)
	if err != nil {
		writeErrorResponse(w, http.StatusInternalServerError, "Failed to process QR authentication")
		log.Printf("Error in QRAuth: %v", err)
		return
	}

	// Respond with the result
	json.NewEncoder(w).Encode(resp)
	log.Printf("QRAuth successful for session_id=%s, user_id=%d", req.SessionId, req.UserId)
}
