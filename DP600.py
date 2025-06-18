import streamlit as st
import pandas as pd
import ast
import os

st.set_page_config(page_title="QCM Formation", layout="centered")
st.title("📘 Questionnaire de formation")

# --- Chargement des données ---
def charger_questions(fichier):
    df = pd.read_excel(fichier)
    df["bonnes_reponses"] = df["bonnes_reponses"].apply(lambda x: ast.literal_eval(str(x)))
    return df

# --- Initialisation ---
if "index_question" not in st.session_state:
    st.session_state.index_question = 0
if "reponses_utilisateur" not in st.session_state:
    st.session_state.reponses_utilisateur = {}

# --- Chargement automatique du fichier ---
fichier_qcm = "question.xlsx"
if os.path.exists(fichier_qcm):
    questions = charger_questions(fichier_qcm)
    total_questions = len(questions)
    index = st.session_state.index_question
    question_actuelle = questions.iloc[index]

    st.markdown(f"**Question {index + 1}/{total_questions} :**")

    # --- Affichage de l'énoncé ---
    if pd.notna(question_actuelle.get("enonce")):
        st.info(question_actuelle["enonce"])

    # --- Affichage de l'image (via URL uniquement) ---
    image_url = question_actuelle.get("image")
    if pd.notna(image_url) and image_url.startswith("http"):
        st.image(image_url, use_column_width=True)

    st.write(question_actuelle["question"])

    options = [question_actuelle[f"choix_{i}"] for i in range(1, 6) if pd.notna(question_actuelle[f"choix_{i}"])]

    # Affichage selon type de question
    if question_actuelle["type_question"] == "choix_unique":
        choix = st.radio("Choisis une réponse :", options, key=f"q_{index}")
        st.session_state.reponses_utilisateur[index] = [options.index(choix) + 1]
    else:
        choix = st.multiselect("Choisis une ou plusieurs réponses :", options, key=f"q_{index}")
        st.session_state.reponses_utilisateur[index] = [options.index(c) + 1 for c in choix]

    # --- Navigation ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Précédent", disabled=index == 0):
            st.session_state.index_question -= 1
    with col2:
        if index < total_questions - 1:
            if st.button("Suivant ➡️"):
                st.session_state.index_question += 1
        else:
            if st.button("✅ Terminer"):
                st.session_state.index_question += 1  # Pour sortir du questionnaire

# --- Résultats ---
elif "index_question" in st.session_state and os.path.exists("question.xlsx"):
    questions = charger_questions("question.xlsx")
    if st.session_state.index_question >= len(questions):
        st.success("QCM terminé ! Voici vos résultats :")
        score = 0

        for idx, row in questions.iterrows():
            bonnes = set(row["bonnes_reponses"])
            utilisateur = set(st.session_state.reponses_utilisateur.get(idx, []))
            if bonnes == utilisateur:
                score += 1

        st.write(f"Score : {score} / {len(questions)}")

        if st.button("🔁 Recommencer"):
            st.session_state.index_question = 0
            st.session_state.reponses_utilisateur = {}


