from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import Role, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def check_duplicates(
        self,
        email: str,
        mobile_number: Optional[str] = None,
        seller_code: Optional[str] = None,
        sponsor_code: Optional[str] = None,
        udid_number: Optional[str] = None,
    ) -> Optional[User]:
        conditions = [User.email == email]
        if mobile_number:
            conditions.append(User.mobile_number == mobile_number)
        if seller_code:
            conditions.append(User.seller_code == seller_code)
        if sponsor_code:
            conditions.append(User.sponsor_code == sponsor_code)
        if udid_number:
            conditions.append(User.udid_number == udid_number)
        return self.db.query(User).filter(or_(*conditions)).first()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
