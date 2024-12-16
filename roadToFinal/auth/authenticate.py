# 만들어진 jwt의 payload에서 유저 정보를 들고와서 해당 사용자 조회
# 요청 시 마다 파싱하면 비효율적이라서
from fastapi import Depends, HTTPException, status # 의존성 주입, 예외 처리
from fastapi.security import OAuth2PasswordBearer # Authorization 헤더에서 Bearer 토큰을 추출
from sqlmodel import Session, select

from ..database.db import get_session
from ..model.user import User
from .jwt_handler import verify_access_token # 토큰 검증

# tokenUrl: 로그인
# Bearer 토큰 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/signin')

# 의존성을 주입 후 User 타입으로 반환
async def authenticate(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
    ) -> User:
    # Token이 없는 경우 401 Unauthorized
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'} # 클라이언트에게 Bearer 타입의 token을 보내달라는 메시지를 보냄
        )
        
    # Token을 검증하여 payload를 파싱하고 token_data에 저장
    token_data = verify_access_token(token)
    
    # token_data가 없거나, token_datatoken_data에 username 속성이 없다면
    if not token_data or not hasattr(token_data, 'username'): # hasattr: 객체가 특정 속성을 가지고 있는지 확인
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token data',
            headers={'WWW-authenticate': 'Bearer'} 
        )
        
    # DB에서 조회
    # 로그인 입력 모델이 email, Token 입력 모델은 username -> 그래서 email과 username을 비교
    db_user = session.exec(select(User).where(User.email == token_data.username)).first()
    
    # 유저 정보가 없는 경우 403 Forbidden
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials'
        )
        
    return db_user