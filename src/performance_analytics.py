import streamlit as st
import pandas as pd
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

    colaboradores = pd.read_csv(
        "data/tb_colaboradores.csv"
    )

    desempenho = pd.read_csv(
        "data/tb_desempenho.csv"
    )

    return colaboradores.merge(
        desempenho,
        on="ID_Colaborador",
        how="left"
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

        st.title("📈 Performance")

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

        treinamento = st.selectbox(
            "Treinamento",
            [
                "Todos",
                "Sim",
                "Não"
            ]
        )

    # ==============================================
    # FILTROS
    # ==============================================

    df_f = df.copy()

    if departamento != 'Todos':
        df_f = df_f[
            df_f['Departamento'] == departamento
        ]

    if senioridade != 'Todos':
        df_f = df_f[
            df_f['Senioridade'] == senioridade
        ]

    if treinamento != 'Todos':
        df_f = df_f[
            df_f['Participou_Treinamento_Estrategico']
            == treinamento
        ]

    # ==============================================
    # KPIS
    # ==============================================

    performance_media = (
        df_f['Nota_Avaliacao_Atual']
        .mean()
    )

    enps_medio = (
        df_f['eNPS_Nota']
        .mean()
    )

    receita_media = (
        df_f['Receita_Gerada_BRL']
        .mean()
    )

    pct_treinados = (
        (
            df_f[
                df_f['Participou_Treinamento_Estrategico']
                == 'Sim'
            ].shape[0]
            /
            len(df_f)
        )
        * 100
        if len(df_f) > 0
        else 0
    )

    # ==============================================
    # HEADER
    # ==============================================

    st.title("📈 Performance Analytics")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Performance Média",
            f"{performance_media:.1f}",
            COLORS[0]
        )

    with c2:
        kpi_card(
            "eNPS Médio",
            f"{enps_medio:.1f}",
            COLORS[1]
        )

    with c3:
        kpi_card(
            "Receita Média",
            f"R$ {receita_media:,.0f}",
            COLORS[2]
        )

    with c4:
        kpi_card(
            "% Treinados",
            f"{pct_treinados:.1f}%",
            COLORS[3]
        )


    st.divider()

    # ==============================================
    # GRÁFICOS SUPERIORES
    # ==============================================

    col1, col2 = st.columns(2)

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Box(
                y=df_f['Nota_Avaliacao_Atual'],
                name='Performance',
                marker_color=COLORS[0]
            )
        )

        fig.update_layout(
            title="Distribuição da Performance",
            plot_bgcolor=CARD_COLOR,
            paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        comparativo = (
            df_f
            .groupby(
                'Participou_Treinamento_Estrategico'
            )
            [
                [
                    'Nota_Avaliacao_Atual',
                    'Receita_Gerada_BRL',
                    'eNPS_Nota'
                ]
            ]
            .mean()
            .reset_index()
        )

        fig2 = go.Figure()

        fig2.add_trace(
            go.Bar(
                x=comparativo[
                    'Participou_Treinamento_Estrategico'
                ],
                y=comparativo[
                    'Nota_Avaliacao_Atual'
                ],
                name='Performance'
            )
        )

        fig2.update_layout(
            title='Treinamento x Performance',
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
    # PROMOÇÃO
    # ==============================================

    col3, col4 = st.columns(2)

    with col3:

        promo = (
            df_f
            .groupby(
                [
                    'Departamento',
                    'Promovido_Ultimos_12m'
                ]
            )
            .size()
            .reset_index(name='Qtd')
        )

        fig3 = go.Figure()

        for status in promo[
            'Promovido_Ultimos_12m'
        ].unique():

            temp = promo[
                promo[
                    'Promovido_Ultimos_12m'
                ] == status
            ]

            fig3.add_trace(
                go.Bar(
                    x=temp['Departamento'],
                    y=temp['Qtd'],
                    name=status
                )
            )

        fig3.update_layout(
            barmode='stack',
            title='Promoções por Departamento',
            plot_bgcolor=CARD_COLOR,
            paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR)
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    with col4:

        treinados = (
            df_f[
                'Participou_Treinamento_Estrategico'
            ]
            .value_counts()
        )

        fig4 = go.Figure(
            data=[
                go.Pie(
                    labels=treinados.index,
                    values=treinados.values,
                    hole=0.4
                )
            ]
        )

        fig4.update_layout(
            title='Participação em Treinamento',
            plot_bgcolor=CARD_COLOR,
            paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR)
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    st.divider()

    # ==============================================
    # INSIGHTS
    # ==============================================

    st.markdown("### 🧠 Insights de Performance")

    st.info(
        f"""
✅ Performance média: {performance_media:.1f}

✅ eNPS médio: {enps_medio:.1f}

✅ Receita média por colaborador:
R$ {receita_media:,.0f}

✅ Participação em treinamento:
{pct_treinados:.1f}%
"""
    )