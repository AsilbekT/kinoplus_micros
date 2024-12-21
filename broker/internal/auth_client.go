package internal

import (
	authpb "broker/proto/auth"
	"context"
	"fmt"
	"log"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type authClient struct {
	client authpb.AuthServiceClient
}

func NewAuthClient(serviceAddr string) (AuthClient, error) {
	conn, err := grpc.Dial(serviceAddr, grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithBlock())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Auth Service: %w", err)
	}
	return &authClient{client: authpb.NewAuthServiceClient(conn)}, nil
}

func (ac *authClient) SendOTP(ctx context.Context, phoneNumber string) (*authpb.SendOTPResponse, error) {
	req := &authpb.SendOTPRequest{PhoneNumber: phoneNumber}
	return ac.client.SendOTP(ctx, req)
}

func (ac *authClient) VerifyOTP(ctx context.Context, phoneNumber, otp string) (*authpb.VerifyOTPResponse, error) {
	req := &authpb.VerifyOTPRequest{
		PhoneNumber: phoneNumber,
		Otp:         otp,
	}
	return ac.client.VerifyOTP(ctx, req)
}

func (ac *authClient) QRAuth(ctx context.Context, sessionID string, userID int32) (*authpb.QRAuthResponse, error) {
	log.Println()
	req := &authpb.QRAuthRequest{
		SessionId: sessionID,
		UserId:    userID,
	}
	log.Println("in qrauth client -> ", req)

	return ac.client.QRAuth(ctx, req)
}
