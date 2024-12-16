from fastapi import APIRouter, Depends, HTTPException, status, Header, Response
from sqlmodel import Session, select
from typing import List

from ..model.user import User
from ..model.event import Event, EventPublic, EventInput, EventUpdate, EventPublicWithUser
from ..database.db import get_session
from ..auth.authenticate import authenticate

router = APIRouter(
    prefix='/event',
    tags=['event'],
)

# 작성
@router.post('/', response_model=EventPublic)
async def insert_new_event(
    event: EventInput, # 초기값을 가지지 않는 이 코드를 제일 위로 (아니면 *, 사용)
    user: User = Depends(authenticate),
    session: Session = Depends(get_session
)):
    # event 모델과, user.id를 이용해서 model 생성
    db_event = Event.model_validate(event, update={'user_id': user.id})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

# 전체 조회
@router.get('/', response_model=List[EventPublic])
async def get_event_list(user: User = Depends(authenticate)):
    return user.events

# 상세 보기
@router.get('/{id}', response_model=EventPublicWithUser)
async def get_event(id: int, user: User = Depends(authenticate)):
    for event in user.events:
        if event.id == id:
            return event
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Authorized event with supplied id is not found'
    )

# 삭제
@router.delete('/{id}')
async def delete_event(id: int, user: User = Depends(authenticate), session: Session = Depends(get_session)):
    for event in user.events:
        if event.id == id:
            user.events.remove(event) # user 객체의 events 리스트에서 event를 제거, cascade 옵션에 의해서 event도 제거됨
            session.add(user)
            session.commit()
            return {
                'ok' : True
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Authorized event with supplied id is not found'
    )
    
# 수정
@router.put('/{id}', response_model=EventPublic)
async def update_event(id: int, event: EventUpdate, user: User = Depends(authenticate), session: Session = Depends(get_session)):
    for user_event in user.events:
        if user_event.id == id:
            # dump: 값을 dic으로 변환
            # exclude_unset=True: 변경된 값만 수정
            event_data = event.model_dump(exclude_unset=True)
            
            # 여기서 교수님이 말씀하신 문제점
            # SQLAlchemy Session이 스프링에서 영속성 컨테이너와 비슷한 개념인데
            # user와 관계를 맺는 event를 바꾸고 user를 더티채킹 하였기 때문에
            # SQLAlchemy가 event까지 추적을 못할 수 있다
            # 이게 SQLAlchemy의 설정에 따라 다르다
            # 해결방법1. user_event를 add 해준다
            # 해결방법2. cascade 설정에서 save-update를 해준다
            # 근데 이 코드에서 되는 이유 : cascade
            # 관계를 설정하면, user.events를 통해 불러온 event 객체는 자동으로 user와 동일한 세션에서 관리
            # 부모 객체와 동일한 세션에서 관리된다는 뜻(user와 event가 세션에 존재)
            user_event.sqlmodel_update(event_data) # 더티채킹
            session.add(user)
            session.commit()
            return user_event
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Authorized event with supplied id is not found'
    )