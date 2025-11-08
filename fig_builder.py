import plotly.express as px
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st



# Removes zoom and pan features from figure
def remove_fig_features(fig):
    fig.update_layout(dragmode=False)  # disables click-drag interaction
    fig.update_layout(
        modebar_remove=[
            "zoom", "zoomIn", "zoomOut", "pan", "select", "lasso2d", "autoScale", "resetGeo"
        ]
    )
    return fig

def discrete_color_map(palette, n):
    seq_map = {
        "viridis": px.colors.sequential.Viridis,
        "magma": px.colors.sequential.Magma,
        "cividis": px.colors.sequential.Cividis,
        "blues": px.colors.sequential.Blues,
        "greys": px.colors.sequential.Greys
    }
    seq = seq_map.get(palette, None)

    if seq and len(seq) >= n:
        colors = [seq[int(i*(len(seq)-1)/(n-1))] for i in range(n)] if n > 1 else [seq[len(seq)//2]]
    else:
        colors = px.colors.qualitative.Pastel
    
    return colors 


# Cloropleth/Map Plot
@st.cache_data(show_spinner=False)
def make_choropleth(input_df, selected_category, input_colour_theme, text_size, text_color, background_color):
    fig = px.choropleth(
        input_df,
        locations="country",
        color=selected_category,
        locationmode="country names",
        color_continuous_scale=input_colour_theme,
        range_color=(input_df[selected_category].min(), input_df[selected_category].max()),
        scope="world",
        width=1800,
        height=700,
        labels={
            'pop': 'Population',
            'gdppercap': 'GDP Per Capita ',
            'log_pop': 'Population (Log Scale)',
            'lifeexp': 'Life Expectancy',
            'log_gdppercap': 'GDP Per Capita (Log Scale)',
            'log_gdp': 'GDP (Log Scale)'
        },

        hover_data={
        "lifeexp": ":.1f", 
        "pop": ":,", 
        "gdppercap": ":.0f", 
        "continent": True,
        "log_pop": False
    },
    )

    fig.update_geos(
        projection_type="equirectangular",
        showcountries=True,
        showcoastlines=False,
        showland=True,
        fitbounds="locations",
        oceancolor=background_color,
        showocean=False,
        lonaxis_range=[-180, 180],
        lataxis_range=[-60, 85],
    )   

    # Make the colorbar horizontal under the map
    fig.update_layout(
        geo=dict(bgcolor=background_color, center=dict(lat=10, lon=0)),
        template='plotly_dark',
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        margin=dict(l=0, r=0, t=30, b=50),
        font=dict(size=text_size, color=text_color),
        coloraxis_colorbar=dict(
            orientation='h',         
            yanchor='bottom',        
            y=-0.25,                 
            xanchor='center',        
            x=0.5,                   
            title_side='top',        
            thicknessmode='pixels',
            thickness=12,
            lenmode='fraction',
            len=0.6,
            title_font=dict(size=text_size),
            tickfont=dict(size=text_size - 4)
        )
    )

    fig = remove_fig_features(fig)

    return fig



# Scatter/Bubble Plot
@st.cache_resource
def make_bubble(df, palette, text_size, text_color, background_color):

    conts = sorted(df["continent"].unique())
    n_cont = len(conts)

    colors = discrete_color_map(palette, n_cont)

    fig = px.scatter(
        df,
        x="gdppercap",
        y="lifeexp",
        animation_frame="year",
        animation_group="country",
        size="pop",
        color="continent",
        color_discrete_sequence=colors,
        hover_name="country",
        log_x=True,
        size_max=60, # max bubble size
        height=800,
        labels={
            'gdppercap':'GDP per capita (Log Scale)',
            'lifeexp': 'Life Expectancy'
        },
    )

    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color="rgba(255,255,255,0.15)")))

    fig.update_yaxes(range=[30, 90], title_font=dict(size=text_size + 2), gridcolor="rgba(255,255,255,0.06)")

    fig.update_xaxes(title_font=dict(size=text_size + 2))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color, 
        paper_bgcolor=background_color, 
        font=dict(size=text_size, color=text_color),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(title="Continent", orientation="h", y=1.02, x=0.2),
        transition=dict(duration=1600)
    )

    fig = remove_fig_features(fig)

    return fig  

def make_income_health_scatter(input_df, input_colour_theme, text_size, text_color, background_color):
    d = input_df.copy()
    # n_decs = len(d.groupby("continent"))
    # colors = discrete_color_map(input_colour_theme, n_decs)
    fig = px.scatter(
        d,
        x="log_gdp",
        y="lifeexp",
        color="continent",
        hover_name="country",
        facet_col="continent",
        #color_discrete_sequence=colors,
        opacity=0.6,
        labels={"log_gdp": "GDP per capita (Log Scale)", "lifeexp": "Life expectancy"}
    )
    facet_order = [a.text.split("=")[-1] for a in fig.layout.annotations]

    for c in facet_order:
        g = d[d["continent"] == c]
        xs = np.array(sorted(g["log_gdp"].unique()))
        if len(xs) > 2:
            b1, b0 = np.polyfit(g["log_gdp"], g["lifeexp"], 1)
            ys = b1 * xs + b0
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    line=dict(width=2),
                    name=f"{c} fit",
                    showlegend=False,
                    hovertemplate=f"<b>Continent:</b> {c}<br>Gradient: {b1:.2f}<extra></extra>"
                ),
                row=1,
                col=facet_order.index(c)+1
            )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(size=text_size, color=text_color),
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False
    )

    fig = remove_fig_features(fig)
    return fig

def make_decade_facets(input_df, input_colour_theme, text_size, text_color, background_color):
    d = input_df.copy()
    d["decade"] = (d["year"] // 10) * 10
    decs = sorted(d["decade"].unique())
    n_decs = len(decs)
    colors = discrete_color_map(input_colour_theme, n_decs)
    fig = px.scatter(
        d,
        x="log_gdp",
        y="lifeexp",
        color="continent",
        hover_name="country",
        facet_col="decade",
        category_orders={"decade": decs},
        color_discrete_sequence=colors,
        opacity=0.6,
        labels={"log_gdp": "GDP per capita (Log Scale)", "lifeexp": "Life expectancy", "decade": "decade"}
    )


    for i, dec in enumerate(decs, start=1):
        g = d[d["decade"] == dec]
        xs = np.array(sorted(g["log_gdp"].unique()))
        b1, b0 = np.polyfit(g["log_gdp"], g["lifeexp"], 1)
        ys = b1 * xs + b0
        fig.add_trace(
            go.Scatter(x=xs, y=ys, mode="lines", line=dict(width=2), name=f"{dec} fit", showlegend=False, hovertemplate=f"<b>Decade:</b> {dec}<br>Gradient: {b1:.2f} years per 10x GDP<extra></extra>"),
            row=1, col=i, 
        )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(size=text_size, color=text_color),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    for ax in fig.layout.annotations:
        ax.font.size = text_size
    
    fig = remove_fig_features(fig)
    return fig

def make_continent_time_trends(input_df, input_colour_theme, text_size, text_color, background_color):
    fig = px.scatter(
        input_df,
        x="year",
        y="lifeexp",
        color="continent",
        hover_name="country",
        opacity=0.2,
        labels={"year": "Year", "lifeexp": "Life expectancy"}
    )
    
    # quik fix to get rid of the dupe legend
    fig.for_each_trace(lambda t: t.update(showlegend=False))

    for c, g in input_df.groupby("continent"):
        xs = np.array(sorted(g["year"].unique()))
        b1, b0 = np.polyfit(g["year"], g["lifeexp"], 1)
        ys = b1 * xs + b0
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(width=2), name=f"{c} trend", hovertemplate=f"<b>Continent:</b> {c}<br>Gradient: {b1:.2f}<extra></extra>"))
    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(size=text_size, color=text_color),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    fig = remove_fig_features(fig)
    return fig

def make_latest_residual_bars(input_df, input_colour_theme, text_size, text_color, background_color, top_n=6):
    d = input_df.copy()
    latest_year = int(d["year"].max())
    d = d[d["year"] == latest_year].copy()
    d["log_gdp"] = np.log10(d["gdppercap"])
    x = d["log_gdp"].to_numpy()
    y = d["lifeexp"].to_numpy()
    b1, b0 = np.polyfit(x, y, 1)
    d["resid"] = y - (b1 * x + b0)
    pos = d.nlargest(top_n, "resid")[["country", "continent", "resid"]].assign(group="Over perform")
    neg = d.nsmallest(top_n, "resid")[["country", "continent", "resid"]].assign(group="Under perform")
    show = pd.concat([pos, neg], axis=0)

    fig = px.bar(
        show.sort_values(["group", "resid"]),
        x="resid",
        y="country",
        color="group",
        orientation="h",
        text="continent",
        labels={"resid": "Residual (years)", "country": f"Countries {latest_year}"}
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(size=text_size, color=text_color),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True
    )
    fig = remove_fig_features(fig)
    return fig

def make_logpop_vs_loggdp_facets(input_df, input_colour_theme, text_size, text_color, background_color):
    d = input_df.copy()
    d["log_gdp"] = np.log10(d["gdppercap"])
    d["log_pop"] = np.log10(d["pop"])
    fig = px.scatter(
        d,
        x="log_pop",
        y="log_gdp",
        color="continent",
        hover_name="country",
        facet_col="continent",
        opacity=0.6,
        labels={"log_pop": "Population (Log Scale)", "log_gdp": "GDP per capita (Log Scale)"}
    )
    continents = list(d["continent"].unique())
    for c in continents:
        g = d[d["continent"] == c]
        xs = np.array(sorted(g["log_pop"].unique()))
        b1, b0 = np.polyfit(g["log_pop"], g["log_gdp"], 1)
        ys = b1 * xs + b0
        fig.add_trace(
            go.Scatter(x=xs, y=ys, mode="lines", line=dict(width=2), name=f"{c} fit", hovertemplate=f"<b>Continent:</b> {c}<br>Gradient: {b1:.2f}<extra></extra>", showlegend=False),
            row=1, col=continents.index(c)+1
        )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(size=text_size, color=text_color),
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False
    )
    for ax in fig.layout.annotations:
        ax.font.size = text_size

    fig = remove_fig_features(fig)
    return fig

def make_summary_slopes(input_df, input_colour_theme, text_size, text_color, background_color):
    d = input_df.copy()
    rows = []
    for c, g in d.groupby("continent"):
        b1, b0 = np.polyfit(g["log_gdp"], g["lifeexp"], 1)
        rows.append({"continent": c, "slope_years_per_10x_gdp": b1})
    t = pd.DataFrame(rows)
    colors = discrete_color_map(input_colour_theme, len(rows))
    fig = px.scatter(
        t,
        x="slope_years_per_10x_gdp",
        y="continent",
        color="continent",
        color_discrete_sequence=colors,
        labels={"slope_years_per_10x_gdp": "Slope (years per 10x GDP)", "continent": "Continent"}
    )
    fig.update_traces(marker=dict(size=14))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font=dict(size=text_size, color=text_color),
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False
    )
    fig = remove_fig_features(fig)
    return fig
