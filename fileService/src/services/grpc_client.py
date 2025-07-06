import grpc
from src.grpc import auth_pb2, auth_pb2_grpc  # Adjust this import based on where you generate proto files!

async def validateAccessToken(access_token: str):
    async with grpc.aio.insecure_channel("localhost:9000") as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        request = auth_pb2.ValidateTokenRequest(access_token=access_token)
        try:
            response = await stub.ValidateToken(request)
            return {
                "status": response.status,
                "userId": response.user_id if response.status == "valid" else None
            }
        except grpc.aio.AioRpcError as e:
            print(f"gRPC error: {e}")
            return {"status": "error", "userId": None}