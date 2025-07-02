from src.app.v1.Users.api.userController import *
from src.app.v1.Users.api.rolesController import *
from src.app.v1.Users.api.inviteController import *
from src.app.v1.Users.api.authController import *
from fastapi import APIRouter

userRouter = APIRouter()
inviteRouter = APIRouter()
rolesRouter = APIRouter()
authRouter = APIRouter()

userRoutes = [
    {
        "method": "GET",
        "name": "Get Users - Used by Admin users to get all users",
        "path": "",
        "endpoint": GetUsers                  # Used by Admin users to get all users
    },
    {
        "method": "POST",
        "name": "Create User - Used by onboarding users (they become admins) (Admin Sign Up)",
        "path": "",
        "endpoint": CreateOnboardingUser      # Should only be used by onboarding users (they become admins)
    },
    {
        "method": "PUT",
        "name": "Update User - Used by all users to update their details",
        "path": "",
        "endpoint": UpdateUser                # Should only be used by Admin users
    },
    {
        "method": "PUT",
        "name": "Update Password - Used by all users to update their password inside the system",
        "path": "/password",
        "endpoint": UpdatePassword             # Accessible by everyone
    },
    {
        "method": "DELETE",
        "name": "Delete User - Used by Admin users to delete users",
        "path": "",
        "endpoint": DeleteUser                 # Should only be used by Admin users
    }
]

inviteRoutes = [
    {
        "method": "GET",
        "name": "Get User Info of the created user during registration",
        "path": "/{inviteId}",
        "endpoint": GetCreatedUserInfo         # Only used for the invite link and created users (Not Admin)
    },
    {
        "method": "GET",
        "name": "Get Invite Links - Used by Admin users to list all invite links",
        "path": "",
        "endpoint": GetInviteLink             # Only used by Admin users to list all invite links
    },
    {
        "method": "POST",
        "name": "Create Invite Link - Used by Admin users to create invite links",
        "path": "",
        "endpoint": GenerateInviteLink           # Only used by Admin users to create invite links
    }
]

authRoutes = [
    {
        "method": "POST",
        "name": "Login User - Common login endpoint",
        "path": "/login",
        "endpoint": LoginUser                 # Accessible by everyone. Common login endpoint
    },
    {
        "method": "POST",
        "name": "Refresh Token to validate and generate new access token",
        "path": "/refresh",
        "endpoint": RefreshAccessToken         # Used by all users to login with refresh token
    },
    {
        "method": "POST",
        "name": "Validate Access Token - Used by all users to validate access token",
        "path": "/validate-token",
        "endpoint": ValidateAccessToken        # Used by all users to validate access token
    }
]

roleRoutes = [
    {
        "method": "GET",
        "name": "Get Roles - Used by Admin users to get all roles",
        "path": "",
        "endpoint": GetRoles                   # Used by Admin users to get all roles
    },
    {
        "method": "PUT",
        "name": "Update Role - Used by Admin users to update roles",
        "path": "",
        "endpoint": ChangeUserRole                 # Used by Admin users to update roles
    }
]


for route in userRoutes:
    userRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])
    

for route in inviteRoutes:
    inviteRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])
    
for route in authRoutes:
    authRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])
    
for route in roleRoutes:
    rolesRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])