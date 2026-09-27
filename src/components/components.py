import streamlit as st

CARD_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
TICK_COLOR = "#8b949e"


def kpi_card(
    label,
    value,
    color
):

    st.markdown(
        f"""
<div style="
background:{CARD_COLOR};
padding:18px;
border-radius:12px;
border-left:5px solid {color};
text-align:center;
">

<p style="
margin:0;
font-size:12px;
color:{TICK_COLOR};
">
{label}
</p>

<p style="
margin-top:10px;
font-size:26px;
font-weight:bold;
color:{TEXT_COLOR};
">
{value}
</p>

</div>
""",
        unsafe_allow_html=True
    )