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
# LOAD
# ==================================================

@st.cache_data
def load_data():

    colaboradores = pd.read_csv(
        "data/tb_colaboradores.csv"
    )

    jornada = pd.read_csv(
        "data/tb_jornada.csv"
    )

    return colaboradores.merge(
        jornada,
        on="ID_Colaborador",
        how="inner"
    )

# ==================================================
# PAGE
# ==================================================

def run():

    df = load_data()

    # ==============================================
    # SIDEBAR
    # ==============================================

    with st.sidebar:

        st.title("👥 Workforce")

        departamentos = (
            ['Todos']
            +
            sorted(
                df['Departamento']
                .dropna()
                .unique()
                .tolist()
            )
        )

        departamento = st.selectbox(
            "Departamento",
            departamentos
        )

    # ==============================================
    # FILTRO
    # ==============================================

    df_f = df.copy()

    if departamento != 'Todos':

        df_f = df_f[
            df_f['Departamento']
            == departamento
        ]

    # ==============================================
    # KPIs
    # ==============================================

    horas_extras = (
        df_f['Horas_Extras']
        .sum()
    )

    horas_ausentes = (
        df_f['Horas_Ausentes']
        .sum()
    )

    horas_contratuais = (
        df_f['Horas_Contratuais']
        .sum()
    )

    absenteismo = (
        horas_ausentes
        /
        horas_contratuais
        * 100
        if horas_contratuais > 0
        else 0
    )

    bradford = (
        (
            df_f['Episodios_Ausencia']
            .mean()
        ) ** 2
    ) * (
        df_f['Horas_Ausentes']
        .mean()
    )

    burnout = (
        (horas_extras * 0.6)
        +
        (horas_ausentes * 0.4)
    )

    # ==============================================
    # HEADER
    # ==============================================

    st.title("👥 Workforce Analytics")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Absenteísmo",
            f"{absenteismo:.2f}%",
            COLORS[0]
        )

    with c2:
        kpi_card(
            "Horas Extras",
            f"{horas_extras:,.0f}",
            COLORS[1]
        )

    with c3:
        kpi_card(
            "Bradford",
            f"{bradford:.0f}",
            COLORS[2]
        )

    with c4:
        kpi_card(
            "Burnout Score",
            f"{burnout:,.0f}",
            COLORS[3]
        )

    st.divider()

    # ==============================================
    # GRAFICOS
    # ==============================================

    g1, g2 = st.columns(2)

    with g1:

        extras_dep = (
            df_f
            .groupby('Departamento')
            ['Horas_Extras']
            .sum()
            .reset_index()
            .sort_values(
                'Horas_Extras',
                ascending=False
            )
        )

        fig1 = px.bar(
            extras_dep,
            x='Departamento',
            y='Horas_Extras',
            title='Horas Extras por Departamento'
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

    with g2:

        falta_dep = (
            df_f
            .groupby('Departamento')
            ['Horas_Ausentes']
            .sum()
            .reset_index()
            .sort_values(
                'Horas_Ausentes',
                ascending=False
            )
        )

        fig2 = px.bar(
            falta_dep,
            x='Departamento',
            y='Horas_Ausentes',
            color='Horas_Ausentes',
            title='Horas Ausentes por Departamento'
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
    # MATRIZ DE EXAUSTÃO
    # ==============================================

    matriz = (
        df_f
        .groupby("Departamento")
        .agg(
            Horas_Extras=("Horas_Extras", "sum"),
            Horas_Ausentes=("Horas_Ausentes", "sum")
        )
        .reset_index()
    )

    fig3 = px.scatter(
        matriz,
        x="Horas_Extras",
        y="Horas_Ausentes",
        color="Departamento",
        size="Horas_Extras",
        title="Matriz de Exaustão"
    )

    fig3.update_layout(
        plot_bgcolor=CARD_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR)
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.divider()

    # ==============================================
    # INSIGHTS
    # ==============================================

    maior_he = extras_dep.iloc[0]["Departamento"]

    maior_abs = falta_dep.iloc[0]["Departamento"]

    st.info(
        f"""
✅ Maior volume de horas extras:
{maior_he}

✅ Maior volume de ausências:
{maior_abs}

✅ Absenteísmo geral:
{absenteismo:.2f}%

✅ Bradford médio:
{bradford:.0f}
"""
    )