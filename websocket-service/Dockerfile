# Use an official Go runtime as a parent image
FROM golang:1.17 as builder

# Set the working directory in the container
WORKDIR /go/src/app

# Copy the current directory contents into the container at /go/src/app
COPY . .

# Download all dependencies
RUN go mod download

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -v -o app

# Use a Docker multi-stage build to minimize size
FROM alpine:latest
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary from the builder stage to the production image
COPY --from=builder /go/src/app/app .

# Run the app when the container launches
CMD ["./app"]
