import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import traceback

# -------------------------------
# Get client from query parameters
# -------------------------------
client = st.experimental_get_query_params().get("client", ["Unknown"])[0]

# -------------------------------
# Language selector
# -------------------------------
language = st.selectbox("Choose your language", ["English", "Spanish", "German"])

# -------------------------------
# Translations
# -------------------------------
translations = {
    "English": {
        "title": "Post Clinical Trial Feedback",
        "submit": "Submit",
        "success": "Thank you for your feedback!",
        "warning": "Please select valid options for all required questions before submitting.",
        "error": "An error occurred while saving your feedback:",

        "q1": "Looking back, how would you describe your overall experience in the study?",
        "q1_options": ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"],

        "q2": "What were the most valuable aspects of your participation? (Select all that apply)",
        "q2_options": ["Access to treatment", "Learning about my health", "Interaction with study staff", "Contribution to research", "Other"],
        "q2_other": "Other (please specify):",

        "q3": "Have you noticed any lasting physical or emotional effects since completing the study?",
        "q3_options": ["Yes – Physical", "Yes – Emotional", "No"],
        "q3_desc": "If yes, please describe:",

        "q4": "Have you considered dropping out at any point?",
        "q4_options": ["Yes", "No"],
        "q4_desc": "If yes, please describe:",

        "q5": "Did the study influence your perspective on clinical research or healthcare?",
        "q5_options": ["Very Positively", "Positively", "No Impact", "Negatively", "Very Negatively"],

        "q6": "Would you recommend participating in a study like this to others?",
        "q6_options": ["Definitely", "Probably", "Not Sure", "Probably Not", "Definitely Not"],

        "q7": "What would encourage you to participate in future studies? (Select all that apply)",
        "q7_options": ["Better communication", "More flexible scheduling", "Clearer expectations", "Support services", "Financial incentives", "Other"],
        "q7_other": "Other (please specify):",

        "q8": "What improvements would you suggest for future studies?",
        "q8_desc": "Open-ended:",

        "q9": "Were there any moments during the study that stood out positively or negatively?",
        "q9_desc": "Open-ended:"
    },
    "Spanish": {
        "title": "Ensayo Clínico - Retroalimentación Post-Estudio",
        "submit": "Enviar",
        "success": "¡Gracias por su retroalimentación!",
        "warning": "Por favor seleccione opciones válidas para todas las preguntas obligatorias antes de enviar.",
        "error": "Ocurrió un error al guardar su retroalimentación:",

        "q1": "Mirando hacia atrás, ¿cómo describiría su experiencia general en el estudio?",
        "q1_options": ["Muy Positiva", "Positiva", "Neutral", "Negativa", "Muy Negativa"],

        "q2": "¿Cuáles fueron los aspectos más valiosos de su participación? (Seleccione todos los que correspondan)",
        "q2_options": ["Acceso al tratamiento", "Aprender sobre mi salud", "Interacción con el personal del estudio", "Contribución a la investigación", "Otro"],
        "q2_other": "Otro (por favor especifique):",

        "q3": "¿Ha notado efectos físicos o emocionales duraderos desde que completó el estudio?",
        "q3_options": ["Sí – Físicos", "Sí – Emocionales", "No"],
        "q3_desc": "Si es así, por favor descríbalos:",

        "q4": "¿Ha considerado abandonar el estudio en algún momento?",
        "q4_options": ["Sí", "No"],
        "q4_desc": "Si es así, por favor describa:",

        "q5": "¿El estudio influyó en su perspectiva sobre la investigación clínica o la atención médica?",
        "q5_options": ["Muy Positivamente", "Positivamente", "Sin Impacto", "Negativamente", "Muy Negativamente"],

        "q6": "¿Recomendaría participar en un estudio como este a otros?",
        "q6_options": ["Definitivamente", "Probablemente", "No estoy seguro", "Probablemente no", "Definitivamente no"],

        "q7": "¿Qué le animaría a participar en futuros estudios? (Seleccione todos los que correspondan)",
        "q7_options": ["Mejor comunicación", "Horarios más flexibles", "Expectativas más claras", "Servicios de apoyo", "Incentivos económicos", "Otro"],
        "q7_other": "Otro (por favor especifique):",

        "q8": "¿Qué mejoras sugeriría para futuros estudios?",
        "q8_desc": "Abierto:",

        "q9": "¿Hubo algún momento durante el estudio que se destacara positiva o negativamente?",
        "q9_desc": "Abierto:"
    },
    "German": {
        "title": "Klinische Studie - Feedback nach Abschluss",
        "submit": "Absenden",
        "success": "Vielen Dank für Ihr Feedback!",
        "warning": "Bitte wählen Sie gültige Optionen für alle erforderlichen Fragen aus, bevor Sie absenden.",
        "error": "Beim Speichern Ihres Feedbacks ist ein Fehler aufgetreten:",

        "q1": "Rückblickend, wie würden Sie Ihre Gesamterfahrung in der Studie beschreiben?",
        "q1_options": ["Sehr Positiv", "Positiv", "Neutral", "Negativ", "Sehr Negativ"],

        "q2": "Was waren die wertvollsten Aspekte Ihrer Teilnahme? (Mehrfachauswahl möglich)",
        "q2_options": ["Zugang zur Behandlung", "Über meine Gesundheit lernen", "Interaktion mit dem Studienteam", "Beitrag zur Forschung", "Sonstiges"],
        "q2_other": "Sonstiges (bitte angeben):",

        "q3": "Haben Sie seit Abschluss der Studie anhaltende körperliche oder emotionale Auswirkungen bemerkt?",
        "q3_options": ["Ja – Körperlich", "Ja – Emotional", "Nein"],
        "q3_desc": "Wenn ja, bitte beschreiben:",

        "q4": "Haben Sie jemals darüber nachgedacht, aus der Studie auszusteigen?",
        "q4_options": ["Ja", "Nein"],
        "q4_desc": "Wenn ja, bitte beschreiben:",

        "q5": "Hat die Studie Ihre Perspektive auf klinische Forschung oder das Gesundheitswesen beeinflusst?",
        "q5_options": ["Sehr Positiv", "Positiv", "Keine Auswirkungen", "Negativ", "Sehr Negativ"],

        "q6": "Würden Sie anderen empfehlen, an einer Studie wie dieser teilzunehmen?",
        "q6_options": ["Definitiv", "Wahrscheinlich", "Nicht sicher", "Wahrscheinlich nicht", "Auf keinen Fall"],

        "q7": "Was würde Sie motivieren, an zukünftigen Studien teilzunehmen? (Mehrfachauswahl möglich)",
        "q7_options": ["Bessere Kommunikation", "Flexiblere Terminplanung", "Klarere Erwartungen", "Unterstützungsangebote", "Finanzielle Anreize", "Sonstiges"],
        "q7_other": "Sonstiges (bitte angeben):",

        "q8": "Welche Verbesserungen würden Sie für zukünftige Studien vorschlagen?",
        "q8_desc": "Offen:",

        "q9": "Gab es während der Studie Momente, die positiv oder negativ auffielen?",
        "q9_desc": "Offen:"
    }
}

t = translations[language]

# -------------------------------
# Initialize session state
# -------------------------------
question_keys = [
    "q1", "q2", "q2_other", "q3", "q3_desc", "q4", "q4_desc",
    "q5", "q6", "q7", "q7_other", "q8_desc", "q9_desc"
]

for key in question_keys:
    if key not in st.session_state:
        if key in ["q2", "q7"]:
            st.session_state[key] = []
        elif "desc" in key or "other" in key:
            st.session_state[key] = ""
        else:
            st.session_state[key] = None

# -------------------------------
# Display Questions
# -------------------------------
st.title(t["title"])

st.radio(t["q1"], t["q1_options"], key="q1")

st.multiselect(t["q2"], t["q2_options"], key="q2")
if any(opt in st.session_state.q2 for opt in ["Other", "Otro", "Sonstiges"]):
    st.text_input(t["q2_other"], key="q2_other")

st.radio(t["q3"], t["q3_options"], key="q3")
if st.session_state.q3 not in [None, "No", "Nein", "No", "Nein"]:
    st.text_area(t["q3_desc"], key="q3_desc")

st.radio(t["q4"], t["q4_options"], key="q4")
if st.session_state.q4 in ["Yes", "Sí", "Ja"]:
    st.text_area(t["q4_desc"], key="q4_desc")

st.radio(t["q5"], t["q5_options"], key="q5")
st.radio(t["q6"], t["q6_options"], key="q6")

st.multiselect(t["q7"], t["q7_options"], key="q7")
if any(opt in st.session_state.q7 for opt in ["Other", "Otro", "Sonstiges"]):
    st.text_input(t["q7_other"], key="q7_other")

st.text_area(t["q8"], key="q8_desc")
st.text_area(t["q9"], key="q9_desc")

# -------------------------------
# Google Sheets setup (Sheet2)
# -------------------------------
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_url(st.secrets["sheet"]["url"]).worksheet("Post-Trial")
except Exception as e:
    st.error("❌ Error in Google Sheets setup or authorization:")
    st.text(str(e))
    st.text(traceback.format_exc())
    sheet = None

# -------------------------------
# Add headers to Sheet2 if empty
# -------------------------------
if sheet:
    headers = [
        "Timestamp", "Participant ID / Code", "Language",
        "Overall Experience", "Valuable Aspects", "Valuable Aspects - Other",
        "Lasting Effects", "Lasting Effects - Description",
        "Considered Dropping Out", "Considered Dropping Out - Description",
        "Study Influence on Perspective", "Recommendation Likelihood",
        "Future Participation Encouragement", "Future Participation Encouragement - Other",
        "Suggested Improvements", "Memorable Moments"
    ]
    # Check if sheet is empty (first row)
    if sheet.row_count == 0 or sheet.row_values(1) == []:
        sheet.append_row(headers)

# -------------------------------
# Submit button
# -------------------------------
if st.button(t["submit"]):
    required_keys = ["q1", "q2", "q3", "q4", "q5", "q6", "q7"]
    missing = [k for k in required_keys if st.session_state.get(k) in [None, "", []]]

    if missing:
        st.warning(t["warning"])
    else:
        response = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            client,
            language,
            st.session_state.q1,
            ", ".join(st.session_state.q2),
            st.session_state.get("q2_other", ""),
            st.session_state.q3,
            st.session_state.get("q3_desc", ""),
            st.session_state.q4,
            st.session_state.get("q4_desc", ""),
            st.session_state.q5,
            st.session_state.q6,
            ", ".join(st.session_state.q7),
            st.session_state.get("q7_other", ""),
            st.session_state.get("q8_desc", ""),
            st.session_state.get("q9_desc", "")
        ]

        try:
            sheet.append_row(response)

            # Clear all session keys
            for key in question_keys:
                if key in st.session_state:
                    del st.session_state[key]

            st.success(t["success"])
            st.rerun()

        except Exception as e:
            st.error(f"{t['error']} {e}")
            st.text(traceback.format_exc())






