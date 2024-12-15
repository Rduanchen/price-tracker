from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.database import open_database_session
from src.users.modal import User
from src.users.config import pwd_context
from src.users.schema import oauth2_scheme
from src.news.modal import user_news_association_table
from fastapi import Depends
from datetime import datetime, timedelta

from jose import JWTError, jwt


def get_article_upvote_data(article_id, user_id, db):
    total_upvotes = (
        db.query(user_news_association_table)
        .filter_by(news_article_id=article_id)
        .count()
    )
    user_voted = False
    if user_id:
        user_voted = (
            db.query(user_news_association_table)
            .filter_by(news_article_id=article_id, user_id=user_id)
            .first()
            is not None
        )
    return total_upvotes, user_voted


def authenticate_user_token(
    token=Depends(oauth2_scheme), db=Depends(open_database_session)
):
    payload = jwt.decode(token, "1892dhianiandowqd0n", algorithms=["HS256"])
    return db.query(User).filter(User.username == payload.get("sub")).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# FIXME: Problem might here
def authenticate_user(db, username, password):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return False


def create_jwt_token(data, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "1892dhianiandowqd0n", algorithm="HS256")
    return encoded_jwt
