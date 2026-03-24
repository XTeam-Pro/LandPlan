"""Маршруты идентификации и доступа"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.bounded_contexts.identity_access.service import AuthService
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Аутентификация"])


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создать новый аккаунт пользователя",
    responses={
        201: {"description": "Пользователь успешно создан"},
        409: {"description": "Email уже существует"},
        422: {"description": "Ошибка валидации"},
    },
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового аккаунта пользователя.

    **Параметры:**
    - **email**: Email пользователя (должен быть уникальным)
    - **password**: Пароль (минимум 8 символов)
    - **full_name**: Полное имя пользователя (опционально)
    - **phone**: Номер телефона (опционально)
    - **role**: Роль пользователя - 'user' или 'company' (по умолчанию: 'user')

    **Возвращает:**
    - ID пользователя, email и роль
    """
    result = AuthService.register(db, user_data)
    return result


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Вход пользователя",
    description="Аутентификация пользователя и получение JWT токенов",
    responses={
        200: {"description": "Вход успешен"},
        401: {"description": "Неверные учётные данные"},
    },
)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя и выдача токенов доступа/обновления.

    **Параметры:**
    - **email**: Email пользователя
    - **password**: Пароль пользователя

    **Возвращает:**
    - **access_token**: JWT токен для API запросов (действителен 24 часа)
    - **refresh_token**: Токен для получения нового токена доступа (действителен 30 дней)
    - **token_type**: Всегда 'bearer'
    """
    return AuthService.login(db, login_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление токена доступа",
    description="Получить новый токен доступа используя токен обновления",
    responses={
        200: {"description": "Токен обновлён"},
        401: {"description": "Неверный токен обновления"},
    },
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Получить новый токен доступа используя токен обновления.

    **Параметры:**
    - **refresh_token**: Действительный токен обновления из входа

    **Возвращает:**
    - Новый токен доступа и токен обновления
    """
    return AuthService.refresh_access_token(request.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход пользователя",
)
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint. Client should discard tokens."""
    return {"message": "Выход выполнен успешно"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
    description="Получить информацию о текущем аутентифицированном пользователе",
)
async def get_me(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Получить информацию о текущем аутентифицированном пользователе.

    **Авторизация:** Требуется (Bearer токен)

    **Возвращает:**
    - Информацию о пользователе (ID, email, роль, статус и т.д.)
    """
    user = AuthService.get_user(db, current_user["user_id"])
    return user
