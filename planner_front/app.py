import streamlit as st
from api import signin, signup, get_events, get_event_detail, add_event, update_event, delete_event
from utils import save_token, get_token, clear_token

# 페이지 전환 함수
def navigate(page, event_id=None): # 페이지, 게시물 ID
    st.session_state['page'] = page
    st.session_state['current_event_id'] = event_id
    st.rerun()
    
# 페이지 상태 관리
if 'page' not in st.session_state:
    st.session_state['page'] = 'login' # 초기화면을 로그인 화면으로 설정
if 'current_event_id' not in st.session_state:
    st.session_state['current_event_id'] = None # 게시물 ID 추적
    
st.title("Planner Project")

# 로그인된 경우에만 로그아웃 버튼 표시
if 'token' in st.session_state:
    if st.button("Logout", key="logout_button"):
        clear_token()
        navigate('login')
        
st.write("---")

# 로그인 페이지
if st.session_state['page'] == 'login':
    st.header("로그인")
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        response = signin(email, password)
        if response.get('access_token'): # JWT가 있으면 로그인 성공
            save_token(response['access_token'])
            navigate('list') # 글 목록 페이지 이동
        else:
            st.error("이메일 또는 비밀번호가 잘못되었습니다.")
            
    st.markdown("<br><p>회원이 아니신가요?</p>", unsafe_allow_html=True)
    if st.button("회원가입"):
        navigate('signup')

# 회원가입 페이지
elif st.session_state['page'] == 'signup':
    st.header("회원가입")
    email = st.text_input("이메일")
    name = st.text_input("이름")
    password = st.text_input("비밀번호", type="password")
    if st.button("회원가입"):
        response = signup(email, name, password)
        if response:
            st.success("계정이 생성되었습니다. 로그인 해주세요.")
            navigate('login')
        else:
            st.error("회원가입에 실패했습니다. 다시 시도해주세요.")
            
    st.markdown("<br><p>회원이신가요?</p>", unsafe_allow_html=True)        
    if st.button("로그인"):
        navigate('login')

# 글 목록 페이지
elif st.session_state['page'] == 'list':
    if 'token' not in st.session_state: # JWT가 없다면 로그인
        navigate('login')

    token = get_token()
    
    events = get_events(token)
    
    col1, col2, col3 = st.columns([1.8, 1, 1])  # 버튼 위치 설정
    with col2:
        if st.button("글쓰기", key="create_button"):
            navigate('create')


    if events:
        for event in events:
            st.write("---")
            st.markdown(f"<h5 style='font-size: 20px;'>{event['title'][:10]}</h4>", unsafe_allow_html=True)  # 제목 10자로 자르기
            st.write(event['description'][:20] + "...")  # 내용 20자로 자르기

            if st.button("자세히 보기", key=f"view_{event['id']}"): # 버튼마다 고유 키 부여
                navigate('detail', event_id=event['id'])

# 글 작성 페이지
elif st.session_state['page'] == 'create':
    if 'token' not in st.session_state:
        navigate('login')

    token = get_token()

    st.header("글 작성")
    title = st.text_input("제목")
    content = st.text_area("내용")
    tags = st.text_input("태그")
    location = st.text_input("지역")

    if st.button("저장"):
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] # 쉼표로 구분
        add_event(token, {
            "title": title,
            "description": content,
            "tags": tags_list,
            "location": location
        })
        navigate('list')

    if st.button("목록으로 돌아가기"):
        navigate('list')

# 글 상세보기 페이지
elif st.session_state['page'] == 'detail':
    if 'token' not in st.session_state:
        navigate('login')

    token = get_token()
    event_id = st.session_state['current_event_id'] # 현재 게시물 ID

    if not event_id:
        st.error("글 정보를 찾을 수 없습니다.")
        navigate('list')

    post = get_event_detail(token, event_id)

    if post:
        st.subheader(post['title'])
        
        st.markdown("<br>", unsafe_allow_html=True) # 한 줄 띄우기

        st.markdown("<h6>description</h6>", unsafe_allow_html=True)
        st.write(post['description'])

        st.markdown("<h6>tag</h6>", unsafe_allow_html=True)
        st.write(", ".join(post['tags']))

        st.markdown("<h6>location</h6>", unsafe_allow_html=True)
        st.write(post['location'])

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("수정"):
            navigate('edit', event_id=event_id)
        
        if st.button("삭제"):
            delete_event(token, event_id)
            navigate('list')

    if st.button("목록으로"):
        navigate('list')

# 글 수정 페이지
elif st.session_state['page'] == 'edit':
    if 'token' not in st.session_state:
        navigate('login')

    token = get_token()
    event_id = st.session_state['current_event_id']

    if not event_id:
        st.error("글 정보를 찾을 수 없습니다.")
        navigate('list')

    event = get_event_detail(token, event_id)

    if event:
        st.header("글 수정")
        updated_title = st.text_input("제목", value=event['title'])
        updated_content = st.text_area("내용", value=event['description'])
        updated_tags = st.text_input("태그", value=", ".join(event['tags']))
        updated_location = st.text_input("지역", value=event['location'])

        if st.button("저장"):
            updated_tags_list = [tag.strip() for tag in updated_tags.split(",") if tag.strip()]
            update_event(token, event_id, {
                "title": updated_title,
                "description": updated_content,
                "tags": updated_tags_list,
                "location": updated_location
            })
            navigate('detail', event_id=event_id)

    if st.button("취소"):
        navigate('detail', event_id=event_id)