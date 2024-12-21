package main

import (
	"auth/internal"
	"auth/proto"
	"auth/proto/users"
	"context"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/go-redis/redis/v8"
	"github.com/joho/godotenv"
	"google.golang.org/grpc"
)

func main() {
	log.Println("Starting the Auth microservice...")

	if err := godotenv.Load(); err != nil {
		log.Fatalf("Failed to load .env: %v", err)
	}

	// Load configuration from environment variables
	databaseURL, redisAddr, userServiceAddr := loadConfig()

	// Setup gRPC client for UserService
	userServiceClient, conn := setupUserService(userServiceAddr)
	defer conn.Close()

	// Initialize storage
	storage := internal.InitDB(databaseURL, userServiceClient)
	defer storage.Close()

	// Setup Redis
	redisClient := setupRedis(redisAddr)
	defer redisClient.Close()

	// Initialize the application
	app := internal.NewApp(storage, redisClient, userServiceClient)

	// Setup and start the gRPC servers
	grpcServer := setupServers(app)
	startServers(grpcServer)

	// Handle graceful shutdown
	gracefulShutdown(grpcServer, redisClient)
}

// Load configuration from environment variables
func loadConfig() (string, string, string) {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		log.Fatalf("DATABASE_URL is not set")
	}

	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		log.Fatalf("REDIS_ADDR is not set")
	}

	userServiceAddr := os.Getenv("USER_SERVICE_ADDR")
	if userServiceAddr == "" {
		log.Fatalf("USER_SERVICE_ADDR is not set")
	}

	return databaseURL, redisAddr, userServiceAddr
}

// Setup gRPC client for UserService
func setupUserService(addr string) (users.UserServiceClient, *grpc.ClientConn) {
	conn, err := grpc.Dial(addr, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Failed to connect to UserService: %v", err)
	}
	log.Println("Connected to UserService at:", addr)
	client := users.NewUserServiceClient(conn)
	return client, conn
}

// Setup Redis connection
func setupRedis(addr string) *redis.Client {
	client := redis.NewClient(&redis.Options{Addr: addr})
	if _, err := client.Ping(context.Background()).Result(); err != nil {
		log.Fatalf("Redis connection failed: %v", err)
	}
	log.Println("Redis connected successfully")
	return client
}

// Setup gRPC servers
func setupServers(app *internal.App) *grpc.Server {
	grpcServer := grpc.NewServer()
	proto.RegisterAuthServiceServer(grpcServer, app)
	return grpcServer
}

// Start gRPC servers
func startServers(grpcServer *grpc.Server) {
	go func() {
		lis, err := net.Listen("tcp", ":50052")
		if err != nil {
			log.Fatalf("Failed to start gRPC server: %v", err)
		}
		log.Println("gRPC server running on port 50052")
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("gRPC server error: %v", err)
		}
	}()
}

// Graceful shutdown handling
func gracefulShutdown(grpcServer *grpc.Server, redisClient *redis.Client) {
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	log.Println("Shutting down servers...")
	grpcServer.GracefulStop()
	log.Println("Servers stopped successfully")
}
