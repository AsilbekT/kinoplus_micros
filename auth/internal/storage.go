package internal

import (
	"auth/proto/users"
	"context"
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/dgrijalva/jwt-go"
	_ "github.com/lib/pq"
	"google.golang.org/api/oauth2/v2"
)

type Storage struct {
	DB                *sql.DB
	UserServiceClient users.UserServiceClient
}

func InitDB(dataSourceName string, userServiceClient users.UserServiceClient) *Storage {
	db, err := sql.Open("postgres", dataSourceName)
	if err != nil {
		log.Fatalf("Could not connect to database: %v", err)
	}
	if err := db.Ping(); err != nil {
		log.Fatalf("Could not ping database: %v", err)
	}
	return &Storage{DB: db, UserServiceClient: userServiceClient}
}

func (s *Storage) Close() error {
	if s.DB != nil {
		return s.DB.Close()
	}
	return nil
}

func NewStorage(db *sql.DB) *Storage {
	return &Storage{DB: db}
}

func (s *Storage) getUserByID(userID int) (*UserInfo, error) {
	var user UserInfo
	err := s.DB.QueryRow("SELECT id, email, phone_number, name FROM users WHERE id = $1", userID).Scan(&user.ID, &user.Email, &user.PhoneNumber, &user.Name)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (s *Storage) verifyGoogleIDToken(idToken string) (*UserInfo, error) {
	httpC := &http.Client{}
	oauth2Service, err := oauth2.New(httpC)
	if err != nil {
		return nil, fmt.Errorf("oauth2 service creation failed: %v", err)
	}

	tokenInfoCall := oauth2Service.Tokeninfo()
	tokenInfoCall.IdToken(idToken)
	tokenInfo, err := tokenInfoCall.Do()
	if err != nil {
		return nil, fmt.Errorf("failed to get token info: %v", err)
	}

	return &UserInfo{
		ID:    tokenInfo.UserId,
		Email: tokenInfo.Email,
	}, nil
}

func (s *Storage) verifyAppleIDToken(idToken string) (*UserInfo, error) {
	creds := DefaultCredentials

	token, err := jwt.Parse(idToken, func(token *jwt.Token) (interface{}, error) {
		return creds.ApplePublicKey, nil
	})

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		return &UserInfo{
			ID:       claims["sub"].(string),
			Email:    claims["email"].(string),
			AuthType: "apple",
		}, nil
	} else {
		return nil, err
	}
}
func (s *Storage) getOrCreateUser(ctx context.Context, userInfo *UserInfo) (*User, error) {
	var user User

	query := `
		SELECT id, email, phone_number, name 
		FROM users 
		WHERE (google_id = $1 AND google_id IS NOT NULL AND google_id != '') 
		OR (apple_id = $2 AND apple_id IS NOT NULL AND apple_id != '') 
		OR (email = $3 AND email IS NOT NULL AND email != '') 
		OR (phone_number = $4 AND phone_number IS NOT NULL AND phone_number != '')
	`
	err := s.DB.QueryRow(query, userInfo.GoogleID, userInfo.AppleID, userInfo.Email, userInfo.PhoneNumber).Scan(
		&user.ID, &user.Email, &user.PhoneNumber, &user.Name,
	)

	log.Println("here on get or create -> ", err, userInfo)
	if err == sql.ErrNoRows {
		// Insert new user if not found and fetch its ID
		now := time.Now()
		log.Printf("here before using createuser method > %+v", userInfo)

		createUserResp, err := s.UserServiceClient.CreateUser(ctx, &users.CreateUserRequest{
			Username:    userInfo.Name,
			Email:       userInfo.Email,
			PhoneNumber: userInfo.PhoneNumber,
			GoogleId:    userInfo.GoogleID,
			AppleId:     userInfo.AppleID,
		})
		if err != nil {
			log.Printf("Failed to call CreateUser on Users Service: %v", err)
			return nil, fmt.Errorf("failed to create user in Users Service: %w", err)
		}

		// Store the user in the local database
		userID := createUserResp.UserId
		log.Printf("CreateUser response received: %+v", userID)

		// Use `NULL` for empty fields in the INSERT query
		err = s.DB.QueryRow(`
            INSERT INTO users (email, phone_number, name, google_id, apple_id, auth_type, created_at, updated_at) 
            VALUES (NULLIF($1, ''), NULLIF($2, ''), $3, NULLIF($4, ''), NULLIF($5, ''), $6, $7, $8)
            RETURNING id`,
			userInfo.Email, userInfo.PhoneNumber, userInfo.Name, userInfo.GoogleID, userInfo.AppleID, userInfo.AuthType, now, now).Scan(&user.ID)
		if err != nil {
			return nil, fmt.Errorf("failed to create user: %v", err)
		}

		// Populate other fields of the newly created user
		user.Email = userInfo.Email
		user.PhoneNumber = userInfo.PhoneNumber
		user.Name = userInfo.Name
	} else if err != nil {
		return nil, fmt.Errorf("error checking user existence: %v", err)
	}

	return &user, nil
}

func (s *Storage) InsertSession(userID int, deviceName, token string) error {
	query := `
        INSERT INTO sessions (user_id, device_name, token, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (token) 
        DO UPDATE SET updated_at = $5, device_name = $2
    `
	now := time.Now()
	_, err := s.DB.Exec(query, userID, deviceName, token, now, now)
	if err != nil {
		log.Printf("Error inserting session: %v; Query: %s", err, query)
		return fmt.Errorf("failed to insert or update session: %w", err)
	}

	return nil
}

func (s *Storage) DeleteSession(token string) error {
	query := `DELETE FROM sessions WHERE token = $1`
	_, err := s.DB.Exec(query, token)
	if err != nil {
		log.Printf("Error deleting session: %v", err)
		return fmt.Errorf("failed to delete session: %w", err)
	}
	return nil
}
