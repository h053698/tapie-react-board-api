from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models import User, User_Pydantic, UserIn_Pydantic
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_current_user(request: Request):
    session_token = request.cookies.get(settings.COOKIE_NAME)
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Remove 'Bearer ' prefix if present
        if session_token.startswith("Bearer "):
            session_token = session_token[7:]
            
        payload = jwt.decode(session_token, settings.SECRET_KEY, algorithms=["HS256"])
        user = await User.get(id=payload.get("sub"))
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=User_Pydantic)
async def register(user_in: UserIn_Pydantic):
    # Check if username already exists
    user = await User.filter(username=user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if nickname already exists
    user = await User.filter(nickname=user_in.nickname).first()
    if user:
        raise HTTPException(status_code=400, detail="Nickname already registered")

    # Hash the password before storing
    hashed_password = get_password_hash(user_in.password)
    
    user = await User.create(
        username=user_in.username,
        nickname=user_in.nickname,
        password=hashed_password
    )
    return await User_Pydantic.from_tortoise_orm(user)


@router.post("/token")
async def login(response: Response, login_data: LoginRequest):
    user = await User.filter(username=login_data.username).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Set cookie with session token
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    
    return {"message": "Successfully logged in"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User_Pydantic)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return await User_Pydantic.from_tortoise_orm(current_user)
