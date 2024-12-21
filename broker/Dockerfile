# Start from the official Golang base image
FROM golang:1.23 as builder

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy go mod and sum files
COPY go.mod go.sum ./

# Download all dependencies. Dependencies will be cached if the go.mod and go.sum files are not changed
RUN go mod download

# Copy the whole project into the container
# Ensure this copy includes the Go source files in the right subdirectory
COPY . .

# Navigate to the directory containing the main package and build the application
# Adjust this path if your main package is located in another subdirectory
WORKDIR /app/cmd/broker

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o broker .

# Use a lightweight Alpine base image for the final stage
FROM alpine:latest  

# Install ca-certificates for HTTPS requests (if needed)
RUN apk --no-cache add ca-certificates

# Set the working directory in the final image
WORKDIR /root/

# Copy the binary from the builder stage
COPY --from=builder /app/cmd/broker/broker .

# Expose the port the broker service listens on
EXPOSE 8080

# Command to run the executable
CMD ["./broker"]
