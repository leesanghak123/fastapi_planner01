from typing import Optional
# datetime: 날짜 시간 정보 계산
# timezone: 시간대 정보 처리
# timedelta: 시간 간격 계산 (1시간, 2시간 등)
from datetime import datetime, timezone, timedelta
import jwt
from jwt.exceptions import InvalidTokenError # JWT 예외처리
from fastapi import HTTPException, status

from ..config import settings # env로 만든 모델
from ..model.token import TokenData # payload 값

# JWT 생성
def create_access_token(
    data: TokenData,
    expire_delta: Optional[timedelta] = None
) -> str: # 이 함수는 문자열 반환
    payload = data.model_dump() # payload값을 dic형태로 변환
    if expire_delta: # 만료시간이 있다면
        expires = datetime.now(timezone.utc) + expire_delta # 현재시간 + 만료시간
    else: # 실행 (현재 코드에서는 전달하고 있지 않음)
        expires = datetime.now(timezone.utc) + timedelta(minutes=15) # 기본 만료시간 15분
        
    payload.update({'exp': expires}) # payload 딕셔너리에 exp라는 키를 추가하고 만료시간을 expires로 설정, exp가 jwt에서 만료시간을 의미
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, settings.SECRET_ALGORITHM)
    return encoded_jwt

# 로그인 후에 들어오는 요청 검증 (매번 호출)
def verify_access_token(
    token: str # str 타입의 token을 입력 받은 후
) -> TokenData: # TokenData 타입으로 return
    
    # 유효하지 않은 Token인 경우
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}, # 클라이언트에게 Bearer 타입의 token을 보내달라는 메시지를 보냄
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.SECRET_ALGORITHM) # decoding
        expires = payload['exp'] # exp 필드 값
        
        # 만료시간이 없으면
        if not expires:
            raise credentials_exception # 유효하지 않다는 알림
        
        # 시간이 더 경과했으면
        if datetime.now(timezone.utc) > datetime.fromtimestamp(expires, timezone.utc): # fromtimestamp: timestamp 값을 받아 datetime 객체로 변환
            raise credentials_exception
        
        # payload에서 exp를 삭제
        # 클라이언트의 exp를 삭제하는 것이 아닌 서버측의 exp를 삭제하는 것 
        # 이미 만료시간은 검증했으니 필요없다고 생각
        # 사실 이 코드에서 이 부분은 삭제해도 됨
        # 애초에 stateless 상태이므로 저장이 안됨
        payload['exp'] = None
        
        return TokenData(**payload) # payload 딕셔너리를 TokenData 모델에 매핑하여 반환
    
    except InvalidTokenError: # decoding이 잘못되는 경우
        raise credentials_exception