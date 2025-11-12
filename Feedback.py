import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import traceback
import json

# -------------------------------
# Hidden treatment code & client
# -------------------------------
treatment_code = "36c0c05b"
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
        "success": "✅ Thank you for your feedback!",
        "warning": "⚠️ Please select valid options for all questions before submitting.",
        "error": "❌ An error occurred while saving your feedback:",
        "upload": "Upload your Google Service Account JSON file",
        "sheet_url_label": "Enter your Google Sheet URL",
        "sheet_missing": "⚠️ Google Sheet URL is missing.",
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
        "success": "✅ ¡Gracias por su retroalimentación!",
        "warning": "⚠️ Por favor seleccione opciones válidas para todas las preguntas antes de enviar.",
        "error": "❌ Ocurrió un error al guardar su retroalimentación:",
        "upload": "Suba su archivo JSON de la cuenta de servicio de Google",
        "sheet_url_label": "Ingrese la URL de su hoja de Google",
        "sheet_missing": "⚠️ Falta la URL de la hoja de Google.",
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
        "success": "✅ Vielen Dank für Ihr Feedback!",
        "warning": "⚠️ Bitte wählen Sie gültige Optionen für alle Fragen aus, bevor Sie absenden.",
        "error": "❌ Beim Speichern Ihres Feedbacks ist ein Fehler aufgetreten:",
        "upload": "Laden Sie Ihre Google-Servicekonto-JSON-Datei hoch",
        "sheet_url_label": "Geben Sie die URL Ihrer Google-Tabelle ein",
        "sheet_missing": "⚠️ Google-Sheet-URL fehlt.",
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
# Display form
# -------------------------------
st.title(t["title"])
st.divider()

st.radio(t["q1"], t["q1_options"], key="q1")
if st.session_state.q1 == t["q1_options"][0]:
    st.text_area(t["q1_desc"], key="q1_desc")

st.radio(t["q2"], t["q2_options"], key="q2")
st.radio(t["q3"], t["q3_options"], key="q3")
st.radio(t["q4"], t["q4_options"], key="q4")
st.radio(t["q5"], t["q5_options"], key="q5")
if st.session_state.q5 == t["q5_options"][0]:
    st.text_area(t["q5_desc"], key="q5_desc")

st.radio(t["q6"], t["q6_options"], key="q6")
st.radio(t["q7"], t["q7_options"], key="q7")
st.multiselect(t["q8"], t["q8_options"], key="q8")
if any(opt in st.session_state.q8 for opt in ["Other", "Otro", "Sonstiges"]):
    st.text_input(t["q8_other"], key="q8_other")

st.radio(t["q9"], t["q9_options"], key="q9")
if st.session_state.q9 == t["q9_options"][0]:
    st.text_area(t["q9_desc"], key="q9_desc")

st.divider()

# -------------------------------
# Upload credentials + Sheet URL
# -------------------------------
uploaded_file = st.file_uploader(t["upload"], type="json")
sheet_url = st.text_input(t["sheet_url_label"])

# -------------------------------
# Submit
# -------------------------------
if st.button(t["submit"]):
    if not uploaded_file:
        st.error("⚠️ Please upload your service account JSON file.")
    elif not sheet_url:
        st.error(t["sheet_missing"])
    else:
        try:
            creds_dict = json.load(uploaded_file)
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
            gc = gspread.authorize(creds)
            sheet = gc.open_by_url(sheet_url).sheet1

            data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client, language, treatment_code,
                st.session_state.q1, st.session_state.q1_desc,
                st.session_state.q2, st.session_state.q3, st.session_state.q4,
                st.session_state.q5, st.session_state.q5_desc,
                st.session_state.q6, st.session_state.q7,
                ", ".join(st.session_state.q8), st.session_state.q8_other,
                st.session_state.q9, st.session_state.q9_desc
            ]

            sheet.append_row(data)
            st.success(t["success"])
        except Exception as e:
            st.error(f"{t['error']} {e}")
            st.text(traceback.format_exc())
