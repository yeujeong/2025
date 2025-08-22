import streamlit as st
import requests
import pandas as pd

WHO_LIMIT = 25
API_KEY = "여기에_식품안전나라_API_키_입력"  

st.title("🥤 설탕 섭취량 계산기")
st.write("음식 이름을 입력하면 자동으로 당류(g)를 불러옵니다.")

if "records" not in st.session_state:
    st.session_state.records = []

# 음식 입력
food = st.text_input("🍪 음식 이름 입력")
qty = st.number_input("🍽 섭취 개수/횟수", min_value=1, step=1, value=1)

if st.button("검색 및 추가"):
    if food:
        # 식품안전나라 API 호출
        url = f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/I2790/json/1/5/DESC_KOR={food}"
        response = requests.get(url).json()

        try:
            item = response["I2790"]["row"][0]
            sugar = float(item["NUTR_CONT11"])  # 당류(g)
            
            st.session_state.records.append({
                "품목": item["DESC_KOR"],
                "개수": qty,
                "총 당류(g)": sugar * qty
            })
        except:
            st.error("⚠️ 해당 음식 정보를 찾을 수 없습니다.")
    else:
        st.warning("음식 이름을 입력하세요.")

# 결과 출력
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    total_sugar = df["총 당류(g)"].sum()

    st.subheader("📊 섭취 내역")
    st.table(df)

    st.subheader("📈 총 섭취량")
    st.write(f"오늘 섭취한 총 당류: **{total_sugar} g**")

    if total_sugar <= WHO_LIMIT:
        st.success("👍 WHO 권장 섭취량(25g) 이하로 잘 지켰습니다!")
    else:
        st.error(f"⚠️ 권장 섭취량 초과! ({total_sugar - WHO_LIMIT}g 초과)")
