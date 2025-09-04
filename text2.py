import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --------------------------
# 페이지 기본 설정
# --------------------------
st.set_page_config(
    page_title="하루 권장 설탕 섭취량 계산기",
    page_icon="🥤",
    layout="wide",
)

st.title("🥤 하루 권장 설탕 섭취량 계산기")
st.write("👉 성별, 연령, 건강 상태에 따라 맞춤형 권장 섭취량을 알려드립니다!")

# --------------------------
# 1. 개인 정보 입력
# --------------------------
st.subheader("👤 개인 정보 입력")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("나이 (세)", min_value=5, max_value=120, value=30)
with col2:
    height = st.number_input("키 (cm)", min_value=100, max_value=220, value=170)
with col3:
    weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200, value=65)

# BMI 계산
bmi = weight / ((height/100) ** 2)
st.write(f"👉 현재 BMI: **{bmi:.1f}**")

# --------------------------
# 2. 성별 / 당뇨 여부 입력
# --------------------------
st.subheader("⚖️ 조건 선택")

col1, col2 = st.columns(2)
with col1:
    gender = st.radio("성별을 선택하세요", ["남성", "여성"])
with col2:
    diabetes = st.checkbox("당뇨병 환자입니다")

# 권장 섭취량 설정
if diabetes:
    limit = 15
elif age < 18:
    limit = 20
elif gender == "남성":
    limit = 36
else:  # 여성
    limit = 25

st.success(f"💡 당신의 하루 권장 설탕 섭취량은 **{limit} g 이하**입니다.")

# --------------------------
# 3. 음식 입력
# --------------------------
st.subheader("🍽 음식 입력")

if "records" not in st.session_state:
    st.session_state.records = []

food = st.text_input("🍪 음식 이름을 입력하세요")
qty = st.number_input("개수/횟수", min_value=1, step=1, value=1)

if st.button("🔍 검색 & 추가"):
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
                st.success(f"✅ {food} 추가 완료! ({sugar*qty} g)")
            else:
                st.error("⚠️ 당류 정보를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
    else:
        st.warning("⚠️ 음식 이름을 입력하세요.")

# --------------------------
# 4. 결과 출력
# --------------------------
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    total_sugar = df["총 당류(g)"].sum()

    st.subheader("📊 섭취 내역")
    st.table(df)

    st.subheader("📈 총 섭취량")
    st.write(f"오늘 섭취한 총 당류: **{total_sugar:.1f} g**")

    progress = min(total_sugar / limit, 1.0)
    st.progress(progress)

    if total_sugar <= limit:
        st.success("👍 권장 섭취량 이하로 잘 지켰습니다!")
    else:
        st.error(f"⚠️ 권장 섭취량({limit} g)을 초과했습니다! ({total_sugar - limit:.1f} g 초과)")
