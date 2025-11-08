import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import fig_builder as fb

engine = create_engine("sqlite:///data/data.db")

# Store df in cache
@st.cache_data
def grab_df():
    q = """
    SELECT country, continent, year, lifeexp, pop, gdppercap,
           pop * gdppercap AS gdp
    FROM data
    ORDER BY country, year
    """
    df = pd.read_sql(text(q), engine)

    # Create log values for metrics
    df["log_pop"] = np.log10(df["pop"])
    df["log_gdppercap"] = np.log10(df["gdppercap"])
    df["log_gdp"] = np.log10(df["gdp"])
    return df

df = grab_df()

# Global page config
text_color = "#DAE7FF"
background_color = '#0E1117'
text_size = 16

st.set_page_config(
    page_title="Bearibles UCL Challenge Submission",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed")

# Remove top toolbar and running man animations
st.markdown("""
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
""", unsafe_allow_html=True) 

# Remove top paddingS
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


cols = st.columns([0.1, 5, 0.3])

# Title
with cols[1]:
    st.markdown(f"<h1 style='color:{text_color}; margin-top:-10px; text-align: center; margin-bottom:10px; font-size:{text_size * 4}px;'>Gapminder Economics Dashboard</h1>", unsafe_allow_html=True)

# Accessibility settings
with cols[-1]:
    with st.popover('⚙️'):
        st.markdown("### 🧩 Accessibility Options")
        color_mode = st.selectbox("Color Palette", ["Default","Protanopia","Deuteranopia","Tritanopia","Grayscale"])
        text_size = st.slider("Text Size", 1, 5, 3) * 4 + 5
        dyslexia_mode = st.checkbox("Dyslexia-friendly font")
        high_contrast = st.checkbox("High Contrast Mode")

conv = {"Default":"blues","Protanopia":"viridis","Deuteranopia":"magma","Tritanopia":"cividis", "Grayscale":"greys"}
palette = conv[color_mode]

if high_contrast:
    background_color = "black"
    text_color = "white"
    st.markdown("""
    <style>
    .stApp{background-color:black!important;color:white!important}
    [data-testid="stSidebar"]{background-color:black!important} 
    </style>
    """, unsafe_allow_html=True)

# Adjust global font sizes
st.markdown(f"""
<style>
html, body,
[class*="block-container"],
[class*="stMarkdown"],
[class*="stText"],
[class*="stSelectbox"],
[class*="stButton"],
[class*="stSlider"],
[class*="stDataFrame"] {{
    font-size: {int(text_size)}px !important;
}}

h1 {{ font-size: {int(text_size * 4)}px !important; }}
h2 {{ font-size: {int(text_size * 2.0)}px !important; }}
h3 {{ font-size: {int(text_size * 1.6)}px !important; }}
h4 {{ font-size: {int(text_size * 1.3)}px !important; }}
h5 {{ font-size: {int(text_size * 1.1)}px !important; }}
h6 {{ font-size: {int(text_size)}px !important; }}
</style>
""", unsafe_allow_html=True)

if dyslexia_mode:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
    html,body,[class*="block-container"],[class*="stMarkdown"],[class*="stText"],
    [class*="stSelectbox"],[class*="stButton"],[class*="stSlider"],
    [class*="stDataFrame"],h1,h2,h3,h4,h5,h6 {
        font-family:'Atkinson Hyperlegible', sans-serif !important;
        font-weight:700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.divider()

# Map config
title_ph = st.empty()
desc_ph = st.empty()

year_list = sorted(df["year"].unique().tolist())
col1, col2, col3 = st.columns([1, 2, 3])

with col1:
    selected_year = st.select_slider("Select a Year", options=year_list, value=year_list[-1])
with col2:
    selected_label = st.selectbox("Select a category", ["Population", "Life Expectancy", "GDP Per Capita", "GDP"])

title_ph.markdown(f"#### {selected_label} Map")
desc_ph.markdown(f"""
                This map shows how each country's {selected_label.lower()} change over time for the selected category.  
                Use the slider to move between years and the dropdown to switch between metrics such as population, life expectancy, GDP per capita, or total GDP.  
                Darker shades represent higher values within the chosen metric for that year.
                """)

cols = ["country","continent","year","lifeexp","pop","gdppercap","gdp","log_pop","log_gdppercap","log_gdp"]
df_selected = df.loc[df["year"].eq(selected_year), cols].copy()
selected_category = {"Population":"log_pop","Life Expectancy":"lifeexp","GDP Per Capita":"log_gdppercap","GDP":"log_gdp"}[selected_label]

choropleth = fb.make_choropleth(df_selected, selected_category, palette, text_size, text_color, background_color)
st.plotly_chart(choropleth, use_container_width=True)

st.divider()


# Bubble plot config
st.markdown(f"<h2 style='margin:0 0 0.25rem 0'>Life Expectancy vs GDP per capita</h2>", unsafe_allow_html=True)
st.markdown("""
            
This view shows how how life expectancy vs income evolves for each country over time.
Click play to see how the average life expectancy and GDP per capita vastly increase for each country over time.
This improvement was not just in rich countries; almost all countries see an increase in life expectancy over time 
            

        """) 
bubble = fb.make_bubble(df.copy(), palette, text_size, text_color, background_color)
st.plotly_chart(bubble, use_container_width=True)


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "By Continent",
    "By Decade",
    "Trends",
    "Residuals",
    "Population vs Income",
    "Slope Summary"
])

with tab1:
    st.markdown("#### Life expectancy vs GDP per capita by continent")
    st.markdown("""
        This view compares how life expectancy increases with income for each continent.
        The slope of each line indicates how strongly economic growth translates into longer lives
        in that region, steeper slopes mean greater health gains per increase in income.
        \n All continents see an upwards trend, meaning life expectancy and income are highly correlated around the world.
                """)
    fig_inc_health = fb.make_income_health_scatter(df.copy(), palette, text_size, text_color, background_color)
    st.plotly_chart(fig_inc_health, use_container_width=True)

with tab2:
    st.markdown("#### Relationship by decade")
    st.markdown("""
    This view compares the life expectancy - GDP per capita relationship for each decade since the 1950s.
    As global health and wealth improved, the correlation between GDP per capita and life expectancy
    stayed relatively consistent, so the gradient of the trend line doesn't change much.
                """)

    fig_decades = fb.make_decade_facets(df.copy(), palette, text_size, text_color, background_color)
    st.plotly_chart(fig_decades, use_container_width=True)

with tab3:
    st.markdown("#### Life expectancy trends over time by Continent")
    st.markdown("""
    This view tracks life expectancy through time for each continent. 
    The trend lines show the average improvement rate: Asia and the Americas rise the fastest,
    while Europe and Oceania rise the slowest.
                """)
    fig_trends = fb.make_continent_time_trends(df.copy(), palette, text_size, text_color, background_color)
    st.plotly_chart(fig_trends, use_container_width=True)

with tab4:
    st.markdown("#### Life expectancy vs GDP per capita Residuals")
    st.markdown("""
    This view shows the greatest Residuals for life expectancy vs GDP per capita. 
    Residuals measure how far each country's life expectancy is from the global average expected 
    for its GDP per capita. It's split into two groups, highlighting the top 6 overperforming
    and underperforming countries relative to their peers.
                """)

    fig_resid = fb.make_latest_residual_bars(df.copy(), palette, text_size, text_color, background_color)
    st.plotly_chart(fig_resid, use_container_width=True)

with tab5:
    st.markdown('#### GDP per capita vs Population (Log Scale)')
    st.markdown("""
    This view shows the relationship between population and income for each continent.
    The gradient of each trend line indicates how strongly population ties into economic growth.
    Larger populations coincide with higher income in the Americas, but with lower income in parts of Asia.
                """)

    fig_pop_vs_inc = fb.make_logpop_vs_loggdp_facets(df.copy(), palette, text_size, text_color, background_color)
    st.plotly_chart(fig_pop_vs_inc, use_container_width=True)

with tab6:
    st.markdown("#### Life Expectancy vs Income Slopes for each Continent")
    st.markdown("""
        This view compares the gradients of life expectancy vs income for each continent.
        It tells you how many years of life every 10x rise in GDP per capita gets you for each continent
        and hence how effectively higher income correlates to longer life across regions.
                """)
    fig_slopes = fb.make_summary_slopes(df.copy(), palette, text_size, text_color, background_color)
    st.plotly_chart(fig_slopes, use_container_width=True)

with st.expander('🔍 View Raw Data'):
    st.dataframe(df)