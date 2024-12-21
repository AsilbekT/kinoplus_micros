package internal

import (
	"log"
	"os"
	"strconv"
)

// Config structure that holds all necessary configuration for the application.
type Config struct {
	DBConnectionString string
	RedisAddr          string
	RedisPassword      string
	RedisDB            int
}

// LoadConfig initializes and returns a new Config struct populated from environment variables.
func LoadConfig() *Config {
	return &Config{
		DBConnectionString: GetEnv("DB_CONNECTION_STRING", "fallback_db_connection_string"),
		RedisAddr:          GetEnv("REDIS_ADDR", "localhost:6379"),
		RedisPassword:      GetEnv("REDIS_PASSWORD", ""),
		RedisDB:            getEnvAsInt("REDIS_DB", 0),
	}
}

// GetEnv retrieves an environment variable or returns a fallback value.
func GetEnv(key, fallback string) string {
	value, exists := os.LookupEnv(key)
	if !exists {
		return fallback
	}
	return value
}

// getEnvAsInt tries to retrieve an environment variable as an integer or returns a fallback value.
func getEnvAsInt(key string, fallback int) int {
	valueStr := GetEnv(key, "")
	if valueStr == "" {
		return fallback
	}
	value, err := strconv.Atoi(valueStr)
	if err != nil {
		log.Printf("Error converting environment variable %s to int: %v", key, err)
		return fallback
	}
	return value
}
