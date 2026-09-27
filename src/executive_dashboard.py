import streamlit as st
import pandas as pd
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
# LOAD DATA
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

    return (
        colaboradores,
        desempenho,
        jornada,
        recrutamento
    )

# ==================================================
# DASHBOARD
# ==================================================

def run():

    (
        colaboradores,
        desempenho,
        jornada,
        recrutamento
    ) = load_data()

    # ==================================================
    # JOIN PRINCIPAL
    # ==================================================

    df = colaboradores.merge(
        desempenho,
        on="ID_Colaborador",
        how="left"
    )

    # ==================================================
    # SIDEBAR
    # ==================================================

    with st.sidebar:

        st.title("🏠 Executive Dashboard")

        departamentos = (
            ['Todos']
            +
            sorted(
                colaboradores['Departamento']
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
            ['Todos']
            +
            sorted(
                colaboradores['Senioridade']
                .dropna()
                .unique()
                .tolist()
            )
        )

        senioridade = st.selectbox(
            "Senioridade",
            senioridades
        )

        status_list = (
            ['Todos']
            +
            sorted(
                colaboradores['Status']
                .dropna()
                .unique()
                .tolist()
            )
        )

        status = st.selectbox(
            "Status",
            status_list
        )

    # ==================================================
    # FILTROS
    # ==================================================

    df_f = df.copy()

    if departamento != 'Todos':
        df_f = df_f[
            df_f['Departamento'] == departamento
        ]

    if senioridade != 'Todos':
        df_f = df_f[
            df_f['Senioridade'] == senioridade
        ]

    if status != 'Todos':
        df_f = df_f[
            df_f['Status'] == status
        ]

    # ==================================================
    # KPIs
    # ==================================================

    total_colaboradores = len(df_f)

    ativos = (
        df_f['Status']
        .eq('Ativo')
        .sum()
    )

    desligados = (
        df_f['Status']
        .eq('Desligado')
        .sum()
    )

    turnover = (
        desligados / total_colaboradores * 100
        if total_colaboradores > 0
        else 0
    )

    receita_total = (
        df_f['Receita_Gerada_BRL']
        .fillna(0)
        .sum()
    )

    receita_por_colaborador = (
        receita_total / total_colaboradores
        if total_colaboradores > 0
        else 0
    )

    # ==================================================
    # HEADER
    # ==================================================

    st.title("👥 People Analytics Executive Dashboard")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        kpi_card(
            "Headcount",
            f"{total_colaboradores:,.0f}",
            COLORS[0]
        )

    with c2:

        kpi_card(
            "Ativos",
            f"{ativos:,.0f}",
            COLORS[1]
        )

    with c3:

        kpi_card(
            "Turnover",
            f"{turnover:.1f}%",
            COLORS[3]
        )

    with c4:

        kpi_card(
            "Receita / Colaborador",
            f"R$ {receita_por_colaborador:,.0f}",
            COLORS[2]
        )

    st.divider()

    # ==================================================
    # GRAFICOS
    # ==================================================

    g1, g2 = st.columns(2)

    # --------------------------------------------------
    # RECEITA POR DEPARTAMENTO
    # --------------------------------------------------

    with g1:

        receita_dep = (
            df_f
            .groupby("Departamento")
            ['Receita_Gerada_BRL']
            .sum()
            .reset_index()
            .sort_values(
                "Receita_Gerada_BRL",
                ascending=False
            )
        )

        fig1 = px.bar(
            receita_dep,
            x='Departamento',
            y='Receita_Gerada_BRL',
            color='Departamento',
            title='Receita por Departamento'
        )

        fig1.update_layout(
            plot_bgcolor=CARD_COLOR,
            paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR),
            showlegend=False
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    # --------------------------------------------------
    # TURNOVER POR DEPARTAMENTO
    # --------------------------------------------------

    with g2:

        turnover_dep = (
            df_f
            .groupby(
                ['Departamento', 'Status']
            )
            .size()
            .unstack(fill_value=0)
        )

        if (
            'Ativo' in turnover_dep.columns
            and
            'Desligado' in turnover_dep.columns
        ):

            turnover_dep['Taxa'] = (
                turnover_dep['Desligado']
                /
                (
                    turnover_dep['Ativo']
                    +
                    turnover_dep['Desligado']
                )
            ) * 100

            turnover_dep = (
                turnover_dep
                .reset_index()
                .sort_values(
                    'Taxa',
                    ascending=False
                )
            )

            fig2 = px.bar(
                turnover_dep,
                x='Departamento',
                y='Taxa',
                color='Taxa',
                title='Turnover por Departamento'
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

    # ==================================================
    # INSIGHTS
    # ==================================================

    st.markdown("### 🧠 Insights Executivos")

    departamento_maior_receita = (
        receita_dep.iloc[0]['Departamento']
        if len(receita_dep) > 0
        else "-"
    )

    maior_receita = (
        receita_dep.iloc[0]['Receita_Gerada_BRL']
        if len(receita_dep) > 0
        else 0
    )

    st.info(
        f"""
✅ Departamento líder em receita:
{departamento_maior_receita}
(R$ {maior_receita:,.0f})

✅ Turnover atual:
{turnover:.1f}%

✅ Headcount analisado:
{total_colaboradores:,.0f} colaboradores

✅ Receita total gerada:
R$ {receita_total:,.0f}
"""
    )