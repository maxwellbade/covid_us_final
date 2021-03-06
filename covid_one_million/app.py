#import requests
import dash  # (version 1.12.0) pip install dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly
import numpy as np
# import seaborn as sns

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import plotly.figure_factory as ff

import csv
from urllib.request import urlopen
import urllib.request

# gapminder = px.data.gapminder()

bgcolors = {
    'background': '#13263a',
    'text': '#FFFFFF'
}

#------------------------------
# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
# external_stylesheets = [
#     'https://codepen.io/chriddyp/pen/bWLwgP.css',
#     {
#         'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
#         'rel': 'stylesheet',
#         'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
#         'crossorigin': 'anonymous'
#     }
# ]

# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#-------------------------------------------------------------------------------
#app stuff
app = dash.Dash(__name__,
                external_scripts=external_scripts
                ,external_stylesheets=external_stylesheets)

server = app.server

# app.config.requests_pathname_prefix = app.config.routes_pathname_prefix.split('/')[-1]

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)

#Server certificate verification by default has been
# introduced to Python recently (in 2.7.9).
# This protects against man-in-the-middle attacks,
# and it makes the client sure that the server is indeed who it claims to be.
# if the first execution doesn't run, just run it again.
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


url = "https://covidtracking.com/api/v1/us/daily.csv"
df = pd.read_csv(url)
# df.head()


#make new date column
df['year'] = df.date.astype(str).str[:4]
df['month_day'] = df.date.astype(str).str[-4:]
df['day'] = df.date.astype(str).str[-2:]
df['month'] = df.month_day.astype(str).str[:2]
df['date_new'] = df['year'] + "-" + df['month'] + "-" + df['day']

# df.head()


df['date_new'] = df['date_new'].astype('datetime64')
df.dtypes


cases = df[['date_new', 'totalTestResultsIncrease', 'negativeIncrease', 'positiveIncrease', 'deathIncrease', 'hospitalizedIncrease']]
# cases.head(20).style.background_gradient(cmap='Pastel1')


#create percent columns
cases['percent_positive'] = cases['positiveIncrease']/cases['totalTestResultsIncrease']
cases['percent_negative'] = cases['negativeIncrease']/cases['totalTestResultsIncrease']
cases['percent_death'] = cases['deathIncrease']/cases['totalTestResultsIncrease']
cases['percent_hospitalized'] = cases['hospitalizedIncrease']/cases['totalTestResultsIncrease']
# cases.head(20)

#create percent change columns
cases['positive_pct_change'] = cases['percent_positive'].pct_change()
cases['negative_pct_change'] = cases['percent_negative'].pct_change()
cases['total_cases_pct_change'] = cases['totalTestResultsIncrease'].pct_change()
cases['death_pct_change'] = cases['percent_death'].pct_change()
cases['hospitalized_pct_change'] = cases['percent_hospitalized'].pct_change()
# cases

#filter out old dates
cases = cases[cases['date_new'] > '2020-03-20']
# cases.head(20).style.background_gradient(cmap="Blues")


#make variables for subplots
percent_positive = list(cases.percent_positive)
percent_negative = list(cases.percent_negative)
percent_death = list(cases.percent_death)
percent_hospitalized = list(cases.percent_hospitalized)

negativeIncrease = list(cases.negativeIncrease)
positiveIncrease = list(cases.positiveIncrease)
deathIncrease = list(cases.deathIncrease)
hospitalizedIncrease = list(cases.hospitalizedIncrease)

totalTestResultsIncrease = list(cases.totalTestResultsIncrease)
total_cases_pct_change = list(cases.total_cases_pct_change)
positive_pct_change = list(cases.positive_pct_change)
negative_pct_change = list(cases.negative_pct_change)
death_pct_change = list(cases.death_pct_change)
hospitalized_pct_change = list(cases.hospitalized_pct_change)
date = list(cases.date_new)

# print("percent_positive")
# print(percent_positive)
# print("")
# print("percent_negative")
# print(percent_negative)
# print("")
# print("negativeIncrease")
# print(negativeIncrease)
# print("")
# print("positiveIncrease")
# print(positiveIncrease)
# print("")
# print("totalTestResultsIncrease")
# print(totalTestResultsIncrease)
# print("")
# print("total_cases_pct_change")
# print(total_cases_pct_change)
# print("")
# print("positive_pct_change")
# print(positive_pct_change)
# print("")
# print("negative_pct_change")
# print(negative_pct_change)
# print("")
# print("date")
# print(date)
# print("")


#melt daily percent change columns into one dataframe
positive_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['positive_pct_change'])
negative_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['negative_pct_change'])
death_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['death_pct_change'])
hospitalized_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['hospitalized_pct_change'])
total_cases_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['total_cases_pct_change'])

# print(positive_pct_melt.head())
# print(negative_pct_melt.head())
# print(death_pct_melt.head())
# print(hospitalized_pct_melt.head())
# print(total_cases_pct_melt.head())

cases_melted1 = positive_pct_melt.append(negative_pct_melt,ignore_index=True)
cases_melted2 = cases_melted1.append(death_pct_melt,ignore_index=True)
cases_melted3 = cases_melted2.append(hospitalized_pct_melt,ignore_index=True)
cases_melted = cases_melted3.append(total_cases_pct_melt,ignore_index=True)
# cases_melted.head()
# cases_melted.variable.value_counts()


fig0 = px.bar(df
             ,x="date_new"
             ,y="totalTestResults"
             ,hover_data=['totalTestResults']
             ,title="<b>Total Covid Tests (Cummulative)</b>")

# Add figure title
fig0.update_layout(
    template='plotly_dark'
)
# fig0.show()

percent_positive = list(cases.percent_positive)
percent_negative = list(cases.percent_negative)
date = list(cases.date_new)

cases_melt = pd.melt(cases, id_vars=['date_new'], value_vars=['negativeIncrease'
                                                              ,'positiveIncrease'
                                                              ,'totalTestResultsIncrease'
                                                             ]
                    )

# Create fig2ure with secondary y-axis
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

fig1 = px.line(cases_melt, x='date_new', y='value', color='variable')

# Add traces
fig1.add_trace(
    go.Scatter(x=date, y=percent_negative, name="percent_negative"),
    secondary_y=False,
)

fig1.add_trace(
    go.Scatter(x=date, y=percent_positive, name="percent_positive"),
    secondary_y=False,
)

# Add fig2ure title
fig1.update_layout(
    title_text="<b>Daily Covid Cases with Percent Changes</b>"
    ,template='plotly_dark'
    ,showlegend=False
)

#update legend
# fig1.update_layout(
    # legend=dict(
    #     yanchor="top",
    #     y=0.99,
    #     xanchor="left",
    #     x=0.01
    #     )
    # )

# Set x-axis title
fig1.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig1.update_yaxes(title_text="<b>Count</b>", secondary_y=False)
# fig2.show()


fig2 = make_subplots(specs=[[{"secondary_y": True}]])

fig2.add_trace(
    go.Scatter(x=date
               ,y=percent_negative
               ,name="percent_negative"
               ,marker_color=px.colors.qualitative.Plotly[2]),
    secondary_y=True,
)
fig2.add_trace(
    go.Scatter(x=date
               ,y=percent_positive
               ,name="percent_positive"
               ,marker_color=px.colors.qualitative.D3[3]),
    secondary_y=True,
)

# Add figure title
fig2.update_layout(
    title_text="<b>Daily Pos/Neg Percent of Covid Tests</b>"
)

# Set x-axis title
fig2.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig2.update_yaxes(title_text="<b>Percent</b>", secondary_y=True)

# Change the bar mode
fig2.update_layout(barmode='stack')

# Customize aspect
fig2.update_traces(marker_line_width=.01)

#update legend
fig2.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig2.show()


fig3 = make_subplots(specs=[[{"secondary_y": True}]])

fig3.add_trace(
    go.Bar(x=date
           ,y=negativeIncrease
           ,name="negativeIncrease"
           ,marker_color=px.colors.qualitative.Pastel1[3]),
    secondary_y=False,
)
fig3.add_trace(
    go.Bar(x=date
           ,y=positiveIncrease
           ,name="positiveIncrease"),
    secondary_y=False,
)
fig3.add_trace(
    go.Scatter(x=date
               ,y=totalTestResultsIncrease
               ,opacity=.7
               ,name="totalTestResultsIncrease"
               ,mode="markers"
               ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)

# Add fig3ure title
fig3.update_layout(
    title_text="<b>Daily Pos/Neg and Total Tests</b>"
)

# Set x-axis title
fig3.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig3.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)

# Change the bar mode
fig3.update_layout(barmode='stack')

# Customize aspect
fig3.update_traces(marker_line_width=.01)

#update legend
fig3.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig3.show()


fig4 = make_subplots(specs=[[{"secondary_y": True}]])

fig4.add_trace(
    go.Scatter(x=date
               ,y=positive_pct_change
               ,name="positive_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.T10[2]),
    secondary_y=False,
)
fig4.add_trace(
    go.Scatter(x=date
               ,y=negative_pct_change
               ,name="negative_pct_change"
               ,mode="markers"
               ,marker_color=px.colors.qualitative.Plotly[5]),
    secondary_y=True,
)
fig4.add_trace(
    go.Scatter(x=date
               ,y=total_cases_pct_change
               ,name="total_cases_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)


# Add fig4ure title
fig4.update_layout(
    title_text="<b>Daily Percent Changes of Covid Positive Tests and Total Tests</b>"
)

# Set x-axis title
fig4.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig4.update_yaxes(title_text="<b>Percent Change</b>", secondary_y=False)

# Change the bar mode
fig4.update_layout(barmode='stack')

# Customize aspect
fig4.update_traces(marker_line_width=.01)

#update legend
fig4.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig4.show()


fig5 = make_subplots(specs=[[{"secondary_y": True}]])

fill_colors = ['none', 'tozeroy', 'tozerox', 'tonexty', 'tonextx', 'toself', 'tonext']

#negative
fig5.add_trace(
    go.Scatter(x=date
           ,y=negativeIncrease
           ,name="negativeIncrease"
           ,line=dict(width=0.5, color='rgb(111, 231, 219)')
           ,stackgroup='one'
            ),
    secondary_y=False,
)
#positive
fig5.add_trace(
    go.Scatter(x=date
           ,y=positiveIncrease
           ,fill=fill_colors[1]
           ,mode="markers+lines"
           ,name="positiveIncrease"),
    secondary_y=False,
)
#total
fig5.add_trace(
    go.Scatter(x=date
               ,y=totalTestResultsIncrease
               ,opacity=.7
               ,name="totalTestResultsIncrease"
               ,line=dict(width=0.5, color='rgb(131, 90, 241)')
               ,stackgroup='one'),
    secondary_y=False,
)

# Add fig5ure title
fig5.update_layout(
    title_text="<b>Daily Pos/Neg and Total Tests</b>"
)

# Set x-axis title
fig5.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig5.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)

# Change the bar mode
fig5.update_layout(barmode='stack')

# Customize aspect
fig5.update_traces(marker_line_width=.01)

#update legend
fig5.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig5.show()


# In[156]:


fig6 = make_subplots(specs=[[{"secondary_y": True}]])

fig6.add_trace(
    go.Scatter(x=date
               ,y=positive_pct_change
               ,name="positive_pct_change"
               ,marker_color=px.colors.qualitative.T10[2]
               ,yaxis="y1")
#     secondary_y=False,
)
fig6.add_trace(
    go.Scatter(x=date
               ,y=negative_pct_change
               ,name="negative_pct_change"
               ,marker_color=px.colors.qualitative.T10[4]
               ,yaxis="y2")
#     secondary_y=False,
)
fig6.add_trace(
    go.Scatter(x=date
               ,y=total_cases_pct_change
               ,name="total_cases_pct_change"
               ,marker_color=px.colors.qualitative.Plotly[3]
               ,yaxis="y3")
#     secondary_y=False,
)

# Create axis objects
fig6.update_layout(
#     xaxis=date,
    yaxis1=dict(
        title="positive_pct_change",
        titlefont=dict(
            color="#663399"
        ),
        tickfont=dict(
            color="#663399"
        )
    ),
    yaxis2=dict(
        title="negative_pct_change",
        titlefont=dict(
            color="#006600"
        ),
        tickfont=dict(
            color="#006600"
        ),
        anchor="free",
        overlaying="y",
        side="right",
        position=1
    ),
    yaxis3=dict(
        title="total_cases_pct_change",
        titlefont=dict(
            color="#d62728"
        ),
        tickfont=dict(
            color="#d62728"
        ),
        anchor="x",
        overlaying="y",
        side="right"
    )
)

# Add fig6ure title
fig6.update_layout(
    title_text="<b>Daily Percent Changes of Covid Pos/Neg Tests and Total Tests</b>"
)

# Set x-axis title
fig6.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig6.update_yaxes(title_text="<b>Percent Change</b>", secondary_y=False)

# Change the bar mode
fig6.update_layout(barmode='stack')

# Customize aspect
fig6.update_traces(marker_line_width=.01)

#update legend
fig6.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

fig6.update_layout(
    # width=1200
    template='plotly_dark'
)
# fig6.show()


#second fig7ure
fig7 = make_subplots(specs=[[{"secondary_y": True}]])

fig7.add_trace(
    go.Scatter(x=date
               ,y=death_pct_change
               ,name="death_pct_change"
               ,marker_color=px.colors.qualitative.T10[0]),
    secondary_y=False,
)
fig7.add_trace(
    go.Scatter(x=date
               ,y=hospitalized_pct_change
               ,name="hospitalized_pct_change"
               ,marker_color=px.colors.qualitative.T10[6]),
    secondary_y=False,
)

# Add fig7ure title
fig7.update_layout(
    title_text="<b>Daily Percent Changes of Covid Death/Hospitalized</b>"
)

# Set x-axis title
fig7.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig7.update_yaxes(title_text="<b>Percent Change</b>", secondary_y=False)
# fig7.update_yaxes(title_text="<b>% Change</b>", secondary_y=True)

# Change the bar mode
fig7.update_layout(barmode='stack')

# Customize aspect
fig7.update_traces(
#                   marker_color='rgb(158,202,225)'
#                   , marker_line_color='rgb(8,48,107)',
                  marker_line_width=.1)
#                   ,opacity=0.6)

#update legend
fig7.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
))

fig7.update_layout(
    # width=1200
    template='plotly_dark'
)
# fig7.show()

fig8 = px.scatter(cases
                 ,x="date_new"
                 ,y="positive_pct_change"
                 ,trendline="lowess"
                 ,color_continuous_scale=px.colors.sequential.Inferno
                )
fig8.update_layout(
    height=800
    ,template='plotly_dark')

fig8.add_trace(
    go.Scatter(x=date
               ,y=negative_pct_change
               ,name="negative_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.T10[1]
              )
#     secondary_y=False,
),
fig8.add_trace(
    go.Scatter(x=date
               ,y=death_pct_change
               ,name="death_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.T10[2]
              )
#     secondary_y=False,
),
fig8.add_trace(
    go.Scatter(x=date
               ,y=hospitalized_pct_change
               ,name="hospitalized_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.T10[3]
              )
#     secondary_y=False,
),
fig8.add_trace(
    go.Scatter(x=date
               ,y=total_cases_pct_change
               ,name="total_cases_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.T10[4]
              )
#     secondary_y=False,
)
# fig8.show()


fig9 = px.scatter(cases, x="date_new", y="positive_pct_change", trendline="lowess"
                  , title="positive_pct_change"
#                   , color_continuous_scale="icefire"
                  , color="positive_pct_change", color_continuous_scale=px.colors.sequential.Inferno
                  , marginal_y="histogram", marginal_x="violin")
fig9.update_layout(
    height=400
    ,template='plotly_dark')
# fig9.show()

fig10 = px.scatter(cases, x="date_new", y="negative_pct_change", color="negative_pct_change"
                  , trendline="lowess", title="negative_pct_change"
                  , color_continuous_scale=px.colors.sequential.Inferno
                  , marginal_y="histogram", marginal_x="violin")
fig10.update_layout(
    height=400
    ,template='plotly_dark')
# fig10.show()

fig11 = px.scatter(cases, x="date_new", y="death_pct_change", color="death_pct_change"
                  , trendline="lowess", title="death_pct_change"
                  , color_continuous_scale=px.colors.sequential.Inferno
                  , marginal_y="histogram", marginal_x="violin")
fig11.update_layout(
    height=400
    ,template='plotly_dark')
# fig11.show()

fig12 = px.scatter(cases, x="date_new", y="hospitalized_pct_change", color="hospitalized_pct_change"
                  , trendline="lowess", title="hospitalized_pct_change"
                  , color_continuous_scale=px.colors.sequential.Inferno
                  , marginal_y="histogram", marginal_x="violin")
fig12.update_layout(
    height=400
    ,template='plotly_dark')
# fig12.show()

fig13 = px.scatter(cases, x="date_new", y="total_cases_pct_change", color="total_cases_pct_change"
                  , trendline="lowess", title="total_cases_pct_change"
                  , color_continuous_scale=px.colors.sequential.Inferno
                  , marginal_y="histogram", marginal_x="violin")
fig13.update_layout(
    height=400
    ,template='plotly_dark')
# fig13.show()

#add traces
trace1 = fig9['data'][0]
trace2 = fig10['data'][0]
trace3 = fig11['data'][0]
trace4 = fig12['data'][0]
trace5 = fig13['data'][0]

fig14 = make_subplots(rows=3
                    ,cols=2
                    ,shared_xaxes=False
                    ,row_heights=[9., 9., 9.]
                    ,column_widths=[.1, .1]
                    ,shared_yaxes=False
                    ,vertical_spacing=0.10
                    ,subplot_titles=['<b>positive_pct_change</b>'
                                     ,'<b>negative_pct_change</b>'
                                     ,'<b>death_pct_change</b>'
                                     ,'<b>hospitalized_pct_change</b>'
                                     ,'<b>total_cases_pct_change</b>'
                                    ]
                    ,x_title="<b>date</b>"
                    ,y_title="<b>percent_change</b>"
                   )

fig14.add_trace(trace1, row=1, col=1)
fig14.add_trace(trace2, row=1, col=2)
fig14.add_trace(trace3, row=2, col=1)
fig14.add_trace(trace4, row=2, col=2)
fig14.add_trace(trace5, row=3, col=1)

fig14['layout'].update(height=800
# , width=1200
        , title='<b>Covid Test Outcome Trends</b>'
        , template='plotly_dark')
# fig14.show()


# cases_melted.head()
cases_melted.variable.value_counts()
values_list = list(cases_melted.value)

fig15 = px.scatter(cases_melted, x="date_new", y="value"
                 , color="variable", facet_col="variable"
                 , trendline="lowess", trendline_color_override="white"
                 , color_continuous_scale=px.colors.sequential.Inferno
                 , marginal_y="bar", marginal_x="box"
                 , labels = ['test','test','test','test','test'])

fig15['layout'].update(height=800
# , width=1200
        , title='<b>Covid Test Outcome Trends</b>'
        , template='plotly_dark')
fig15.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig15.show()


#make variables for subplots
percent_positive = list(cases.percent_positive)
percent_negative = list(cases.percent_negative)
negativeIncrease = list(cases.negativeIncrease)
positiveIncrease = list(cases.positiveIncrease)
totalTestResultsIncrease = list(cases.totalTestResultsIncrease)
total_cases_pct_change = list(cases.total_cases_pct_change)
positive_pct_change = list(cases.positive_pct_change)
date = list(cases.date_new)

# Create fig16ure with secondary y-axis
fig16 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig16.add_trace(
    go.Bar(x=date
           ,y=negativeIncrease
           ,name="negativeIncrease"
           ,marker_color=px.colors.qualitative.Pastel1[3]),
    secondary_y=False,
)
fig16.add_trace(
    go.Bar(x=date, y=positiveIncrease, name="positiveIncrease"),
    secondary_y=False,
)
fig16.add_trace(
    go.Scatter(x=date
               ,y=totalTestResultsIncrease
               ,opacity=.7
               ,name="totalTestResultsIncrease"
               ,mode="markers"
               ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)
fig16.add_trace(
    go.Scatter(x=date
               ,y=percent_negative
               ,name="percent_negative"
               ,marker_color=px.colors.qualitative.Plotly[2]),
    secondary_y=True,
)
fig16.add_trace(
    go.Scatter(x=date
               ,y=percent_positive
               ,name="percent_positive"
               ,marker_color=px.colors.qualitative.D3[3]),
    secondary_y=True,
)
fig16.add_trace(
    go.Scatter(x=date
               ,y=positive_pct_change
               ,name="positive_pct_change"
               ,marker_color=px.colors.qualitative.T10[2]),
    secondary_y=True,
)
fig16.add_trace(
    go.Scatter(x=date
               ,y=negative_pct_change
               ,name="negative_pct_change"
               ,marker_color=px.colors.qualitative.Plotly[5]),
    secondary_y=True,
)
fig16.add_trace(
    go.Scatter(x=date
               ,y=total_cases_pct_change
               ,name="total_cases_pct_change"
               ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=True,
)


# Add fig16ure title
fig16.update_layout(
    title_text="<b>Daily Covid Cases</b>"
    ,height=800
    # ,width=1200
)

# Set x-axis title
fig16.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig16.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
fig16.update_yaxes(title_text="<b>% Change</b>", secondary_y=True)

# Change the bar mode
fig16.update_layout(barmode='stack')

# Customize aspect
fig16.update_traces(marker_line_width=.01)

#update legend
fig16.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig16.show()


#create a day of week column
s = pd.date_range(min(df.date_new),max(df.date_new), freq='D').to_series()
s = s.dt.dayofweek.tolist()
df['day_of_week'] = s

def day_of_week(df):
    if df['day_of_week'] == 0:
        return "Tuesday"
    elif df['day_of_week'] == 1:
        return "Monday"
    elif df['day_of_week'] == 2:
        return "Sunday"
    elif df['day_of_week'] == 3:
        return "Saturday"
    elif df['day_of_week'] == 4:
        return "Friday"
    elif df['day_of_week'] == 5:
        return "Thursday"
    elif df['day_of_week'] == 6:
        return "Wednesday"
    else:
        return ""

df['dayofweek'] = df.apply(day_of_week, axis=1)
# df.head(30)


#create min and max variables
y_min = min(df.totalTestResultsIncrease)
y_max = max(df.totalTestResultsIncrease)
# x_min = min(df.index)
# x_max = max(df.index)
x_min = min(df.month)
x_max = max(df.month)
x_range = [x_min,x_max]
y_range = [y_min,y_max]

# print('y_min:',y_min)
# print('y_max:',y_max)
# print('x_min:',x_min)
# print('x_max:',x_max)
# print('x_range:',x_range)
# print('y_range:',y_range)


#create total pos/neg/total variables by day
total_pos_increase_grp_day = df.groupby(['dayofweek'])['positiveIncrease'].sum()
avg_total_pos_increase_grp_day = df.groupby(['dayofweek'])['positiveIncrease'].mean()

total_neg_increase_grp_day = df.groupby(['dayofweek'])['negativeIncrease'].sum()
avg_total_neg_increase_grp_day = df.groupby(['dayofweek'])['negativeIncrease'].mean()

total_increase_grp_day = df.groupby(['dayofweek'])['totalTestResultsIncrease'].sum()
avg_total_increase_grp_day = df.groupby(['dayofweek'])['totalTestResultsIncrease'].mean()

avg_total_per_week = avg_total_increase_grp_day/7
avg_pos_per_week = avg_total_pos_increase_grp_day/7
avg_neg_per_week = avg_total_neg_increase_grp_day/7


# print('total_pos_increase_grp_day:',total_pos_increase_grp_day)
# print("")
# print('total_neg_increase_grp_day:',total_neg_increase_grp_day)
# print("")
# print('total_increase_grp_day:',total_increase_grp_day)
# print("")
# print("")
# print('avg_total_pos_increase_grp_day:',avg_total_pos_increase_grp_day)
# print("")
# print('avg_total_neg_increase_grp_day:',avg_total_neg_increase_grp_day)
# print("")
# print('avg_total_increase_grp_day:',avg_total_increase_grp_day)
# print("")
# print("")
# print('avg_pos_per_week:',avg_pos_per_week)
# print("")
# print('avg_neg_per_week:',avg_neg_per_week)
# print("")
# print('avg_total_per_week:',avg_total_per_week)

#put totals in a list for labeling later on
total_totals = list(total_increase_grp_day)
pos_totals = list(total_pos_increase_grp_day)
neg_totals = list(total_neg_increase_grp_day)

# print('total_totals:', total_totals)
# print('pos_totals:', pos_totals)
# print('neg_totals:', neg_totals)

#make day list
x_labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']
# print('x_labels:', x_labels)


#plots by day
fig17 = px.bar(df
             ,x='dayofweek'
             ,y='positiveIncrease'
             ,text='positiveIncrease'
             ,color='dayofweek'
             ,height=500
             ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
             ,hover_name="positiveIncrease")
fig17.update_traces(texttemplate='%{text:.2s}'
                  ,textposition='outside')
fig17.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Covid Tests Outcome</b>"
                 ,template='plotly_dark'
                 # ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 )

# Set x-axis title
fig17.update_xaxes(title_text="<b>Date</b>")

fig17.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
)

fig17.add_annotation( # add a text callout with arrow
    text="Lowest", x="Friday", y=500000, arrowhead=1, showarrow=True
)

total_labels = [{"x": x, "y": pos_totals*1.3, "text": str(pos_totals), "showarrow": False} for x, pos_totals in zip(x_labels, pos_totals)]

fig17.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 # ,width=1200
                 ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 # ,annotations=total_labels
                 )
# fig17.show()



fig18 = px.bar(df
             ,x='dayofweek'
             ,y='negativeIncrease'
             ,text='negativeIncrease'
             ,color='dayofweek'
             ,height=500
             ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
             ,hover_name="negativeIncrease")
fig18.update_traces(texttemplate='%{text:.2s}'
                  ,textposition='outside')
fig18.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,template='plotly_dark'
                 ,title_text="<b>Neagtive Covid Tests Grouped by Day</b>"
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

# Set x-axis title
fig18.update_xaxes(title_text="<b>Date</b>")

fig18.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
)

fig18.add_annotation( # add a text callout with arrow
    text="Highest", x="Tuesday", y=6700000, arrowhead=1, showarrow=True
)

fig18.add_annotation( # add a text callout with arrow
    text="Lowest", x="Friday", y=6000000, arrowhead=1, showarrow=True
)

total_labels = [{"x": x, "y": neg_totals*1.25, "text": str(neg_totals), "showarrow": False} for x, neg_totals in zip(x_labels, neg_totals)]

fig18.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 # ,width=1200
                 ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 # ,annotations=total_labels
                 )
# fig18.show()


fig19 = px.bar(df
             ,x='dayofweek'
             ,y='totalTestResultsIncrease'
             ,text='totalTestResultsIncrease'
             ,color='dayofweek'
             ,height=500
             ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
             ,hover_name="totalTestResultsIncrease")
fig19.update_traces(texttemplate='%{text:.2s}'
                  ,textposition='outside')

# Set x-axis title
fig19.update_xaxes(title_text="<b>Date</b>")

fig19.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
)

fig19.add_annotation( # add a text callout with arrow
    text="Highest", x="Tuesday", y=7400000, arrowhead=1, showarrow=True
)

fig19.add_annotation( # add a text callout with arrow
    text="Lowest", x="Friday", y=6600000, arrowhead=1, showarrow=True
)

total_labels = [{"x": x, "y": total_totals*.95, "text": str(total_totals), "showarrow": True} for x, total_totals in zip(x_labels, total_totals)]

fig19.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 # ,width=1200
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 # ,annotations=total_labels
                 )
# fig19.show()


#deaths
fig20 = px.bar(df
             ,x='dayofweek'
             ,y='deathIncrease'
             ,text='deathIncrease'
             ,color='dayofweek'
             ,height=500
             ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease','deathIncrease']
             ,hover_name="deathIncrease")
fig20.update_traces(texttemplate='%{text:.2s}'
                  ,textposition='outside')
fig20.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 # ,width=1200
                 ,title_text="<b>Death Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

# Set x-axis title
fig20.update_xaxes(title_text="<b>Date</b>")

fig20.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
)

fig20.add_annotation( # add a text callout with arrow
    text="Highest", x="Monday", y=24000, arrowhead=1, showarrow=True
)

fig20.add_annotation( # add a text callout with arrow
    text="Lowest", x="Friday", y=12000, arrowhead=1, showarrow=True
)

fig20.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 # ,width=1200
                 ,title_text="<b>Total Covid Deaths Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})
#                  ,annotations=total_labels)
# fig20.show()



fig21 = px.bar(df
             ,x='dayofweek'
             ,y='hospitalizedIncrease'
             ,text='hospitalizedIncrease'
             ,color='dayofweek'
             ,height=500
             ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease','deathIncrease','hospitalizedIncrease']
             ,hover_name="hospitalizedIncrease")
fig21.update_traces(texttemplate='%{text:.2s}'
                  ,textposition='outside')
fig21.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Hospitalized Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 # ,width=1200
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

# Set x-axis title
fig21.update_xaxes(title_text="<b>Date</b>")

fig21.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
)

fig21.add_annotation( # add a text callout with arrow
    text="Highest", x="Tuesday", y=55000, arrowhead=1, showarrow=True
)

fig21.add_annotation( # add a text callout with arrow
    text="Lowest", x="Thursday", y=25000, arrowhead=1, showarrow=True
)

fig21.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Total Hospitalized Covid Deaths Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})
# fig21.show()


#map day of week column to cases_melted dataframe
mapping = df[['date_new', 'dayofweek']]
# mapping
cases_melted = pd.merge(cases_melted, mapping, how='left', on=['date_new', 'date_new'])
# print(cases_melted)
# print(df.dayofweek)


fig22 = px.scatter(cases_melted, x="date_new", y="value"
                 , color="variable", facet_row="variable", facet_col="dayofweek"
                 , trendline="lowess", trendline_color_override="white"
                 , color_continuous_scale=px.colors.sequential.Inferno
                 , marginal_y="bar", marginal_x="box")

fig22['layout'].update(height=1000
                # , width=1200
                , title='<b>Covid Test Outcome Trends</b>'
                , template='plotly_dark')
fig22.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig22.show()

fig23 = px.bar(cases_melted, x="date_new", y="value"
                 , color="variable", facet_row="variable", facet_col="dayofweek"
                 , color_continuous_scale=px.colors.sequential.Inferno)

fig23['layout'].update(height=1000
                # , width=1200
                , title='<b>Covid Test Outcome Trends</b>'
                , template='plotly_dark')
fig23.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig23.show()


# cases_melted = cases_melted.drop(['dayofweek_x', 'dayofweek_y'], axis=1)
# cases_melted.style.background_gradient(cmap='Blues')


cases_melted['rank_value'] = cases_melted['value'].rank(method="max")
# print(cases_melted.head(30).sort_values(by='rank_value'))
# print(cases_melted.tail(30).sort_values(by='rank_value'))


#sum percent changes by day
#sundays have the highest positive percent changes
#tuesdays have the highest negative percent changes
cases_day = cases_melted[['dayofweek','value']]
cases_day = cases_day.groupby('dayofweek').sum().reset_index()
# cases_day.head(10).style.background_gradient(cmap='inferno')

fig24 = px.bar(cases_day, x="dayofweek", y="value"
                 , color="dayofweek"
                 , text="value"
                 , color_continuous_scale=px.colors.sequential.Inferno
                 , template="plotly_dark")

fig24['layout'].update(height=800
                     # , width=1200
                     , title='<b>Sum of Covid Test Daily Perent Changes per Day Of Week</b>'
                     , template='plotly_dark'
                     , yaxis_title="Sum of % Change"
                     , xaxis_title="Day of Week"
                     , legend_title="Day of Week"
                     , xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                    )
# fig24.show()


fig40 = px.bar(cases_melted
                 , x="dayofweek", y="value"
                 , color="variable"
                 , hover_name="value"
                 , range_y=[-2,2]
                 , animation_group="dayofweek"
                 , animation_frame=cases_melted.index)


fig40['layout'].update(height=500
                # , width=1200
                , title='<b>Covid Test Outcome Trends</b>'
                , template='plotly_dark')
fig40.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig40.show()


fig25 = px.bar(cases_melted, x="date_new", y="value"
                 , color="variable"
                 , color_continuous_scale=px.colors.sequential.Inferno)

fig25['layout'].update(height=500
                     # , width=1200
                     , title='<b>Sum of Covid Test Daily Percent Changes by Outcome</b>'
                     , yaxis_title="Sum of Daily % Changes"
                     , xaxis_title="Date"
                     , legend_title="Sum of Daily % Changes"
                     , template='plotly_dark')
fig25.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig25.show()

fig26 = px.bar(cases_melted, x="date_new", y="value"
                 , color="dayofweek"
                 , color_continuous_scale=px.colors.sequential.Inferno)


fig26['layout'].update(height=500
                     # , width=1200
                     , title='<b>Sum of Covid Test Daily Percent Changes by Outcome</b>'
                     , yaxis_title="Sum of Daily % Changes"
                     , xaxis_title="Date"
                     , legend_title="Day of Week"
                     , template='plotly_dark')
fig26.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig26.show()

fig27 = px.bar(cases_melted, x="date_new", y="value"
                 , color="dayofweek", facet_col="dayofweek"
                 , color_continuous_scale=px.colors.sequential.Inferno)
#                  , facet_col_wrap=3)
#                  , size=cases_melted.index)

fig27['layout'].update(height=500
                     # , width=1200
                     , title='<b>Covid Test Outcome Trends Grouped by Day Of Week</b>'
                     , template='plotly_dark'
                     , yaxis_title="Sum of Daily % Changes"
                     , xaxis_title="Day of Week"
                     , legend_title="Sum of Daily % Changes")
fig27.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig27.show()

fig28 = px.bar(cases_melted, x="dayofweek", y="value"
                 , color="value"
                 , color_continuous_scale=px.colors.sequential.Inferno)
#                  , facet_col_wrap=3)
#                  , size=cases_melted.index)

fig28['layout'].update(height=500
                     # , width=1200
                     , title='<b>Covid Test Outcome Trends Grouped by Day Of Week</b>'
                     , template='plotly_dark'
                     , yaxis_title="Sum of Daily % Changes"
                     , xaxis_title="Day of Week"
                     , legend_title="Sum of Daily % Changes")
fig28.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig28.show()

fig29 = px.bar(cases_melted, x="variable", y="value"
                 , color="dayofweek"
                 , color_continuous_scale=px.colors.sequential.Inferno)
#                  , facet_col_wrap=3)
#                  , size=cases_melted.index)

fig29['layout'].update(height=500
                     # , width=1200
                     , title='<b>Covid Test Outcome Trends Grouped by Day Of Week</b>'
                     , template='plotly_dark'
                     , yaxis_title="Sum of Daily % Changes"
                     , xaxis_title="Outcome"
                     , legend_title="Sum of Daily % Changes")
fig29.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig29.show()

#create rounded columns and df
cases['total_rounded'] = cases.totalTestResultsIncrease.round(-4)
cases['percent_positive_rounded'] = cases.percent_positive.round(2)
cases['percent_negative_rounded'] = cases.percent_negative.round(2)
cases['percent_death_rounded'] = cases.percent_death.round(2)
cases['percent_hospitalized_rounded'] = cases.percent_hospitalized.round(2)

cases_rounded = cases[['date_new','total_rounded','percent_positive_rounded'
                      ,'percent_negative_rounded','percent_death_rounded'
                      ,'percent_hospitalized_rounded']]

#add 5 day moving average columns
cases_rounded['percent_pos_5d_avg'] = cases_rounded.rolling(window=5)['percent_positive_rounded'].mean()
cases_rounded['total_rounded_5d_avg'] = cases_rounded.rolling(window=5)['total_rounded'].mean()
cases_rounded['percent_neg_5d_avg'] = cases_rounded.rolling(window=5)['percent_negative_rounded'].mean()
cases_rounded['percent_death_5d_avg'] = cases_rounded.rolling(window=5)['percent_death_rounded'].mean()
cases_rounded['percent_hospitalized_5d_avg'] = cases_rounded.rolling(window=5)['percent_hospitalized_rounded'].mean()

#create slope cols
cases_rounded['percent_pos_5d_avg_slope'] = cases_rounded.percent_pos_5d_avg.diff().fillna(0)
cases_rounded['total_rounded_5d_avg_slope'] = cases_rounded.total_rounded_5d_avg.diff().fillna(0)
cases_rounded['percent_neg_5d_avg_slope'] = cases_rounded.percent_neg_5d_avg.diff().fillna(0)
cases_rounded['percent_death_5d_avg_slope'] = cases_rounded.percent_death_5d_avg.diff().fillna(0)
cases_rounded['percent_hospitalized_5d_avg_slope'] = cases_rounded.percent_hospitalized_5d_avg.diff().fillna(0)

#convert lists
#rounded lists
total_rounded = list(cases_rounded.total_rounded)
percent_positive_rounded = list(cases_rounded.percent_positive_rounded)
percent_negative_rounded = list(cases_rounded.percent_negative_rounded)
percent_death_rounded = list(cases_rounded.percent_death_rounded)
percent_hospitalized_rounded = list(cases_rounded.percent_hospitalized_rounded)

#5d avg lists
percent_pos_5d_avg = list(cases_rounded.percent_pos_5d_avg)
total_rounded_5d_avg = list(cases_rounded.total_rounded_5d_avg)
percent_neg_5d_avg = list(cases_rounded.percent_neg_5d_avg)
percent_death_5d_avg = list(cases_rounded.percent_death_5d_avg)
percent_hospitalized_5d_avg = list(cases_rounded.percent_hospitalized_5d_avg)

#slope lists
percent_pos_5d_avg_slope = list(cases_rounded.percent_pos_5d_avg_slope)
total_rounded_5d_avg_slope = list(cases_rounded.total_rounded_5d_avg_slope)
percent_neg_5d_avg_slope = list(cases_rounded.percent_neg_5d_avg_slope)
percent_death_5d_avg_slope = list(cases_rounded.percent_death_5d_avg_slope)
percent_hospitalized_5d_avg_slope = list(cases_rounded.percent_hospitalized_5d_avg_slope)


# Create fig30ure with secondary y-axis
fig30 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig30.add_trace(
    go.Scatter(x=date
           ,y=total_rounded
           ,name="total_rounded"
           ,mode="lines+markers"
#            ,opacity=.5
           ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)
fig30.add_trace(
    go.Scatter(x=date
           , y=percent_positive_rounded
#            , opacity=.5
           , mode="lines+markers"
           , marker_color=px.colors.qualitative.Plotly[5]
           , name="percent_positive_rounded"),
    secondary_y=True,
)

#moving averages
fig30.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="total_rounded_5d_avg"),
    secondary_y=False,
)
fig30.add_trace(
    go.Scatter(x=date
           , y=percent_pos_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="percent_pos_5d_avg"),
    secondary_y=True,
)

#slopes
fig30.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[3]
           , name="total_rounded_5d_avg_slope"),
    secondary_y=False,
)
fig30.add_trace(
    go.Scatter(x=date
           , y=percent_pos_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[5]
           , name="percent_pos_5d_avg_slope"),
    secondary_y=True,
)

# Add fig30ure title
fig30.update_layout(
    title_text="<b>Total Daily Cases vs. Daily Percent Positive (Rounded) with 5 Day Moving Average and Slope</b>"
    ,height=800
)

# Set x-axis title
fig30.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig30.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
fig30.update_yaxes(title_text="<b>% Positive Cases</b>", secondary_y=True)

# Change the bar mode
fig30.update_layout(barmode='stack')

# Customize aspect
fig30.update_traces(
#                   marker_color='rgb(158,202,225)'
#                   , marker_line_color='rgb(8,48,107)',
                  marker_line_width=.01)
#                   ,opacity=0.6)

#update legend
fig30.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.01,
    xanchor="right",
    x=1
))
# fig30.show()

# Create fig30ure with secondary y-axis
fig31 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig31.add_trace(
    go.Scatter(x=date
           ,y=total_rounded
           ,name="total_rounded"
           ,mode="lines+markers"
#            ,opacity=.5
           ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)
fig31.add_trace(
    go.Scatter(x=date
           , y=percent_negative_rounded
#            , opacity=.5
           , mode="lines+markers"
           , marker_color=px.colors.qualitative.Plotly[2]
           , name="percent_negative_rounded"),
    secondary_y=True,
)

#moving averages
fig31.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="total_rounded_5d_avg"),
    secondary_y=False,
)
fig31.add_trace(
    go.Scatter(x=date
           , y=percent_neg_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="percent_neg_5d_avg"),
    secondary_y=True,
)

#slopes
fig31.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[3]
           , name="total_rounded_5d_avg_slope"),
    secondary_y=False,
)
fig31.add_trace(
    go.Scatter(x=date
           , y=percent_neg_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[2]
           , name="percent_neg_5d_avg_slope"),
    secondary_y=True,
)

# Add fig30ure title
fig31.update_layout(
    title_text="<b>Total Daily Cases vs. Daily Percent Negative (Rounded) with 5 Day Moving Average and Slope</b>"
    ,height=800
)

# Set x-axis title
fig31.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig31.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
fig31.update_yaxes(title_text="<b>% Negative Cases</b>", secondary_y=True)

# Change the bar mode
fig31.update_layout(barmode='stack')

# Customize aspect
fig31.update_traces(
#                   marker_color='rgb(158,202,225)'
#                   , marker_line_color='rgb(8,48,107)',
                  marker_line_width=.01)
#                   ,opacity=0.6)

#update legend
fig31.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.01,
    xanchor="right",
    x=1
))
# fig31.show()

# Create fig30ure with secondary y-axis
fig32 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig32.add_trace(
    go.Scatter(x=date
           ,y=total_rounded
           ,name="total_rounded"
           ,mode="lines+markers"
#            ,opacity=.5
           ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)
fig32.add_trace(
    go.Scatter(x=date
           , y=percent_death_rounded
#            , opacity=.5
           , mode="lines+markers"
           , marker_color=px.colors.qualitative.Plotly[6]
           , name="percent_death_rounded"),
    secondary_y=True,
)

#moving averages
fig32.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="total_rounded_5d_avg"),
    secondary_y=False,
)
fig32.add_trace(
    go.Scatter(x=date
           , y=percent_death_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="percent_death_5d_avg"),
    secondary_y=True,
)

#slopes
fig32.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[3]
           , name="total_rounded_5d_avg_slope"),
    secondary_y=False,
)
fig32.add_trace(
    go.Scatter(x=date
           , y=percent_death_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[6]
           , name="percent_death_5d_avg_slope"),
    secondary_y=True,
)

# Add fig30ure title
fig32.update_layout(
    title_text="<b>Total Daily Cases vs. Daily Percent Death (Rounded) with 5 Day Moving Average and Slope</b>"
    ,height=800
)

# Set x-axis title
fig32.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig32.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
fig32.update_yaxes(title_text="<b>% Death Cases</b>", secondary_y=True)

# Change the bar mode
fig32.update_layout(barmode='stack')

# Customize aspect
fig32.update_traces(
#                   marker_color='rgb(158,202,225)'
#                   , marker_line_color='rgb(8,48,107)',
                  marker_line_width=.01)
#                   ,opacity=0.6)

#update legend
fig32.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.01,
    xanchor="right",
    x=1
))
# fig32.show()

# Create fig30ure with secondary y-axis
fig33 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig33.add_trace(
    go.Scatter(x=date
           ,y=total_rounded
           ,name="total_rounded"
           ,mode="lines+markers"
#            ,opacity=.5
           ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=False,
)
fig33.add_trace(
    go.Scatter(x=date
           , y=percent_hospitalized_rounded
#            , opacity=.5
           , mode="lines+markers"
           , marker_color=px.colors.qualitative.Plotly[4]
           , name="percent_hospitalized_rounded"),
    secondary_y=True,
)

#moving averages
fig33.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="total_rounded_5d_avg"),
    secondary_y=False,
)
fig33.add_trace(
    go.Scatter(x=date
           , y=percent_hospitalized_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="percent_hospitalized_5d_avg"),
    secondary_y=True,
)

#slopes
fig33.add_trace(
    go.Scatter(x=date
           , y=total_rounded_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[3]
           , name="total_rounded_5d_avg_slope"),
    secondary_y=False,
)
fig33.add_trace(
    go.Scatter(x=date
           , y=percent_hospitalized_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[4]
           , name="percent_hospitalized_5d_avg_slope"),
    secondary_y=True,
)

# Add fig30ure title
fig33.update_layout(
    title_text="<b>Total Daily Cases vs. Daily Percent Hospitalized (Rounded) with 5 Day Moving Average and Slope</b>"
    ,height=800
)

# Set x-axis title
fig33.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig33.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
fig33.update_yaxes(title_text="<b>% Hospitalized Cases</b>", secondary_y=True)

# Change the bar mode
fig33.update_layout(barmode='stack')

# Customize aspect
fig33.update_traces(
#                   marker_color='rgb(158,202,225)'
#                   , marker_line_color='rgb(8,48,107)',
                  marker_line_width=.01)
#                   ,opacity=0.6)

#update legend
fig33.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.0,
    xanchor="right",
    x=1
))
# fig33.show()

# Create fig34ure with secondary y-axis
fig34 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig34.add_trace(
    go.Scatter(x=date
           ,y=percent_death_rounded
           ,name="percent_death_rounded"
           ,mode="lines+markers"
#            ,opacity=.5
           ,marker_color=px.colors.qualitative.Plotly[6]),
    secondary_y=False,
)
fig34.add_trace(
    go.Scatter(x=date
           , y=percent_positive_rounded
#            , opacity=.5
           , mode="lines+markers"
           , marker_color=px.colors.qualitative.Plotly[5]
           , name="percent_positive_rounded"),
    secondary_y=True,
)

#moving averages
fig34.add_trace(
    go.Scatter(x=date
           , y=percent_death_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="percent_death_5d_avg"),
    secondary_y=False,
)
fig34.add_trace(
    go.Scatter(x=date
           , y=percent_pos_5d_avg
           , opacity=.6
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[1]
           , name="percent_pos_5d_avg"),
    secondary_y=True,
)

#slopes
fig34.add_trace(
    go.Scatter(x=date
           , y=percent_death_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[6]
           , name="percent_death_5d_avg_slope"),
    secondary_y=False,
)
fig34.add_trace(
    go.Scatter(x=date
           , y=percent_pos_5d_avg_slope
           , opacity=.7
           , mode="lines"
           , marker_color=px.colors.qualitative.Plotly[5]
           , name="percent_pos_5d_avg_slope"),
    secondary_y=True,
)

# Add fig34ure title
fig34.update_layout(
    title_text="<b>Daily Percent Death vs. Daily Percent Positive (Rounded) with 5 Day Moving Average and Slope</b>"
    ,height=800
)

# Set x-axis title
fig34.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig34.update_yaxes(title_text="<b>% Death Cases</b>", secondary_y=False)
fig34.update_yaxes(title_text="<b>% Positive Cases</b>", secondary_y=True)

# Change the bar mode
fig34.update_layout(barmode='stack')

# Customize aspect
fig34.update_traces(
#                   marker_color='rgb(158,202,225)'
#                   , marker_line_color='rgb(8,48,107)',
                  marker_line_width=.01)
#                   ,opacity=0.6)

#update legend
fig34.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.01,
    xanchor="right",
    x=1
))
# fig34.show()

# Create fig35ure with secondary y-axis
fig35 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
#increases
fig35.add_trace(
    go.Bar(x=date
           ,y=deathIncrease
           ,name="deathIncrease"
           ,marker_color=px.colors.qualitative.Plotly[5]),
    secondary_y=False,
)
fig35.add_trace(
    go.Bar(x=date
           , y=positiveIncrease
           , name="positiveIncrease"
           , marker_color=px.colors.qualitative.D3[7]),
    secondary_y=False,
)
# fig35.add_trace(
#     go.Scatter(x=date
#                ,y=totalTestResultsIncrease
#                ,opacity=.7
#                ,name="totalTestResultsIncrease"
#                ,mode="markers"
#                ,marker_color=px.colors.qualitative.Plotly[3]),
#     secondary_y=False,
# )
#percent
fig35.add_trace(
    go.Scatter(x=date
               ,y=percent_death
               ,name="percent_death"
               ,marker_color=px.colors.qualitative.Plotly[2]),
    secondary_y=True,
)
fig35.add_trace(
    go.Scatter(x=date
               ,y=percent_positive
               ,name="percent_positive"
               ,marker_color=px.colors.qualitative.Plotly[3]),
    secondary_y=True,
)
#pct change
fig35.add_trace(
    go.Scatter(x=date
               ,y=positive_pct_change
               ,name="positive_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.T10[2]),
    secondary_y=True,
)
fig35.add_trace(
    go.Scatter(x=date
               ,y=death_pct_change
               ,name="death_pct_change"
               ,mode="lines+markers"
               ,marker_color=px.colors.qualitative.Plotly[5]),
    secondary_y=True,
)
# fig35.add_trace(
#     go.Scatter(x=date
#                ,y=total_cases_pct_change
#                ,name="total_cases_pct_change"
#                ,marker_color=px.colors.qualitative.Plotly[3]),
#     secondary_y=True,
# )

# Add fig35ure title
fig35.update_layout(
    title_text="<b>Positive vs. Death Covid Cases</b>"
    ,height=800
)

# Set x-axis title
fig35.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig35.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
fig35.update_yaxes(title_text="<b>% Change</b>", secondary_y=True)

# Change the bar mode
fig35.update_layout(barmode='stack')

# Customize aspect
fig35.update_traces(
                  marker_line_width=.01)

#update legend
fig35.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig35.show()

#-------------------------------------------------------------
#run app layout things

# app = dash.Dash()

app.layout = html.Div(children=[
        html.Br()
        ,html.Br()
        ,html.Br()

        ,html.H1(children='A Deeper Look into the Analytics of Covid-19')

        ,html.Div([
        html.H6(children='By: Max Bade')
        ], style={"color": "#B2B7B7"})

        ,html.Br()
        ,html.Br()

        ,html.Div(children='''
        The purpose of this page is to provide a more in-depth analysis of \
        the Covid-19 outbreak. The charts on this page offer a range of \
        analytical views. From daily percent changes and trends for each \
        day of the week, to the slope and moving averages for each outcome/metric.\
        ''')

        ,html.Br()

        ,html.Div(children='''
        The data used for this analysis comes from '''),dcc.Markdown('''\
        [Our World in Data]("https://covidtracking.com/api/v1/us/daily.csv")''')
        ,html.Div(children='''
        A more detailed description of the data can be found at the '''),dcc.Markdown('''\
        [OWID Website]("https://ourworldindata.org/coronavirus-data")''')

        ,html.Br()

        ,html.Div(children='''
        *The charts below provide analysis for the United States.
        ''')

        ,html.Br()

        ,html.Div([
        html.H4("Here's a glance of the initial dataframe we'll be using:"),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns],
            data=df.to_dict('records'),
            style_cell = {
                    'font-family': 'sans-serif',
                    'font-size': '14px',
                    'text-align': 'center'
                },
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 10,
            style_table={'overflowX': 'scroll'}
            )
        ],style={'padding-left': '2%', 'padding-right': '2%'})

        ,html.Br()
        ,html.Br()
        ,html.Br(),

    html.Div([
        html.Div([
        html.H4("Cumulative Tests"),
        dcc.Graph(figure=fig0)
        # ])
        ], className="six columns"
        ,style={'padding-left': '2%', 'padding-right': '2%',
                'vertical-align': 'middle'})

        ,html.Br(),

        html.Div([
        html.H4("Daily Tests"),
        dcc.Graph(figure=fig1)
        # ])
        ], className="six columns"
        ,style={'padding-left': '2%', 'padding-right': '2%',
                'margin-top': -24})

    ], className="row")

        ,html.Br()
        ,html.Br()
        ,html.Br()

        ,html.H2("Daily Covid Tests Meets Percentage Pos/Neg Meets Daily Percent Change")

        ,html.Div([
        dcc.Markdown('''

        ```
        #make variables for subplots
        percent_positive = list(cases.percent_positive)
        percent_negative = list(cases.percent_negative)
        negativeIncrease = list(cases.negativeIncrease)
        positiveIncrease = list(cases.positiveIncrease)
        totalTestResultsIncrease = list(cases.totalTestResultsIncrease)
        total_cases_pct_change = list(cases.total_cases_pct_change)
        positive_pct_change = list(cases.positive_pct_change)
        date = list(cases.date_new)

        # Create fig16ure with secondary y-axis
        fig16 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig16.add_trace(
            go.Bar(x=date
                   ,y=negativeIncrease
                   ,name="negativeIncrease"
                   ,marker_color=px.colors.qualitative.Pastel1[3]),
            secondary_y=False,
        )
        fig16.add_trace(
            go.Bar(x=date, y=positiveIncrease, name="positiveIncrease"),
            secondary_y=False,
        )
        fig16.add_trace(
            go.Scatter(x=date
                       ,y=totalTestResultsIncrease
                       ,opacity=.7
                       ,name="totalTestResultsIncrease"
                       ,mode="markers"
                       ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )
        fig16.add_trace(
            go.Scatter(x=date
                       ,y=percent_negative
                       ,name="percent_negative"
                       ,marker_color=px.colors.qualitative.Plotly[2]),
            secondary_y=True,
        )
        fig16.add_trace(
            go.Scatter(x=date
                       ,y=percent_positive
                       ,name="percent_positive"
                       ,marker_color=px.colors.qualitative.D3[3]),
            secondary_y=True,
        )
        fig16.add_trace(
            go.Scatter(x=date
                       ,y=positive_pct_change
                       ,name="positive_pct_change"
                       ,marker_color=px.colors.qualitative.T10[2]),
            secondary_y=True,
        )
        fig16.add_trace(
            go.Scatter(x=date
                       ,y=negative_pct_change
                       ,name="negative_pct_change"
                       ,marker_color=px.colors.qualitative.Plotly[5]),
            secondary_y=True,
        )
        fig16.add_trace(
            go.Scatter(x=date
                       ,y=total_cases_pct_change
                       ,name="total_cases_pct_change"
                       ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=True,
        )

        # Add fig16ure title
        fig16.update_layout(
            title_text="<b>Daily Covid Cases</b>"
            ,height=800
        )

        # Set x-axis title
        fig16.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig16.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
        fig16.update_yaxes(title_text="<b>% Change</b>", secondary_y=True)

        # Change the bar mode
        fig16.update_layout(barmode='stack')

        # Customize aspect
        fig16.update_traces(
                          marker_line_width=.01)

        #update legend
        fig16.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        fig16.show()
        ```
        ''')
        ], className='divBorder', style={
                 "height": 350
                , "overflowY": "scroll"
                , "background-color": "#4F90D1"
                , "color": "Black"
                , "font-family": "sans-serif"
                , "size": 16}
        )
        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig16)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()
        ,html.Br()

        ,html.H1(children='A Breakdown of the Above Chart')

        ,html.Div(children='''
        The charts below offer a breakdown of the above chart. Given the \
        complexity, I figured it might be nice to offer a view for each of \
        the pieces for this chart.
        ''')

        ,html.Br()

        ,html.H5(children='Key Take Aways:')

        ,html.Div(children='''
        -The more daily covid tests, the more positive tests\
        It's simply in the numbers. Below we'll take a look at death rates\
        to answer the question "does more covid tests equal more covid deaths?"
        ''')

        ,html.Br()

        ,html.Div(children='''
        -In July we're averageing roughly 700k total daily covid tests.
        ''')

        ,html.Br()

        ,html.Div([
        dcc.Markdown('''

        ```
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        fig2.add_trace(
            go.Scatter(x=date
                       ,y=percent_negative
                       ,name="percent_negative"
                       ,marker_color=px.colors.qualitative.Plotly[2]),
            secondary_y=True,
        )
        fig2.add_trace(
            go.Scatter(x=date
                       ,y=percent_positive
                       ,name="percent_positive"
                       ,marker_color=px.colors.qualitative.D3[3]),
            secondary_y=True,
        )

        # Add figure title
        fig2.update_layout(
            title_text="<b>Daily Pos/Neg Percent of Covid Tests</b>"
        )

        # Set x-axis title
        fig2.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig2.update_yaxes(title_text="<b>Percent</b>", secondary_y=True)

        # Change the bar mode
        fig2.update_layout(barmode='stack')

        # Customize aspect
        fig2.update_traces(marker_line_width=.01)

        #update legend
        fig2.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        # fig2.show()


        fig3 = make_subplots(specs=[[{"secondary_y": True}]])

        fig3.add_trace(
            go.Bar(x=date
                   ,y=negativeIncrease
                   ,name="negativeIncrease"
                   ,marker_color=px.colors.qualitative.Pastel1[3]),
            secondary_y=False,
        )
        fig3.add_trace(
            go.Bar(x=date
                   ,y=positiveIncrease
                   ,name="positiveIncrease"),
            secondary_y=False,
        )
        fig3.add_trace(
            go.Scatter(x=date
                       ,y=totalTestResultsIncrease
                       ,opacity=.7
                       ,name="totalTestResultsIncrease"
                       ,mode="markers"
                       ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )

        # Add fig3ure title
        fig3.update_layout(
            title_text="<b>Daily Pos/Neg and Total Tests</b>"
        )

        # Set x-axis title
        fig3.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig3.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)

        # Change the bar mode
        fig3.update_layout(barmode='stack')

        # Customize aspect
        fig3.update_traces(marker_line_width=.01)

        #update legend
        fig3.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        # fig3.show()


        fig4 = make_subplots(specs=[[{"secondary_y": True}]])

        fig4.add_trace(
            go.Scatter(x=date
                       ,y=positive_pct_change
                       ,name="positive_pct_change"
                       ,mode="lines+markers"
                       ,marker_color=px.colors.qualitative.T10[2]),
            secondary_y=False,
        )
        fig4.add_trace(
            go.Scatter(x=date
                       ,y=negative_pct_change
                       ,name="negative_pct_change"
                       ,mode="markers"
                       ,marker_color=px.colors.qualitative.Plotly[5]),
            secondary_y=True,
        )
        fig4.add_trace(
            go.Scatter(x=date
                       ,y=total_cases_pct_change
                       ,name="total_cases_pct_change"
                       ,mode="lines+markers"
                       ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )


        # Add fig4ure title
        fig4.update_layout(
            title_text="<b>Daily Percent Changes of Covid Positive Tests and Total Tests</b>"
        )

        # Set x-axis title
        fig4.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig4.update_yaxes(title_text="<b>Percent Change</b>", secondary_y=False)

        # Change the bar mode
        fig4.update_layout(barmode='stack')

        # Customize aspect
        fig4.update_traces(marker_line_width=.01)

        #update legend
        fig4.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        # fig4.show()


        fig5 = make_subplots(specs=[[{"secondary_y": True}]])

        fill_colors = ['none', 'tozeroy', 'tozerox', 'tonexty', 'tonextx', 'toself', 'tonext']

        #negative
        fig5.add_trace(
            go.Scatter(x=date
                   ,y=negativeIncrease
                   ,name="negativeIncrease"
                   ,line=dict(width=0.5, color='rgb(111, 231, 219)')
                   ,stackgroup='one'
                    ),
            secondary_y=False,
        )
        #positive
        fig5.add_trace(
            go.Scatter(x=date
                   ,y=positiveIncrease
                   ,fill=fill_colors[1]
                   ,mode="markers+lines"
                   ,name="positiveIncrease"),
            secondary_y=False,
        )
        #total
        fig5.add_trace(
            go.Scatter(x=date
                       ,y=totalTestResultsIncrease
                       ,opacity=.7
                       ,name="totalTestResultsIncrease"
                       ,line=dict(width=0.5, color='rgb(131, 90, 241)')
                       ,stackgroup='one'),
            secondary_y=False,
        )

        # Add fig5ure title
        fig5.update_layout(
            title_text="<b>Daily Pos/Neg and Total Tests</b>"
        )

        # Set x-axis title
        fig5.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig5.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)

        # Change the bar mode
        fig5.update_layout(barmode='stack')

        # Customize aspect
        fig5.update_traces(marker_line_width=.01)

        #update legend
        fig5.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        # fig5.show()


        # In[156]:


        fig6 = make_subplots(specs=[[{"secondary_y": True}]])

        fig6.add_trace(
            go.Scatter(x=date
                       ,y=positive_pct_change
                       ,name="positive_pct_change"
                       ,marker_color=px.colors.qualitative.T10[2]
                       ,yaxis="y1")
        #     secondary_y=False,
        )
        fig6.add_trace(
            go.Scatter(x=date
                       ,y=negative_pct_change
                       ,name="negative_pct_change"
                       ,marker_color=px.colors.qualitative.T10[4]
                       ,yaxis="y2")
        #     secondary_y=False,
        )
        fig6.add_trace(
            go.Scatter(x=date
                       ,y=total_cases_pct_change
                       ,name="total_cases_pct_change"
                       ,marker_color=px.colors.qualitative.Plotly[3]
                       ,yaxis="y3")
        #     secondary_y=False,
        )

        # Create axis objects
        fig6.update_layout(
        #     xaxis=date,
            yaxis1=dict(
                title="positive_pct_change",
                titlefont=dict(
                    color="#663399"
                ),
                tickfont=dict(
                    color="#663399"
                )
            ),
            yaxis2=dict(
                title="negative_pct_change",
                titlefont=dict(
                    color="#006600"
                ),
                tickfont=dict(
                    color="#006600"
                ),
                anchor="free",
                overlaying="y",
                side="right",
                position=1
            ),
            yaxis3=dict(
                title="total_cases_pct_change",
                titlefont=dict(
                    color="#d62728"
                ),
                tickfont=dict(
                    color="#d62728"
                ),
                anchor="x",
                overlaying="y",
                side="right"
            )
        )

        # Add fig6ure title
        fig6.update_layout(
            title_text="<b>Daily Percent Changes of Covid Pos/Neg Tests and Total Tests</b>"
        )

        # Set x-axis title
        fig6.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig6.update_yaxes(title_text="<b>Percent Change</b>", secondary_y=False)

        # Change the bar mode
        fig6.update_layout(barmode='stack')

        # Customize aspect
        fig6.update_traces(marker_line_width=.01)

        #update legend
        fig6.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        fig6.update_layout(
            # width=1200
            template='plotly_dark'
        )
        # fig6.show()


        #second fig7ure
        fig7 = make_subplots(specs=[[{"secondary_y": True}]])

        fig7.add_trace(
            go.Scatter(x=date
                       ,y=death_pct_change
                       ,name="death_pct_change"
                       ,marker_color=px.colors.qualitative.T10[0]),
            secondary_y=False,
        )
        fig7.add_trace(
            go.Scatter(x=date
                       ,y=hospitalized_pct_change
                       ,name="hospitalized_pct_change"
                       ,marker_color=px.colors.qualitative.T10[6]),
            secondary_y=False,
        )

        # Add fig7ure title
        fig7.update_layout(
            title_text="<b>Daily Percent Changes of Covid Death/Hospitalized</b>"
        )

        # Set x-axis title
        fig7.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig7.update_yaxes(title_text="<b>Percent Change</b>", secondary_y=False)
        # fig7.update_yaxes(title_text="<b>% Change</b>", secondary_y=True)

        # Change the bar mode
        fig7.update_layout(barmode='stack')

        # Customize aspect
        fig7.update_traces(
        #                   marker_color='rgb(158,202,225)'
        #                   , marker_line_color='rgb(8,48,107)',
                          marker_line_width=.1)
        #                   ,opacity=0.6)

        #update legend
        fig7.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ))

        fig7.update_layout(
            # width=1200
            template='plotly_dark'
        )
        # fig7.show()
        ```
        ''')
        ], className='divBorder', style={
                 "height": 350
                , "overflowY": "scroll"
                , "background-color": "#4F90D1"
                , "color": "Black"
                , "font-family": "sans-serif"
                , "size": 16}
        )
        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig2)
        ])
        # ], className="six columns"),

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig3)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig4)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig5)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig6)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig7)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()
        ,html.Br(),

        html.H1(children='Distribution Trends of Daily Outcomes')

        ,html.Div(children='''
        The charts below offer a breakdown of each covid test metric (positive, \
        negative, death, hospitalized). There are several ways to view the following \
        charts - I offer a few views in and around heatmaps, scatter plots with subplots, \
        and histograms.
        ''')

        ,html.Br()

        ,html.Div(children='''
        The highs and lows of each marker on the below scatter plots reprepsent \
        daily percent changes; thus the higher and lighter the mark, the greater the \
        percent change/increase from the previous day.
        ''')

        ,html.Br()

        ,html.H5(children='Key Take Aways:')

        ,html.Div(children='''
        -The majority of the spikes occured during the beginning \
        of the covid outbreak - March and April months. Daily percent changes \
        have flattened for the most part within each metric.
        ''')

        ,html.Br()

        ,html.Div(children='''
        *Keep in mind, we are at the mercy of the data being reported - \
        from what I understand, the data are reported differently from each state \
        and each hospital; all have different reporting methods, none of which are \
        fully automated. Plus, with the combined feature of insurance companies \
        incentivizing hospitals for each covid case, it's hard to truly predict these metrics.
        ''')

        ,html.Br()

        ,html.Div([
        dcc.Markdown('''

        ```
        fig8 = px.scatter(cases
                         ,x="date_new"
                         ,y="positive_pct_change"
                         ,trendline="lowess"
                         ,color_continuous_scale=px.colors.sequential.Inferno
                        )
        fig8.update_layout(
            height=800
            ,template='plotly_dark')

        fig8.add_trace(
            go.Scatter(x=date
                       ,y=negative_pct_change
                       ,name="negative_pct_change"
                       ,mode="lines+markers"
                       ,marker_color=px.colors.qualitative.T10[1]
                      )
        #     secondary_y=False,
        ),
        fig8.add_trace(
            go.Scatter(x=date
                       ,y=death_pct_change
                       ,name="death_pct_change"
                       ,mode="lines+markers"
                       ,marker_color=px.colors.qualitative.T10[2]
                      )
        #     secondary_y=False,
        ),
        fig8.add_trace(
            go.Scatter(x=date
                       ,y=hospitalized_pct_change
                       ,name="hospitalized_pct_change"
                       ,mode="lines+markers"
                       ,marker_color=px.colors.qualitative.T10[3]
                      )
        #     secondary_y=False,
        ),
        fig8.add_trace(
            go.Scatter(x=date
                       ,y=total_cases_pct_change
                       ,name="total_cases_pct_change"
                       ,mode="lines+markers"
                       ,marker_color=px.colors.qualitative.T10[4]
                      )
        #     secondary_y=False,
        )
        # fig8.show()


        fig9 = px.scatter(cases, x="date_new", y="positive_pct_change", trendline="lowess"
                          , title="positive_pct_change"
        #                   , color_continuous_scale="icefire"
                          , color="positive_pct_change", color_continuous_scale=px.colors.sequential.Inferno
                          , marginal_y="histogram", marginal_x="violin")
        fig9.update_layout(
            height=400
            ,template='plotly_dark')
        # fig9.show()

        fig10 = px.scatter(cases, x="date_new", y="negative_pct_change", color="negative_pct_change"
                          , trendline="lowess", title="negative_pct_change"
                          , color_continuous_scale=px.colors.sequential.Inferno
                          , marginal_y="histogram", marginal_x="violin")
        fig10.update_layout(
            height=400
            ,template='plotly_dark')
        # fig10.show()

        fig11 = px.scatter(cases, x="date_new", y="death_pct_change", color="death_pct_change"
                          , trendline="lowess", title="death_pct_change"
                          , color_continuous_scale=px.colors.sequential.Inferno
                          , marginal_y="histogram", marginal_x="violin")
        fig11.update_layout(
            height=400
            ,template='plotly_dark')
        # fig11.show()

        fig12 = px.scatter(cases, x="date_new", y="hospitalized_pct_change", color="hospitalized_pct_change"
                          , trendline="lowess", title="hospitalized_pct_change"
                          , color_continuous_scale=px.colors.sequential.Inferno
                          , marginal_y="histogram", marginal_x="violin")
        fig12.update_layout(
            height=400
            ,template='plotly_dark')
        # fig12.show()

        fig13 = px.scatter(cases, x="date_new", y="total_cases_pct_change", color="total_cases_pct_change"
                          , trendline="lowess", title="total_cases_pct_change"
                          , color_continuous_scale=px.colors.sequential.Inferno
                          , marginal_y="histogram", marginal_x="violin")
        fig13.update_layout(
            height=400
            ,template='plotly_dark')
        # fig13.show()

        #add traces
        trace1 = fig9['data'][0]
        trace2 = fig10['data'][0]
        trace3 = fig11['data'][0]
        trace4 = fig12['data'][0]
        trace5 = fig13['data'][0]

        fig14 = make_subplots(rows=3
                            ,cols=2
                            ,shared_xaxes=False
                            ,row_heights=[9., 9., 9.]
                            ,column_widths=[.1, .1]
                            ,shared_yaxes=False
                            ,vertical_spacing=0.10
                            ,subplot_titles=['<b>positive_pct_change</b>'
                                             ,'<b>negative_pct_change</b>'
                                             ,'<b>death_pct_change</b>'
                                             ,'<b>hospitalized_pct_change</b>'
                                             ,'<b>total_cases_pct_change</b>'
                                            ]
                            ,x_title="<b>date</b>"
                            ,y_title="<b>percent_change</b>"
                           )

        fig14.add_trace(trace1, row=1, col=1)
        fig14.add_trace(trace2, row=1, col=2)
        fig14.add_trace(trace3, row=2, col=1)
        fig14.add_trace(trace4, row=2, col=2)
        fig14.add_trace(trace5, row=3, col=1)

        fig14['layout'].update(height=800
        # , width=1200
                , title='<b>Covid Test Outcome Trends</b>'
                , template='plotly_dark')
        # fig14.show()


        # cases_melted.head()
        cases_melted.variable.value_counts()
        values_list = list(cases_melted.value)

        fig15 = px.scatter(cases_melted, x="date_new", y="value"
                         , color="variable", facet_col="variable"
                         , trendline="lowess", trendline_color_override="white"
                         , color_continuous_scale=px.colors.sequential.Inferno
                         , marginal_y="bar", marginal_x="box"
                         , labels = ['test','test','test','test','test'])

        fig15['layout'].update(height=800
        # , width=1200
                , title='<b>Covid Test Outcome Trends</b>'
                , template='plotly_dark')
        fig15.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        # fig15.show()
        ```
        ''')
        ], className='divBorder', style={
                 "height": 350
                , "overflowY": "scroll"
                , "background-color": "#4F90D1"
                , "color": "Black"
                , "font-family": "sans-serif"
                , "size": 16}
        )
        ,html.Br()

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig8)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig9)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig10)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig11)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig12)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig13)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig14)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig15)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()
        ,html.Br(),

        html.H1(children='Day of Week Meets Daily Metrics')

        ,html.Div(children='''
        The charts below analyze the trends within specific days of the week \
        combined with the each metric. Thus we can answer questions like \
        "which day of the week saw the highest number of positive covid tests" or \
        "which day are people more likely to be hospitalized due to covid-19".
        ''')

        ,html.Br()

        ,html.Div(children='''
        The relevance of these charts may not be enough for your high-level boss \
        who's only concern is "are we trending up or down", love those questions, \
        those people are smart, but it will be enough for your inquisitive mind \
        to help you better understand daily trends and thus the minds of covid patients; \
        which I always found far more interesting than broad questions like \
        "why are sales down".
        ''')

        ,html.Br()

        ,html.H5(children='Key Take Aways:')

        ,html.Div(children='''
        -Highest positive test day of the week is Tuesday, with Sunday as a close runner-up \
        and lowest positive day is Friday.
        ''')

        ,html.Br()

        ,html.Div(children='''
        -Highest negative days is also Tuesdays, while lowest on Fridays.
        ''')

        ,html.Br()

        ,html.Div(children='''
        -The above take away makes sense given Tuesdays and Fridays are the \
        highest and lowest testing days, respectively.
        ''')

        ,html.Br()

        ,html.Div(children='''
        -Deaths occur more regularly on Mondays and Sundays, and are least likely \
        to occur on Thursdays and Fridays.
        ''')

        ,html.Br()

        ,html.Div(children='''
        -Hospitalizations occur mainly on Tuesdays and Saturdays, and are least likely \
        to fall on Thursdays.
        ''')

        ,html.Br()
        ,html.Br()

        ,html.Div([
        dcc.Markdown('''

        ```
        x_labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']
        # print('x_labels:', x_labels)


        #plots by day
        fig17 = px.bar(df
                     ,x='dayofweek'
                     ,y='positiveIncrease'
                     ,text='positiveIncrease'
                     ,color='dayofweek'
                     ,height=500
                     ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
                     ,hover_name="positiveIncrease")
        fig17.update_traces(texttemplate='%{text:.2s}'
                          ,textposition='outside')
        fig17.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         ,title_text="<b>Covid Tests Outcome</b>"
                         ,template='plotly_dark'
                         # ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                         )

        # Set x-axis title
        fig17.update_xaxes(title_text="<b>Date</b>")

        fig17.add_shape( # add a horizontal "target" line
            type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
            x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
        )

        fig17.add_annotation( # add a text callout with arrow
            text="Lowest", x="Friday", y=500000, arrowhead=1, showarrow=True
        )

        total_labels = [{"x": x, "y": pos_totals*1.3, "text": str(pos_totals), "showarrow": False} for x, pos_totals in zip(x_labels, pos_totals)]

        fig17.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         # ,width=1200
                         ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                         ,template='plotly_dark'
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                         # ,annotations=total_labels
                         )
        # fig17.show()



        fig18 = px.bar(df
                     ,x='dayofweek'
                     ,y='negativeIncrease'
                     ,text='negativeIncrease'
                     ,color='dayofweek'
                     ,height=500
                     ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
                     ,hover_name="negativeIncrease")
        fig18.update_traces(texttemplate='%{text:.2s}'
                          ,textposition='outside')
        fig18.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         ,template='plotly_dark'
                         ,title_text="<b>Neagtive Covid Tests Grouped by Day</b>"
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

        # Set x-axis title
        fig18.update_xaxes(title_text="<b>Date</b>")

        fig18.add_shape( # add a horizontal "target" line
            type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
            x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
        )

        fig18.add_annotation( # add a text callout with arrow
            text="Highest", x="Tuesday", y=6700000, arrowhead=1, showarrow=True
        )

        fig18.add_annotation( # add a text callout with arrow
            text="Lowest", x="Friday", y=6000000, arrowhead=1, showarrow=True
        )

        total_labels = [{"x": x, "y": neg_totals*1.25, "text": str(neg_totals), "showarrow": False} for x, neg_totals in zip(x_labels, neg_totals)]

        fig18.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         # ,width=1200
                         ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                         ,template='plotly_dark'
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                         # ,annotations=total_labels
                         )
        # fig18.show()


        fig19 = px.bar(df
                     ,x='dayofweek'
                     ,y='totalTestResultsIncrease'
                     ,text='totalTestResultsIncrease'
                     ,color='dayofweek'
                     ,height=500
                     ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
                     ,hover_name="totalTestResultsIncrease")
        fig19.update_traces(texttemplate='%{text:.2s}'
                          ,textposition='outside')

        # Set x-axis title
        fig19.update_xaxes(title_text="<b>Date</b>")

        fig19.add_shape( # add a horizontal "target" line
            type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
            x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
        )

        fig19.add_annotation( # add a text callout with arrow
            text="Highest", x="Tuesday", y=7400000, arrowhead=1, showarrow=True
        )

        fig19.add_annotation( # add a text callout with arrow
            text="Lowest", x="Friday", y=6600000, arrowhead=1, showarrow=True
        )

        total_labels = [{"x": x, "y": total_totals*.95, "text": str(total_totals), "showarrow": True} for x, total_totals in zip(x_labels, total_totals)]

        fig19.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                         ,template='plotly_dark'
                         # ,width=1200
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                         # ,annotations=total_labels
                         )
        # fig19.show()


        #deaths
        fig20 = px.bar(df
                     ,x='dayofweek'
                     ,y='deathIncrease'
                     ,text='deathIncrease'
                     ,color='dayofweek'
                     ,height=500
                     ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease','deathIncrease']
                     ,hover_name="deathIncrease")
        fig20.update_traces(texttemplate='%{text:.2s}'
                          ,textposition='outside')
        fig20.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         # ,width=1200
                         ,title_text="<b>Death Covid Tests Grouped by Day</b>"
                         ,template='plotly_dark'
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

        # Set x-axis title
        fig20.update_xaxes(title_text="<b>Date</b>")

        fig20.add_shape( # add a horizontal "target" line
            type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
            x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
        )

        fig20.add_annotation( # add a text callout with arrow
            text="Highest", x="Monday", y=24000, arrowhead=1, showarrow=True
        )

        fig20.add_annotation( # add a text callout with arrow
            text="Lowest", x="Friday", y=12000, arrowhead=1, showarrow=True
        )

        fig20.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         # ,width=1200
                         ,title_text="<b>Total Covid Deaths Grouped by Day</b>"
                         ,template='plotly_dark'
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})
        #                  ,annotations=total_labels)
        # fig20.show()



        fig21 = px.bar(df
                     ,x='dayofweek'
                     ,y='hospitalizedIncrease'
                     ,text='hospitalizedIncrease'
                     ,color='dayofweek'
                     ,height=500
                     ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease','deathIncrease','hospitalizedIncrease']
                     ,hover_name="hospitalizedIncrease")
        fig21.update_traces(texttemplate='%{text:.2s}'
                          ,textposition='outside')
        fig21.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         ,title_text="<b>Hospitalized Covid Tests Grouped by Day</b>"
                         ,template='plotly_dark'
                         # ,width=1200
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

        # Set x-axis title
        fig21.update_xaxes(title_text="<b>Date</b>")

        fig21.add_shape( # add a horizontal "target" line
            type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
            x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
        )

        fig21.add_annotation( # add a text callout with arrow
            text="Highest", x="Tuesday", y=55000, arrowhead=1, showarrow=True
        )

        fig21.add_annotation( # add a text callout with arrow
            text="Lowest", x="Thursday", y=25000, arrowhead=1, showarrow=True
        )

        fig21.update_layout(uniformtext_minsize=8
                         ,uniformtext_mode='hide'
                         ,title_text="<b>Total Hospitalized Covid Deaths Grouped by Day</b>"
                         ,template='plotly_dark'
                         ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})
        # fig21.show()
        ```
        ''')
        ], className='divBorder', style={
                 "height": 350
                , "overflowY": "scroll"
                , "background-color": "#4F90D1"
                , "color": "Black"
                , "font-family": "sans-serif"
                , "size": 16}
        )
        ,html.Br()

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig17)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig18)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig19)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig20)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig21)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig22)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig23)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig24)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()
        ,html.Br()

        ,html.H1(children='Historic Metrics Meet Day of Week Meet Cumulative Totals')

        ,html.Div(children='''
        The charts below differ from the few above in that they analyze the metrics \
        on a daily level - where as most of the charts above were grouped by day. \
        The below charts offer a bigger picture of spikes in metrics per day; thus \
        to better understand weekly and monthly trends as well as outlier spikes.
        ''')

        ,html.Br()

        ,html.Div(children='''
        Some questins one might ask would be: \
        "were there previous days in the week that increased over time?", \
        "which days of the week are more/less volatile?",
        "which metrics have the highest/lowest spikes?",
        "in aggregate, which days have the lowest/greatest daily percent change?" \
        ''')

        ,html.Br()

        ,html.H5(children='Key Take Aways:')

        ,html.Div(children='''
        -It appears that Wednesdays have increased in the number of spikes, while \
        Tuesdays started out with a bit more spikes, but have dwindled down.
        ''')
        ,html.Br()

        ,html.Div(children='''
        -Saturday saw the highest spike in daily percent changes out of all - but \
        it makes you wonder, why? Monday saw the lowest spike in daily percent changes.
        ''')
        ,html.Br()

        ,html.Div(children='''
        -Sundays, Fridays and Thursdays appear to have the same amount of volatility \
        when it comes to cumulative daily percent changes.
        ''')
        ,html.Br()

        ,html.Div(children='''
        -Hospitalizations have the most spikes as well as the highest and lowest \
        overall spike in cumulative daily percent changes.
        ''')
        ,html.Br()

        ,html.Div(children='''
        -Fridays tend to have the lowest spikes in cumulative daily percent changes. \
        Over 50% of Fridays have a negative spike.
        ''')

        ,html.Br()
        ,html.Br()

        ,html.Div([
        dcc.Markdown('''
        ```
        fig25 = px.bar(cases_melted, x="date_new", y="value"
                         , color="variable"
                         , color_continuous_scale=px.colors.sequential.Inferno)

        fig25['layout'].update(height=500
                             # , width=1200
                             , title='<b>Sum of Covid Test Daily Percent Changes by Outcome</b>'
                             , yaxis_title="Sum of Daily % Changes"
                             , xaxis_title="Date"
                             , legend_title="Sum of Daily % Changes"
                             , template='plotly_dark')
        fig25.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        # fig25.show()

        fig26 = px.bar(cases_melted, x="date_new", y="value"
                         , color="dayofweek"
                         , color_continuous_scale=px.colors.sequential.Inferno)


        fig26['layout'].update(height=500
                             # , width=1200
                             , title='<b>Sum of Covid Test Daily Percent Changes by Outcome</b>'
                             , yaxis_title="Sum of Daily % Changes"
                             , xaxis_title="Date"
                             , legend_title="Day of Week"
                             , template='plotly_dark')
        fig26.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        # fig26.show()

        fig27 = px.bar(cases_melted, x="date_new", y="value"
                         , color="dayofweek", facet_col="dayofweek"
                         , color_continuous_scale=px.colors.sequential.Inferno)
        #                  , facet_col_wrap=3)
        #                  , size=cases_melted.index)

        fig27['layout'].update(height=500
                             # , width=1200
                             , title='<b>Covid Test Outcome Trends Grouped by Day Of Week</b>'
                             , template='plotly_dark'
                             , yaxis_title="Sum of Daily % Changes"
                             , xaxis_title="Day of Week"
                             , legend_title="Sum of Daily % Changes")
        fig27.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        # fig27.show()

        fig28 = px.bar(cases_melted, x="dayofweek", y="value"
                         , color="value"
                         , color_continuous_scale=px.colors.sequential.Inferno)
        #                  , facet_col_wrap=3)
        #                  , size=cases_melted.index)

        fig28['layout'].update(height=500
                             # , width=1200
                             , title='<b>Covid Test Outcome Trends Grouped by Day Of Week</b>'
                             , template='plotly_dark'
                             , yaxis_title="Sum of Daily % Changes"
                             , xaxis_title="Day of Week"
                             , legend_title="Sum of Daily % Changes")
        fig28.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        # fig28.show()

        fig29 = px.bar(cases_melted, x="variable", y="value"
                         , color="dayofweek"
                         , color_continuous_scale=px.colors.sequential.Inferno)
        #                  , facet_col_wrap=3)
        #                  , size=cases_melted.index)

        fig29['layout'].update(height=500
                             # , width=1200
                             , title='<b>Covid Test Outcome Trends Grouped by Day Of Week</b>'
                             , template='plotly_dark'
                             , yaxis_title="Sum of Daily % Changes"
                             , xaxis_title="Outcome"
                             , legend_title="Sum of Daily % Changes")
        fig29.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        # fig29.show()
        ```
        ''')
        ], className='divBorder', style={
                 "height": 350
                , "overflowY": "scroll"
                , "background-color": "#4F90D1"
                , "color": "Black"
                , "font-family": "sans-serif"
                , "size": 16}
        )
        # ,html.Br()
        #
        # ,html.Div([
        # dcc.Graph(figure=fig40)
        # ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig25)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig26)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig27)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig28)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig29)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()
        ,html.Br(),

        html.H1(children='5 Day Moving Average Meets % of Daily Outcomes (Rounded)')

        ,html.Div(children='''
        The charts below offer a more analytical view by comparing rounded cumulative daily \
        percent changes of each metric to the total daily tests. I also added the slope \
        of each metric compared to the total daily tests, which shines through at the \
        bottom of each chart. The 5 day moving averages are rounded to further smooth \
        out the lines (helps show the slope more easily). The goal of these charts is \
        to provide a correlation between the metric and the total daily tests. The \
        hypothesis is "the more tests, the more of each metric".
        ''')

        ,html.Br()

        ,html.Div(children='''
        Some questins one might ask would be: \
        "what do the slopes of each metric look like compared to total daily tests?" \
        "are the slopes correlated with total daily tests? \
        ''')

        ,html.Br()

        ,html.H5(children='Key Take Aways:')

        ,html.Div(children='''
        -The positive tests and total daily tests appear to correlate very well \
        beginning in June. The increase in daily tests proves to show a direct \
        correlation to the number of positive tests; 450k daily tests equates to \
        about 5% positive tests per day; and thus 800k daily tests equates to \
        about 10% positive tests.
        ''')
        ,html.Br()

        ,html.Div(children='''
        -Other metrics do not appear to have much of a correlation as the numbers \
        are simply too low. Perhpas a logarithmic view might help, but that's \
        reaching if you ask me.
        ''')
        ,html.Br()

        ,html.Div(children='''
        -Fridays tend to have the lowest spikes in cumulative daily percent changes. \
        Over 50% of Fridays have a negative spike.
        ''')

        ,html.Br()

        ,html.Div([
        dcc.Markdown('''
        ```
        #create rounded columns and df
        cases['total_rounded'] = cases.totalTestResultsIncrease.round(-4)
        cases['percent_positive_rounded'] = cases.percent_positive.round(2)
        cases['percent_negative_rounded'] = cases.percent_negative.round(2)
        cases['percent_death_rounded'] = cases.percent_death.round(2)
        cases['percent_hospitalized_rounded'] = cases.percent_hospitalized.round(2)

        cases_rounded = cases[['date_new','total_rounded','percent_positive_rounded'
                              ,'percent_negative_rounded','percent_death_rounded'
                              ,'percent_hospitalized_rounded']]

        #add 5 day moving average columns
        cases_rounded['percent_pos_5d_avg'] = cases_rounded.rolling(window=5)['percent_positive_rounded'].mean()
        cases_rounded['total_rounded_5d_avg'] = cases_rounded.rolling(window=5)['total_rounded'].mean()
        cases_rounded['percent_neg_5d_avg'] = cases_rounded.rolling(window=5)['percent_negative_rounded'].mean()
        cases_rounded['percent_death_5d_avg'] = cases_rounded.rolling(window=5)['percent_death_rounded'].mean()
        cases_rounded['percent_hospitalized_5d_avg'] = cases_rounded.rolling(window=5)['percent_hospitalized_rounded'].mean()

        #create slope cols
        cases_rounded['percent_pos_5d_avg_slope'] = cases_rounded.percent_pos_5d_avg.diff().fillna(0)
        cases_rounded['total_rounded_5d_avg_slope'] = cases_rounded.total_rounded_5d_avg.diff().fillna(0)
        cases_rounded['percent_neg_5d_avg_slope'] = cases_rounded.percent_neg_5d_avg.diff().fillna(0)
        cases_rounded['percent_death_5d_avg_slope'] = cases_rounded.percent_death_5d_avg.diff().fillna(0)
        cases_rounded['percent_hospitalized_5d_avg_slope'] = cases_rounded.percent_hospitalized_5d_avg.diff().fillna(0)

        #convert lists
        #rounded lists
        total_rounded = list(cases_rounded.total_rounded)
        percent_positive_rounded = list(cases_rounded.percent_positive_rounded)
        percent_negative_rounded = list(cases_rounded.percent_negative_rounded)
        percent_death_rounded = list(cases_rounded.percent_death_rounded)
        percent_hospitalized_rounded = list(cases_rounded.percent_hospitalized_rounded)

        #5d avg lists
        percent_pos_5d_avg = list(cases_rounded.percent_pos_5d_avg)
        total_rounded_5d_avg = list(cases_rounded.total_rounded_5d_avg)
        percent_neg_5d_avg = list(cases_rounded.percent_neg_5d_avg)
        percent_death_5d_avg = list(cases_rounded.percent_death_5d_avg)
        percent_hospitalized_5d_avg = list(cases_rounded.percent_hospitalized_5d_avg)

        #slope lists
        percent_pos_5d_avg_slope = list(cases_rounded.percent_pos_5d_avg_slope)
        total_rounded_5d_avg_slope = list(cases_rounded.total_rounded_5d_avg_slope)
        percent_neg_5d_avg_slope = list(cases_rounded.percent_neg_5d_avg_slope)
        percent_death_5d_avg_slope = list(cases_rounded.percent_death_5d_avg_slope)
        percent_hospitalized_5d_avg_slope = list(cases_rounded.percent_hospitalized_5d_avg_slope)


        # Create fig30ure with secondary y-axis
        fig30 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig30.add_trace(
            go.Scatter(x=date
                   ,y=total_rounded
                   ,name="total_rounded"
                   ,mode="lines+markers"
        #            ,opacity=.5
                   ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )
        fig30.add_trace(
            go.Scatter(x=date
                   , y=percent_positive_rounded
        #            , opacity=.5
                   , mode="lines+markers"
                   , marker_color=px.colors.qualitative.Plotly[5]
                   , name="percent_positive_rounded"),
            secondary_y=True,
        )

        #moving averages
        fig30.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="total_rounded_5d_avg"),
            secondary_y=False,
        )
        fig30.add_trace(
            go.Scatter(x=date
                   , y=percent_pos_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="percent_pos_5d_avg"),
            secondary_y=True,
        )

        #slopes
        fig30.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[3]
                   , name="total_rounded_5d_avg_slope"),
            secondary_y=False,
        )
        fig30.add_trace(
            go.Scatter(x=date
                   , y=percent_pos_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[5]
                   , name="percent_pos_5d_avg_slope"),
            secondary_y=True,
        )

        # Add fig30ure title
        fig30.update_layout(
            title_text="<b>Total Daily Cases vs. Daily Percent Positive (Rounded) with 5 Day Moving Average and Slope</b>"
            ,height=800
        )

        # Set x-axis title
        fig30.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig30.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
        fig30.update_yaxes(title_text="<b>% Positive Cases</b>", secondary_y=True)

        # Change the bar mode
        fig30.update_layout(barmode='stack')

        # Customize aspect
        fig30.update_traces(
        #                   marker_color='rgb(158,202,225)'
        #                   , marker_line_color='rgb(8,48,107)',
                          marker_line_width=.01)
        #                   ,opacity=0.6)

        #update legend
        fig30.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1
        ))
        # fig30.show()

        # Create fig30ure with secondary y-axis
        fig31 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig31.add_trace(
            go.Scatter(x=date
                   ,y=total_rounded
                   ,name="total_rounded"
                   ,mode="lines+markers"
        #            ,opacity=.5
                   ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )
        fig31.add_trace(
            go.Scatter(x=date
                   , y=percent_negative_rounded
        #            , opacity=.5
                   , mode="lines+markers"
                   , marker_color=px.colors.qualitative.Plotly[2]
                   , name="percent_negative_rounded"),
            secondary_y=True,
        )

        #moving averages
        fig31.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="total_rounded_5d_avg"),
            secondary_y=False,
        )
        fig31.add_trace(
            go.Scatter(x=date
                   , y=percent_neg_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="percent_neg_5d_avg"),
            secondary_y=True,
        )

        #slopes
        fig31.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[3]
                   , name="total_rounded_5d_avg_slope"),
            secondary_y=False,
        )
        fig31.add_trace(
            go.Scatter(x=date
                   , y=percent_neg_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[2]
                   , name="percent_neg_5d_avg_slope"),
            secondary_y=True,
        )

        # Add fig30ure title
        fig31.update_layout(
            title_text="<b>Total Daily Cases vs. Daily Percent Negative (Rounded) with 5 Day Moving Average and Slope</b>"
            ,height=800
        )

        # Set x-axis title
        fig31.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig31.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
        fig31.update_yaxes(title_text="<b>% Negative Cases</b>", secondary_y=True)

        # Change the bar mode
        fig31.update_layout(barmode='stack')

        # Customize aspect
        fig31.update_traces(
        #                   marker_color='rgb(158,202,225)'
        #                   , marker_line_color='rgb(8,48,107)',
                          marker_line_width=.01)
        #                   ,opacity=0.6)

        #update legend
        fig31.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1
        ))
        # fig31.show()

        # Create fig30ure with secondary y-axis
        fig32 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig32.add_trace(
            go.Scatter(x=date
                   ,y=total_rounded
                   ,name="total_rounded"
                   ,mode="lines+markers"
        #            ,opacity=.5
                   ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )
        fig32.add_trace(
            go.Scatter(x=date
                   , y=percent_death_rounded
        #            , opacity=.5
                   , mode="lines+markers"
                   , marker_color=px.colors.qualitative.Plotly[6]
                   , name="percent_death_rounded"),
            secondary_y=True,
        )

        #moving averages
        fig32.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="total_rounded_5d_avg"),
            secondary_y=False,
        )
        fig32.add_trace(
            go.Scatter(x=date
                   , y=percent_death_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="percent_death_5d_avg"),
            secondary_y=True,
        )

        #slopes
        fig32.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[3]
                   , name="total_rounded_5d_avg_slope"),
            secondary_y=False,
        )
        fig32.add_trace(
            go.Scatter(x=date
                   , y=percent_death_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[6]
                   , name="percent_death_5d_avg_slope"),
            secondary_y=True,
        )

        # Add fig30ure title
        fig32.update_layout(
            title_text="<b>Total Daily Cases vs. Daily Percent Death (Rounded) with 5 Day Moving Average and Slope</b>"
            ,height=800
        )

        # Set x-axis title
        fig32.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig32.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
        fig32.update_yaxes(title_text="<b>% Death Cases</b>", secondary_y=True)

        # Change the bar mode
        fig32.update_layout(barmode='stack')

        # Customize aspect
        fig32.update_traces(
        #                   marker_color='rgb(158,202,225)'
        #                   , marker_line_color='rgb(8,48,107)',
                          marker_line_width=.01)
        #                   ,opacity=0.6)

        #update legend
        fig32.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1
        ))
        # fig32.show()

        # Create fig30ure with secondary y-axis
        fig33 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig33.add_trace(
            go.Scatter(x=date
                   ,y=total_rounded
                   ,name="total_rounded"
                   ,mode="lines+markers"
        #            ,opacity=.5
                   ,marker_color=px.colors.qualitative.Plotly[3]),
            secondary_y=False,
        )
        fig33.add_trace(
            go.Scatter(x=date
                   , y=percent_hospitalized_rounded
        #            , opacity=.5
                   , mode="lines+markers"
                   , marker_color=px.colors.qualitative.Plotly[4]
                   , name="percent_hospitalized_rounded"),
            secondary_y=True,
        )

        #moving averages
        fig33.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="total_rounded_5d_avg"),
            secondary_y=False,
        )
        fig33.add_trace(
            go.Scatter(x=date
                   , y=percent_hospitalized_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="percent_hospitalized_5d_avg"),
            secondary_y=True,
        )

        #slopes
        fig33.add_trace(
            go.Scatter(x=date
                   , y=total_rounded_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[3]
                   , name="total_rounded_5d_avg_slope"),
            secondary_y=False,
        )
        fig33.add_trace(
            go.Scatter(x=date
                   , y=percent_hospitalized_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[4]
                   , name="percent_hospitalized_5d_avg_slope"),
            secondary_y=True,
        )

        # Add fig30ure title
        fig33.update_layout(
            title_text="<b>Total Daily Cases vs. Daily Percent Hospitalized (Rounded) with 5 Day Moving Average and Slope</b>"
            ,height=800
        )

        # Set x-axis title
        fig33.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig33.update_yaxes(title_text="<b>Count Cases</b>", secondary_y=False)
        fig33.update_yaxes(title_text="<b>% Hospitalized Cases</b>", secondary_y=True)

        # Change the bar mode
        fig33.update_layout(barmode='stack')

        # Customize aspect
        fig33.update_traces(
        #                   marker_color='rgb(158,202,225)'
        #                   , marker_line_color='rgb(8,48,107)',
                          marker_line_width=.01)
        #                   ,opacity=0.6)

        #update legend
        fig33.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="right",
            x=1
        ))
        # fig33.show()

        # Create fig34ure with secondary y-axis
        fig34 = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig34.add_trace(
            go.Scatter(x=date
                   ,y=percent_death_rounded
                   ,name="percent_death_rounded"
                   ,mode="lines+markers"
        #            ,opacity=.5
                   ,marker_color=px.colors.qualitative.Plotly[6]),
            secondary_y=False,
        )
        fig34.add_trace(
            go.Scatter(x=date
                   , y=percent_positive_rounded
        #            , opacity=.5
                   , mode="lines+markers"
                   , marker_color=px.colors.qualitative.Plotly[5]
                   , name="percent_positive_rounded"),
            secondary_y=True,
        )

        #moving averages
        fig34.add_trace(
            go.Scatter(x=date
                   , y=percent_death_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="percent_death_5d_avg"),
            secondary_y=False,
        )
        fig34.add_trace(
            go.Scatter(x=date
                   , y=percent_pos_5d_avg
                   , opacity=.6
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[1]
                   , name="percent_pos_5d_avg"),
            secondary_y=True,
        )

        #slopes
        fig34.add_trace(
            go.Scatter(x=date
                   , y=percent_death_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[6]
                   , name="percent_death_5d_avg_slope"),
            secondary_y=False,
        )
        fig34.add_trace(
            go.Scatter(x=date
                   , y=percent_pos_5d_avg_slope
                   , opacity=.7
                   , mode="lines"
                   , marker_color=px.colors.qualitative.Plotly[5]
                   , name="percent_pos_5d_avg_slope"),
            secondary_y=True,
        )

        # Add fig34ure title
        fig34.update_layout(
            title_text="<b>Daily Percent Death vs. Daily Percent Positive (Rounded) with 5 Day Moving Average and Slope</b>"
            ,height=800
        )

        # Set x-axis title
        fig34.update_xaxes(title_text="<b>Date</b>")

        # Set y-axes titles
        fig34.update_yaxes(title_text="<b>% Death Cases</b>", secondary_y=False)
        fig34.update_yaxes(title_text="<b>% Positive Cases</b>", secondary_y=True)

        # Change the bar mode
        fig34.update_layout(barmode='stack')

        # Customize aspect
        fig34.update_traces(
        #                   marker_color='rgb(158,202,225)'
        #                   , marker_line_color='rgb(8,48,107)',
                          marker_line_width=.01)
        #                   ,opacity=0.6)

        #update legend
        fig34.update_layout(
            template='plotly_dark'
            ,legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1
        ))
        # fig34.show()
        ```
        ''')
        ], className='divBorder', style={
                 "height": 350
                , "overflowY": "scroll"
                , "background-color": "#4F90D1"
                , "color": "Black"
                , "font-family": "sans-serif"
                , "size": 16}
        )

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig30)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig31)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig32)
        ])

        ,html.Br(),

        html.Div([
        dcc.Graph(figure=fig33)
        ])

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig34)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()
        ,html.Br()

        ,html.H1(children='Additional Charts')

        ,html.Div(children='''
        The charts (one chart for now) will offer additional, less themed analytics. \
        The type of stuff that doesn't fit into one box.
        ''')

        ,html.Br()

        ,html.Div(children='''
        The first chart shows the correlation of positive daily tests vs daily \
        death rates, as well as the daily percent changes of each of those metrics, \
        and the percent positive for the day.
        ''')

        ,html.Br()

        ,html.H5(children='Key Take Aways:')

        ,html.Div(children='''
        -Death rates are going down in the US, despite the exponential increases \
        in daily tests as well as the number of positive tests. There was a bit \
        spike in the beginning (during April and May), but those numbers went down \
        dramatically during June and July. We appear to be experiencing a slight \
        uptick towards the end of July though.
        ''')

        ,html.Br()

        ,html.Div(children='''
        -Deaths do appear to spike on Sundays and Mondays and fall as the week progresses. \
        This accounts for the spikes in the blue line (daily death percentage change).
        ''')

        ,html.Br()

        ,html.Div([
        dcc.Graph(figure=fig35)
        ])

        ,html.Br()
        ,html.Br()
        ,html.Br()

        ,html.H5(children='For more information or questions, please reach out.')

        ,html.Div(children='''
        Source ''')
        ,dcc.Markdown('''\
        [GitHub]("https://github.com/maxwellbade/covid_us_final")''')

        ,html.Div(children='''
        Social Media''')

        ,dcc.Markdown('''\
        [LinkedIn]("https://www.linkedin.com/in/maxbade/")
        ''')

        ,dcc.Markdown('''\
        [Instagram]("https://www.instagram.com/maxbade/")
        ''')

        ,html.Br()

],style={'padding-left': '20%'
        , 'padding-right': '20%'
        , 'backgroundColor':'white'}
        )

# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

# app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
#web: gunicorn app:server
# web gunicorn app:server --timeout 10

# @app.callback(Output('fig0','figure'),
#              [Input("submit-button", "n_clicks")],
#              [State("country-input", "value")]
#              )

#have to have a function for the callback
# def update_fig(n_clicks, input_value):
#     df = pd.read_csv('bigmac.csv')
#
#     data = []
#
#     fig1 = go.Scatter(x=list(df3.country)
#                      ,y=list(df3.dollar_price)
#                      ,name="df3_dollar_price")
#     data.append(fig1)
#
#     layout = {"title": "Callback Graph"}
#
#     return {
#         "data": data,
#         "layout": layout
#     }

#-------------------------------------
#run it

if __name__ == '__main__':
    app.run_server(debug=True)
