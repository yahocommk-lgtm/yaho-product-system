import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="야호배대지 상품 자동화", page_icon="📦", layout="wide")

if "products" not in st.session_state:
    st.session_state.products = []

st.title("📦 야호배대지 상품 자동화 시스템")
st.caption("촬영 → 상품정보 → 상세페이지 초안 → 검수 → 판매등록 준비")

menu = st.sidebar.radio("메뉴", ["상품 등록", "상품 관리", "상세페이지 미리보기"])

if menu == "상품 등록":
    st.header("① 상품 등록 / 촬영")
    col1, col2 = st.columns(2)
    with col1:
        name_cn = st.text_input("중국 상품명")
        sku = st.text_input("상품번호", value=f"YH-{datetime.now():%Y%m%d-%H%M%S}")
        cost = st.number_input("중국 원가 (RMB)", min_value=0.0, step=1.0)
        option = st.text_input("옵션", placeholder="예: 화이트 / 2인용")
    with col2:
        weight = st.number_input("중량 (kg)", min_value=0.0, step=0.1)
        price = st.number_input("한국 판매가격 (원)", min_value=0, step=1000)
        photos = st.file_uploader("상품 사진 업로드", type=["jpg","jpeg","png","webp"], accept_multiple_files=True)

    st.divider()
    st.subheader("② AI 상세페이지 초안")
    if st.button("✨ AI 상세페이지 초안 만들기", type="primary"):
        if not name_cn:
            st.warning("중국 상품명을 먼저 입력해주세요.")
        else:
            st.session_state.draft = {
                "상품명": f"{name_cn} | 실용적인 생활용품",
                "핵심특징": "실용적인 디자인과 편리한 사용성을 중심으로 구성한 상품입니다.",
                "상세설명": "상품의 주요 특징과 사용 방법을 고객이 이해하기 쉽게 설명하는 영역입니다.",
                "옵션": option or "기본 옵션",
                "주의사항": "실제 상품의 소재, 사이즈, 인증 및 주의사항을 확인한 후 최종 등록하세요."
            }
            st.success("상세페이지 초안이 생성되었습니다. 실제 AI API 연결 시 사진·상품정보를 기반으로 자동 생성할 수 있습니다.")

    draft = st.session_state.get("draft")
    if draft:
        st.subheader("③ 직원 검수")
        edited = {}
        for k, v in draft.items():
            edited[k] = st.text_area(k, v, key=f"edit_{k}")
        if st.button("✅ 상품 저장"):
            st.session_state.products.append({
                "상품번호": sku,
                "상품명": edited["상품명"],
                "원가(RMB)": cost,
                "판매가(원)": price,
                "옵션": edited["옵션"],
                "사진수": len(photos or []),
                "상태": "검수완료",
                "등록일": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.session_state.last_detail = edited
            st.success("상품이 저장되었습니다.")

elif menu == "상품 관리":
    st.header("상품 관리")
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info("다음 개발 단계에서 네이버·쿠팡 API를 연결해 '판매채널 등록' 버튼으로 자동 등록할 수 있습니다.")
    else:
        st.info("등록된 상품이 없습니다.")

elif menu == "상세페이지 미리보기":
    st.header("상세페이지 미리보기")
    detail = st.session_state.get("last_detail")
    if detail:
        st.markdown(f"# {detail['상품명']}")
        st.markdown("## 주요 특징")
        st.write(detail["핵심특징"])
        st.markdown("## 상품 설명")
        st.write(detail["상세설명"])
        st.markdown("## 옵션")
        st.write(detail["옵션"])
        st.markdown("## 구매 전 확인")
        st.write(detail["주의사항"])
    else:
        st.info("상품 등록에서 상세페이지 초안을 먼저 만들어주세요.")
