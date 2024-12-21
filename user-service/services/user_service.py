import logging
from proto import users_pb2, users_pb2_grpc
import grpc

logger = logging.getLogger(__name__)

class UserService(users_pb2_grpc.UserServiceServicer):
    def __init__(self, db):
        self.db = db

    async def CreateUser(self, request, context):
        logger.info(f"Received CreateUser request: {request}")
        try:
            # Create or update the user
            user_id = await self.db.create_or_update_user(
                username=request.username  if request.username else None,
                email=request.email if request.email else None,
                phone_number=request.phone_number if request.phone_number else None,
                google_id=request.google_id if request.google_id else None,
                apple_id=request.apple_id if request.apple_id else None
            )
            response = users_pb2.UserResponse(
                user_id=str(user_id),
                username=request.username,
                email=request.email,
                phone_number=request.phone_number,
                google_id=request.google_id,
                apple_id=request.apple_id
            )
            logger.info(f"Response sent: {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing CreateUser request: {e}")
            context.set_details("Internal server error")
            context.set_code(grpc.StatusCode.INTERNAL)
            return users_pb2.UserResponse()


    async def GetUser(self, request, context):
        logger.info(f"Received GetUser request: {request}")
        try:
            # Validate user_id
            if not request.user_id or not request.user_id.isdigit():
                context.set_details("Invalid user_id format. Must be a non-empty numeric value.")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return users_pb2.UserResponse()

            user_id = int(request.user_id)

            # Fetch user from the database
            user = await self.db.get_user(user_id)
            if not user:
                context.set_details("User not found.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return users_pb2.UserResponse()

            # Construct the response
            response = users_pb2.UserResponse(
                user_id=str(user["id"]),
                username=user["username"] if user["username"] else "",
                email=user["email"] if user["email"] else "",
                phone_number=user["phone_number"] if user["phone_number"] else "",
                google_id=user["google_id"] if user["google_id"] else "",
                apple_id=user["apple_id"] if user["apple_id"] else ""
            )
            logger.info(f"Response sent: {response}")
            return response

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            context.set_details("An internal error occurred while processing the request.")
            context.set_code(grpc.StatusCode.INTERNAL)
            return users_pb2.UserResponse()