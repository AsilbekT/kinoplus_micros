package internal

import (
	"context"
	"fmt"

	userspb "broker/proto/users"

	"google.golang.org/grpc"
)

type UsersClient struct {
	client userspb.UserServiceClient
}

// NewUsersClient creates a new gRPC client for the Users Service
func NewUsersClient(address string) (*UsersClient, error) {
	conn, err := grpc.Dial(address, grpc.WithInsecure())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Users Service: %w", err)
	}
	return &UsersClient{client: userspb.NewUserServiceClient(conn)}, nil
}

// CreateUser calls the CreateUser method on the Users Service
func (u *UsersClient) CreateUser(ctx context.Context, email, phone, name string) (*userspb.CreateUserResponse, error) {
	req := &userspb.CreateUserRequest{
		Email:       email,
		PhoneNumber: phone,
		Name:        name,
	}
	return u.client.CreateUser(ctx, req)
}

// GetUser calls the GetUser method on the Users Service
func (u *UsersClient) GetUser(ctx context.Context, userID string) (*userspb.GetUserResponse, error) {
	req := &userspb.GetUserRequest{
		UserId: userID,
	}
	return u.client.GetUser(ctx, req)
}
