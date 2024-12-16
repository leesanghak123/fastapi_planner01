from passlib.context import CryptContext

# schemes: 사용할 알고리즘 선택, auto: 자동 업데이트
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 현재 여기서 self는 사실상 필요 X
class HashPassword():
    # hash화 된 pw 반환
    def create_hash(self, password: str):
        return pwd_context.hash(password)
    
    # boolean을 반환
    def verify_hash(self, password: str, hashed_password: str):
        return pwd_context.verify(password, hashed_password)