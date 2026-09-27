import streamlit as st

from src.executive_dashboard import run as executive_dashboard
from src.performance_analytics import run as performance_analytics
from src.workforce_analytics import run as workforce_analytics
from src.recruitment_analytics import run as recruitment_analytics
from src.turnover_analytics import run as turnover_analytics
from src.talent_intelligence import run as talent_intelligence



st.set_page_config(
    page_title="People Analytics Hub",
    page_icon="👥",
    layout="wide"
)

pagina = st.sidebar.radio(
    "Selecione uma Página",
    [
        "🏠 Executive Dashboard",
        "📈 Performance Analytics",
        "👥 Workforce Analytics",
        "🎯 Recruitment Analytics",
        "🔄 Turnover Analytics",
        "🧠 Talent Intelligence"
    ]
)

if pagina == "🏠 Executive Dashboard":
    executive_dashboard()

elif pagina == "📈 Performance Analytics":
    performance_analytics()

elif pagina == "👥 Workforce Analytics":
    workforce_analytics()

elif pagina == "🎯 Recruitment Analytics":
    recruitment_analytics()

elif pagina == "🔄 Turnover Analytics":
    turnover_analytics()

elif pagina == "🧠 Talent Intelligence":
    talent_intelligence()
