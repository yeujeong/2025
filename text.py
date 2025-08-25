import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --------------------------
# 페이지 기본 설정
# --------------------------
st.set_page_config(
    page_title="설탕 섭취량 계산기",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
        color: #333333;
    }
    .sugar-box {
        background: #f0f9ff;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #90caf9;
        margin-bottom: 15px;
    }
    .result-box {
        background: #fff3e0;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #ffcc80;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# 제목
# --------------------------
st.markdown("<h1 style='text-align: center;'>🥤 맞춤형 설탕 섭취량 계산기</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>개인 신체정보와 섭취 음식을 입력하면 오늘의 설탕 섭취 상태를 알려드립니다!</p>", unsafe_allow_html=True)
st.markdown("---")

# --------------------------
# 1. 개인 정보 입력
# --------------------------
st.markdown("### 👤 개인 신체 정보 입력")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("🎂 나이", min_value=5, max_value=120, value=30)
with col2:
    height = st.number_input("📏 키 (cm)", min_value=100, max_value=220, value=170)
with col3:
    weight = st.number_input("⚖️ 몸무게 (kg)", min_value=30, max_value=200, value=65)

# BMI 계산
bmi = weight / ((height/100) ** 2)
st.markdown(f"<div class='sugar-box'>👉 현재 BMI: <span class='big-font'>{bmi:.1f}</span></div>", unsafe_allow_html=True)

# BMI 해석
if bmi < 18.5:
    st.info("저체중입니다. 혈당 관리와 충분한 영양 섭취가 필요합니다.")
elif 18.5 <= bmi < 23:
    st.success("정상 체중 범위입니다. 당류 섭취를 잘 조절하세요.")
elif 23 <= bmi < 25:
    st.warning("과체중입니다. 당류를 특히 조심해야 합니다.")
else:
    st.error("비만 단계입니다. 혈당 관리가 매우 중요합니다.")

# 나이에 따른 피드백
if age < 18:
    st.warning("⚠️ 아동·청소년은 성장기에 있어 당류 과다 섭취 시 비만 및 당뇨 위험이 큽니다.")
elif 18 <= age < 65:
    st.info("✅ 성인은 하루 25g 이하의 자유당 섭취를 권장합니다.")
else:
    st.warning("⚠️ 노인의 경우 합병증 예방을 위해 당류 섭취에 특히 주의해야 합니다.")

st.markdown("---")

# --------------------------
# 2. 음식 입력
# --------------------------
st.markdown("### 🍽 음식 입력")

if "records" not in st.session_state:
    st.session_state.records = []

col1, col2 = st.columns([2,1])
with col1:
    food = st.text_input("🍪 음식 이름 입력")
with col2:
    qty = st.number_input("🍴 개수/횟수", min_value=1, step=1, value=1)

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

st.markdown("---")

# --------------------------
# 3. 결과 출력
# --------------------------
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    total_sugar = df["총 당류(g)"].sum()

    st.markdown("### 📊 섭취 내역")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📈 총 섭취량")
    st.markdown(f"<div class='result-box'>오늘 섭취한 총 당류: <span class='big-font'>{total_sugar:.1f} g</span></div>", unsafe_allow_html=True)

    # 권장 기준 (WHO)
    limit = 25

    # 프로그레스바 표시
    progress = min(total_sugar / limit, 1.0)
    st.progress(progress)

    if total_sugar <= limit:
        st.success("👍 권장 섭취량 이하로 잘 지켰습니다!")
    else:
        st.error(f"⚠️ 권장 섭취량(25g)을 초과했습니다! ({total_sugar - limit:.1f} g 초과)")
