# Start from the official Golang base image
FROM golang:1.23 as builder

WORKDIR /app

# Copy go mod and sum files
COPY go.mod go.sum ./

# Download all dependencies
RUN go mod download

# Copy the whole project into the container
COPY . .

WORKDIR /app/cmd

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o auth .

FROM alpine:latest  

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary and the .env file from the builder stage
COPY --from=builder /app/cmd/auth /root/
COPY --from=builder /app/.env /root/

CMD ["./auth"]
