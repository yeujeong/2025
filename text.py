import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="영양 코치", page_icon="🥗", layout="wide")

# -----------------------------
# 기본 데이터 및 유틸 함수
# -----------------------------
ACTIVITY_FACTORS = {
    "비활동(거의 운동 안함)": 1.2,
    "가벼운 활동(주 1-3회)": 1.375,
    "보통 활동(주 3-5회)": 1.55,
    "활동적(주 6-7회)": 1.725,
    "매우 활동적(고강도/육체노동)": 1.9,
}

DEFAULT_MACROS = {"carb": 0.5, "protein": 0.2, "fat": 0.3}

# 간단 샘플 식품 DB (100g 또는 1회 제공 기준)
FOOD_DB = {
    "백미밥(210g/한공기)": {"kcal": 300, "carb": 66, "protein": 6, "fat": 1},
    "현미밥(210g/한공기)": {"kcal": 290, "carb": 62, "protein": 6, "fat": 2},
    "닭가슴살(100g)": {"kcal": 165, "carb": 0, "protein": 31, "fat": 3.6},
    "삶은달걀(1개)": {"kcal": 78, "carb": 0.6, "protein": 6.3, "fat": 5.3},
    "두부(150g)": {"kcal": 120, "carb": 3, "protein": 13, "fat": 7},
    "고등어구이(100g)": {"kcal": 230, "carb": 0, "protein": 20, "fat": 16},
    "사과(1개/200g)": {"kcal": 104, "carb": 27.6, "protein": 0.5, "fat": 0.3},
    "바나나(1개/120g)": {"kcal": 105, "carb": 27, "protein": 1.3, "fat": 0.4},
    "고구마(150g)": {"kcal": 135, "carb": 31, "protein": 2.2, "fat": 0.2},
    "샐러드(한그릇)": {"kcal": 80, "carb": 10, "protein": 4, "fat": 3},
    "우유(200ml)": {"kcal": 130, "carb": 10, "protein": 6.6, "fat": 7.2},
    "요거트 플레인(150g)": {"kcal": 95, "carb": 12, "protein": 5, "fat": 3},
    "아몬드(30g)": {"kcal": 173, "carb": 6, "protein": 6, "fat": 15},
    "식빵(1장/60g)": {"kcal": 160, "carb": 30, "protein": 5, "fat": 2},
}

# BMR: Mifflin-St Jeor

def calc_bmr(sex: str, weight: float, height: float, age: int) -> float:
    if sex == "남성":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def apply_disease_adjustments(disease: str, tdee: float, base_macros: dict):
    """질환별 칼로리/거시영양 비율 조정 및 가이드 텍스트 반환"""
    macros = base_macros.copy()
    kcal = tdee
    guide = []

    if disease == "당뇨":
        # 당질 40~45%, 단백질 20~25%, 지방 30~35% 권장 예시
        macros = {"carb": 0.43, "protein": 0.22, "fat": 0.35}
        guide += [
            "정제 탄수화물(설탕, 흰빵, 과자) 줄이고 복합탄수화물/식이섬유(현미, 채소, 콩) 위주",
            "식사 간격을 일정하게, 과일은 1회 1쪽/1개 내외로 분배",
            "단백질은 살코기·생선·콩류 위주, 불포화지방(견과·올리브유) 활용",
        ]
    elif disease == "고혈압":
        # DASH 스타일, 거시비율 크게 변동 X
        macros = base_macros
        guide += [
            "나트륨 2000mg/day 이하(가공식품·국물류 줄이기)",
            "칼륨·칼슘·마그네슘 풍부한 식품(채소, 과일, 저지방 유제품) 늘리기",
            "포화지방/트랜스지방 줄이고 생선·견과 등 불포화지방 섭취",
        ]
    elif disease == "비만":
        # 15~20% 열량 감량, 단백질 비중 소폭 상향
        kcal = tdee * 0.85
        macros = {"carb": 0.45, "protein": 0.27, "fat": 0.28}
        guide += [
            "총 열량 15~20% 감량을 목표(과도한 절식은 금물)",
            "매 끼니 단백질 포함(근손실 예방), 설탕 음료·야식 줄이기",
            "주 150~300분 유산소 + 2~3회 근력운동 권장",
        ]
    else:
        guide += [
            "가공식품·설탕 섭취 줄이고 채소·통곡·단백질을 균형 있게",
            "불포화지방 위주, 수분 충분히(물 6~8컵)",
        ]

    return kcal, macros, guide


def macro_targets_from_kcal(kcal: float, macros: dict):
    carb_kcal = kcal * macros["carb"]
    protein_kcal = kcal * macros["protein"]
    fat_kcal = kcal * macros["fat"]
    return {
        "kcal": kcal,
        "carb_g": carb_kcal / 4,
        "protein_g": protein_kcal / 4,
        "fat_g": fat_kcal / 9,
    }


def init_state():
    if "log" not in st.session_state:
        st.session_state.log = pd.DataFrame(columns=["날짜", "음식", "양", "kcal", "carb", "protein", "fat"])
    if "target" not in st.session_state:
        st.session_state.target = None
    if "disease" not in st.session_state:
        st.session_state.disease = "해당 없음"


init_state()

# -----------------------------
# 사이드바: 사용자 입력
# -----------------------------
st.sidebar.header("사용자 정보")
col1, col2 = st.sidebar.columns(2)
with col1:
    height = st.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
    age = st.number_input("나이", min_value=10, max_value=100, value=30, step=1)
with col2:
    weight = st.number_input("몸무게 (kg)", min_value=30.0, max_value=250.0, value=65.0, step=0.1)
    sex = st.selectbox("성별", ["남성", "여성"])

activity = st.sidebar.selectbox("활동량", list(ACTIVITY_FACTORS.keys()), index=2)
disease = st.sidebar.selectbox("질환", ["해당 없음", "당뇨", "고혈압", "비만"])
st.session_state.disease = disease

st.sidebar.markdown("---")
st.sidebar.subheader("커스텀 식품 추가")
with st.sidebar.form("add_food"):
    new_name = st.text_input("식품명")
    c_kcal = st.number_input("열량(kcal)", min_value=0.0, value=0.0)
    c_carb = st.number_input("탄수화물(g)", min_value=0.0, value=0.0)
    c_prot = st.number_input("단백질(g)", min_value=0.0, value=0.0)
    c_fat = st.number_input("지방(g)", min_value=0.0, value=0.0)
    submitted = st.form_submit_button("DB에 추가")
    if submitted and new_name:
        FOOD_DB[new_name] = {"kcal": c_kcal, "carb": c_carb, "protein": c_prot, "fat": c_fat}
        st.success(f"'{new_name}' 추가 완료!")

# -----------------------------
# 권장 칼로리 & 영양소 계산
# -----------------------------
bmr = calc_bmr(sex, weight, height, age)
tdee = bmr * ACTIVITY_FACTORS[activity]
rec_kcal, macro_ratio, disease_guide = apply_disease_adjustments(disease, tdee, DEFAULT_MACROS)

st.session_state.target = macro_targets_from_kcal(rec_kcal, macro_ratio)

# 헤더
st.title("🥗 환자 맞춤형 영양 코치")
left, right = st.columns([1.1, 1])

with left:
    st.subheader("1) 오늘의 권장 섭취량")
    st.write(
        f"**하루 권장 칼로리:** {st.session_state.target['kcal']:.0f} kcal  ")
    st.write(
        f"**영양소 비율(탄/단/지):** {int(macro_ratio['carb']*100)}/{int(macro_ratio['protein']*100)}/{int(macro_ratio['fat']*100)} %"
    )
    st.write(
        f"**탄수화물:** {st.session_state.target['carb_g']:.0f} g  |  **단백질:** {st.session_state.target['protein_g']:.0f} g  |  **지방:** {st.session_state.target['fat_g']:.0f} g"
    )

    with st.expander("질환별 식이 가이드"):
        for tip in disease_guide:
            st.markdown(f"- {tip}")

with right:
    st.subheader("BMR/TDEE 계산")
    st.metric("기초대사량(BMR)", f"{bmr:.0f} kcal")
    st.metric("활동대사량(TDEE)", f"{tdee:.0f} kcal")

st.markdown("---")

# -----------------------------
# 섭취 기록 입력
# -----------------------------
st.subheader("2) 오늘 섭취 기록")
log_date = st.date_input("날짜", value=date.today())
food = st.selectbox("음식 선택", list(FOOD_DB.keys()))
amount = st.number_input("섭취량(기준 1회분 대비 배수)", min_value=0.1, value=1.0, step=0.1)

add_col1, add_col2 = st.columns([1, 3])
with add_col1:
    if st.button("기록 추가"):
        info = FOOD_DB[food]
        row = {
            "날짜": log_date,
            "음식": food,
            "양": amount,
            "kcal": info["kcal"] * amount,
            "carb": info["carb"] * amount,
            "protein": info["protein"] * amount,
            "fat": info["fat"] * amount,
        }
        st.session_state.log = pd.concat([st.session_state.log, pd.DataFrame([row])], ignore_index=True)
        st.success("추가되었습니다!")
with add_col2:
    uploaded = st.file_uploader("CSV 업로드(날짜,음식,양,kcal,carb,protein,fat)")
    if uploaded is not None:
        try:
            df_up = pd.read_csv(uploaded)
            # 간단 검증
            required_cols = {"날짜", "음식", "양", "kcal", "carb", "protein", "fat"}
            if required_cols.issubset(set(df_up.columns)):
                df_up["날짜"] = pd.to_datetime(df_up["날짜"]).dt.date
                st.session_state.log = pd.concat([st.session_state.log, df_up], ignore_index=True)
                st.success("업로드 완료!")
            else:
                st.error("컬럼명이 올바르지 않습니다.")
        except Exception as e:
            st.error(f"업로드 오류: {e}")

# 오늘 데이터 필터
log_today = st.session_state.log[st.session_state.log["날짜"] == log_date]

if log_today.empty:
    st.info("아직 오늘 기록이 없습니다. 상단에서 음식을 추가하세요.")
else:
    st.dataframe(log_today.drop(columns=["날짜"]).reset_index(drop=True))

# -----------------------------
# 합계 & 피드백
# -----------------------------
if not log_today.empty:
    totals = log_today[["kcal", "carb", "protein", "fat"]].sum()
    t_kcal = st.session_state.target["kcal"]

    # 진행률
    pct = totals["kcal"] / t_kcal * 100 if t_kcal > 0 else 0
    st.markdown(
        f"### 3) 피드백: 오늘 권장 칼로리의 **{pct:.0f}%** 섭취"
    )

    if pct < 70:
        st.warning("섭취가 다소 부족합니다. 간식 또는 한 끼를 보완해 보세요.")
    elif pct <= 110:
        st.success("아주 좋아요! 권장 범위 내에서 잘 섭취 중입니다.")
    else:
        st.error("권장치를 초과했습니다. 다음 끼니에서 가벼운 선택을 고려해요.")

    # -----------------------------
    # 시각화: 섭취 vs 권장 (칼로리, 거시영양)
    # -----------------------------
    colA, colB = st.columns(2)

    with colA:
        st.subheader("칼로리 비교")
        fig1, ax1 = plt.subplots()
        ax1.bar(["섭취", "권장"], [totals["kcal"], t_kcal])
        ax1.set_ylabel("kcal")
        ax1.set_title("오늘 칼로리 섭취 vs 권장")
        st.pyplot(fig1)

    with colB:
        st.subheader("영양소 비율")
        # 실제 섭취 비율
        actual_macro_kcal = [
            totals["carb"] * 4,
            totals["protein"] * 4,
            totals["fat"] * 9,
        ]
        labels = ["탄수화물", "단백질", "지방"]
        fig2, ax2 = plt.subplots()
        ax2.pie(actual_macro_kcal, labels=labels, autopct="%1.0f%%", startangle=90)
        ax2.set_title("실제 섭취 거시영양 비율")
        ax2.axis("equal")
        st.pyplot(fig2)

    st.subheader("영양소(그램) 비교")
    target_carb = st.session_state.target["carb_g"]
    target_prot = st.session_state.target["protein_g"]
    target_fat = st.session_state.target["fat_g"]

    fig3, ax3 = plt.subplots()
    x = np.arange(3)
    width = 0.35
    ax3.bar(x - width/2, [totals["carb"], totals["protein"], totals["fat"]], width, label="섭취")
    ax3.bar(x + width/2, [target_carb, target_prot, target_fat], width, label="권장")
    ax3.set_xticks(x, labels)
    ax3.set_ylabel("g")
    ax3.set_title("오늘 영양소 섭취 vs 권장")
    ax3.legend()
    st.pyplot(fig3)

# -----------------------------
# 내보내기 / 초기화
# -----------------------------
colx, coly, colz = st.columns([1,1,2])
with colx:
    if st.button("CSV로 내보내기"):
        csv = st.session_state.log.to_csv(index=False).encode("utf-8-sig")
        st.download_button("다운로드", csv, file_name="nutrition_log.csv", mime="text/csv")
with coly:
    if st.button("오늘 기록 초기화"):
        st.session_state.log = st.session_state.log[st.session_state.log["날짜"] != log_date]
        st.experimental_rerun()

st.markdown("""
---
ℹ️ **주의**: 본 앱은 일반적인 건강 정보 제공용이며, 개인의 의학적 진단이나 치료를 대체하지 않습니다. 특정 질환, 약물 복용 중인 경우 전문가와 상담하세요.
""")

