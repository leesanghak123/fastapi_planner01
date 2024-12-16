from sqlmodel import Field, Relationship, SQLModel, Column, JSON
from typing import Optional, List

from .user import User, UserPublic

# 공통 부분
class EventBase(SQLModel):
    title: str = Field(index=True)
    description: str
    # JSON 문자열로 Column에 넣기
    # 리스트나 딕셔너리 같은 복잡한 구조를 JSON에 바꿔서 저장
    tags: List[str] = Field(sa_column=Column(JSON))
    location: str
    
# Table
class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='user.id')
    # events: user 파일에서 table을 만들기 위해 만든 Model
    user: User = Relationship(back_populates='events')
    
# 출력
class EventPublic(EventBase):
    id: int
    
# 상세보기
class EventPublicWithUser(EventPublic):
    user: UserPublic

# 입력
class EventInput(EventBase):
    pass # 공통과 같음
    
# 업데이트 (Null값이 들어갈 수 있기 때문에 Optional)
class EventUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None