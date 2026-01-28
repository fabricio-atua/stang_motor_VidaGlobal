import streamlit as st
import os
import base64

from calculo.engine import calcula_premio_grupo
from calculo.taxas import DESCRICOES
from utils.formatacao import moeda


# -----------------------------
# CONFIG LIMITES
# -----------------------------

CAPITAL_MAX_FUNC = 100_000
CAPITAL_MAX_SOCIO = 250_000
VIDAS_MAX = 600


# -----------------------------
# SESSION STATE
# -----------------------------

if "capital_func_txt" not in st.session_state:
    st.session_state.capital_func_txt = "100.000,00"

if "capital_socio_txt" not in st.session_state:
    st.session_state.capital_socio_txt = "200.000,00"

if "erro_func" not in st.session_state:
    st.session_state.erro_func = False

if "erro_socio" not in st.session_state:
    st.session_state.erro_socio = False


# -----------------------------
# FUNÇÕES
# -----------------------------

def moeda_para_float(valor):
    return float(valor.replace(".", "").replace(",", "."))


def formatar_input(key, limite):

    texto = st.session_state[key]

    # mantém só números
    numeros = "".join(filter(str.isdigit, texto))

    if numeros == "":
        st.session_state[key] = "0,00"
        return

    # impede número absurdo digitando
    numeros = numeros[-9:]

    valor_float = int(numeros) / 100

    estourou = False

    if valor_float > limite:
        valor_float = limite
        estourou = True

    valor_formatado = f"{valor_float:,.2f}"
    valor_formatado = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")

    st.session_state[key] = valor_formatado

    if key == "capital_func_txt":
        st.session_state.erro_func = estourou

    if key == "capital_socio_txt":
        st.session_state.erro_socio = estourou


def carregar_logo(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()


def aplicar_css_inputs():
    st.markdown("""
    <style>

    input {
        border-radius: 12px !important;
        background-color: #0e1117 !important;
        border: 1px solid #2c2f36 !important;
        color: white !important;
        padding-left: 42px !important;
    }

    .prefix-rs {
        position: relative;
    }

    .prefix-rs:before {
        content: "R$";
        position: absolute;
        left: 12px;
        top: 9px;
        color: #9aa0a6;
        font-size: 14px;
        pointer-events: none;
    }

    </style>
    """, unsafe_allow_html=True)


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Simulador Vida em Grupo",
    layout="centered"
)

aplicar_css_inputs()


# -----------------------------
# LOGO
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "img", "New_logo.png")

logo_base64 = carregar_logo(logo_path)

st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:12px;">
        <img src="data:image/png;base64,{logo_base64}" width="120">
        <h1 style="margin:0;">Simulador Vida em Grupo</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# =====================================================
# FUNCIONÁRIOS
# =====================================================

st.subheader("Funcionários")

col1, col2 = st.columns(2)

with col1:

    st.markdown("**Quantidade de Vidas**")

    vidas_func = st.number_input(
        "vidas_func",
        min_value=0,
        max_value=VIDAS_MAX,
        value=100,
        step=1,
        label_visibility="collapsed"
    )

    st.caption("Limite máximo: 600 vidas")


with col2:

    st.markdown("**Capital Segurado por Vida**")

    st.text_input(
        "capital_func_txt",
        key="capital_func_txt",
        on_change=formatar_input,
        args=("capital_func_txt", CAPITAL_MAX_FUNC),
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
    "<div style='margin-top:-20px; font-size:16px; color:#ff4b4b;'>Capital máximo permitido: R$ 100.000,00</div>",
    unsafe_allow_html=True
)



# =====================================================
# SÓCIOS
# =====================================================

st.markdown("---")
st.subheader("Sócios")

col3, col4 = st.columns(2)

with col3:

    st.markdown("**Quantidade de Vidas**")

    vidas_socio = st.number_input(
        "vidas_socio",
        min_value=0,
        max_value=VIDAS_MAX,
        value=5,
        step=1,
        label_visibility="collapsed"
    )

    st.caption("Limite máximo: 600 vidas")


with col4:

    st.markdown("**Capital Segurado por Vida**")

    st.text_input(
        "capital_socio_txt",
        key="capital_socio_txt",
        on_change=formatar_input,
        args=("capital_socio_txt", CAPITAL_MAX_SOCIO),
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)

 
    st.markdown(
    "<div style='margin-top:-20px; font-size:16px; color:#ff4b4b;'>Capital máximo permitido: R$ 250.000,00</div>",
    unsafe_allow_html=True
)


# -----------------------------
# COBERTURAS
# -----------------------------

st.markdown("---")

st.subheader("Cobertura Básica")
st.checkbox("MORTE (Obrigatória)", value=True, disabled=True)

st.subheader("Coberturas Adicionais")

opcoes_adicionais = {
    "IEA": DESCRICOES["IEA"],
    "IPA": DESCRICOES["IPA"],
    "IPTA": DESCRICOES["IPTA"],
    "IPDF": DESCRICOES["IPDF"],
    "IPDL": DESCRICOES["IPDL"],
    "AF": DESCRICOES["AF"],
    "DMHO": DESCRICOES["DMHO"],
    "DMH": DESCRICOES["DMH"]
}

adicionais = []

for codigo, descricao in opcoes_adicionais.items():
    if st.checkbox(descricao):
        adicionais.append(codigo)

coberturas = ["MORTE"] + adicionais


# -----------------------------
# BOTÃO CALCULAR
# -----------------------------

st.markdown("---")

if st.button("Calcular Prêmio"):

    capital_func = moeda_para_float(st.session_state.capital_func_txt)
    capital_socio = moeda_para_float(st.session_state.capital_socio_txt)

    total_vidas = vidas_func + vidas_socio

    if total_vidas == 0:
        st.error("Informe pelo menos 1 vida.")

    else:

        premio_func_vida, premio_func_total, detalhes_func = calcula_premio_grupo(
            capital_func, coberturas, vidas_func
        )

        premio_socio_vida, premio_socio_total, detalhes_socios = calcula_premio_grupo(
            capital_socio, coberturas, vidas_socio
        )

        premio_grupo = premio_func_total + premio_socio_total

        st.success("✅ Cotação Gerada com Sucesso")

        # -----------------------------
        # RESUMO
        # -----------------------------

        st.markdown("---")
        st.subheader("Resumo - Prêmios Totais")

        r1, r2, r3 = st.columns(3)

        r1.metric("Prêmio Funcionários", moeda(premio_func_total))
        r2.metric("Prêmio Sócios", moeda(premio_socio_total))
        r3.metric("Prêmio Total do Grupo", moeda(premio_grupo))

        # -----------------------------
        # DETALHAMENTO
        # -----------------------------

        st.markdown("---")
        st.subheader("Detalhamento por Cobertura (por Vida)")

        h1, h2, h3 = st.columns([2, 1.5, 1.5])

        h1.markdown("**Cobertura**")
        h2.markdown("**Funcionários**")
        h3.markdown("**Sócios**")

        for cobertura in detalhes_func.keys():

            taxa = detalhes_func[cobertura]["taxa"]

            premio_func = detalhes_func[cobertura]["premio"]
            premio_soc = detalhes_socios[cobertura]["premio"]

            c1, c2, c3 = st.columns([2, 1.5, 1.5])

            c1.write(
                f"""
                **{cobertura}**  
                <span style='font-size:12px;color:#9aa0a6'>
                Taxa: {taxa*100:.5f}%
                </span>
                """,
                unsafe_allow_html=True
            )

            c2.write(moeda(premio_func))
            c3.write(moeda(premio_soc))

        st.markdown("---")
