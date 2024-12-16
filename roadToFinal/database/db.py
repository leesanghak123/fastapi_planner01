from sqlmodel import SQLModel, Session, create_engine

from ..model import user, event # 테이블을 만들기 위함

SQLITE_FILE = 'database.db'
SQLITE_URL = f'sqlite:///{SQLITE_FILE}' # 파일에 저장
SQLITE_MEM_URL = f'sqlite:///:memory:' # 메모리 상에 저장

# SQL는 단일 쓰레드에서만 연결을 허용
# fastapi는 비동기로 작동 시 여러 쓰레드가 세션에 접근하여 오류 발생
# check_same_thread: False: 하나의 쓰레드만 사용하는 것을 false
connect_args = {"check_same_thread": False}
# echo=True: DB 실행문 보여주기
engine = create_engine(SQLITE_URL, echo=True, connect_args=connect_args)

# DB와 table 생성 (application 시작 시점에 발생)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
# CRUD 작업에 필요한 Session을 생성
def get_session():
    with Session(engine) as session: # 새로운 세션을 생성 후, with: 자동 종료
        yield session # 세션 반환(종료)