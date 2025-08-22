import streamlit as st
import pandas as pd

# 음식/음료별 평균 당류(g) 데이터 (예시)
sugar_db = {
    "콜라 (355ml)": 39,
    "사이다 (355ml)": 37,
    "초코바": 20,
    "아이스크림 (1개)": 24,
    "쿠키 (1개)": 8,
    "케이크 조각": 30,
    "커피믹스 (1봉)": 12,
    "과일주스 (200ml)": 21,
}

WHO_LIMIT = 25  # WHO 권장 일일 섭취량 (g)

st.title("🥤 설탕 섭취량 계산기")
st.write("하루 동안 먹은 음료/과자를 선택하고 개수를 입력하세요.")

# 사용자 입력 받기
user_data = {}
for item, sugar in sugar_db.items():
    qty = st.number_input(f"{item} (1개당 {sugar}g 당류)", min_value=0, step=1)
    if qty > 0:
        user_data[item] = qty * sugar

# 총 섭취량 계산
total_sugar = sum(user_data.values())

st.subheader("📊 결과")
st.write(f"오늘 섭취한 총 당류: **{total_sugar} g**")

# WHO 권장량과 비교
if total_sugar == 0:
    st.info("아직 아무 음식도 선택하지 않았습니다.")
elif total_sugar <= WHO_LIMIT:
    st.success(f"👍 권장 섭취량(25g) 이하로 잘 지켰습니다!")
else:
    st.error(f"⚠️ 권장 섭취량을 초과했습니다! (25g 기준, 현재 {total_sugar - WHO_LIMIT}g 초과)")

# 상세표 보여주기
if user_data:
    st.subheader("🍪 섭취 상세 내역")
    df = pd.DataFrame(user_data.items(), columns=["품목", "섭취한 당류(g)"])
    st.table(df)
