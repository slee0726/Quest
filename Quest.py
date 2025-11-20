import streamlit as st
import pandas as pd
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -----------------------------
# Google Sheets 인증 (Secrets 사용)
#-------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Streamlit Secrets에서 인증 정보 가져오기
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open("2025 Quality Event").sheet1


# 문제 은행 (20문항)
allQuestions = [
    {"q":"모든 직원이 데이터 무결성과 관련하여 교육받아야 할 기본 원칙은 무엇입니까?",
     "c":["비밀번호를 동료와 공유하는 것","데이터 입력 관행을 무시하는 것","필요할 때 데이터를 수정하는 것","항상 컴퓨터를 잠그는 것"],
     "a":"항상 컴퓨터를 잠그는 것"},
    {"q":"기록을 수정해야 할 경우 어떻게 해야 합니까?",
     "c":["지우개를 사용한다","잘못된 항목을 가로줄로 지우고 올바른 항목을 이니셜과 날짜와 함께 적는다","기록을 완전히 다시 쓴다","무시한다"],
     "a":"잘못된 항목을 가로줄로 지우고 올바른 항목을 이니셜과 날짜와 함께 적는다"},
    {"q":"작업 공간을 떠날 때 데이터 보안을 유지하기 위해 중요한 관행은 무엇입니까?",
     "c":["컴퓨터를 잠근다","문서를 닫는다","그대로 두고 간다","팀에 알린다"],
     "a":"컴퓨터를 잠근다"},
    {"q":"데이터 입력은 언제 기록해야 합니까?",
     "c":["하루가 끝날 때","작업이 수행되는 시점에","기억이 날 때마다","감독자가 있을 때만"],
     "a":"작업이 수행되는 시점에"},
    {"q":"클린룸에서 허용되는 공기 입자 수는 얼마입니까?",
     "c":["<50ea@0.5um","<500ea@0.5um","<200ea@0.5um","<100ea@0.5um"],
     "a":"<100ea@0.5um"},
    {"q":"문서의 변경 이력을 기록하는 이유는 무엇입니까?",
     "c":["변경 사항을 추적하고 책임을 명확히 하기 위해","문서가 오래되었음을 보여주기 위해","문서의 길이를 늘리기 위해","모든 항목을 무시하기 위해"],
     "a":"변경 사항을 추적하고 책임을 명확히 하기 위해"},
    {"q":"클린룸의 적정 온도 범위는 무엇입니까?",
     "c":["15∼20℃","20∼27℃","30∼40℃","25∼35℃"],
     "a":"20∼27℃"},
    {"q":"팀의 주요 책임은 무엇입니까?",
     "c":["이상점의 조사 및 사용 결정","직원 교육","고객 요구사항 수집","생산 계획 수립"],
     "a":"이상점의 조사 및 사용 결정"},
    {"q":"샘플링 후 어떤 조치를 취해야 합니까?",
     "c":["무시한다","문서에 기록하지 않는다","다른 직원에게 알린다","샘플의 무게를 확인하고 최종 무게를 라벨링한다"],
     "a":"샘플의 무게를 확인하고 최종 무게를 라벨링한다"},
    {"q":"OOC(Out of Control)가 발생했을 경우 어떤 조치를 취해야 합니까?",
     "c":["무시한다","DRB 시스템에 등록한다","다른 직원에게 알린다","문서에 기록하지 않는다"],
     "a":"DRB 시스템에 등록한다"},
    {"q":"이상점이 아닌 항목은 무엇입니까?",
     "c":["원재료 투입 중 시스템의 중단","다른 완제품의 라벨을 부착","NMT를 위해 STO를 신청","제품의 파티클이 고객과 협의한 관리선을 초과"],
     "a":"NMT를 위해 STO를 신청"},
    {"q":"이상점이 발견 시 가장 먼저 취해야 할 행동은 무엇입니까?",
     "c":["선임자에게 보고","혼자만 인지함","무시하고 다음 공정을 진행","배치를 폐기하고 다시 시작"],
     "a":"선임자에게 보고"},
    {"q":"DRB 팀이 하지 말아야 할 것은 무엇입니까?",
     "c":["테스트 용도로 생산된 제품의 사용 여부 결정","원재료 수입검사 시 관리선 초과 제품 사용 논의","SPC 검토 시 특이점에 대한 조사","조사 없이 제품을 폐기함"],
     "a":"조사 없이 제품을 폐기함"},
    {"q":"변경점이 적용된 제품은 식별을 위해 (ㅇㅇㅇ, ㅇㅇㅇㅇㅇ)를 진행합니다. 괄호안에 들어갈 알맞은 내용은 무엇입니까?",
     "c":["눈관리, 시스템관리","눈금관리, 배차관리","무검사","육안검사, 정밀검사"],
     "a":"눈관리, 시스템관리"},
    {"q":"변경점에 해당하지 않는 것은 무엇입니까?",
     "c":["담당자의 변경","바코드 로직 변경","생산시 원재료의 배치 변경","ERP 시스템 변경"],
     "a":"생산시 원재료의 배치 변경"},
    {"q":"변경점은 왜 관리하여야 합니까?",
     "c":["배용절감 하기 위해","고객이 하라고 해서","잠재적인 위험 요소를 최소화하기 위해","일거리를 만드려고"],
     "a":"잠재적인 위험 요소를 최소화하기 위해"},
    {"q":"변경점 평가용 제품을 만들기 위해 주의해야 할 사항은 무엇입니까?",
     "c":["모든 요소를 다르게 조절","단독 작업 금지","식전에 작업","비교군 배치와 차이를 최소로 컨트롤"],
     "a":"비교군 배치와 차이를 최소로 컨트롤"},
    {"q":"다음 중 회사 SOP(Standard Operating Procedure, 표준운영절차)에 따라 '양식(templates)과 외부 출처 문서를 제외한 모든 문서'의 검토 주기로 올바른 것은 무엇입니까?",
     "c":["매년 1회","최소 2년마다","최소 3년마다","필요 시에만 검토한다"],
     "a":"최소 3년마다"},
    {"q":"문서 보존관련: SMSPC 내 (단, 양식과 외부출처문서는 제외) 모든 문서의 보존 기한은 얼마입니까?",
     "c":["3년","7년","10년","15년"],
     "a":"15년"},
    {"q":"품질 관리 용어 COPQ의 정확한 의미는 무엇입니까?",
     "c":["Cost of Product Quality (제품 품질 유지비용)","Cost of Poor Quality (품질 불량으로 인한 비용)","Cost of Production Quantity (생산 수량 관련 비용)","Cost of Process Quality (공정 품질 비용)"],
     "a":"Cost of Poor Quality (품질 불량으로 인한 비용)"}
]


# -----------------------------
# CSS 스타일
# -----------------------------
st.markdown("""
    <style>
    body {background-color: #f9f9f9;}
    .main-title {color: #004080; font-size: 36px; font-weight: bold; text-align: center;}
    .card {background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
    .timer {font-size: 24px; color: #ff6600; font-weight: bold;}
    .stButton button {background-color: #004080; color: white; font-size: 18px; border-radius: 8px;}
    .stButton button:hover {background-color: #0066cc;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(layout="wide")
st.markdown('<div class="main-title">2025 전사 품질 퀴즈 이벤트</div>', unsafe_allow_html=True)

# -----------------------------
# 사용자 입력
# -----------------------------
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    name = st.text_input("이름 입력")
    dept = st.text_input("부서 입력")
    emp_id = st.text_input("사번 입력")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if "start_time" in st.session_state:
        elapsed = round(time.time() - st.session_state["start_time"], 1)
        st.markdown(f'<div class="timer">⏱ 경과 시간: {elapsed}초</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="timer">⏱ 준비 중</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.image("logo.png", width=120)

# -----------------------------
# 게임 시작
# -----------------------------
if st.button("게임 시작"):
    if not name or not dept or not emp_id:
        st.error("이름, 부서, 사번을 입력하세요.")
    else:
        st.session_state["start_time"] = time.time()
        st.session_state["questions"] = random.sample(allQuestions, min(8, len(allQuestions)))
        st.session_state["score"] = 0
        st.session_state["current_q"] = 0
        st.session_state["name"] = name
        st.session_state["dept"] = dept
        st.session_state["emp_id"] = emp_id

# -----------------------------
# 퀴즈 진행
# -----------------------------
if "questions" in st.session_state:
    q_index = st.session_state["current_q"]
    if q_index < len(st.session_state["questions"]):
        question = st.session_state["questions"][q_index]
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"문제 {q_index+1}: {question['q']}")
        choice = st.radio("정답 선택", question["c"], key=f"choice_{q_index}")
        if st.button("제출", key=f"submit_{q_index}"):
            if choice == question["a"]:
                st.session_state["score"] += 1
            st.session_state["current_q"] += 1
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        end_time = time.time()
        elapsed = round(end_time - st.session_state["start_time"], 2)
        st.success(f"게임 종료! ✅ 정답 수: {st.session_state['score']} / ⏱ 소요시간: {elapsed}초")

        # 결과 저장
        if st.button("결과 저장"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([
                "2025 Quality Event",
                st.session_state["name"],
                st.session_state["dept"],
                st.session_state["emp_id"],
                st.session_state["score"],
                elapsed,
                timestamp
            ])
            st.success("결과가 Google Sheets에 저장되었습니다!")

# -----------------------------
# 실시간 결과 표시
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 실시간 결과 (순위 포함)")
results = sheet.get_all_records()
results_df = pd.DataFrame(results)

if not results_df.empty:
    results_df = results_df.sort_values(by=["정답 수", "소요시간"], ascending=[False, True]).reset_index(drop=True)
    results_df["순위"] = results_df.index + 1
    st.dataframe(results_df.style.set_properties(**{'background-color': '#e6f2ff'}))
else:
    st.write("아직 결과가 없습니다.")
