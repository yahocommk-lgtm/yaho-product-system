import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="야호배대지 상품 자동화", page_icon="📦", layout="wide")

CATEGORY_TAGS = [
    (["라면", "냄비", "프라이팬", "조리", "주방", "식기", "밥솥", "믹서"], "편리한 주방 필수템"),
    (["원피스", "티셔츠", "바지", "자켓", "패딩", "니트", "코트", "치마"], "감각적인 데일리 패션 아이템"),
    (["화장품", "크림", "마스크팩", "로션", "선크림", "뷰티", "향수"], "믿고 쓰는 뷰티 아이템"),
    (["가방", "백팩", "파우치", "캐리어", "지갑"], "실용적인 외출·여행 필수템"),
    (["장난감", "완구", "블록", "키즈", "인형"], "아이와 함께하는 즐거운 시간"),
    (["조명", "무드등", "가습기", "히터", "선풍기"], "집안 분위기를 살리는 리빙 아이템"),
]


def pick_category_tag(name: str) -> str:
    for keywords, tag in CATEGORY_TAGS:
        if any(k in name for k in keywords):
            return tag
    return "실용적인 생활용품"


def build_detail_draft(name_cn: str, cost: float, price: int, weight: float, option: str) -> dict:
    tag = pick_category_tag(name_cn)
    opts = [o.strip() for o in option.replace("/", ",").split(",") if o.strip()] if option else []

    features = [f"‣ {name_cn}의 기본기에 충실하면서도 가볍고 실용적인 구성 (무게 약 {weight:.2f}kg)"]
    if opts:
        features.append(f"‣ {', '.join(opts)} 등 원하는 옵션을 선택해 주문 가능")
    if price:
        features.append(f"‣ 판매가 {price:,}원, 합리적인 가격대로 부담 없이 시작하는 상품")
    features.append("‣ 실사용 후기를 반영해 지속적으로 품질을 관리하는 상품입니다.")

    description = (
        f"{name_cn}는 {tag}으로, 현지에서 직접 소싱해 품질을 확인한 뒤 국내로 들여오는 상품입니다. "
        f"일상에서 부담 없이 사용할 수 있는 구성으로, 처음 구매하시는 분도 만족하실 수 있도록 "
        f"핵심 기능 위주로 구성했습니다."
    )

    spec_lines = [f"‣ 중량: 약 {weight:.2f}kg", f"‣ 판매가: {price:,}원"]
    if opts:
        spec_lines.append(f"‣ 선택 가능 옵션: {', '.join(opts)}")
    spec_lines.append("‣ 원산지: 중국 (통관 규정에 따라 표기)")

    caution = (
        "실측 사이즈·색상은 옵션 및 촬영 환경에 따라 차이가 있을 수 있습니다. "
        "소재, 사이즈, KC 인증 등 필수 표기사항은 실제 등록 전 반드시 확인 후 최종 반영해주세요. "
        "전기·유아용품 등 인증이 필요한 품목은 관련 서류를 별도로 준비해주세요."
    )

    return {
        "상품명": f"{name_cn} | {tag}",
        "핵심특징": "\n\n".join(features),
        "상세설명": description,
        "스펙": "\n\n".join(spec_lines),
        "옵션": option or "기본 옵션",
        "주의사항": caution,
    }

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
        if photos:
            st.image([p.getvalue() for p in photos], width=100)

    st.divider()
    st.subheader("② 상세페이지 완성본 만들기")
    if st.button("✨ 상세페이지 완성본 만들기", type="primary"):
        if not name_cn:
            st.warning("중국 상품명을 먼저 입력해주세요.")
        else:
            st.session_state.draft = build_detail_draft(name_cn, cost, price, weight, option)
            st.success("입력하신 상품정보를 바탕으로 상세페이지 내용이 완성되었습니다. 그대로 등록하셔도 되고, 아래에서 다듬으셔도 됩니다.")

    draft = st.session_state.get("draft")
    if draft:
        st.subheader("③ 직원 검수")
        edited = {}
        for k, v in draft.items():
            edited[k] = st.text_area(k, v, key=f"edit_{k}")
        if st.button("✅ 상품 저장"):
            photo_bytes = [p.getvalue() for p in (photos or [])]
            st.session_state.products.append({
                "상품번호": sku,
                "상품명": edited["상품명"],
                "원가(RMB)": cost,
                "판매가(원)": price,
                "옵션": edited["옵션"],
                "사진수": len(photo_bytes),
                "상태": "검수완료",
                "등록일": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.session_state.last_detail = edited
            st.session_state.last_detail_photos = photo_bytes
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
        photos_data = st.session_state.get("last_detail_photos")
        if photos_data:
            st.markdown("## 상품 사진")
            st.image(photos_data, width=220)
        st.markdown("## 주요 특징")
        st.write(detail["핵심특징"])
        st.markdown("## 상품 설명")
        st.write(detail["상세설명"])
        if detail.get("스펙"):
            st.markdown("## 스펙")
            st.write(detail["스펙"])
        st.markdown("## 옵션")
        st.write(detail["옵션"])
        st.markdown("## 구매 전 확인")
        st.write(detail["주의사항"])
    else:
        st.info("상품 등록에서 상세페이지 초안을 먼저 만들어주세요.")

