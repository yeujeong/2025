import streamlit as st

# 앱 제목
st.title("🍭 하루 권장 설탕 섭취량 계산기")

# 사용자 선택
st.subheader("당신은 누구인가요?")
user_type = st.selectbox(
    "대상을 선택하세요:",
    ["남성", "여성", "아동", "당뇨 환자"]
)

# 권장 섭취량 데이터 (WHO 권장 기준 + 의학 자료 참고)
recommended_sugar = {
    "남성": "하루 약 36g 이하 (약 9티스푼)",
    "여성": "하루 약 25g 이하 (약 6티스푼)",
    "아동": "하루 약 20~25g 이하 (나이별 차이 있음)",
    "당뇨 환자": "가능한 한 섭취를 최소화 (권장량 없음, 의사 상담 필요)"
}

# 결과 출력
st.subheader("📝 결과")
st.write(f"**{user_type}**의 하루 권장 설탕 섭취량은:")
st.success(recommended_sugar[user_type])
