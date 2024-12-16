from pydantic import BaseModel

# payload 값 (인증하기 위한 정보)
class TokenData(BaseModel):
    username: str
    
# 유효기간
class Token(TokenData):
    expires: float
    
# 응답 모델
class TokenResponse(BaseModel):
    access_token: str
    token_type: str