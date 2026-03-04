import streamlit as st

st.set_page_config(layout="wide")  

st.sidebar.title("Seleção de Produto")

produto = st.sidebar.selectbox(
    "Produto:",
    ["Vida Em Grupo", "Transporte"]
)

if produto == "Vida Em Grupo":
    import vida_app
    vida_app.run()

elif produto == "Transporte":
    import transporte_app
    transporte_app.run()