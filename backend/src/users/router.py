from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, sessionmaker
from src.users.modal import User
from src.database import open_database_session
from src.users.config import pwd_context
from src.users.schema import UserAuthSchema
from src.users.service import (
    authenticate_user_token,
    authenticate_user,
    create_jwt_token,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register")
def register_user(user: UserAuthSchema, db: Session = Depends(open_database_session)):
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/me")
def get_current_user(user=Depends(authenticate_user_token)):
    return {"username": user.username}


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(open_database_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    #     )
    access_token = create_jwt_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}
