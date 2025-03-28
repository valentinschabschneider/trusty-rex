from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app import crud
from app.api.deps import AuthDep, DBSessionDep
from app.models import LogbookBase, RecordState, RecordStateBase, RecordStateCreate
from app.utils import DiffNotation, generate_diff, generate_diff_any, generate_diffs

from .schemas import DiffDict, PreviewDiff, RecordStateAmount, RecordStateDiff

router = APIRouter(tags=["logbook"])


@router.post("/logbook", response_model=LogbookBase, dependencies=[AuthDep])
def create_logbook(
    logbook: LogbookBase,
    db: DBSessionDep,
):
    return crud.create_logbook(db, logbook)


@router.get("/logbook", response_model=list[LogbookBase], dependencies=[AuthDep])
def get_logbooks(
    db: DBSessionDep,
):
    return crud.find_all_logbooks(db)


@router.delete("/logbook/{logbook_key}", dependencies=[AuthDep])
def delete_logbook(
    logbook_key: str,
    db: DBSessionDep,
):
    crud.delete_logbook(db, logbook_key)

    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/logbook/{logbook_key}/record",
    response_model=list[RecordStateAmount],
    dependencies=[AuthDep],
)
def get_records(
    logbook_key: str,
    db: DBSessionDep,
):
    return crud.find_all_record_keys(db, logbook_key)


@router.delete(
    "/logbook/{logbook_key}/record/{record_key}",
    dependencies=[AuthDep],
)
def delete_record(
    logbook_key: str,
    record_key: str,
    db: DBSessionDep,
):
    crud.delete_record(db, logbook_key, record_key)

    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/logbook/{logbook_key}/record/{record_key}/state",
    response_model=RecordState,
    dependencies=[AuthDep],
)
def create_record_state(
    logbook_key: str,
    record_key: str,
    new_record_state: RecordStateCreate,
    db: DBSessionDep,
    prevent_no_changes: bool = False,
):
    if prevent_no_changes:
        latest_state = crud.get_latest_record_state(db, logbook_key, record_key)

        if latest_state is not None:
            diff = generate_diff_any(
                latest_state.data,
                new_record_state.data,
            )

            if len(diff.affected_paths) == 0:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="No changes detected",
                )

    return crud.create_record_state(db, logbook_key, record_key, new_record_state)


@router.get(
    "/logbook/{logbook_key}/record/{record_key}/state",
    response_model=list[RecordStateDiff],
    dependencies=[AuthDep],
)
def get_record_states(
    logbook_key: str,
    record_key: str,
    db: DBSessionDep,
    notation: DiffNotation = DiffNotation.python,
):
    return generate_diffs(
        crud.find_record_states(db, logbook_key, record_key), notation
    )


@router.get(
    "/logbook/{logbook_key}/record/{record_key}/state/{record_state_id}",
    response_model=RecordState,
    dependencies=[AuthDep],
)
def get_record_state(
    logbook_key: str,
    record_key: str,
    record_state_id: UUID,
    db: DBSessionDep,
):
    return crud.get_record_state(
        db, logbook_key, record_key, record_state_id
    )


@router.put(
    "/logbook/{logbook_key}/record/{record_key}/state/{record_state_id}",
    response_model=RecordState,
    dependencies=[AuthDep],
)
def update_record_state(
    logbook_key: str,
    record_key: str,
    record_state_id: UUID,
    updated_record_state: RecordStateBase,
    db: DBSessionDep,
):
    return crud.update_record_state(
        db, logbook_key, record_key, record_state_id, updated_record_state
    )


@router.delete(
    "/logbook/{logbook_key}/record/{record_key}/state/{record_state_id}",
    dependencies=[AuthDep],
)
def delete_record_state(
    logbook_key: str,
    record_key: str,
    record_state_id: UUID,
    db: DBSessionDep,
):
    crud.delete_record_state(db, logbook_key, record_key, record_state_id)

    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/logbook/{logbook_key}/record/{record_key}/state/{record_state_id}/compare",
    response_model=DiffDict,
    dependencies=[AuthDep],
)
def get_record_state_compare(
    logbook_key: str,
    record_key: str,
    record_state_id: UUID,
    other_record_state_id: UUID,
    db: DBSessionDep,
    notation: DiffNotation = DiffNotation.python,
):
    diff = generate_diff(
        crud.get_record_state(db, logbook_key, record_key, record_state_id),
        crud.get_record_state(db, logbook_key, record_key, other_record_state_id),
        notation,
    )

    return diff


@router.post(
    "/logbook/{logbook_key}/record/{record_key}/state/preview-diff",
    response_model=DiffDict,
    dependencies=[AuthDep],
)
def preview_diff(
    logbook_key: str,
    record_key: str,
    preview_diff_data: PreviewDiff,
    db: DBSessionDep,
    notation: DiffNotation = DiffNotation.python,
):
    diff = generate_diff_any(
        crud.get_latest_record_state_or_raise(db, logbook_key, record_key).data,
        preview_diff_data.data,
        notation,
    )

    return diff
