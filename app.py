from models.llm import get_chatgroq_model
from utils.rag_utils import retrieve_docs
from utils.web_search import web_search
from utils.response_mode import build_prompt
from utils.symptom_checker import analyze_symptoms
from utils.vectorstore_loader import get_vectorstore
from datetime import datetime
import streamlit as st
import random
import re
import pandas as pd

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="wide"
)


# ----------------------------------------------------
# RESPONSIVE CSS + JS
# ----------------------------------------------------

st.markdown("""
<style>

/* GLOBAL BACKGROUND */

body{
background:linear-gradient(120deg,#e3f2fd,#fce4ec,#e8f5e9);
background-size:300% 300%;
animation:gradientMove 12s ease infinite;
}

@keyframes gradientMove{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

/* MAIN CONTAINER */

.block-container{
max-width:1200px;
padding-top:2rem;
padding-bottom:2rem;
}

/* HEADER TITLE */

h1{
color:#0d47a1;
text-shadow:0px 3px 8px rgba(0,0,0,0.2);
}

/* HEALTH CARD */

.health-card{
background:linear-gradient(135deg,#ffffff,#e3f2fd);
padding:25px;
border-radius:16px;
box-shadow:0px 8px 20px rgba(0,0,0,0.15);
margin-bottom:25px;
transition:all 0.3s ease;
}

.health-card:hover{
transform:translateY(-6px);
box-shadow:0px 14px 30px rgba(0,0,0,0.25);
}

/* CHAT BUBBLES */

[data-testid="stChatMessage"]{
border-radius:12px;
padding:12px;
margin-bottom:10px;
box-shadow:0px 3px 8px rgba(0,0,0,0.1);
}

/* USER CHAT */

[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]){
background:#e3f2fd;
}

/* AI CHAT */

[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]){
background:#f1f8e9;
}

/* FLOATING HELP BUTTON */

.floating-help{
position:fixed;
bottom:25px;
right:25px;
background:linear-gradient(45deg,#ff4b4b,#ff8a80);
color:white;
padding:14px 20px;
border-radius:30px;
font-weight:bold;
cursor:pointer;
box-shadow:0px 10px 20px rgba(0,0,0,0.3);
z-index:9999;
transition:all 0.3s;
}

.floating-help:hover{
transform:scale(1.1);
box-shadow:0px 12px 28px rgba(0,0,0,0.4);
}

/* DAILY TIP */

.health-tip{
position:fixed;
top:90px;
left:10px;
background:linear-gradient(120deg,#f1f8e9,#ffffff);
padding:12px;
border-radius:12px;
width:220px;
box-shadow:0px 4px 12px rgba(0,0,0,0.2);
font-size:14px;
}

/* METRIC GLOW */

[data-testid="stMetric"]{
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 5px 15px rgba(0,0,0,0.15);
transition:all 0.3s;
}

[data-testid="stMetric"]:hover{
transform:scale(1.05);
box-shadow:0px 8px 22px rgba(0,0,0,0.3);
}

/* BUTTON STYLE */

.stButton button{
background:linear-gradient(45deg,#1e88e5,#42a5f5);
color:white;
border:none;
border-radius:8px;
font-weight:bold;
padding:8px 18px;
transition:all 0.3s;
}

.stButton button:hover{
background:linear-gradient(45deg,#1565c0,#1e88e5);
transform:scale(1.05);
}

/* INPUT BOX */

.stTextInput input{
border-radius:8px;
border:1px solid #90caf9;
box-shadow:0px 2px 6px rgba(0,0,0,0.1);
}

/* MOBILE RESPONSIVE */

@media (max-width:768px){

.block-container{
padding-left:1rem;
padding-right:1rem;
}

h1{font-size:24px !important;}
h2{font-size:20px !important;}
p{font-size:15px !important;}

}

</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# HEADER
# ----------------------------------------------------

st.title("🩺 AI Healthcare Assistant")

st.image(
"https://chatlms.s3.ap-south-1.amazonaws.com/image_health.png",
caption="AI Healthcare Assistant",
width=1000
)

st.write(
"An intelligent chatbot that analyzes symptoms, retrieves medical knowledge, "
"and searches the web to provide helpful health guidance."
)


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

st.sidebar.title("Settings")

response_mode = st.sidebar.selectbox(
"Response Mode",
["Concise","Detailed"]
)

st.sidebar.markdown("---")

st.sidebar.info(
"⚠️ Educational medical guidance only.\n"
"Not a replacement for professional doctors."
)


tips = [
"💧 Drink 2-3 liters of water daily.",
"🥗 Eat fruits and vegetables.",
"🚶 Walk 30 minutes every day.",
"😴 Sleep at least 7-8 hours.",
"🦟 Prevent mosquito bites.",
"🧼 Wash hands frequently."
]

if "daily_tip" not in st.session_state:
    st.session_state.daily_tip = random.choice(tips)

st.sidebar.markdown("### 🌿 Daily Health Tip")
st.sidebar.success(st.session_state.daily_tip)



# ----------------------------------------------------
# HEALTH METRICS
# ----------------------------------------------------

st.markdown('<div class="health-card">',unsafe_allow_html=True)

col1,col2,col3=st.columns(3)

with col1:
    st.metric("🦟 Dengue Risk Areas","100+ Countries")

with col2:
    st.metric("🌍 Population at Risk","50%")

with col3:
    st.metric("🧪 Annual Cases","100M+")

st.markdown('</div>',unsafe_allow_html=True)



# ----------------------------------------------------
# LOAD MODEL
# ----------------------------------------------------

@st.cache_resource
def load_model():
    return get_chatgroq_model()

chat_model=load_model()



# ----------------------------------------------------
# LOAD VECTOR STORE
# ----------------------------------------------------

@st.cache_resource
def load_vectorstore():
    return get_vectorstore()

vectorstore=load_vectorstore()



# ----------------------------------------------------
# RISK SCORE EXTRACTOR
# ----------------------------------------------------

def extract_risk_score(text):

    match = re.search(r"Risk Score[: ]*(\d+)", text)

    if match:
        return min(int(match.group(1)),100)

    return 30



# ----------------------------------------------------
# PROMPT TEMPLATE
# ----------------------------------------------------

prompt_template=build_prompt(response_mode)



# ----------------------------------------------------
# TABS
# ----------------------------------------------------

tab1,tab2,tab3=st.tabs([
"💬 Chat Assistant",
"🧪 Symptom Checker",
"🔎 Medical Search",
])



# ====================================================
# TAB 1 CHATBOT
# ====================================================

with tab1:

    if "messages" not in st.session_state:
        st.session_state.messages=[]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input=st.chat_input("Describe your symptoms or ask a health question...")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):

            with st.spinner("Analyzing your query..."):

                symptom_analysis=analyze_symptoms(chat_model,user_input)

                risk_score = extract_risk_score(symptom_analysis)

                st.progress(risk_score)

                rag_context=retrieve_docs(user_input,vectorstore)

                web_results=web_search(user_input)

                final_prompt=f"""
System Prompt:
{prompt_template}

User Query:
{user_input}

Symptom Analysis:
{symptom_analysis}

Medical Knowledge Base:
{rag_context}

Web Search Results:
{web_results}

Provide structured medical guidance.
"""

                response=chat_model.invoke(final_prompt)

                ai_response=response.content

                st.markdown(ai_response)

                # chart_data=pd.DataFrame({"Risk":[risk_score]})
                # st.bar_chart(chart_data)

                report=f"""
AI HEALTH REPORT
Date: {datetime.now()}

User Symptoms:
{user_input}

Analysis:
{ai_response}

Risk Score: {risk_score}
"""

                st.download_button(
                    label="📄 Download Medical Report",
                    data=report,
                    file_name="health_report.txt",
                    mime="text/plain"
                )

                if "High" in symptom_analysis:
                    st.error("🚨 HIGH RISK: Seek medical attention immediately")

                elif "Moderate" in symptom_analysis:
                    st.warning("⚠️ MODERATE RISK: Monitor symptoms and consult doctor")

                else:
                    st.success("🟢 LOW RISK: Rest, hydration, monitoring recommended")

        st.session_state.messages.append({"role":"assistant","content":ai_response})



# ====================================================
# TAB 2 SYMPTOM CHECKER
# ====================================================

with tab2:

    st.subheader("🧪 Quick Symptom Checker")

    fever=st.checkbox("Fever")
    headache=st.checkbox("Headache")
    body_pain=st.checkbox("Body Pain")
    vomiting=st.checkbox("Vomiting")
    rash=st.checkbox("Skin Rash")

    if st.button("Check Symptoms"):

        symptoms=[]

        if fever: symptoms.append("fever")
        if headache: symptoms.append("headache")
        if body_pain: symptoms.append("body pain")
        if vomiting: symptoms.append("vomiting")
        if rash: symptoms.append("skin rash")

        if symptoms:

            symptom_text=", ".join(symptoms)

            st.info(f"Symptoms detected: {symptom_text}")

            result=analyze_symptoms(chat_model,symptom_text)

            st.success(result)

        else:
            st.warning("Please select at least one symptom.")



# ====================================================
# TAB 3 MEDICAL SEARCH
# ====================================================

with tab3:

    st.subheader("🔎 Search Medical Knowledge")

    search_query=st.text_input("Enter disease or symptom")

    if st.button("Search"):

        if search_query:

            docs=retrieve_docs(search_query,vectorstore)

            web=web_search(search_query)

            st.markdown("### 🌐 Web Results")
            st.write(docs)

        else:
            st.warning("Please enter a search query.")
