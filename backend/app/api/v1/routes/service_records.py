from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.service import (
    ServiceReceipt,
    ServiceRecord,
)
from app.models.user import User
from app.models.user_vehicle import UserVehicle
from app.schemas.service import (
    ServiceReceiptRead,
    ServiceRecordCreate,
    ServiceRecordRead,
    ServiceRecordUpdate,
)
from app.services.file_storage import (
    ReceiptUploadError,
    delete_stored_receipt,
    resolve_receipt_path,
    save_service_receipt,
)


router = APIRouter()


DbSession = Annotated[
    Session,
    Depends(get_db),
]


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


def require_owned_vehicle(
    db: Session,
    user_id: int,
    vehicle_id: int,
) -> None:
    ownership = db.scalar(
        select(UserVehicle).where(
            UserVehicle.user_id
            == user_id,
            UserVehicle.vehicle_id
            == vehicle_id,
        )
    )

    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Vehicle not found "
                "in My Vehicles"
            ),
        )


def get_owned_service_record(
    db: Session,
    user_id: int,
    vehicle_id: int,
    service_record_id: int,
) -> ServiceRecord:
    record = db.scalar(
        select(ServiceRecord)
        .options(
            selectinload(
                ServiceRecord.receipts
            )
        )
        .where(
            ServiceRecord.id
            == service_record_id,
            ServiceRecord.user_id
            == user_id,
            ServiceRecord.vehicle_id
            == vehicle_id,
        )
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Service record not found"
            ),
        )

    return record


@router.get(
    "/{vehicle_id}/service-records",
    response_model=list[ServiceRecordRead],
)
def list_service_records(
    vehicle_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[ServiceRecord]:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    statement = (
        select(ServiceRecord)
        .options(
            selectinload(
                ServiceRecord.receipts
            )
        )
        .where(
            ServiceRecord.user_id
            == current_user.id,
            ServiceRecord.vehicle_id
            == vehicle_id,
        )
        .order_by(
            ServiceRecord.service_date.desc(),
            ServiceRecord.id.desc(),
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


@router.post(
    "/{vehicle_id}/service-records",
    response_model=ServiceRecordRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service_record(
    vehicle_id: int,
    payload: ServiceRecordCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ServiceRecord:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    record = ServiceRecord(
        user_id=current_user.id,
        vehicle_id=vehicle_id,
        **payload.model_dump(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        record.id,
    )


@router.put(
    "/{vehicle_id}/service-records/{service_record_id}",
    response_model=ServiceRecordRead,
)
def update_service_record(
    vehicle_id: int,
    service_record_id: int,
    payload: ServiceRecordUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ServiceRecord:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    record = get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        service_record_id,
    )

    changes = payload.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(
            record,
            field,
            value,
        )

    db.commit()
    db.refresh(record)

    return get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        service_record_id,
    )


@router.delete(
    "/{vehicle_id}/service-records/{service_record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_record(
    vehicle_id: int,
    service_record_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    record = get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        service_record_id,
    )

    for receipt in record.receipts:
        delete_stored_receipt(
            receipt.stored_path
        )

    db.delete(record)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    (
        "/{vehicle_id}/service-records/"
        "{service_record_id}/receipts"
    ),
    response_model=ServiceReceiptRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_service_receipt(
    vehicle_id: int,
    service_record_id: int,
    file: Annotated[
        UploadFile,
        File(),
    ],
    db: DbSession,
    current_user: CurrentUser,
) -> ServiceReceipt:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    record = get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        service_record_id,
    )

    try:
        stored = await save_service_receipt(
            file,
            user_id=current_user.id,
            vehicle_id=vehicle_id,
            service_record_id=(
                service_record_id
            ),
        )

    except ReceiptUploadError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc

    receipt = ServiceReceipt(
        service_record_id=record.id,
        original_filename=(
            stored.original_filename
        ),
        stored_path=stored.stored_path,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
    )

    db.add(receipt)

    try:
        db.commit()
        db.refresh(receipt)

    except Exception:
        db.rollback()

        delete_stored_receipt(
            stored.stored_path
        )

        raise

    return receipt


@router.get(
    (
        "/{vehicle_id}/service-records/"
        "{service_record_id}/receipts/"
        "{receipt_id}/file"
    ),
    response_class=FileResponse,
)
def open_service_receipt(
    vehicle_id: int,
    service_record_id: int,
    receipt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> FileResponse:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    record = get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        service_record_id,
    )

    receipt = next(
        (
            item
            for item in record.receipts
            if item.id == receipt_id
        ),
        None,
    )

    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    try:
        path = resolve_receipt_path(
            receipt.stored_path
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt file not found",
        ) from exc

    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt file not found",
        )

    return FileResponse(
        path=Path(path),
        media_type=receipt.content_type,
        filename=receipt.original_filename,
        content_disposition_type="inline",
    )


@router.delete(
    (
        "/{vehicle_id}/service-records/"
        "{service_record_id}/receipts/"
        "{receipt_id}"
    ),
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_receipt(
    vehicle_id: int,
    service_record_id: int,
    receipt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    require_owned_vehicle(
        db,
        current_user.id,
        vehicle_id,
    )

    record = get_owned_service_record(
        db,
        current_user.id,
        vehicle_id,
        service_record_id,
    )

    receipt = next(
        (
            item
            for item in record.receipts
            if item.id == receipt_id
        ),
        None,
    )

    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found",
        )

    delete_stored_receipt(
        receipt.stored_path
    )

    db.delete(receipt)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )