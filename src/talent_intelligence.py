import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px

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

    colaboradores = pd.read_csv(
        "data/tb_colaboradores.csv"
    )

    desempenho = pd.read_csv(
        "data/tb_desempenho.csv"
    )

    jornada = pd.read_csv(
        "data/tb_jornada.csv"
    )

    recrutamento = pd.read_csv(
        "data/tb_recrutamento.csv"
    )

    jornada = (
        jornada
        .groupby("ID_Colaborador")
        .agg(
            Horas_Contratuais=("Horas_Contratuais", "sum"),
            Horas_Extras=("Horas_Extras", "sum"),
            Horas_Ausentes=("Horas_Ausentes", "sum"),
            Episodios_Ausencia=("Episodios_Ausencia", "sum")
        )
        .reset_index()
    )

    df = (
        colaboradores
        .merge(
            desempenho,
            on="ID_Colaborador",
            how="left"
        )
        .merge(
            jornada,
            on="ID_Colaborador",
            how="left"
        )
        .merge(
            recrutamento,
            on="ID_Colaborador",
            how="left"
        )
    )

    return df

# ==================================================
# NORMALIZADOR
# ==================================================

def normalize(series):

    series = series.fillna(0)

    minimo = series.min()
    maximo = series.max()

    if maximo == minimo:

        return pd.Series(
            [50] * len(series),
            index=series.index
        )

    return (
        (series - minimo)
        /
        (maximo - minimo)
    ) * 100

# ==================================================
# PAGE
# ==================================================

def run():

    df = load_data()

    # ==============================================
    # SIDEBAR
    # ==============================================

    with st.sidebar:

        st.title("🧠 Talent Intelligence")

        departamentos = (
            ["Todos"]
            +
            sorted(
                df["Departamento"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        departamento = st.selectbox(
            "Departamento",
            departamentos
        )

        senioridades = (
            ["Todos"]
            +
            sorted(
                df["Senioridade"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        senioridade = st.selectbox(
            "Senioridade",
            senioridades
        )

    # ==============================================
    # FILTRO
    # ==============================================

    df_f = df.copy()

    if departamento != "Todos":

        df_f = df_f[
            df_f["Departamento"]
            == departamento
        ]

    if senioridade != "Todos":

        df_f = df_f[
            df_f["Senioridade"]
            == senioridade
        ]

    # ==============================================
    # ABSENTEÍSMO
    # ==============================================

    df_f["Absenteismo"] = (
        df_f["Horas_Ausentes"].fillna(0)
        /
        df_f["Horas_Contratuais"].replace(0, np.nan)
    ) * 100

    df_f["Absenteismo"] = (
        df_f["Absenteismo"]
        .fillna(0)
    )

    # ==============================================
    # FLIGHT RISK
    # ==============================================

    enps_risk = (
        100 -
        normalize(df_f["eNPS_Nota"])
    )

    performance_risk = (
        100 -
        normalize(df_f["Nota_Avaliacao_Atual"])
    )

    abs_risk = normalize(
        df_f["Absenteismo"]
    )

    overtime_risk = normalize(
        df_f["Horas_Extras"]
    )

    promovido = (
        df_f["Promovido_Ultimos_12m"]
        .astype(str)
        .str.upper()
        .isin(
            [
                "SIM",
                "TRUE",
                "1"
            ]
        )
    )

    promo_risk = (
        (~promovido)
        .astype(int)
        * 100
    )

    df_f["FlightRisk"] = (

        enps_risk * 0.30 +

        performance_risk * 0.20 +

        abs_risk * 0.20 +

        overtime_risk * 0.15 +

        promo_risk * 0.15

    )

    # ==============================================
    # BURNOUT
    # ==============================================

    bradford = (
        (
            df_f["Episodios_Ausencia"]
            .fillna(0)
            ** 2
        )
        *
        df_f["Horas_Ausentes"]
        .fillna(0)
    )

    df_f["BurnoutScore"] = (

        normalize(df_f["Horas_Extras"]) * 0.50 +

        normalize(df_f["Absenteismo"]) * 0.30 +

        normalize(bradford) * 0.20

    )

    # ==============================================
    # PROMOTION SCORE
    # ==============================================

    performance = normalize(
        df_f["Nota_Avaliacao_Atual"]
    )

    fit = normalize(
        df_f["Nota_Fit_Cultural"]
    )

    receita = normalize(
        df_f["Receita_Gerada_BRL"]
    )

    enps = normalize(
        df_f["eNPS_Nota"]
    )

    evolucao = normalize(
        (
            df_f["Nota_Avaliacao_Atual"]
            .fillna(0)
        )
        -
        (
            df_f["Nota_Avaliacao_Anterior"]
            .fillna(0)
        )
    )

    df_f["PromotionScore"] = (

        performance * 0.35 +

        evolucao * 0.25 +

        fit * 0.20 +

        enps * 0.10 +

        receita * 0.10

    )

    # ==============================================
    # HCROI
    # ==============================================

    df_f["Custo_Total"] = (

        df_f["Salario_Base"].fillna(0)

        +

        df_f["Beneficios"].fillna(0)

        +

        df_f["Encargos_Trabalhistas"].fillna(0)

    )

    df_f["HCROI"] = (

        df_f["Receita_Gerada_BRL"]
        .fillna(0)

        /

        df_f["Custo_Total"]
        .replace(0, np.nan)

    )

    # ==============================================
    # KPIS
    # ==============================================

    flight = df_f["FlightRisk"].mean()

    burnout = df_f["BurnoutScore"].mean()

    promotion = df_f["PromotionScore"].mean()

    hcroi = df_f["HCROI"].mean()

    # ==============================================
    # HEADER
    # ==============================================

    st.title("🧠 Talent Intelligence")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Flight Risk",
            f"{flight:.1f}",
            COLORS[0]
        )

    with c2:
        kpi_card(
            "Burnout Score",
            f"{burnout:.1f}",
            COLORS[1]
        )

    with c3:
        kpi_card(
            "Promotion Score",
            f"{promotion:.1f}",
            COLORS[2]
        )

    with c4:
        kpi_card(
            "HCROI",
            f"{hcroi:.2f}",
            COLORS[3]
        )

    st.divider()

    # ==============================================
    # TOP FLIGHT RISK
    # ==============================================

    top_risk = (
        df_f[
            [
                "ID_Colaborador",
                "Departamento",
                "FlightRisk"
            ]
        ]
        .sort_values(
            "FlightRisk",
            ascending=False
        )
        .head(15)
    )

    fig1 = px.bar(
        top_risk,
        x="ID_Colaborador",
        y="FlightRisk",
        color="FlightRisk",
        title="Top 15 Flight Risk"
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

    # ==============================================
    # MATRIZ TALENTO
    # ==============================================

    fig2 = px.scatter(
        df_f,
        x="PromotionScore",
        y="FlightRisk",
        size="Receita_Gerada_BRL",
        color="Departamento",
        hover_name="ID_Colaborador",
        title="Matriz Talento (Promoção x Risco)"
    )

    fig2.update_layout(
        plot_bgcolor=CARD_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR)
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    # ==============================================
    # HIGH POTENTIAL
    # ==============================================

    st.markdown(
        "### 🚀 High Potential Talent"
    )

    high_potential = (
        df_f[
            [
                "ID_Colaborador",
                "Departamento",
                "PromotionScore",
                "FlightRisk",
                "HCROI"
            ]
        ]
        .sort_values(
            "PromotionScore",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        high_potential,
        use_container_width=True
    )

    st.markdown(
        "### 🧠 Insights Estratégicos"
    )

    risco_alto = (
        df_f["FlightRisk"] > 70
    ).sum()

    burnout_alto = (
        df_f["BurnoutScore"] > 70
    ).sum()

    st.info(
        f"""
✅ Flight Risk médio: {flight:.1f}

✅ Colaboradores em alto risco: {risco_alto}

✅ Possível burnout: {burnout_alto}

✅ Promotion Score médio: {promotion:.1f}

✅ HCROI médio: {hcroi:.2f}
"""
    )