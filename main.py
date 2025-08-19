import streamlit as st

# MBTI별 직업 추천 데이터
type_jobs = {
    "INTJ": ["전략 기획가", "데이터 과학자", "연구원"],
    "INTP": ["발명가", "소프트웨어 엔지니어", "철학자"],
    "ENTJ": ["기업가", "경영 컨설턴트", "변호사"],
    "ENTP": ["마케터", "방송인", "창업가"],
    "INFJ": ["상담가", "작가", "교육자"],
    "INFP": ["예술가", "심리상담사", "사회복지사"],
    "ENFJ": ["교사", "리더십 코치", "홍보 전문가"],
    "ENFP": ["기자", "홍보 기획자", "배우"],
    "ISTJ": ["회계사", "판사", "군인"],
    "ISFJ": ["간호사", "교사", "행정직"],
    "ESTJ": ["경영자", "정치가", "군 장교"],
    "ESFJ": ["사회복지사", "교사", "간호사"],
    "ISTP": ["기계공학자", "응급구조사", "운동선수"],
    "ISFP": ["패션 디자이너", "예술가", "작곡가"],
    "ESTP": ["영업사원", "스포츠 코치", "기자"],
    "ESFP": ["배우", "연예인", "이벤트 플래너"]
}

# 앱 제목
st.title("🎯 MBTI 기반 직업 추천 사이트")

# 설명
st.write("자신의 MBTI 유형을 선택하면 적절한 직업을 추천해드립니다.")

# 사용자 입력: MBTI 선택
mbti = st.selectbox("당신의 MBTI를 선택하세요:", list(type_jobs.keys()))

# 추천 결과 출력
if mbti:
    st.subheader(f"{mbti} 유형에 적합한 직업 추천:")
    for job in type_jobs[mbti]:
        st.write(f"- {job}")

# 추가 기능: 버튼 눌러 랜덤 추천
import random
if st.button("랜덤으로 다른 직업 추천받기"):
    random_job = random.choice(type_jobs[mbti])
    st.success(f"추가 추천 직업: {random_job}")
