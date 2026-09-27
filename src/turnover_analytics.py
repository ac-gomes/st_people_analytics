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

    df = pd.read_csv(
        "data/tb_colaboradores.csv"
    )

    df["Data_Admissao"] = pd.to_datetime(
        df["Data_Admissao"]
    )

    if "Data_Desligamento" in df.columns:

        df["Data_Desligamento"] = pd.to_datetime(
            df["Data_Desligamento"],
            errors="coerce"
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

        st.title("🔄 Turnover")

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

        senioridades = (
            ['Todos']
            +
            sorted(
                df['Senioridade']
                .dropna()
                .unique()
                .tolist()
            )
        )

        senioridade = st.selectbox(
            "Senioridade",
            senioridades
        )

    # ==========================================
    # FILTRO
    # ==========================================

    df_f = df.copy()

    if departamento != 'Todos':

        df_f = df_f[
            df_f['Departamento']
            == departamento
        ]

    if senioridade != 'Todos':

        df_f = df_f[
            df_f['Senioridade']
            == senioridade
        ]

    # ==========================================
    # METRICAS
    # ==========================================

    total = len(df_f)

    desligados = (
        df_f['Status']
        .eq('Desligado')
        .sum()
    )

    turnover = (
        desligados / total * 100
        if total > 0
        else 0
    )
    voluntarios = len(
        df_f[
            df_f["Motivo_Desligamento"]
            == "Voluntário"
        ]
    )

    involuntarios = len(
        df_f[
            df_f["Motivo_Desligamento"]
            == "Involuntário"
        ]
    )


    turnover_vol = (
        voluntarios / total * 100
        if total > 0
        else 0
    )

    turnover_inv = (
        involuntarios / total * 100
        if total > 0
        else 0
    )

    # ==========================================
    # EARLY TURNOVER
    # ==========================================

    desligados_df = df_f[
        df_f["Data_Desligamento"]
        .notna()
    ].copy()

    desligados_df["Tempo_Casa"] = (
        desligados_df["Data_Desligamento"]
        -
        desligados_df["Data_Admissao"]
    ).dt.days

    early = len(
        desligados_df[
            desligados_df["Tempo_Casa"] <= 90
        ]
    )

    early_turnover = (
        early /
        total
        * 100
        if total > 0
        else 0
    )

    # ==========================================
    # HEADER
    # ==========================================

    st.title("🔄 Turnover Analytics")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Turnover Geral",
            f"{turnover:.1f}%",
            COLORS[0]
        )

    with c2:
        kpi_card(
            "Voluntário",
            f"{turnover_vol:.1f}%",
            COLORS[1]
        )

    with c3:
        kpi_card(
            "Involuntário",
            f"{turnover_inv:.1f}%",
            COLORS[2]
        )

    with c4:
        kpi_card(
            "Early Turnover",
            f"{early_turnover:.1f}%",
            COLORS[3]
        )



    st.divider()

    # ==========================================
    # GRAFICOS
    # ==========================================

    col1, col2 = st.columns(2)

    with col1:

        dep = (
            df_f
            .groupby("Departamento")
            ["Status"]
            .apply(
                lambda x: (
                    x.eq("Desligado").sum()
                    /
                    len(x)
                ) * 100
            )
            .reset_index(name="Turnover")
            .sort_values(
                "Turnover",
                ascending=False
            )
        )

        fig1 = px.bar(
            dep,
            x="Departamento",
            y="Turnover",
            color="Turnover",
            title="Turnover por Departamento"
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

    with col2:

        senior = (
            df_f
            .groupby("Senioridade")
            ["Status"]
            .apply(
                lambda x: (
                    x.eq("Desligado").sum()
                    /
                    len(x)
                ) * 100
            )
            .reset_index(name="Turnover")
        )

        fig2 = px.bar(
            senior,
            x="Senioridade",
            y="Turnover",
            color="Turnover",
            title="Turnover por Senioridade"
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

    # ==========================================
    # VOLUNTARIO X INVOLUNTARIO
    # ==========================================
    # st.write("Valores reais de Motivo_Desligamento")

    # st.write(
    #     df_f["Motivo_Desligamento"]
    #     .value_counts(dropna=False)
    # )

    motivos = pd.DataFrame({
        "Tipo": [
            "Voluntário",
            "Involuntário"
        ],
        "Quantidade": [
            voluntarios,
            involuntarios
        ]
    })

    fig3 = go.Figure(
        data=[
            go.Pie(
                labels=motivos["Tipo"],
                values=motivos["Quantidade"],
                hole=0.45
            )
        ]
    )

    fig3.update_layout(
        title="Composição dos Desligamentos",
        plot_bgcolor=CARD_COLOR,
        paper_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR)
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.divider()

    # ==========================================
    # INSIGHTS
    # ==========================================

    dep_critico = (
        dep.iloc[0]["Departamento"]
        if len(dep) > 0
        else "-"
    )

    turnover_critico = (
        dep.iloc[0]["Turnover"]
        if len(dep) > 0
        else 0
    )

    st.markdown(
        "### 🧠 Insights de Retenção"
    )

    st.info(
        f"""
✅ Departamento mais crítico:
{dep_critico}

✅ Turnover do departamento:
{turnover_critico:.1f}%

✅ Early turnover:
{early_turnover:.1f}%

✅ Saídas voluntárias:
{voluntarios}

✅ Saídas involuntárias:
{involuntarios}
"""
    )