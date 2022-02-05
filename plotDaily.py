#!/usr/bin/env python3

import calcHourlyCAP as a
import datetime
import plotly.express as px
import plotly.graph_objects as go

d = a.getHourlyPricesH0('de')

time = []
awattar_price = []
price_diff = []
for p in d:
    time.append(p[0])
    awattar_price.append(p[1])
    price_diff.append(p[2])

fig = go.Figure(data=[
    go.Bar(
        name='diff from cap',
        x=time, y=price_diff),
    go.Bar(
        name='price without cap',
        x=time, y=awattar_price)
])


fig.update_layout(barmode='overlay', hovermode='x')
fig.layout['xaxis_tickformat'] = '%H'
fig.layout['xaxis_hoverformat'] = '%y/%m/%d %H:00'
fig.update_layout(
    title='Awattar CAP prices',
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        font_family="Rockwell"
    )
)
fig.update_xaxes(dtick=3600000)
fig.show()



