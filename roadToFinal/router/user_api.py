from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm # 로그인 시 사용, 안전하고 오버헤드도 적대~

from ..model.hash_password import HashPassword
from ..model.user import User, UserInput, UserPublic, UserSignIn
from ..database.db import get_session
from ..auth.jwt_handler import create_access_token
from ..model.token import TokenData, TokenResponse

router = APIRouter(
    prefix='/users',
    tags=['users'], # doc에서 확인
)

hashPassword = HashPassword()

# 회원가입
# 응답 모델: UserPublic, 입력 모델: UserInput
@router.post('/signup', response_model=UserPublic)
async def users_sign_up(user: UserInput, session: Session = Depends(get_session)):
    # table로 정의한 model에서 user 찾기 (email이 같은 것), One()은 결과가 업슬 시 예외 발생
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    
    # db_user가 이미 있는 경우
    if(db_user):
        raise HTTPException(status.HTTP_409_CONFLICT, detail='User account with supplied email already exist')
    
    # hash된 비밀번호를 포함하는 딕셔너리
    extra_data = {'hashed_password': hashPassword.create_hash(user.password)}
    
    # model_validate: 입력받은 user와 hashed_password를 병합하여 User 객체 생성
    # UserInput의 password는 User 테이블에서 정의하지 않았기 때문에 저장 X
    db_user = User.model_validate(user, update=extra_data)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # UserPublic 반환
    return db_user


# 로그인
@router.post('/signin', response_model=TokenResponse)
async def users_sign_in(user: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.username)).first()
    
    # db_user가 없다면
    if (not db_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User with supplied email address not exists')
    
    # pw가 맞지 않다면
    if (not hashPassword.verify_hash(user.password, db_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong credentials passed')
    
    # token data 만들기
    access_token = create_access_token(
        TokenData(username = db_user.email) # username에 db_user.email을 넣음
    )
    
    return {
        'access_token': access_token,
        'token_type': 'Bearer'
    }