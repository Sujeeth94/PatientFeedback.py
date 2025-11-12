import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# Hidden treatment code
treatment_code = "36c0c05b"

# Get client name from URL (QR code)
query_params = st.query_params
client = query_params.get("client", "Unknown")

# Language selector
language = st.selectbox(
    "Choose your language / Elija su idioma / Wählen Sie Ihre Sprache",
    ["English", "Spanish", "German"]
)

# Translation dictionary
translations = {
    "English": {
        "title": "Clinical Trial Feedback Form",
        "intro": "Please answer the following questions based on your experience:",
        "questions": [
            "How satisfied are you with the overall treatment process?",
            "How would you rate the professionalism of the clinical staff?",
            "Was the information provided before the trial clear and understandable?",
            "Was the appointment scheduling convenient for you?",
            "How comfortable were the clinic facilities?",
            "Were your concerns addressed in a timely manner?",
            "How satisfied are you with the communication during the trial?",
            "Did you feel your privacy was respected during the process?",
            "Would you recommend participation in this trial to others?"
        ],
        "comments": "Any additional comments or suggestions?",
        "upload": "Upload your Google Service Account JSON file",
        "submit": "Submit Feedback",
        "thanks": "✅ Thank you! Your feedback has been recorded.",
        "no_file": "⚠️ Please upload your service account JSON file.",
        "no_sheet": "⚠️ Google Sheet URL not found in secrets.",
        "error_sheet": "Cannot submit feedback because the Google Sheet is not accessible."
    },
    "Spanish": {
        "title": "Formulario de Retroalimentación del Ensayo Clínico",
        "intro": "Por favor, responda las siguientes preguntas según su experiencia:",
        "questions": [
            "¿Qué tan satisfecho está con el proceso de tratamiento en general?",
            "¿Cómo calificaría la profesionalidad del personal clínico?",
            "¿Fue clara y comprensible la información proporcionada antes del ensayo?",
            "¿Fue conveniente la programación de las citas para usted?",
            "¿Qué tan cómodas eran las instalaciones de la clínica?",
            "¿Se abordaron sus inquietudes de manera oportuna?",
            "¿Qué tan satisfecho está con la comunicación durante el ensayo?",
            "¿Sintió que se respetó su privacidad durante el proceso?",
            "¿Recomendaría participar en este ensayo a otras personas?"
        ],
        "comments": "¿Algún comentario o sugerencia adicional?",
        "upload": "Suba su archivo JSON de la cuenta de servicio de Google",
        "submit": "Enviar Comentarios",
        "thanks": "✅ ¡Gracias! Sus comentarios han sido registrados.",
        "no_file": "⚠️ Por favor, suba su archivo JSON de cuenta de servicio.",
        "no_sheet": "⚠️ No se encontró la URL de la hoja de Google en los secretos.",
        "error_sheet": "No se puede enviar la retroalimentación porque la hoja de Google no es accesible."
    },
    "German": {
        "title": "Feedbackformular zur Klinischen Studie",
        "intro": "Bitte beantworten Sie die folgenden Fragen basierend auf Ihrer Erfahrung:",
        "questions": [
            "Wie zufrieden sind Sie mit dem gesamten Behandlungsprozess?",
            "Wie bewerten Sie die Professionalität des klinischen Personals?",
            "Waren die vor dem Versuch bereitgestellten Informationen klar und verständlich?",
            "War die Terminplanung für Sie bequem?",
            "Wie komfortabel waren die Klinikeinrichtungen?",
            "Wurden Ihre Bedenken rechtzeitig berücksichtigt?",
            "Wie zufrieden sind Sie mit der Kommunikation während der Studie?",
            "Fühlten Sie sich während des Prozesses in Ihrer Privatsphäre respektiert?",
            "Würden Sie die Teilnahme an dieser Studie anderen empfehlen?"
        ],
        "comments": "Weitere Kommentare oder Vorschläge?",
        "upload": "Laden Sie Ihre Google-Servicekonto-JSON-Datei hoch",
        "submit": "Feedback Absenden",
        "thanks": "✅ Danke! Ihr Feedback wurde gespeichert.",
        "no_file": "⚠️ Bitte laden Sie Ihre Servicekonto-JSON-Datei hoch.",
        "no_sheet": "⚠️ Google-Sheet-URL wurde in den Secrets nicht gefunden.",
        "error_sheet": "Feedback kann nicht gesendet werden, da das Google Sheet nicht zugänglich ist."
    }
}

t = translations[language]

# UI Header
st.title(t["title"])
st.markdown(t["intro"])

# Feedback Questions
responses = []
for i, q in enumerate(t["questions"], 1):
    responses.append(st.slider(f"{i}. {q}", 1, 5, 3))

comments = st.text_area(t["comments"])

# JSON upload
uploaded_file = st.file_uploader(t["upload"], type="json")

# Submit button
if st.button(t["submit"]):
    if uploaded_file is None:
        st.error(t["no_file"])
    else:
        try:
            # Load credentials from uploaded JSON
            creds_dict = json.load(uploaded_file)
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client_g = gspread.authorize(creds)

            # Google Sheet URL from secrets
            sheet_url = st.secrets.get("sheet_url", "")
            if not sheet_url:
                st.error(t["no_sheet"])
            else:
                sheet = client_g.open_by_url(sheet_url).sheet1

                # Prepare data row
                row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    client
                ] + responses + [comments, treatment_code]

                # Append to sheet
                sheet.append_row(row)
                st.success(t["thanks"])

        except Exception as e:
            st.error(f"❌ Error in Google Sheets setup or authorization:\n\n{str(e)}")
