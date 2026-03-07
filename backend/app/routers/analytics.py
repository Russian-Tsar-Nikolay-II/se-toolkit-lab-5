"""Router for analytics endpoints.

Each endpoint performs SQL aggregation queries on the interaction data
populated by the ETL pipeline. All endpoints require a `lab` query
parameter to filter results by lab (e.g., "lab-01").
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import select, func, case
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.item import ItemRecord
from app.models.interaction import InteractionLog
from app.models.learner import Learner

router = APIRouter()


@router.get("/scores")
async def get_scores(
    lab: str = Query(..., description="Lab identifier, e.g. 'lab-01'"),
    session: AsyncSession = Depends(get_session),
):
    """Score distribution histogram for a given lab."""
    lab_title = lab.replace("-", " ").title()
    
    lab_item = (await session.exec(
        select(ItemRecord).where(ItemRecord.title.ilike(f"%{lab_title}%"))
    )).first()
    
    if not lab_item:
        return [
            {"bucket": "0-25", "count": 0},
            {"bucket": "26-50", "count": 0},
            {"bucket": "51-75", "count": 0},
            {"bucket": "76-100", "count": 0},
        ]
    
    tasks = (await session.exec(
        select(ItemRecord).where(ItemRecord.parent_id == lab_item.id)
    )).all()
    
    task_ids = [task.id for task in tasks]
    
    if not task_ids:
        return [
            {"bucket": "0-25", "count": 0},
            {"bucket": "26-50", "count": 0},
            {"bucket": "51-75", "count": 0},
            {"bucket": "76-100", "count": 0},
        ]
    
    bucket_expr = case(
        (InteractionLog.score <= 25, "0-25"),
        (InteractionLog.score <= 50, "26-50"),
        (InteractionLog.score <= 75, "51-75"),
        (InteractionLog.score <= 100, "76-100"),
    ).label("bucket")
    
    query = select(
        bucket_expr,
        func.count(InteractionLog.id).label("count")
    ).where(
        InteractionLog.item_id.in_(task_ids),
        InteractionLog.score.is_not(None)
    ).group_by(bucket_expr)
    
    results = (await session.exec(query)).all()
    
    buckets = {b: 0 for b in ["0-25", "26-50", "51-75", "76-100"]}
    for bucket, count in results:
        buckets[bucket] = count
    
    return [{"bucket": k, "count": v} for k, v in buckets.items()]


@router.get("/pass-rates")
async def get_pass_rates(
    lab: str = Query(..., description="Lab identifier, e.g. 'lab-01'"),
    session: AsyncSession = Depends(get_session),
):
    """Per-task pass rates for a given lab."""
    lab_title = lab.replace("-", " ").title()
    
    lab_item = (await session.exec(
        select(ItemRecord).where(ItemRecord.title.ilike(f"%{lab_title}%"))
    )).first()
    
    if not lab_item:
        return []
    
    tasks = (await session.exec(
        select(ItemRecord).where(ItemRecord.parent_id == lab_item.id)
    )).all()
    
    result = []
    for task in tasks:
        stats = (await session.exec(
            select(
                func.round(func.avg(InteractionLog.score), 1).label("avg_score"),
                func.count(InteractionLog.id).label("attempts")
            ).where(InteractionLog.item_id == task.id)
        )).first()
        
        avg_score, attempts = stats
        if attempts > 0:
            result.append({
                "task": task.title,
                "avg_score": float(avg_score) if avg_score is not None else 0.0,
                "attempts": attempts
            })
    
    return sorted(result, key=lambda x: x["task"])


@router.get("/timeline")
async def get_timeline(
    lab: str = Query(..., description="Lab identifier, e.g. 'lab-01'"),
    session: AsyncSession = Depends(get_session),
):
    """Submissions per day for a given lab."""
    lab_title = lab.replace("-", " ").title()
    
    lab_item = (await session.exec(
        select(ItemRecord).where(ItemRecord.title.ilike(f"%{lab_title}%"))
    )).first()
    
    if not lab_item:
        return []
    
    tasks = (await session.exec(
        select(ItemRecord).where(ItemRecord.parent_id == lab_item.id)
    )).all()
    
    task_ids = [task.id for task in tasks]
    
    if not task_ids:
        return []
    
    # PostgreSQL: to_char возвращает строку, что избегает проблем с типами
    date_column = func.to_char(InteractionLog.created_at, "YYYY-MM-DD").label("date")
    
    query = select(
        date_column,
        func.count(InteractionLog.id).label("submissions")
    ).where(
        InteractionLog.item_id.in_(task_ids)
    ).group_by(date_column).order_by(date_column.asc())
    
    results = (await session.exec(query)).all()
    
    return [
        {"date": date_str, "submissions": count}
        for date_str, count in results
    ]


@router.get("/groups")
async def get_groups(
    lab: str = Query(..., description="Lab identifier, e.g. 'lab-01'"),
    session: AsyncSession = Depends(get_session),
):
    """Per-group performance for a given lab."""
    lab_title = lab.replace("-", " ").title()
    
    lab_item = (await session.exec(
        select(ItemRecord).where(ItemRecord.title.ilike(f"%{lab_title}%"))
    )).first()
    
    if not lab_item:
        return []
    
    tasks = (await session.exec(
        select(ItemRecord).where(ItemRecord.parent_id == lab_item.id)
    )).all()
    
    task_ids = [task.id for task in tasks]
    
    if not task_ids:
        return []
    
    query = select(
        Learner.student_group.label("group"),
        func.round(func.avg(InteractionLog.score), 1).label("avg_score"),
        func.count(InteractionLog.learner_id.distinct()).label("students")
    ).join(
        Learner, InteractionLog.learner_id == Learner.id
    ).where(
        InteractionLog.item_id.in_(task_ids),
        InteractionLog.score.is_not(None),
        Learner.student_group.is_not(None)
    ).group_by(
        Learner.student_group
    ).order_by(
        Learner.student_group.asc()
    )
    
    results = (await session.exec(query)).all()
    
    return [
        {
            "group": group,
            "avg_score": float(avg_score) if avg_score is not None else 0.0,
            "students": students
        }
        for group, avg_score, students in results
    ]