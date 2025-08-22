import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

WHO_LIMIT = 25

st.title("🥤 설탕 섭취량 계산기 (웹 검색 버전)")
st.write("음식 이름을 입력하면 네이버 검색에서 당류 정보를 가져옵니다.")

if "records" not in st.session_state:
    st.session_state.records = []

# 사용자 입력
food = st.text_input("🍪 음식 이름 입력")
qty = st.number_input("🍽 섭취 개수/횟수", min_value=1, step=1, value=1)

if st.button("검색 및 추가"):
    if food:
        try:
            # 네이버 검색 URL
            url = f"https://search.naver.com/search.naver?query={food}+당류"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            # 페이지에서 숫자(g) 추출 시도 (단순화된 예시)
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
                st.error("⚠️ 당류 정보를 찾을 수 없습니다. (검색 결과 확인 필요)")
        except Exception as e:
            st.error(f"오류 발생: {e}")
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
