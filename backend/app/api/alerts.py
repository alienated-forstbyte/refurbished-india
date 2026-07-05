from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(select(Alert).where(Alert.user_id == user.id, Alert.enabled == True))
    alerts = result.scalars().all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    alert = Alert(**alert_data.model_dump(), user_id=user.id)
    session.add(alert)
    await session.flush()
    await session.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await session.delete(alert)
