#!/usr/bin/env python
# coding: utf-8


#import requests

import dash  # (version 1.12.0) pip install dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly
import numpy as np
import seaborn as sns

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
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)

server = app.server

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
df.head()


#make new date column
df['year'] = df.date.astype(str).str[:4]
df['month_day'] = df.date.astype(str).str[-4:]
df['day'] = df.date.astype(str).str[-2:]
df['month'] = df.month_day.astype(str).str[:2]
df['date_new'] = df['year'] + "-" + df['month'] + "-" + df['day']

df.head()


df['date_new'] = df['date_new'].astype('datetime64')
df.dtypes


cases = df[['date_new', 'totalTestResultsIncrease', 'negativeIncrease', 'positiveIncrease', 'deathIncrease', 'hospitalizedIncrease']]
cases.head(20).style.background_gradient(cmap='Pastel1')


#create percent columns
cases['percent_positive'] = cases['positiveIncrease']/cases['totalTestResultsIncrease']
cases['percent_negative'] = cases['negativeIncrease']/cases['totalTestResultsIncrease']
cases['percent_death'] = cases['deathIncrease']/cases['totalTestResultsIncrease']
cases['percent_hospitalized'] = cases['hospitalizedIncrease']/cases['totalTestResultsIncrease']
cases.head(20)

#create percent change columns
cases['positive_pct_change'] = cases['percent_positive'].pct_change()
cases['negative_pct_change'] = cases['percent_negative'].pct_change()
cases['total_cases_pct_change'] = cases['totalTestResultsIncrease'].pct_change()
cases['death_pct_change'] = cases['percent_death'].pct_change()
cases['hospitalized_pct_change'] = cases['percent_hospitalized'].pct_change()
cases

#filter out old dates
cases = cases[cases['date_new'] > '2020-03-20']
cases.head(20).style.background_gradient(cmap="Blues")


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

print("percent_positive")
print(percent_positive)
print("")
print("percent_negative")
print(percent_negative)
print("")
print("negativeIncrease")
print(negativeIncrease)
print("")
print("positiveIncrease")
print(positiveIncrease)
print("")
print("totalTestResultsIncrease")
print(totalTestResultsIncrease)
print("")
print("total_cases_pct_change")
print(total_cases_pct_change)
print("")
print("positive_pct_change")
print(positive_pct_change)
print("")
print("negative_pct_change")
print(negative_pct_change)
print("")
print("date")
print(date)
print("")


#melt daily percent change columns into one dataframe
positive_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['positive_pct_change'])
negative_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['negative_pct_change'])
death_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['death_pct_change'])
hospitalized_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['hospitalized_pct_change'])
total_cases_pct_melt = pd.melt(cases, id_vars=['date_new'],value_vars=['total_cases_pct_change'])

print(positive_pct_melt.head())
print(negative_pct_melt.head())
print(death_pct_melt.head())
print(hospitalized_pct_melt.head())
print(total_cases_pct_melt.head())

cases_melted1 = positive_pct_melt.append(negative_pct_melt,ignore_index=True)
cases_melted2 = cases_melted1.append(death_pct_melt,ignore_index=True)
cases_melted3 = cases_melted2.append(hospitalized_pct_melt,ignore_index=True)
cases_melted = cases_melted3.append(total_cases_pct_melt,ignore_index=True)
cases_melted.head()
cases_melted.variable.value_counts()


fig1 = px.bar(df
             ,x="date_new"
             ,y="totalTestResults"
             ,hover_data=['totalTestResults']
             ,title="Total Covid Tests (Cummulative)")

# Add fig2ure title
fig1.update_layout(
    template='plotly_dark'
)
# fig1.show()

percent_positive = list(cases.percent_positive)
percent_negative = list(cases.percent_negative)
date = list(cases.date_new)

cases_melt = pd.melt(cases, id_vars=['date_new'], value_vars=['negativeIncrease'
                                                              ,'positiveIncrease'
                                                              ,'totalTestResultsIncrease'
                                                             ]
                    )

# Create fig2ure with secondary y-axis
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

fig2 = px.line(cases_melt, x='date_new', y='value', color='variable')

# Add traces
fig2.add_trace(
    go.Scatter(x=date, y=percent_negative, name="percent_negative"),
    secondary_y=False,
)

fig2.add_trace(
    go.Scatter(x=date, y=percent_positive, name="percent_positive"),
    secondary_y=False,
)

# Add fig2ure title
fig2.update_layout(
    title_text="Daily Covid Cases with Percent Changes"
    ,template='plotly_dark'
)

# Set x-axis title
fig2.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig2.update_yaxes(title_text="<b>Count</b>", secondary_y=False)
# fig2.show()


fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x=date
               ,y=percent_negative
               ,name="percent_negative"
               ,marker_color=px.colors.qualitative.Plotly[2]),
    secondary_y=True,
)
fig.add_trace(
    go.Scatter(x=date
               ,y=percent_positive
               ,name="percent_positive"
               ,marker_color=px.colors.qualitative.D3[3]),
    secondary_y=True,
)

# Add figure title
fig.update_layout(
    title_text="<b>Daily Pos/Neg Percent of Covid Tests</b>"
)

# Set x-axis title
fig.update_xaxes(title_text="<b>Date</b>")

# Set y-axes titles
fig.update_yaxes(title_text="<b>Percent</b>", secondary_y=True)

# Change the bar mode
fig.update_layout(barmode='stack')

# Customize aspect
fig.update_traces(marker_line_width=.01)

#update legend
fig.update_layout(
    template='plotly_dark'
    ,legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
# fig.show()


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


cases_melted.head()
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
df.head(30)


#create min and max variables
y_min = min(df.totalTestResultsIncrease)
y_max = max(df.totalTestResultsIncrease)
# x_min = min(df.index)
# x_max = max(df.index)
x_min = min(df.month)
x_max = max(df.month)
x_range = [x_min,x_max]
y_range = [y_min,y_max]

print('y_min:',y_min)
print('y_max:',y_max)
print('x_min:',x_min)
print('x_max:',x_max)
print('x_range:',x_range)
print('y_range:',y_range)


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


print('total_pos_increase_grp_day:',total_pos_increase_grp_day)
print("")
print('total_neg_increase_grp_day:',total_neg_increase_grp_day)
print("")
print('total_increase_grp_day:',total_increase_grp_day)
print("")
print("")
print('avg_total_pos_increase_grp_day:',avg_total_pos_increase_grp_day)
print("")
print('avg_total_neg_increase_grp_day:',avg_total_neg_increase_grp_day)
print("")
print('avg_total_increase_grp_day:',avg_total_increase_grp_day)
print("")
print("")
print('avg_pos_per_week:',avg_pos_per_week)
print("")
print('avg_neg_per_week:',avg_neg_per_week)
print("")
print('avg_total_per_week:',avg_total_per_week)

#put totals in a list for labeling later on
total_totals = list(total_increase_grp_day)
pos_totals = list(total_pos_increase_grp_day)
neg_totals = list(total_neg_increase_grp_day)

print('total_totals:', total_totals)
print('pos_totals:', pos_totals)
print('neg_totals:', neg_totals)

#make day list
x_labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']
print('x_labels:', x_labels)


#plots by day
fig17 = px.bar(df
             ,x='dayofweek'
             ,y='positiveIncrease'
             ,text='positiveIncrease'
             ,color='dayofweek'
             ,height=500
             ,hover_data=['negativeIncrease', 'positiveIncrease', 'totalTestResultsIncrease']
             ,hover_name="positiveIncrease")
fig1.update_traces(texttemplate='%{text:.2s}'
                  ,textposition='outside')
fig1.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Positive Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})

# Set x-axis title
fig17.update_xaxes(title_text="<b>Date</b>")

fig17.add_shape( # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=avg_total_increase_grp_day, y1=avg_total_increase_grp_day, yref="y"
)

fig17.add_annotation( # add a text callout with arrow
    text="Woah...!", x="Friday", y=300, arrowhead=1, showarrow=True
)

total_labels = [{"x": x, "y": pos_totals*1.3, "text": str(pos_totals), "showarrow": False} for x, pos_totals in zip(x_labels, pos_totals)]

fig17.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 # ,width=1200
                 ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 ,annotations=total_labels)
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
    text="Woah...!", x="Friday", y=300, arrowhead=1, showarrow=True
)

total_labels = [{"x": x, "y": neg_totals*1.25, "text": str(neg_totals), "showarrow": False} for x, neg_totals in zip(x_labels, neg_totals)]

fig18.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 # ,width=1200
                 ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 ,annotations=total_labels)
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
    text="Woah...!", x="Friday", y=300, arrowhead=1, showarrow=True
)

total_labels = [{"x": x, "y": total_totals*.95, "text": str(total_totals), "showarrow": True} for x, total_totals in zip(x_labels, total_totals)]

fig19.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Total Covid Tests Grouped by Day</b>"
                 ,template='plotly_dark'
                 # ,width=1200
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']}
                 ,annotations=total_labels)
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

fig21.update_layout(uniformtext_minsize=8
                 ,uniformtext_mode='hide'
                 ,title_text="<b>Total Hospitalized Covid Deaths Grouped by Day</b>"
                 ,template='plotly_dark'
                 ,xaxis={'categoryorder':'array', 'categoryarray':['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']})
# fig21.show()


#map day of week column to cases_melted dataframe
mapping = df[['date_new', 'dayofweek']]
mapping
cases_melted = pd.merge(cases_melted, mapping, how='left', on=['date_new', 'date_new'])
print(cases_melted)
print(df.dayofweek)


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
cases_melted.style.background_gradient(cmap='Blues')


cases_melted['rank_value'] = cases_melted['value'].rank(method="max")
print(cases_melted.head(30).sort_values(by='rank_value'))
print(cases_melted.tail(30).sort_values(by='rank_value'))


#sum percent changes by day
#sundays have the highest positive percent changes
#tuesdays have the highest negative percent changes
cases_day = cases_melted[['dayofweek','value']]
cases_day = cases_day.groupby('dayofweek').sum().reset_index()
cases_day.head(10).style.background_gradient(cmap='inferno')

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


fig = px.bar(cases_melted
                 , x="dayofweek", y="value"
                 , color="variable"
                 , hover_name="value"
                 , range_y=[-2,2]
                 , animation_group="dayofweek"
                 , animation_frame=cases_melted.index)


fig['layout'].update(height=500
                # , width=1200
                , title='<b>Covid Test Outcome Trends</b>'
                , template='plotly_dark')
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# fig.show()


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


#-------------------------------------------------------------
#run app layout things

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig1)
    ,html.Br()
    ,dcc.Graph(figure=fig2)
    ,html.Br()
    ,dcc.Graph(figure=fig3)
    ,html.Br()
    ,dcc.Graph(figure=fig4)
    ,html.Br()
    ,dcc.Graph(figure=fig5)
    ,html.Br()
    ,dcc.Graph(figure=fig6)
    ,html.Br()
    ,dcc.Graph(figure=fig7)
    ,html.Br()
    ,dcc.Graph(figure=fig8)
    ,html.Br()
    ,dcc.Graph(figure=fig9)
    ,html.Br()
    ,dcc.Graph(figure=fig10)
    ,html.Br()
    ,dcc.Graph(figure=fig11)
    ,html.Br()
    ,dcc.Graph(figure=fig12)
    ,html.Br()
    ,dcc.Graph(figure=fig13)
    ,html.Br()
    ,dcc.Graph(figure=fig14)
    ,html.Br()
    ,dcc.Graph(figure=fig15)
    ,html.Br()
    ,dcc.Graph(figure=fig16)
    ,html.Br()
    ,dcc.Graph(figure=fig17)
    ,html.Br()
    ,dcc.Graph(figure=fig18)
    ,html.Br()
    ,dcc.Graph(figure=fig19)
    ,html.Br()
    ,dcc.Graph(figure=fig20)
    ,html.Br()
    ,dcc.Graph(figure=fig21)
    ,html.Br()
    ,dcc.Graph(figure=fig22)
    ,html.Br()
    ,dcc.Graph(figure=fig23)
    ,html.Br()
    ,dcc.Graph(figure=fig24)
    ,html.Br()
    ,dcc.Graph(figure=fig25)
    ,html.Br()
    ,dcc.Graph(figure=fig26)
    ,html.Br()
    ,dcc.Graph(figure=fig27)
    ,html.Br()
    ,dcc.Graph(figure=fig28)
    ,html.Br()
    ,dcc.Graph(figure=fig29)
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
#web: gunicorn app:server


# @app.callback(Output('fig0','figure'),
#              [Input("submit-button", "n_clicks")],
#              [State("country-input", "value")]
#              )

#have to have a function for the callback
# def update_fig(n_clicks, input_value):
#     df = pd.read_csv('bigmac.csv')
#
#     df1 = df[['date','name','local_price','dollar_ex','dollar_price']]
#
#     date_unique = df1.date.nunique()
#     date_min = df1.date.min()
#     date_max = df1.date.max()
#     name_unique = df1.name.nunique()
#     dollar_price_min = df1.dollar_price.min()
#     dollar_price_max = df1.dollar_price.max()
#
#     name = df1['name'].value_counts().reset_index()
#     name = name[name['name'] > 20][['index','name']]
#
#     name.columns = ['countries','count']
#
#     countries = list(name['countries'])
#
#     colors = ['#0000ff', '#3300cc', '#660099', '#990066', '#cc0033', '#ff0000']
#
#     df2 = df1[df1['name'].isin(countries)]
#     name_unique = df2.name.nunique()
#     countries_unique = name.countries.nunique()
#
#     df2['average_price'] = df2[['dollar_price']].mean(axis=1)
#
#     df3 = df2.groupby('name').mean().reset_index()
#
#     df3.columns = ['country','local_price','dollar_ex','dollar_price','average_price']
#
#     df4 = df3[['dollar_price','country']]
#
#     prices = list(df1.groupby('name').dollar_price.unique())
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
