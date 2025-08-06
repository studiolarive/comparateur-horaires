import streamlit as st
import openai
import requests

st.set_page_config(page_title="Comparateur d'Horaires PDF", layout="centered")

st.title("📄 Comparateur de Fichiers d'Horaires (GPT-4o)")
st.markdown("**Dépose deux fichiers PDF d’horaires (version interne + version web), et l’IA te dira s’ils contiennent les mêmes infos.**")

# 🔑 Clé API
openai_api_key = st.text_input("🔑 Ta clé API OpenAI", type="password")

# 📁 Fichiers
uploaded_file_1 = st.file_uploader("📁 Fichier 1 – PDF interne", type=["pdf"])
uploaded_file_2 = st.file_uploader("📁 Fichier 2 – PDF web", type=["pdf"])

def upload_file(file_data, file_name):
    response = requests.post(
        "https://api.openai.com/v1/files",
        headers={"Authorization": f"Bearer {openai_api_key}"},
        files={"file": (file_name, file_data)},
        data={"purpose": "assistants"}
    )
    return response.json()["id"]

if uploaded_file_1 and uploaded_file_2 and openai_api_key:
    if st.button("🚀 Comparer les deux fichiers"):
        with st.spinner("📤 Envoi des fichiers à l'IA..."):
            try:
                # Upload des fichiers et récupération des IDs
                file1_id = upload_file(uploaded_file_1, uploaded_file_1.name)
                file2_id = upload_file(uploaded_file_2, uploaded_file_2.name)

                # Création du message de comparaison
                prompt = (
                    f"Tu dois comparer deux fichiers PDF d’horaires de bus. "
                    f"Ils sont au format PDF (différente mise en page), mais contiennent normalement les mêmes infos. "
                    f"Fais un tableau clair ou une liste des différences ou oublis, arrêt par arrêt."
                )

                # Appel à GPT-4o
                client = openai.OpenAI(api_key=openai_api_key)

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Tu es un assistant rigoureux d’analyse de documents."},
                        {"role": "user", "content": prompt}
                    ],
                    tool_choice="auto",
                    temperature=0.2,
                    max_tokens=2500,
                    file_ids=[file1_id, file2_id]
                )

                result = response.choices[0].message.content
                st.success("✅ Comparaison terminée !")
                st.markdown("### Résultat de l'analyse :")
                st.text_area("💬 Rapport de comparaison", value=result, height=400)

            except Exception as e:
                st.error(f"❌ Erreur : {e}")
else:
    st.info("➡️ Charge les deux fichiers et entre ta clé API pour lancer la comparaison.")
