import streamlit as st
import openai

st.set_page_config(page_title="Comparateur d'Horaires PDF", layout="centered")

st.title("📄 Comparateur de Fichiers d'Horaires (GPT-4o)")
st.markdown("**Dépose deux fichiers PDF d’horaires (version interne + version web), et l’IA te dira s’ils contiennent les mêmes infos.**")

openai_api_key = st.text_input("🔑 Ta clé API OpenAI", type="password")

uploaded_file_1 = st.file_uploader("📁 Fichier 1 – PDF interne", type=["pdf"])
uploaded_file_2 = st.file_uploader("📁 Fichier 2 – PDF web", type=["pdf"])

if uploaded_file_1 and uploaded_file_2 and openai_api_key:
    if st.button("🚀 Comparer les deux fichiers"):
        with st.spinner("Analyse en cours avec GPT-4o..."):
            try:
                client = openai.OpenAI(api_key=openai_api_key)

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Tu es un assistant rigoureux chargé de comparer deux fichiers PDF contenant des horaires de bus, dans des formats différents. Concentre-toi uniquement sur les horaires, les arrêts, et les directions. Ignore la mise en page. Détaille les différences et incohérences."
                        },
                        {
                            "role": "user",
                            "content": "Voici deux fichiers PDF. Compare-les arrêt par arrêt et dis-moi s'il y a des différences ou des oublis."
                        }
                    ],
                    files=[
                        {"name": uploaded_file_1.name, "content": uploaded_file_1.read()},
                        {"name": uploaded_file_2.name, "content": uploaded_file_2.read()}
                    ],
                    temperature=0.2,
                    max_tokens=3000
                )

                result = response.choices[0].message.content
                st.success("✅ Comparaison terminée !")
                st.markdown("### Résultat de l'analyse :")
                st.text_area("💬 Rapport de comparaison", value=result, height=400)

            except Exception as e:
                st.error(f"Erreur : {e}")
else:
    st.info("➡️ Charge les deux fichiers et entre ta clé API pour lancer la comparaison.")
