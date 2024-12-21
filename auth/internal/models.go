package internal

import (
	"os"
	"time"
)

type TokenDetails struct {
	Token     string    `json:"token"`
	ExpiresAt time.Time `json:"expires_at"`
}

type UserInfo struct {
	ID          string
	Email       string
	PhoneNumber string
	Name        string
	AuthType    string
	GoogleID    string `json:"google_id"`
	AppleID     string `json:"apple_id"`
}

type User struct {
	ID          string
	Email       string
	PhoneNumber string
	Name        string
}

type Credentials struct {
	Email          string
	Password       string
	ApplePublicKey string
}

var DefaultCredentials = Credentials{
	Email:          os.Getenv("ESKIZ_EMAIL"),
	Password:       os.Getenv("ESKIZ_PASSWORD"),
	ApplePublicKey: os.Getenv("ApplePublicKey"),
}
