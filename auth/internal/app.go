// app.go
package internal

import (
	authProto "auth/proto"
	user_service "auth/proto/users"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/go-redis/redis/v8"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type App struct {
	authProto.UnimplementedAuthServiceServer
	Storage           *Storage
	RedisClient       *redis.Client
	UserServiceClient user_service.UserServiceClient
}

func NewApp(storage *Storage, redisClient *redis.Client, userServiceClient user_service.UserServiceClient) *App {
	return &App{
		Storage:           storage,
		RedisClient:       redisClient,
		UserServiceClient: userServiceClient,
	}
}

func (app *App) GoogleAuthHandler(w http.ResponseWriter, r *http.Request) {
	var request struct {
		GoogleIDToken string `json:"google_id_token"`
	}
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	userInfo, err := app.Storage.verifyGoogleIDToken(request.GoogleIDToken)
	if err != nil {
		http.Error(w, "Failed to verify Google ID token: "+err.Error(), http.StatusUnauthorized)
		return
	}

	user, err := app.Storage.getOrCreateUser(r.Context(), userInfo)

	if err != nil {
		http.Error(w, "Failed to create or retrieve user", http.StatusInternalServerError)
		return
	}

	token, err := generateJWT(user)
	if err != nil {
		http.Error(w, "Failed to generate token", http.StatusInternalServerError)
		return
	}
	ctx := r.Context()
	// Add a new session to redis
	if err := app.addSessionToken(ctx, userInfo.ID, token); err != nil {
		http.Error(w, err.Error(), http.StatusForbidden)
		return
	}
	json.NewEncoder(w).Encode(map[string]string{"token": token})
}

func (app *App) AppleAuthHandler(w http.ResponseWriter, r *http.Request) {
	var request struct {
		AppleIDToken string `json:"apple_id_token"`
	}
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	userInfo, err := app.Storage.verifyAppleIDToken(request.AppleIDToken)
	if err != nil {
		http.Error(w, "Failed to verify Apple ID token: "+err.Error(), http.StatusUnauthorized)
		return
	}

	user, err := app.Storage.getOrCreateUser(r.Context(), userInfo)
	if err != nil {
		http.Error(w, "Failed to create or retrieve user", http.StatusInternalServerError)
		return
	}

	token, err := generateJWT(user)
	if err != nil {
		http.Error(w, "Failed to generate token", http.StatusInternalServerError)
		return
	}
	ctx := r.Context()
	// Add a new session to redis
	if err := app.addSessionToken(ctx, userInfo.ID, token); err != nil {
		http.Error(w, err.Error(), http.StatusForbidden)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{"token": token})
}

func (app *App) QRAuth(ctx context.Context, req *authProto.QRAuthRequest) (*authProto.QRAuthResponse, error) {
	log.Printf("Processing QR Authentication for SessionId: %s and UserId: %d", req.SessionId, req.UserId)

	// Validate SessionId format
	if req.SessionId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "SessionId is required")
	}

	// Retrieve user details by ID
	userInfo, err := app.Storage.getUserByID(int(req.UserId))
	if err != nil {
		log.Printf("Failed to retrieve user: %v", err)
		return nil, status.Errorf(codes.NotFound, "User not found")
	}

	// Generate JWT for the user
	token, err := generateJWT(&User{
		ID:          userInfo.ID,
		Email:       userInfo.Email,
		PhoneNumber: userInfo.PhoneNumber,
		Name:        userInfo.Name,
	})
	if err != nil {
		log.Printf("Failed to generate token: %v", err)
		return nil, status.Errorf(codes.Internal, "Failed to generate token")
	}

	// Store session in Redis
	err = app.addSessionToken(ctx, userInfo.ID, token)
	if err != nil {
		log.Printf("Failed to add session token: %v", err)
		return nil, status.Errorf(codes.Internal, "Failed to add session token")
	}

	// Send token to WebSocket service
	statusCode, responseMessage := sendPostResponse(req.SessionId, token)
	if statusCode != http.StatusOK {
		log.Printf("Failed to deliver token to WebSocket service: %s", responseMessage)
		return nil, status.Errorf(codes.Internal, "Failed to notify WebSocket service")
	}

	log.Printf("QR Authentication successful for UserId: %d", req.UserId)

	return &authProto.QRAuthResponse{
		Success: true,
		Message: "QR authentication successful",
	}, nil
}

func (app *App) SendOTP(ctx context.Context, req *authProto.SendOTPRequest) (*authProto.SendOTPResponse, error) {
	log.Println("in app sending otp")

	if req.PhoneNumber == "" {
		return nil, status.Error(codes.InvalidArgument, "Phone number is required")
	}

	otp, err := generateOTP(ctx, app.RedisClient)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to generate OTP: %v", err)
	}

	message := fmt.Sprintf("Sizning autentifikatsiya kodingiz: %s Ushbu kodni hech kimga bermang. PandaTV ilovasi orqali kirish uchun ushbu kodni kiriting.", otp)
	log.Println(message)
	err = app.RedisClient.Set(ctx, req.PhoneNumber, otp, time.Minute*5).Err()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to save OTP: %v", err)
	}

	message, err = sendSMS(ctx, app.RedisClient, req.PhoneNumber, message)
	log.Println(message, err)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to send SMS: %v", err)
	}

	return &authProto.SendOTPResponse{
		Success: true,
		Message: "OTP sent successfully",
	}, nil
}

func (app *App) VerifyOTP(ctx context.Context, req *authProto.VerifyOTPRequest) (*authProto.VerifyOTPResponse, error) {
	// Validate input
	if req.PhoneNumber == "" || req.Otp == "" {
		return nil, status.Errorf(codes.InvalidArgument, "Phone number and OTP must be provided")
	}

	// Retrieve the OTP from Redis
	storedOTP, err := app.RedisClient.Get(ctx, req.PhoneNumber).Result()
	if err == redis.Nil {
		return nil, status.Errorf(codes.NotFound, "OTP expired or invalid")
	} else if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to retrieve OTP: %v", err)
	}

	// Compare the provided OTP with the one stored in Redis
	if req.Otp != storedOTP {
		return nil, status.Errorf(codes.Unauthenticated, "Invalid OTP")
	}

	// Delete the OTP and its reservation
	err = app.RedisClient.Del(ctx, req.PhoneNumber).Err()
	if err != nil {
		log.Printf("Error deleting OTP for phone number: %v", err)
	}

	err = app.RedisClient.Del(ctx, "otp:"+req.Otp).Err()
	if err != nil {
		log.Printf("Error deleting reserved OTP: %v", err)
	}

	// Retrieve or create user information
	userInfo := &UserInfo{
		PhoneNumber: req.PhoneNumber,
		AuthType:    "OTP",
	}
	log.Println("am on verify otp and passing ctx > ", ctx)
	user, err := app.Storage.getOrCreateUser(ctx, userInfo)

	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to create or retrieve user: %v", err)
	}

	// Generate JWT for the user
	token, err := generateJWT(user)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to generate JWT: %v", err)
	}

	// Manage sessions in Redis
	key := fmt.Sprintf("user_sessions:%s", user.ID)
	sessions, err := app.RedisClient.SMembers(ctx, key).Result()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to retrieve sessions: %v", err)
	}

	// Limit the number of active sessions
	if len(sessions) >= 100 {
		return nil, status.Errorf(codes.ResourceExhausted, "Maximum session limit reached")
	}

	// Add the new session token to Redis with expiration
	err = app.RedisClient.SAdd(ctx, key, token).Err()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to store session token: %v", err)
	}

	err = app.RedisClient.Expire(ctx, key, 24*time.Hour).Err() // Set session expiration to 24 hours
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Failed to set session expiration: %v", err)
	}

	// Store session details in the database (optional)
	userID, err := strconv.Atoi(user.ID)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "Invalid user ID: %v", err)
	}

	err = app.addSessionToDB(userID, "Default Device", token)

	if err != nil {
		log.Printf("Failed to save session in DB: %v", err)
		// Proceed without interrupting OTP verification since Redis is the primary store
	}

	// Return the response
	return &authProto.VerifyOTPResponse{
		Success: true,
		Message: "OTP verified successfully",
		Token:   token,
	}, nil
}

func (app *App) addSessionToken(ctx context.Context, userID string, token string) error {
	key := fmt.Sprintf("user_sessions:%s", userID)

	// Check current number of sessions
	sessions, err := app.RedisClient.SMembers(ctx, key).Result()
	log.Print("current sessions: ", sessions)
	if err != nil {
		return err
	}

	// Limit sessions to 3
	if len(sessions) >= 100 {
		return fmt.Errorf("maximum session limit reached")
	}

	// Add new session token to Redis and set expiration
	_, err = app.RedisClient.SAdd(ctx, key, token).Result()
	if err != nil {
		return err
	}
	_, err = app.RedisClient.Expire(ctx, key, 24*time.Hour).Result()
	return err
}

func (app *App) LogoutHandler(w http.ResponseWriter, r *http.Request) {
	log.Print("On Logout")

	// Extract the token from the Authorization header
	token, err := extractTokenFromHeader(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusUnauthorized)
		return
	}

	// Extract the user ID from the token
	userID, err := getUserIDFromToken(token)
	if err != nil {
		http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
		return
	}

	// Remove the session from Redis
	err = app.removeSessionFromRedis(r.Context(), userID, token)
	if err != nil {
		http.Error(w, "Failed to remove session from Redis", http.StatusInternalServerError)
		return
	}

	// Remove the session from the database
	err = app.Storage.DeleteSession(token)
	if err != nil {
		log.Printf("Failed to delete session from DB: %v", err)
	}

	log.Printf("User %s logged out successfully", userID)
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Logged out successfully"))
}

func (app *App) RemoveSession(token, userID string) error {
	ctx := context.Background()

	// Remove session from Redis
	if _, err := app.RedisClient.Del(ctx, fmt.Sprintf("user_sessions:%s", userID)).Result(); err != nil {
		return err
	}

	// Remove session from the database
	return app.Storage.DeleteSession(token)
}

func (app *App) SessionDetailsHandler(w http.ResponseWriter, r *http.Request) {
	// Extract the User-Agent from the request header
	userAgent := r.Header.Get("User-Agent")
	if userAgent == "" {
		http.Error(w, "User-Agent header is missing", http.StatusBadRequest)
		return
	}

	// Extract authorization token for session identification
	token := r.Header.Get("Authorization")
	if token == "" {
		http.Error(w, "Authorization token is missing", http.StatusUnauthorized)
		return
	}

	// Validate the token and retrieve the user ID
	userID, err := getUserIDFromToken(token)
	if err != nil {
		http.Error(w, "Invalid token provided", http.StatusUnauthorized)
		return
	}

	// Get all active sessions for the user from Redis
	key := fmt.Sprintf("user_sessions:%s", userID)
	sessions, err := app.RedisClient.SMembers(r.Context(), key).Result()
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to retrieve sessions: %v", err), http.StatusInternalServerError)
		return
	}

	// Response with session information and User-Agent
	response := map[string]interface{}{
		"user_id":    userID,
		"user_agent": userAgent,
		"sessions":   sessions,
	}
	json.NewEncoder(w).Encode(response)
}

func (app *App) addSessionToDB(userID int, deviceName, token string) error {
	err := app.Storage.InsertSession(userID, deviceName, token)
	if err != nil {
		log.Printf("Error adding session to DB: %v", err)
		return err
	}
	return nil
}

func (app *App) removeSessionFromRedis(ctx context.Context, userID, token string) error {
	sessionKey := "user_sessions:" + userID
	_, err := app.RedisClient.SRem(ctx, sessionKey, token).Result()
	if err != nil {
		log.Printf("Failed to remove session token from Redis: %v", err)
		return err
	}
	return nil
}
