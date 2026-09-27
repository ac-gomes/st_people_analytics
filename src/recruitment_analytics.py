import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.components.components import kpi_card

# ==================================================
# TEMA
# ==================================================

COLORS = ['#4a90d9', '#7ed321', '#f5a623', '#e94560']

BG_COLOR = '#0d1117'
CARD_COLOR = '#161b22'
GRID_COLOR = '#30363d'
TEXT_COLOR = '#c9d1d9'
TICK_COLOR = '#8b949e'

# ==================================================
# CACHE
# ==================================================

@st.cache_data
def load_data():

    recrutamento = pd.read_csv(
        "data/tb_recrutamento.csv"
    )

    colaboradores = pd.read_csv(
        "data/tb_colaboradores.csv"
    )

    desempenho = pd.read_csv(
        "data/tb_desempenho.csv"
    )

    jornada = pd.read_csv(
        "data/tb_jornada.csv"
    )

    recrutamento["Data_Abertura_Vaga"] = pd.to_datetime(
        recrutamento["Data_Abertura_Vaga"]
    )

    recrutamento["Data_Admissao"] = pd.to_datetime(
        recrutamento["Data_Admissao"]
    )

    colaboradores["Data_Admissao"] = pd.to_datetime(
        colaboradores["Data_Admissao"]
    )

    df = (
        recrutamento
        .merge(
            colaboradores,
            on="ID_Colaborador",
            how="left",
            suffixes=("_REC", "_COL")
        )
        .merge(
            desempenho,
            on="ID_Colaborador",
            how="left"
        )
    )

    absenteismo = (
        jornada
        .groupby("ID_Colaborador")
        .agg(
            Horas_Ausentes=("Horas_Ausentes", "sum"),
            Horas_Contratuais=("Horas_Contratuais", "sum")
        )
        .reset_index()
    )

    absenteismo["Absenteismo"] = (
        absenteismo["Horas_Ausentes"]
        /
        absenteismo["Horas_Contratuais"].replace(0, 1)
    ) * 100

    df = df.merge(
        absenteismo[
            ["ID_Colaborador", "Absenteismo"]
        ],
        on="ID_Colaborador",
        how="left"
    )

    return df

# ==================================================
# PAGE
# ==================================================

def run():

    df = load_data()

    # ==========================================
    # SIDEBAR
    # ==========================================

    with st.sidebar:

        st.title("🎯 Recruitment Analytics")

        fontes = (
            ["Todas"]
            +
            sorted(
                df["Fonte_Aquisicao"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        fonte = st.selectbox(
            "Fonte de Aquisição",
            fontes
        )

    # ==========================================
    # FILTRO
    # ==========================================

    df_f = df.copy()

    if fonte != "Todas":

        df_f = df_f[
            df_f["Fonte_Aquisicao"] == fonte
        ]

    # ==========================================
    # TIME TO FILL
    # ==========================================

    df_f["TimeToFill"] = (
        df_f["Data_Admissao_REC"]
        -
        df_f["Data_Abertura_Vaga"]
    ).dt.days

    # ==========================================
    # QUALITY OF HIRE
    # ==========================================

    df_f["QoH"] = (
        (
            df_f["Nota_Avaliacao_Atual"].fillna(0)
            +
            df_f["Nota_Fit_Cultural"].fillna(0)
            +
            (
                100
                -
                df_f["Absenteismo"].fillna(0)
            )
        )
        / 3
    )

    # ==========================================
    # CUSTO TOTAL
    # ==========================================

    custo_total = (
        df_f["Custo_Externo_BRL"].fillna(0)
        +
        (
            df_f["Horas_Internas_Lideranca"]
            .fillna(0)
            * 100
        )
    )

    # ==========================================
    # KPIs
    # ==========================================

    total_contratacoes = len(df_f)

    cph = custo_total.mean()

    timefill = df_f["TimeToFill"].median()

    qoh = df_f["QoH"].mean()

    roi = (
        (
            df_f["Receita_Gerada_BRL"].fillna(0)
            /
            custo_total.replace(0, 1)
        )
    ).mean()

    # ==========================================
    # HEADER
    # ==========================================

    st.title("🎯 Recruitment Analytics")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Contratações",
            f"{total_contratacoes:,.0f}",
            COLORS[0]
        )

    with c2:
        kpi_card(
            "CPH Médio",
            f"R$ {cph:,.0f}",
            COLORS[1]
        )

    with c3:
        kpi_card(
            "Time To Fill",
            f"{timefill:.0f} dias",
            COLORS[2]
        )

    with c4:
        kpi_card(
            "Quality of Hire",
            f"{qoh:.1f}",
            COLORS[3]
        )

    st.divider()

    # ==========================================
    # ROI POR FONTE
    # ==========================================

    roi_fonte = (
        df_f
        .groupby("Fonte_Aquisicao")
        .agg(
            Receita=("Receita_Gerada_BRL", "sum"),
            Custo=("Custo_Externo_BRL", "sum")
        )
        .reset_index()
    )

    roi_fonte["ROI"] = (
        roi_fonte["Receita"]
        /
        roi_fonte["Custo"].replace(0, 1)
    )

    fig1 = px.bar(
        roi_fonte,
        x="Fonte_Aquisicao",
        y="ROI",
        color="ROI",
        title="ROI por Fonte de Aquisição"
    )

    fig1.update_layout(
        plot_bgcolor=CARD_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR)
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # ======================