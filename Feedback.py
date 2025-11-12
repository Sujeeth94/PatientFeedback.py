import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# Hidden treatment code
treatment_code = "36c0c05b"

# Get client from query parameters (from QR code)
query_params = st.query_params
client = query_params.get("client", "Unknown")

# Language selector
language = st.selectbox("Choose your language", ["English", "Spanish", "German"])

# Translation dictionary
translations = {
    "English": {
        "title": "Clinical Trial Feedback Form",
        "submit": "Submit",
        "success": "Thank you for your feedback!",
        "warning": "Please select valid options for all questions before submitting.",
        "error": "An error occurred while saving your feedback:",
        "q1": "Have you noticed any new symptoms or changes in your health since your last visit?",
        "q1_desc": "If yes, please describe:",
        "q1_options": ["Yes", "No"],
        "q2": "Are the side effects becoming more or less manageable over time?",
        "q2_options": ["Much More Manageable", "Slightly More Manageable", "No Change", "Slightly Less Manageable", "Much Less Manageable"],
        "q3": "Do you feel physically and emotionally supported during the study?",
        "q3_options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
        "q4": "Has your participation affected your ability to perform daily tasks this week?",
        "q4_options": ["Not at All", "Slightly", "Moderately", "Significantly", "Extremely"],
        "q5": "Are there any specific activities you’ve had to avoid due to the study?",
        "q5_desc": "If yes, please specify:",
        "q5_options": ["Yes", "No"],
        "q6": "Do you feel adequately informed about upcoming procedures or visits?",
        "q6_options": ["Very Well Informed", "Well Informed", "Somewhat Informed", "Poorly Informed", "Not Informed at All"],
        "q7": "Is the study team responsive to your questions or concerns?",
        "q7_options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
        "q8": "What keeps you motivated to continue participating? (Select all that apply)",
        "q8_options": ["Personal health improvement", "Contribution to science", "Support from study staff", "Financial compensation", "Other"],
        "q8_other": "Other (please specify):",
        "q9": "Have you considered dropping out at any point?",
        "q9_desc": "If yes, what made you reconsider?",
        "q9_options": ["Yes", "No"]
    }
    # Add Spanish and German translations here if needed
}

# Use selected language
t = translations[language]
st.title(t["title"])

# Initialize session state
question_keys = [
    "new_symptoms", "new_symptoms_desc",
    "side_effects_manageability",
    "support_feeling",
    "daily_tasks_impact",
    "activities_avoided", "activities_avoided_desc",
    "informed_about_procedures",
    "team_responsiveness",
    "motivation_factors", "motivation_other",
]

for key in question_keys:
    if key not in st.session_state:
        if key == "motivation_factors":
            st.session_state[key] = []
        elif "desc" in key or "other" in key:
            st.session_state[key] = ""
        else:
            st.session_state[key] = None

# Questions
st.radio(t["q1"], t["q1_options"], index=None, key="new_symptoms")
if st.session_state.new_symptoms == t["q1_options"][0]:
    st.text_area(t["q1_desc"], key="new_symptoms_desc")

st.radio(t["q2"], t["q2_options"], index=None, key="side_effects_manageability")
st.radio(t["q3"], t["q3_options"], index=None, key="support_feeling")
st.radio(t["q4"], t["q4_options"], index=None, key="daily_tasks_impact")
st.radio(t["q5"], t["q5_options"], index=None, key="activities_avoided")
if st.session_state.activities_avoided == t["q5_options"][0]:
    st.text_area(t["q5_desc"], key="activities_avoided_desc")
st.radio(t["q6"], t["q6_options"], index=None, key="informed_about_procedures")
st.radio(t["q7"], t["q7_options"], index=None, key="team_responsiveness")
st.multiselect(t["q8"], t["q8_options"], key="motivation_factors")
if "Other" in st.session_state.motivation_factors:
    st.text_input(t["q8_other"], key="motivation_other")

# Submit
if st.button(t["submit"]):
    required_keys = [
        "new_symptoms", "side_effects_manageability", "support_feeling",
        "daily_tasks_impact", "activities_avoided", "informed_about_procedures",
        "team_responsiveness", "motivation_factors"
    ]
    missing = [key for key in required_keys if st.session_state.get(key) in [None, ""]]

    if missing:
        st.warning(t["warning"])
    else:
        response = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Client": client,
            "Treatment Code": treatment_code,
            "Language": language,
            "NewSymptoms": st.session_state.new_symptoms,
            "NewSymptoms Description": st.session_state.new_symptoms_desc,
            "SideEffectsManageability": st.session_state.side_effects_manageability,
            "SupportFeeling": st.session_state.support_feeling,
            "DailyTasksImpact": st.session_state.daily_tasks_impact,
            "ActivitiesAvoided": st.session_state.activities_avoided,
            "ActivitiesAvoided Description": st.session_state.activities_avoided_desc,
            "InformedAboutProcedures": st.session_state.informed_about_procedures,
            "TeamResponsiveness": st.session_state.team_responsiveness,
            "MotivationFactors": ", ".join(st.session_state.motivation_factors),
            "Other": st.session_state.motivation_other,
        }

        try:
            # Load Google Sheets credentials from Streamlit secrets
            gcp = st.secrets["gcp"]
            service_account_info = json.loads(gcp["service_account"])

            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
            gc = gspread.authorize(creds)
            sheet = gc.open_by_key(gcp["sheet_id"]).sheet1

            # Append response
            sheet.append_row(list(response.values()))

            st.session_state.feedback_submitted = True
            for key in question_keys:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        except Exception as e:
            import traceback
            st.error(f"{t['error']} {e}")
            st.text(traceback.format_exc())

if st.session_state.get("feedback_submitted"):
    st.success(t["success"])
    del st.session_state["feedback_submitted"]
