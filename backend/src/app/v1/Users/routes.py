from src.app.v1.Users.api.userController import *
from fastapi import APIRouter

router = APIRouter()

routes = [
    {
        "method": "GET",
        "name": "Get Users",
        "path": "",
        "endpoint": getUsers
    },
    {
        "method": "POST",
        "name": "Create User",
        "path": "",
        "endpoint": createUser
    },
    {
        "method": "POST",
        "name": "Login User",
        "path": "/login",
        "endpoint": loginUser
    },
    {
        "method": "PUT",
        "name": "Update User",
        "path": "/{id}",
        "endpoint": updateUser
    }
]

for route in routes:
    router.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])