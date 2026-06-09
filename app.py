# 파일명: app.py
import streamlit as st

# 메인 페이지 설정 (이 페이지 자체의 설정입니다)
st.set_page_config(
    page_title="수학 게임 모음",
    page_icon="🎲",
    layout="wide"
)

st.title("🎲 재미있는 수학 게임 월드에 오신 것을 환영합니다! 🎲")

st.markdown("""
### 왼쪽 사이드바에서 게임을 선택해주세요!

---

**👈 사이드바를 열어 게임 목록을 확인하세요.**

준비된 게임:
1.  **🐛 이차함수 지렁이 대모험**: 그래프의 계수를 맞춰 지렁이를 키우세요!
2.  **🎮 Square Root Drop**: 떨어지는 제곱근 식을 계산하여 폭탄을 막으세요!

---
Created by stop1
""")
