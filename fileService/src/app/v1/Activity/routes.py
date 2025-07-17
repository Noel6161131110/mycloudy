from src.app.v1.Activity.api.controller import *
from fastapi import APIRouter
from src.app.v1.Activity.schemas import ActivityResponseSchema

ActivityRouter = APIRouter()

ActivityController = ActivityController()

activityRoutes = [
    {
        "method": "GET",
        "name": "Get Activities",
        "path": "",
        "endpoint": ActivityController.getAllActivities,
        "response_model": ActivityResponseSchema
    }
]


for route in activityRoutes:
    ActivityRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"], response_model=route.get("response_model"))