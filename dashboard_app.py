# dashboard_app.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, dcc, html

pio.templates.default = "plotly_white"

video_games_sales_df = pd.read_csv("video_games_sales.csv")

for col in ["User_Score", "Critic_Score", "Global_Sales", "NA_Sales", "Year_of_Release"]:
    video_games_sales_df[col] = pd.to_numeric(video_games_sales_df[col], errors="coerce")

top_publishers_list = (
    video_games_sales_df.groupby("Publisher")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .index
)

sales_by_publisher = (
    video_games_sales_df[video_games_sales_df["Publisher"].isin(top_publishers_list)]
    .groupby("Publisher")[["Global_Sales", "NA_Sales"]]
    .sum()
)

sorted_index = sales_by_publisher["Global_Sales"].sort_values(ascending=True).index
sales_by_publisher = sales_by_publisher.loc[sorted_index]

bar_graph = go.Figure(
    data=[
        go.Bar(
            x=sales_by_publisher["Global_Sales"],
            y=sales_by_publisher.index,
            orientation="h",
            hovertemplate="<b>%{y}</b><br>Продажі: %{x:.1f} млн<extra></extra>"
        )
    ]
)

bar_graph.update_layout(
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            x=1.0, y=1.15,
            showactive=True,
            buttons=[
                dict(
                    label="Global_Sales",
                    method="update",
                    args=[
                        {"x": [sales_by_publisher["Global_Sales"]],
                         "hovertemplate": "<b>%{y}</b><br>Продажі: %{x:.1f} млн<extra></extra>"},
                        {"xaxis": {"title": "Global_Sales (млн копій)"},
                         "title": "Топ-10 видавців за Global_Sales"}
                    ]
                ),
                dict(
                    label="NA_Sales",
                    method="update",
                    args=[
                        {"x": [sales_by_publisher["NA_Sales"]],
                         "hovertemplate": "<b>%{y}</b><br>Продажі: %{x:.1f} млн<extra></extra>"},
                        {"xaxis": {"title": "NA_Sales (млн копій)"},
                         "title": "Топ-10 видавців за NA_Sales"}
                    ]
                ),
            ],
        )
    ],
    title="Топ-10 видавців за Global_Sales",
    xaxis_title="Global_Sales (млн копій)",
    yaxis_title="Publisher",
    height=500, width=1000
)

bar_graph.write_html("top_publishers_dropdown.html", include_plotlyjs="cdn")
bar_graph.show()

platforms = ["PS4", "PC", "X360"]
vgs_df_filtered = video_games_sales_df[video_games_sales_df["Platform"].isin(platforms)]

games_per_year = (
    vgs_df_filtered.groupby(["Year_of_Release", "Platform"])
    .size()
    .reset_index(name="Game_Count")
)

line_graph = px.line(
    games_per_year,
    x="Year_of_Release",
    y="Game_Count",
    color="Platform",
    markers=True,
    title="Кількість випущених ігор за роками (PS4, PC, X360)",
    labels={"Year_of_Release": "Year of release", "Game_Count": "Game count", "Platform": "Platform"}
)

line_graph.update_layout(height=500, width=1200)
line_graph.write_html("games_per_year_line.html", include_plotlyjs="cdn")
line_graph.show()

violin_graph = px.violin(
    video_games_sales_df,
    x="Rating",
    y="User_Score",
    box=True,
    points="all",
    title="Розподіл User_Score за віковим рейтингом ESRB"
)

violin_graph.update_layout(height=500, width=1200)
violin_graph.write_html("user_score_violin.html", include_plotlyjs="cdn")
violin_graph.show()

box_graph = px.box(
    video_games_sales_df,
    x="Genre",
    y="Critic_Score",
    points="outliers",
    title="Розподіл Critic_Score за жанром"
)

box_graph.update_layout(height=500, width=1200)
box_graph.write_html("critic_score_box.html", include_plotlyjs="cdn")
box_graph.show()

top5_platforms = (
    video_games_sales_df.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

df_top5 = video_games_sales_df[video_games_sales_df["Platform"].isin(top5_platforms)]

sunburst_graph = px.sunburst(
    df_top5,
    path=["Platform", "Genre"],
    values="Global_Sales",
    title="Розподіл Global_Sales за платформою та жанром (топ-5 платформ)"
)

sunburst_graph.update_layout(height=500, width=1000)
sunburst_graph.write_html("platform_genre_sunburst.html", include_plotlyjs="cdn")
sunburst_graph.show()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Огляд video games sales"),
    dcc.Graph(figure=bar_graph),
    dcc.Graph(figure=line_graph),
    dcc.Graph(figure=violin_graph),
    dcc.Graph(figure=box_graph),
    dcc.Graph(figure=sunburst_graph),
])

if __name__ == "__main__":
    app.run(debug=True)