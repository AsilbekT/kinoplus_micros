package internal

import (
	authpb "broker/proto/auth"
	userspb "broker/proto/users"
	"context"
)

type UserClient interface {
	CreateUser(ctx context.Context, email, phoneNumber, name string) (*userspb.CreateUserResponse, error)
	GetUser(ctx context.Context, userID string) (*userspb.GetUserResponse, error)
}

type AuthClient interface {
	SendOTP(ctx context.Context, phoneNumber string) (*authpb.SendOTPResponse, error)
	VerifyOTP(ctx context.Context, phoneNumber, otp string) (*authpb.VerifyOTPResponse, error)
	QRAuth(ctx context.Context, sessionID string, userID int32) (*authpb.QRAuthResponse, error)
}
