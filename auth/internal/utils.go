// utils.go

package internal

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/go-redis/redis/v8"
	"golang.org/x/exp/rand"
)

var jwtKey = []byte(os.Getenv("JWT_SECRET"))

type Claims struct {
	jwt.StandardClaims
	Email       string `json:"email"`
	PhoneNumber string `json:"phone_number"`
	UserID      string `json:"user_id"`
}

// GenerateJWT creates a JWT for a given user.
func GenerateJWT(email, userID string) (string, error) {
	expirationTime := time.Now().Add(24 * time.Hour)
	claims := &Claims{
		Email:  email,
		UserID: userID,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtKey)
}

func generateJWT(user *User) (string, error) {
	expirationTime := time.Now().Add(24 * time.Hour) // Set token expiration time
	claims := &Claims{
		Email:       user.Email,
		PhoneNumber: user.PhoneNumber,
		UserID:      user.ID,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(jwtKey)
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %v", err)
	}

	return tokenString, nil
}

// VerifyJWT parses and validates a JWT token.
func VerifyJWT(tokenStr string) (*Claims, error) {
	claims := &Claims{}

	token, err := jwt.ParseWithClaims(tokenStr, claims, func(token *jwt.Token) (interface{}, error) {
		return jwtKey, nil
	})

	if err != nil {
		return nil, err
	}

	if !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	return claims, nil
}

func generateOTP(ctx context.Context, redisClient *redis.Client) (string, error) {
	for {
		otp := fmt.Sprintf("%06d", rand.Intn(1000000))
		_, err := redisClient.Get(ctx, "otp:"+otp).Result()
		if err == redis.Nil {
			return otp, nil
		} else if err != nil {
			return "", fmt.Errorf("error checking OTP uniqueness: %v", err)
		}
	}
}

func respondWithError(w http.ResponseWriter, statusCode int, message string) {
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

func sendSMS(ctx context.Context, redisClient *redis.Client, phoneNumber, message string) (string, error) {
	creds := DefaultCredentials
	token, err := getToken(ctx, redisClient, creds.Email, creds.Password)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve token: %v", err)
	}

	apiURL := "https://notify.eskiz.uz/api/message/sms/send"
	data := map[string]string{
		"mobile_phone": phoneNumber,
		"message":      message,
		"from":         os.Getenv("SMS_SENDER_ID"),
	}
	jsonData, err := json.Marshal(data)
	if err != nil {
		return "", fmt.Errorf("error encoding SMS data: %v", err)
	}

	client := &http.Client{Timeout: 10 * time.Second}
	req, err := http.NewRequestWithContext(ctx, "POST", apiURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("error creating SMS request: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to send SMS: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		return "success", nil
	}

	// Read and log the response body for errors
	respBody, _ := ioutil.ReadAll(resp.Body)
	log.Printf("Eskiz API Response Body: %s", string(respBody))

	return "", fmt.Errorf("failed to send SMS: status %d", resp.StatusCode)
}

func fetchAndSaveToken(ctx context.Context, redisClient *redis.Client, email, password string) (string, error) {
	token, err := fetchTokenFromAPI(email, password)
	if err != nil {
		return "", err
	}
	err = redisClient.Set(ctx, "auth:token", token, 30*24*time.Hour).Err()
	if err != nil {
		return "", fmt.Errorf("error saving token to Redis: %w", err)
	}
	return token, nil
}

func getToken(ctx context.Context, redisClient *redis.Client, email, password string) (string, error) {
	token, err := redisClient.Get(ctx, "auth:token").Result()
	if err == redis.Nil {
		return fetchAndSaveToken(ctx, redisClient, email, password)
	} else if err != nil {
		return "", fmt.Errorf("error retrieving token from Redis: %w", err)
	}
	return token, nil
}

func fetchTokenFromAPI(email, password string) (string, error) {
	apiUrl := "https://notify.eskiz.uz/api/auth/login"
	formData := url.Values{}
	formData.Set("email", email)
	formData.Set("password", password)

	req, err := http.NewRequest("POST", apiUrl, bytes.NewBufferString(formData.Encode()))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result struct {
		Message string `json:"message"`
		Data    struct {
			Token string `json:"token"`
		} `json:"data"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	if result.Message != "token_generated" {
		return "", fmt.Errorf("unexpected response message: %s", result.Message)
	}

	return result.Data.Token, nil
}

func sendPostResponse(sessionID string, data string) (int, string) {
	jsonPayload := map[string]string{
		"token": data,
	}

	// Encode the JSON object
	postDataBytes, err := json.Marshal(jsonPayload)
	if err != nil {
		log.Printf("Failed to encode post data: %v", err)
		return http.StatusInternalServerError, "Failed to encode post data"
	}

	notifyURL := fmt.Sprintf("http://localhost:7070/notify/%s", sessionID)
	req, err := http.NewRequest("POST", notifyURL, bytes.NewReader(postDataBytes))
	if err != nil {
		log.Printf("Failed to create POST request: %v", err)
		return http.StatusInternalServerError, "Failed to create POST request"
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("HTTP POST request failed: %v", err)
		return http.StatusInternalServerError, "Failed to send POST request"
	}
	defer resp.Body.Close()

	responseBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Failed to read response from notify endpoint: %v", err)
		return http.StatusInternalServerError, "Failed to read response from notify endpoint"
	}

	log.Printf("Received response from notify endpoint: %s", string(responseBytes))
	logResponseDetails(resp)

	return resp.StatusCode, string(responseBytes)
}

// Additional function to log detailed response headers and status code
func logResponseDetails(resp *http.Response) {
	log.Printf("Response Status Code: %d, Status: %s", resp.StatusCode, resp.Status)
	log.Println("Response Headers:")
	for key, value := range resp.Header {
		log.Printf("%s: %s", key, value)
	}

	// Provide additional information based on the status code.
	switch resp.StatusCode {
	case http.StatusOK:
		log.Println("Message successfully delivered to the WebSocket client.")
	case http.StatusNotFound:
		log.Println("WebSocket session not found, failed to deliver message.")
	default:
		log.Println("An unexpected error occurred while delivering the message.")
	}
}

// func removeSessionToken(ctx context.Context, redisClient *redis.Client, userID, token string) error {
// 	key := fmt.Sprintf("user_sessions:%s", userID)
// 	_, err := redisClient.SRem(ctx, key, token).Result()
// 	return err
// }

func getUserIDFromToken(tokenString string) (string, error) {
	claims := &Claims{}

	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}

		return jwtKey, nil
	})
	if err != nil {
		return "", fmt.Errorf("error parsing token: %v", err)
	}

	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims.UserID, nil
	} else {
		return "", fmt.Errorf("invalid token or could not extract user ID")
	}
}

func extractTokenFromHeader(r *http.Request) (string, error) {
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		return "", fmt.Errorf("authorization header is missing")
	}

	// Authorization header is expected to be in the format: "Bearer <token>"
	const prefix = "Bearer "
	if len(authHeader) < len(prefix) || authHeader[:len(prefix)] != prefix {
		return "", fmt.Errorf("authorization header format must be Bearer <token>")
	}

	// Extract the token by trimming the prefix
	return authHeader[len(prefix):], nil
}
