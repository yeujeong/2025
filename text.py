import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.title("🥤 설탕 섭취량 계산기 (맞춤형 버전)")
st.write("개인 신체정보를 입력하면, 맞춤형 설탕 섭취 권장량을 알려드립니다.")

# --------------------------
# 1. 개인 정보 입력
# --------------------------
col1, col2 = st.columns(2)
with col1:
    height = st.number_input("📏 키 (cm)", min_value=100, max_value=220, value=170)
with col2:
    weight = st.number_input("⚖️ 몸무게 (kg)", min_value=30, max_value=200, value=65)

bmi = weight / ((height/100) ** 2)
st.write(f"👉 현재 BMI: **{bmi:.1f}**")

# BMI 해석
if bmi < 18.5:
    st.info("저체중입니다. 혈당 관리와 충분한 영양 섭취가 필요합니다.")
elif 18.5 <= bmi < 23:
    st.success("정상 체중 범위입니다. 당류 섭취를 잘 조절하세요.")
elif 23 <= bmi < 25:
    st.warning("과체중입니다. 당류를 특히 조심해야 합니다.")
else:
    st.error("비만 단계입니다. 혈당 관리가 매우 중요합니다.")

# --------------------------
# 2. 음식 입력 (웹 검색 크롤링)
# --------------------------
if "records" not in st.session_state:
    st.session_state.records = []

food = st.text_input("🍪 음식 이름 입력")
qty = st.number_input("🍽 섭취 개수/횟수", min_value=1, step=1, value=1)

if st.button("검색 및 추가"):
    if food:
        try:
            url = f"https://search.naver.com/search.naver?query={food}+당류"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            text = soup.get_text()
            sugar = None
            for word in text.split():
                if "g" in word:
                    try:
                        sugar = float(word.replace("g", "").strip())
                        break
                    except:
                        continue

            if sugar:
                st.session_state.records.append({
                    "품목": food,
                    "개수": qty,
                    "총 당류(g)": sugar * qty
                })
            else:
                st.error("⚠️ 당류 정보를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.warning("음식 이름을 입력하세요.")

# --------------------------
# 3. 결과 출력
# --------------------------
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    total_sugar = df["총 당류(g)"].sum()

    st.subheader("📊 섭취 내역")
    st.table(df)

    st.subheader("📈 총 섭취량")
    st.write(f"오늘 섭취한 총 당류: **{total_sugar} g**")

    # 권장 기준: WHO 기본 25g
    limit = 25

    if total_sugar <= limit:
        st.success("👍 권장 섭취량 이하로 잘 지켰습니다!")
    else:
        st.error(f"⚠️ 권장 섭취량(25g)을 초과했습니다! ({total_sugar - limit}g 초과)")
