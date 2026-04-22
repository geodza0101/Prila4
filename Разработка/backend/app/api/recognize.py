"""
Recognition endpoints.

Распознавание еды по фото:
1. YOLOv8 (self-hosted) — быстро, дешево, confidence ≥ 0.7 → принимаем.
2. Gemini Vision — fallback, если YOLO неуверен.
3. Ответ — список кандидатов: [{name, grams, kcal, protein, carbs, fat}].
"""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.schemas import RecognizeResponse

router = APIRouter()

# Допустимые типы фото (из ТЗ раздел 2.2.2, способ 1)
_ALLOWED_CONTENT_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp", "image/heic"}
_MAX_PHOTO_BYTES: int = 10 * 1024 * 1024  # 10 МБ — из соображений скорости + CDN


# -----------------------------------------------------------------
# POST /api/recognize/photo
# -----------------------------------------------------------------
@router.post(
    "/photo",
    response_model=RecognizeResponse,
    summary="Распознать еду по фото",
    description=(
        "Загружает фото → YOLOv8 → (fallback) Gemini Vision → "
        "возвращает список распознанных продуктов с оценкой граммовки."
    ),
)
async def recognize_photo(
    photo: UploadFile = File(..., description="JPEG/PNG/WEBP/HEIC, до 10 МБ"),
) -> RecognizeResponse:
    """Пайплайн распознавания. Критерий по ТЗ — <5 сек end-to-end."""
    # --- Валидация типа и размера ---
    if photo.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {photo.content_type}",
        )

    # TODO: стриминг в лимит — сейчас читаем целиком
    blob = await photo.read()
    if len(blob) > _MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Photo too large: {len(blob)} > {_MAX_PHOTO_BYTES} bytes",
        )

    # TODO: pipeline
    #   1. hash(blob) → проверить Redis-кеш, если есть — вернуть
    #   2. yolo_result = await integrations.yolo.detect(blob)
    #   3. if yolo_result.confidence >= 0.7 → собрать RecognizeResponse
    #   4. else: gemini_result = await integrations.gemini.vision(blob)
    #   5. mapping найденных имён → foods table (по name_ru/name_en/embedding)
    #   6. сохранить photo_url в Supabase Storage (private bucket)
    #   7. закешировать результат на 24ч
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="recognize_photo: not implemented",
    )
