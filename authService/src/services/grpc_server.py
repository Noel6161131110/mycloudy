import grpc
from src.app.v1.Users.grpc import auth_pb2, auth_pb2_grpc
from src.app.v1.Users.services.auth import ValidateAccessToken
from src.database.db import getSession

class AuthServiceServicer(auth_pb2_grpc.AuthServiceServicer):
    async def ValidateToken(self, request, context):
        print("Received ValidateToken request with access token:", request.access_token, "\n\n\n")
        async with getSession() as db:
            user = await ValidateAccessToken(request.access_token, db)
            if user:
                return auth_pb2.ValidateTokenResponse(
                    status="valid",
                    user_id=str(user.id)
                )
            else:
                return auth_pb2.ValidateTokenResponse(
                    status="invalid"
                )

async def serve_grpc():
    server = grpc.aio.server()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceServicer(), server)
    server.add_insecure_port('[::]:9000')
    await server.start()
    print("✅ gRPC server started on port 9000")
    await server.wait_for_termination()