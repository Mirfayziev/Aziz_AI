from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import (
    SocialReplyRequest,
    SocialReplyResponse,
    OfficeDocPlanRequest,
    OfficeDocPlanResponse,
    BrainQueryRequest,
    BrainQueryResponse,
)
from ..services.assistant_service import (
    generate_social_reply,
    plan_office_doc,
    brain_query,
)

router = APIRouter(tags=["assistant"])

@router.post("/social-reply", response_model=SocialReplyResponse)
def social_reply(req: SocialReplyRequest, db: Session = Depends(get_db)):
    try:
        return generate_social_reply(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/office-plan", response_model=OfficeDocPlanResponse)
def office_plan(req: OfficeDocPlanRequest, db: Session = Depends(get_db)):
    try:
        return plan_office_doc(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brain-query", response_model=BrainQueryResponse)
def brain_query_endpoint(req: BrainQueryRequest, db: Session = Depends(get_db)):
    try:
        return brain_query(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
