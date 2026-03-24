"""Сервис идентификации и доступа"""

from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError, ConflictError, AuthenticationException
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models import User, UserProfile
from app.schemas.user import UserCreate, UserLogin, TokenResponse


class AuthService:
    """Сервис аутентификации и авторизации"""

    @staticmethod
    def register(db: Session, user_data: UserCreate) -> dict:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ConflictError(f"Пользователь с email {user_data.email} уже существует")

        # Валидация пароля
        if len(user_data.password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")

        # Создание пользователя
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            status="active",
        )

        db.add(user)
        db.flush()  # Получаем user.id

        # Создание профиля пользователя
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)

        return {"id": user.id, "email": user.email, "role": user.role}

    @staticmethod
    def login(db: Session, login_data: UserLogin) -> TokenResponse:
        """Аутентификация пользователя и выдача токенов"""
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise AuthenticationException("Неверный email или пароль")

        if user.status != "active":
            raise AuthenticationException("Аккаунт пользователя неактивен")

        # Создание токенов
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role}
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    def refresh_access_token(refresh_token: str) -> TokenResponse:
        """Обновление токена доступа"""
        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise AuthenticationException("Неверный токен обновления")

        user_id = payload.get("sub")
        role = payload.get("role", "user")

        access_token = create_access_token(data={"sub": user_id, "role": role})
        new_refresh_token = create_refresh_token(
            data={"sub": user_id, "role": role}
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """Получить пользователя по ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValidationError(f"Пользователь с id {user_id} не найден")
        return user
