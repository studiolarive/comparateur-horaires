import streamlit as st
import openai
import requests
import time

st.set_page_config(page_title="Comparateur PDF (Assistant GPT-4o)", layout="centered")

st.title("📄 Comparateur d'Horaires PDF avec l'Assistant GPT-4o")
st.markdown("Dépose deux fichiers PDF (interne et web), et GPT-4o te dira s’ils sont cohérents.")

api_key = st.text_input("🔑 Clé API OpenAI", type="password")

file1 = st.file_uploader("📁 PDF Interne", type=["pdf"])
file2 = st.file_uploader("📁 PDF Web", type=["pdf"])

def upload_file_to_openai(file, key):
    response = requests.post(
        "https://api.openai.com/v1/files",
        headers={"Authorization": f"Bearer {key}"},
        files={"file": (file.name, file)},
        data={"purpose": "assistants"}
    )
    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception(f"Erreur upload : {response.text}")

if api_key and file1 and file2:
    if st.button("🚀 Lancer la comparaison"):
        with st.spinner("📤 Upload des fichiers..."):
            try:
                id1 = upload_file_to_openai(file1, api_key)
                id2 = upload_file_to_openai(file2, api_key)
            except Exception as e:
                st.error(str(e))
                st.stop()

        with st.spinner("⚙️ Création de l'assistant..."):
            client = openai.OpenAI(api_key=api_key)
            assistant = client.beta.assistants.create(
                name="Comparateur PDF Horaires",
                instructions="Tu es un assistant chargé de comparer deux fichiers PDF contenant des horaires de bus. "
                             "Tu dois signaler les différences ou incohérences, arrêt par arrêt, et ignorer la mise en page.",
                model="gpt-4o"
            )

        with st.spinner("🧠 Analyse en cours (environ 1 minute)..."):
            thread = client.beta.threads.create()

            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=[
                    {
                        "type": "text",
                        "text": "Compare ces deux fichiers PDF d’horaires et signale les différences de contenu."
                    },
                    {
                        "type": "file",
                        "file_id": id1
                    },
                    {
                        "type": "file",
                        "file_id": id2
                    }
                ]
            )

            run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("❌ L'analyse a échoué.")
                    st.stop()
                time.sleep(2)

        with st.spinner("📩 Récupération du résultat..."):
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            final_response = messages.data[0].content[0].text.value
            st.success("✅ Comparaison terminée !")
            st.text_area("💬 Résultat :", final_response, height=400)
else:
    st.info("➡️ Ajoute ta clé API et les deux fichiers pour démarrer.")
