import grpc
import asyncio
import logging
from services.user_service import UserService
from db.database import Database
from proto import users_pb2_grpc
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def serve():
    logger.info("Starting the server...")
    db = Database(settings.database_url)

    try:
        logger.info("Connecting to the database...")
        await db.connect()
        logger.info("Database connected successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        return

    server = grpc.aio.server()
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(db), server)
    server.add_insecure_port('[::]:50051')

    try:
        logger.info("Starting gRPC server on port 50051...")
        await server.start()
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("Shutting down the server...")
        await server.stop(None)  # Gracefully stop the server
        logger.info("Server shutdown complete.")
    finally:
        logger.info("Closing database connection...")
        await db.close()
        logger.info("Database connection closed.")

if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user.")
