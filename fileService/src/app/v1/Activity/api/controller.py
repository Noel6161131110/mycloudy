from fastapi import File, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from src.app.v1.Folders.models.models import Folders, PermissionType
from src.app.v1.FileOperations.models.models import FileModel, Shares
from src.database.db import getSession
from typing import List, Dict, Any
from collections import defaultdict
from uuid import uuid4, UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from src.security import security
import os
from src.dependencies.auth import getCurrentUserId
from datetime import datetime, timedelta
from src.app.v1.Activity.models.models import Activity, ActivityType, ActionType, Tags
from fastapi.encoders import jsonable_encoder
from ..schemas import ActivityHistorySchema, PeriodHistorySchema, ActivityResponseSchema


def formatTimestamp(dt: datetime) -> str:
    now = datetime.now()

    if dt.year == now.year:
        return dt.strftime("%H:%M %d %b")  # 22:11 24 May
    else:
        return dt.strftime("%-d %b %Y, %H:%M:%S")  # 8 Jan 2023, 17:05:05



def getDateRangeCategory(timestamp: datetime) -> str:
    now = datetime.now()
    today = now.date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_week - timedelta(days=7)
    start_of_month = today.replace(day=1)
    start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)

    if timestamp.date() == today:
        return "Today"
    elif timestamp.date() == today - timedelta(days=1):
        return "Yesterday"
    elif timestamp.date() >= start_of_week:
        return "This Week"
    elif timestamp.date() >= start_of_last_week and timestamp.date() < start_of_week:
        return "Last Week"
    elif timestamp.date() >= start_of_month:
        return "This Month"
    elif timestamp.date() >= start_of_last_month and timestamp.date() < start_of_month:
        return "Last Month"
    elif timestamp.date() >= start_of_year:
        return "This Year"
    elif timestamp.date() >= start_of_last_year and timestamp.date() < start_of_year:
        return "Last Year"
    else:
        return "Long time ago"


async def getSubfolderIds(folder_id: UUID, db: AsyncSession) -> List[UUID]:
    subfolder_ids = []

    async def recurse(f_id: UUID):
        result = await db.exec(select(Folders).where(Folders.parentId == f_id))
        subs = result.all()
        for sub in subs:
            subfolder_ids.append(sub.id)
            await recurse(sub.id)

    await recurse(folder_id)
    return subfolder_ids


class ActivityController:

    def __init__(self):
        pass

    async def getAllActivities(
        self,
        entityType: ActivityType,
        entityId: UUID,
        db: AsyncSession = Depends(getSession),
        userId: str = Depends(getCurrentUserId),
    ):
        try:
            folderIds = []
            fileIds = []

            if entityType == "FOLDER":
                folderIds = [entityId] + await getSubfolderIds(entityId, db)
                fileQuery = await db.exec(select(FileModel).where(FileModel.folderId.in_(folderIds)))
                fileIds = [f.id for f in fileQuery.all()]
            elif entityType == "FILE":
                fileIds = [entityId]

            stmt = select(Activity).where(
                (Activity.folderId.in_(folderIds)) |
                (Activity.fileId.in_(fileIds)) |
                (Activity.parentId.in_(folderIds))
            ).order_by(Activity.timestamp.desc())
            result = await db.exec(stmt)
            activities = result.all()

            groupedMap: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

            for activity in activities:
                category = getDateRangeCategory(activity.timestamp)

                # Determine actor name
                actor = "You" if activity.userId == userId else "Kevin"

                # Generate message based on ActionType
                match activity.action:
                    case ActionType.CREATED:
                        message = f"{actor} created an item"
                    case ActionType.UPLOADED:
                        message = f"{actor} uploaded an item"
                    case ActionType.UPDATED:
                        message = f"{actor} updated an item"
                    case ActionType.EDITED:
                        message = f"{actor} edited an item"
                    case ActionType.VIEWED:
                        message = f"{actor} viewed an item"
                    case ActionType.DELETED:
                        message = f"{actor} deleted an item"
                    case ActionType.SHARED:
                        message = f"{actor} shared an item"
                    case ActionType.MOVED:
                        message = f"{actor} moved an item"
                    case ActionType.RENAMED:
                        message = f"{actor} renamed an item"
                    case ActionType.DOWNLOADED:
                        message = f"{actor} downloaded an item"
                    case _:
                        message = f"{actor} performed an action"

                activity_schema = ActivityHistorySchema(
                    entityType=activity.entityType if isinstance(activity.entityType, str) else activity.entityType.value,
                    action=activity.action if isinstance(activity.action, str) else activity.action.value,
                    newValue=activity.newValue,
                    timestamp=formatTimestamp(activity.timestamp),
                    fieldChanged=activity.fieldChanged,
                    oldValue=activity.oldValue,
                    parentFolderName=activity.parentFolderName,
                    message=message
                )
                
                groupedMap[category].append(activity_schema)

            # Convert to list of { periodName, history }

            groupedList = [
                PeriodHistorySchema(periodName=period, history=history)
                for period, history in groupedMap.items()
            ]

            return ActivityResponseSchema(result=groupedList)

        except Exception as e:
            print(f"Error in getAllActivities: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")