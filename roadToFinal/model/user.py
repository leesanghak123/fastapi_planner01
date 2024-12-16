from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr
from typing import Optional, List

# 공통 부분
class UserBase(SQLModel):
    email: EmailStr = Field(min_length=10, max_length=50)
    name: str
    
# Table
class User(UserBase, table=True): # UserBase 상속
    # id는 Optional로 자동 할당이 가능하게
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    # '': 무한참조 -> 전방참조
    # Event: event 파일에서 table을 만들기 위해 만든 Model
    events: List['Event'] = Relationship(back_populates='user', cascade_delete=True)
    
# 회원가입
class UserInput(UserBase):
    password: str = Field(min_length=4, max_length=25)
    
# 회원정보 출력
class UserPublic(UserBase):
    id: int
    
# 로그인 입력 모델
class UserSignIn(SQLModel): # name 입력 X -> SQLModel로 따로 상속
    email: EmailStr = Field(min_length=10, max_length=50)
    password: str = Field(min_length=4, max_length=25)