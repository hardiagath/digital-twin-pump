from fastapi import APIRouter, HTTPException, status
from app.auth import verify_credentials, create_access_token
from app.schemas.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    try:
        valid = verify_credentials(payload.username, payload.password)
    except RuntimeError as e:
        # Server misconfiguration (missing env vars) — not the caller's fault.
        raise HTTPException(status_code=500, detail=str(e))

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(subject=payload.username)
    return TokenResponse(access_token=token, token_type="bearer")
