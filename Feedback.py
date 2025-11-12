import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import traceback

query_params = st.query_params
client = query_params.get("client", "Unknown")

# -------------------------------
# Language selector & translations
# -------------------------------
language = st.selectbox("Choose your language", ["English", "Spanish", "German"])

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
    },
    "Spanish": {
        "title": "Formulario de Retroalimentación del Ensayo Clínico",
        "submit": "Enviar",
        "success": "¡Gracias por su retroalimentación!",
        "warning": "Por favor seleccione opciones válidas para todas las preguntas antes de enviar.",
        "error": "Ocurrió un error al guardar su retroalimentación:",
        "q1": "¿Ha notado nuevos síntomas o cambios en su salud desde su última visita?",
        "q1_desc": "Si es así, por favor descríbalos:",
        "q1_options": ["Sí", "No"],
        "q2": "¿Los efectos secundarios se han vuelto más o menos manejables con el tiempo?",
        "q2_options": ["Mucho más manejables", "Un poco más manejables", "Sin cambios", "Un poco menos manejables", "Mucho menos manejables"],
        "q3": "¿Se siente física y emocionalmente apoyado durante el estudio?",
        "q3_options": ["Totalmente de acuerdo", "De acuerdo", "Neutral", "En desacuerdo", "Totalmente en desacuerdo"],
        "q4": "¿Su participación ha afectado su capacidad para realizar tareas diarias esta semana?",
        "q4_options": ["En absoluto", "Levemente", "Moderadamente", "Significativamente", "Extremadamente"],
        "q5": "¿Ha tenido que evitar actividades específicas debido al estudio?",
        "q5_desc": "Si es así, por favor especifique:",
        "q5_options": ["Sí", "No"],
        "q6": "¿Se siente adecuadamente informado sobre los procedimientos o visitas próximas?",
        "q6_options": ["Muy bien informado", "Bien informado", "Algo informado", "Mal informado", "Nada informado"],
        "q7": "¿El equipo del estudio responde a sus preguntas o inquietudes?",
        "q7_options": ["Siempre", "Frecuentemente", "A veces", "Raramente", "Nunca"],
        "q8": "¿Qué le motiva a seguir participando? (Seleccione todas las que correspondan)",
        "q8_options": ["Mejora de la salud personal", "Contribución a la ciencia", "Apoyo del personal del estudio", "Compensación económica", "Otro"],
        "q8_other": "Otro (por favor especifique):",
        "q9": "¿Ha considerado abandonar el estudio en algún momento?",
        "q9_desc": "Si es así, ¿qué le hizo reconsiderarlo?",
        "q9_options": ["Sí", "No"]
    },
    "German": {
        "title": "Feedbackformular zur klinischen Studie",
        "submit": "Absenden",
        "success": "Vielen Dank für Ihr Feedback!",
        "warning": "Bitte wählen Sie gültige Optionen für alle Fragen aus, bevor Sie absenden.",
        "error": "Beim Speichern Ihres Feedbacks ist ein Fehler aufgetreten:",
        "q1": "Haben Sie seit Ihrem letzten Besuch neue Symptome oder Veränderungen Ihrer Gesundheit bemerkt?",
        "q1_desc": "Wenn ja, bitte beschreiben Sie:",
        "q1_options": ["Ja", "Nein"],
        "q2": "Sind die Nebenwirkungen im Laufe der Zeit besser oder schlechter zu bewältigen?",
        "q2_options": ["Viel besser", "Etwas besser", "Keine Veränderung", "Etwas schlechter", "Viel schlechter"],
        "q3": "Fühlen Sie sich während der Studie körperlich und emotional unterstützt?",
        "q3_options": ["Stimme voll zu", "Stimme zu", "Neutral", "Stimme nicht zu", "Stimme überhaupt nicht zu"],
        "q4": "Hat Ihre Teilnahme Ihre Fähigkeit beeinträchtigt, alltägliche Aufgaben diese Woche zu erledigen?",
        "q4_options": ["Gar nicht", "Leicht", "Mäßig", "Deutlich", "Extrem"],
        "q5": "Gab es bestimmte Aktivitäten, die Sie aufgrund der Studie vermeiden mussten?",
        "q5_desc": "Wenn ja, bitte geben Sie diese an:",
        "q5_options": ["Ja", "Nein"],
        "q6": "Fühlen Sie sich ausreichend über bevorstehende Verfahren oder Besuche informiert?",
        "q6_options": ["Sehr gut informiert", "Gut informiert", "Etwas informiert", "Schlecht informiert", "Gar nicht informiert"],
        "q7": "Reagiert das Studienteam auf Ihre Fragen oder Anliegen?",
        "q7_options": ["Immer", "Oft", "Manchmal", "Selten", "Nie"],
        "q8": "Was motiviert Sie, weiterhin teilzunehmen? (Wählen Sie alle zutreffenden Optionen)",
        "q8_options": ["Verbesserung der eigenen Gesundheit", "Beitrag zur Wissenschaft", "Unterstützung durch das Studienteam", "Finanzielle Entschädigung", "Sonstiges"],
        "q8_other": "Sonstiges (bitte angeben):",
        "q9": "Haben Sie jemals darüber nachgedacht, aus der Studie auszusteigen?",
        "q9_desc": "Wenn ja, was hat Sie zum Weitermachen bewegt?",
        "q9_options": ["Ja", "Nein"]
    }
}
t = translations[language]

# -------------------------------
# Display Questions
# -------------------------------
st.title(t["title"])

st.radio(t["q1"], t["q1_options"], key="new_symptoms", index=None)
if st.session_state.new_symptoms == t["q1_options"][0]:
    st.text_area(t["q1_desc"], key="new_symptoms_desc")

st.radio(t["q2"], t["q2_options"], key="side_effects_manageability", index=None)
st.radio(t["q3"], t["q3_options"], key="support_feeling", index=None)
st.radio(t["q4"], t["q4_options"], key="daily_tasks_impact", index=None)
st.radio(t["q5"], t["q5_options"], key="activities_avoided", index=None)
if st.session_state.activities_avoided == t["q5_options"][0]:
    st.text_area(t["q5_desc"], key="activities_avoided_desc")

st.radio(t["q6"], t["q6_options"], key="informed_about_procedures", index=None)
st.radio(t["q7"], t["q7_options"], key="team_responsiveness", index=None)
st.multiselect(t["q8"], t["q8_options"], key="motivation_factors")
if any(opt in st.session_state.motivation_factors for opt in ["Other", "Otro", "Sonstiges"]):
    st.text_input(t["q8_other"], key="motivation_other")

st.radio(t["q9"], t["q9_options"], key="considered_dropping", index=None)
if st.session_state.considered_dropping == t["q9_options"][0]:
    st.text_area(t["q9_desc"], key="considered_reason")

# -------------------------------
# Google Sheets setup (from secrets)
# -------------------------------
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_url(st.secrets["sheet"]["url"]).sheet1
except Exception as e:
    st.error("❌ Error in Google Sheets setup or authorization:")
    st.text(str(e))
    st.text(traceback.format_exc())
    sheet = None

# -------------------------------
# Submit button
# -------------------------------
if st.button(t["submit"]):
    required_keys = [
        "new_symptoms", "side_effects_manageability", "support_feeling",
        "daily_tasks_impact", "activities_avoided", "informed_about_procedures",
        "team_responsiveness", "motivation_factors", "considered_dropping"
    ]
    missing = [k for k in required_keys if st.session_state.get(k) in [None, ""]]

    if missing:
        st.warning(t["warning"])
    else:
        response = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            client, "36c0c05b", language,
            st.session_state.new_symptoms, st.session_state.get("new_symptoms_desc", ""),
            st.session_state.side_effects_manageability,
            st.session_state.support_feeling,
            st.session_state.daily_tasks_impact,
            st.session_state.activities_avoided, st.session_state.get("activities_avoided_desc", ""),
            st.session_state.informed_about_procedures,
            st.session_state.team_responsiveness,
            ", ".join(st.session_state.motivation_factors),
            st.session_state.get("motivation_other", ""),
            st.session_state.considered_dropping,
            st.session_state.get("considered_reason", "")
        ]

        try:
            sheet.append_row(response)

            # ✅ Mark submission flag
            st.session_state["form_submitted"] = True

        except Exception as e:
            st.error(f"{t['error']} {e}")
            st.text(traceback.format_exc())

# ✅ After button block — handle post-submit UI
if st.session_state.get("form_submitted"):
    st.success(t["success"])
    st.toast(t["success"], icon="✅")

    # ✅ Clear only relevant keys
    for key in [
        "new_symptoms", "new_symptoms_desc", "side_effects_manageability", "support_feeling",
        "daily_tasks_impact", "activities_avoided", "activities_avoided_desc",
        "informed_about_procedures", "team_responsiveness", "motivation_factors",
        "motivation_other", "considered_dropping", "considered_reason"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    # ✅ Remove flag and refresh
    del st.session_state["form_submitted"]
    st.rerun()


        except Exception as e:
            st.error(f"{t['error']} {e}")
            st.text(traceback.format_exc())






