# from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import pandas as pd
# import statsmodels.api as sm
from .models import Post, City, Graph, Page, Tranzact, Cursor
from django.db.models import Sum, Avg, Count, Max, Min, ExpressionWrapper
from django.db.models.functions import TruncDay, TruncHour

import requests
import psycopg2
# import numpy as np
# import matplotlib.pyplot as plt
import json
# import humanize
from datetime import timedelta, datetime, timezone
import time
import pytz
import plotly
import plotly.graph_objs as go
from plotly.graph_objects import Layout
from plotly.subplots import make_subplots

def fig_mode(fig_viz):
    fig_viz.update_layout(legend_orientation="h",
                          legend=dict(x=.47, xanchor="center"),
                          title="",
                          xaxis_title="",
                          yaxis_title="",
                          margin=dict(l=7, r=1, t=5, b=5))
    fig_viz.update_xaxes(showline=True, linewidth=2, linecolor='grey', gridcolor='lightgrey', showspikes=True,
                         spikecolor='#124E6B', spikethickness=1, spikedash='solid', spikemode='toaxis+across',
                         rangeslider_visible=True, spikesnap='cursor')
    fig_viz.update_yaxes(showline=True, linewidth=2, linecolor='grey', gridcolor='lightgrey', showspikes=True,
                         spikecolor='#124E6B', spikethickness=1, spikedash='solid', spikemode='toaxis+across',
                         spikesnap='cursor')
    fig_viz.update_traces(hoverinfo="name+x+y")

    return fig_viz

def coinglass_fuch(url):
    headers = {
        'coinglassSecret': '0558723a13d64290aff82b1d812d40f2'
    }
    df = requests.request("GET", url, headers=headers)
    response_data = df.json()
    dates = pd.to_datetime(response_data['data']['dateList'], unit="ms")

    # dat_all = []
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for i in response_data['data']['dataMap']:
        fig.add_trace(go.Bar(x=dates, y=response_data['data']['dataMap'][i], name=i))

    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1586668800'  # s интервал дат ОТ в формате unix timestamp
    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)
    # Change the bar mode
    fig.update_layout(barmode='stack')
    fig_mode(fig)
    return fig

def glassnode_api(symbol, interval, formdat, start, url):
    apiKey = '27kcGrtdmU64ePdefbu3OJ1VDmu'
    path = 'https://api.glassnode.com' + url + '?a=' + symbol + '&s=' + start + '&timestamp_format=' + formdat + '&i=' + interval + '&api_key=' + apiKey
    return path

def glassnode_adress(toks):
    #  начитка кошельков в цикле -------------------
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1530000000'  # s интервал дат ОТ в формате unix timestamp
    pul = {
        '0.01-0.1': 'min_point_zero_1_count',
        '0.1-1': 'min_point_1_count',
        '1-10': 'min_1_count',
        '10-100': 'min_10_count',
        '100-1000': 'min_100_count',
        '1000-10k': 'min_1k_count',
        '>10k': 'min_10k_count',
    }
    # ---------- наложение графика цены BTC ---------------------------
    # dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    # dates = [d for d in dfp["t"]]
    # values = [l for l in dfp["v"]]

    color_list = ["#0d6efd", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7", "#e1ab09"]
    col = [x for x in color_list]
    c = 0
    for key, value in pul.items():
        url = '/v1/metrics/addresses/'+value
        fig_out = make_subplots(specs=[[{"secondary_y": True}]])
        print(key, '- ', value, url)
        df = pd.read_json(glassnode_api(toks, interval, formdat, start, url))
        minr = min(df["v"])*0.995
        maxr = max(df["v"])*1.001
        fig_out.add_trace(go.Bar(x=df["t"], y=df["v"], marker=dict(color=col[c]), name=key))
        c += 1
        fig_out.update_yaxes(range=[minr, maxr])

        # старый вариант формиривания основных графиков, заменен на  make_subplots (specs=[[{"secondary_y": True}]])
        # fig_out = go.Figure(data=dat_out, layout=layout)

        # ---------- наложение графика цены BTC ---------------------------
        # fig_out.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

        fig_mode(fig_out)
        graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)
        with open('media/'+toks+value+'.js', 'w') as file:
            file.write('var '+toks+value+' = {};'.format(graphJSON))

def glassnode_adress_pul(toks, pul):
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp

    fig_out = make_subplots(specs=[[{"secondary_y": True}]])

    color_list = ["#0d6efd", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7", "#e9700b"]
    # color_list = ["beige", "bisque", "black", "blanchedalmond", "blue", "blueviolet", "brown"]
    col = [x for x in color_list]
    c = 0
    minr = []
    maxr = []
    for key, value in pul.items():
        df = pd.read_json(glassnode_api(toks, interval, formdat, start, value))
        minr.append(min(df["v"]))
        maxr.append(max(df["v"]))
        fig_out.add_trace(go.Bar(x=df["t"], y=df["v"], marker=dict(color=col[c]), name=key))
        c += 1

    minmin = min(minr)*0.99
    maxmax = max(maxr)*1.001
    # fig_out.update_yaxes(range=[minmin, maxmax])

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_out.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_out)
    fig_out.update_layout(barmode='stack')
    graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def glassnode_balance(url, symbol):
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1550000000'  # s интервал дат ОТ в формате unix timestamp

    df = pd.read_json(glassnode_api(symbol, interval, formdat, start, url))
    dates = [i for i in df["t"]]
    list_exch = df['o'][21].keys()
    print(list_exch)

    fig_out = make_subplots(specs=[[{"secondary_y": True}]])

    for bir in list_exch:
        values = []
        for key in df["o"]:
            values.append(key[bir])
        fig_out.add_trace(go.Bar(x=dates, y=values, name=bir))

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_out.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_out)
    fig_out.update_layout(barmode='stack')
    graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def glassnode_one_value(url, symbol):
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp

    fig_out = make_subplots(specs=[[{"secondary_y": True}]])

    df = pd.read_json(glassnode_api(symbol, interval, formdat, start, url))
    dates = [i for i in df["t"]]
    values = [j for j in df["v"]]

    fig_out.add_trace(go.Bar(x=dates, y=values, name='IN / OUT'))

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_out.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_out)
    graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def glassnode_exchage(url, pul):
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp

    fig_out = make_subplots(specs=[[{"secondary_y": True}]])

    color_list = ["#0d6efd", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7", "#e3a710"]
    col = [x for x in color_list]
    c = 0
    # dat_out = []
    for key, value in pul.items():

        df = pd.read_json(glassnode_api(value, interval, formdat, start, url))
        fig_out.add_trace(go.Bar(x=df["t"], y=df["v"], marker=dict(color=col[c]), name=key))
        c += 1

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_out.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_out)
    fig_out.update_layout(barmode='stack')
    graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def change(request):
    # ------------ графики капитализации с Гласнода -------------------------
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp
    # u интервал дат ДО в формате unix timestamp

    #  ----------- BTC price  ----------------------------
    url = '/v1/metrics/market/price_usd_close'
    df = pd.read_json(glassnode_api('btc', interval, formdat, start, url))
    dates = [i for i in df["t"]]
    values = [j for j in df["v"]]
    layout = Layout(plot_bgcolor='rgba(111,210,255,0.3)')
    fig_out = go.Figure(layout=layout)
    fig_out.add_trace(go.Scatter(x=dates, y=values))
    fig_mode(fig_out)
    graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/btc_price.js', 'w') as file:
        file.write('var btc_price = {};'.format(graphJSON))

    #  ----------- капитализация  ----------------------------
    url = '/v1/metrics/market/marketcap_usd'
    #  ----------- монеты ----------------------------
    toks = ['BTC', 'ETH', 'LTC', 'MANA', 'LINK', 'UNI', 'YFI']

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        dates = [i for i in df["t"]]
        values = [j for j in df["v"]]
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name=k))

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/captoks.js', 'w') as file:
        file.write('var captoks = {};'.format(graphJSON))

    # ---------------- стейблы ----------------------------
    toks = ['USDT', 'BUSD', 'USDC', 'DAI']

    # fig = go.Figure(layout=layout)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    type_graf = 'bar'  # вид графика bar если прямо указано, иначе Scatter
    color_list = ["#0d6efd", "#e9700b", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7"]
    col = [x for x in color_list]
    c = 0
    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        dates = [i for i in df["t"]]
        values = [j for j in df["v"]]
        if type_graf == 'bar':
            fig.add_trace(go.Bar(x=dates, y=values, marker=dict(color=col[c]), name=k))
        else:
            fig.add_trace(go.Scatter(x=dates, y=values, name=k, line=dict(color=col[c], width=3)))
        c += 1

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig)
    fig.update_layout(barmode='stack')
    fig.update_xaxes(rangeslider_visible=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/capstable.js', 'w') as file:
        file.write('var capstable = {};'.format(graphJSON))

    # ------------ график 4 просадка от ATH монет с Гласнода -------------------------
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp
    # u интервал дат ДО в формате unix timestamp

    url = '/v1/metrics/market/price_drawdown_relative'
    toks = ['btc', 'eth']

    fig_down = make_subplots(specs=[[{"secondary_y": True}]])

    # dat_down = []
    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        fig_down.add_trace(go.Bar(x=df["t"], y=df["v"], name=k))

    # layout = Layout(plot_bgcolor='#f8f9fa')
    # fig_down = go.Figure(data=dat_down, layout=layout)
    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_down.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_down)
    fig_down.update_xaxes(side='top')
    fig_down.update_layout(barmode='overlay')  # по идее должны бары поверх друг друга, а не рядом

    graphJSON = json.dumps(fig_down, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/athdown.js', 'w') as file:
        file.write('var athdown = {};'.format(graphJSON))

    # ------------ реализованная прибыль  с Гласнода -------------------------
    url = '/v1/metrics/indicators/realized_profit'
    pul1 = {
        'BTC': 'btc',
    }
    graphJSON = glassnode_exchage(url, pul1)
    with open('media/realizedprof.js', 'w') as file:
        file.write('var realizedprof = {};'.format(graphJSON))

    # ------------ реализованный убыток с Гласнода -------------------------
    url = '/v1/metrics/indicators/realized_loss'
    pul2 = {
        'BTC': 'btc',
    }
    graphJSON = glassnode_exchage(url, pul2)
    with open('media/realizedloss.js', 'w') as file:
        file.write('var realizedloss = {};'.format(graphJSON))

    # ------------ НЕ реализованная прибыль  с Гласнода -------------------------
    url = '/v1/metrics/supply/profit_sum'
    pul3 = {
        'BTC': 'btc',
        'ETH': 'eth',
    }
    graphJSON = glassnode_exchage(url, pul3)
    with open('media/supplyprof.js', 'w') as file:
        file.write('var supplyprof = {};'.format(graphJSON))

    # ------------ НЕ реализованный убыток с Гласнода Total Supply in Loss -------------------------
    url = '/v1/metrics/supply/loss_sum'
    pul3 = {
        'BTC': 'btc',
        'ETH': 'eth',
    }
    graphJSON = glassnode_exchage(url, pul3)
    with open('media/supplyloss.js', 'w') as file:
        file.write('var supplyloss = {};'.format(graphJSON))

    # return render(request, 'change.html')

def change_activ(request):
    # ------------ Объемы фьючерсов  coinglass -------------------------
    fig_oi_btc = coinglass_fuch(
        'https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?symbol=BTC&interval=0')
    graphJSON = json.dumps(fig_oi_btc, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/opint_btc.js', 'w') as file:
        file.write('var opint_btc = {};'.format(graphJSON))

    fig_oi_eth = coinglass_fuch(
        'https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?symbol=ETH&interval=0')
    graphJSON = json.dumps(fig_oi_eth, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/opint_eth.js', 'w') as file:
        file.write('var opint_eth = {};'.format(graphJSON))

    fig_oi_xrp = coinglass_fuch(
        'https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?symbol=XRP&interval=0')
    graphJSON = json.dumps(fig_oi_xrp, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/opint_xrp.js', 'w') as file:
        file.write('var opint_xrp = {};'.format(graphJSON))

    # ------------ Открытый интерес на футуресах  coinglass -------------------------
    fig_btc = coinglass_fuch('https://open-api.coinglass.com/api/pro/v1/futures/vol/chart?&symbol=BTC')
    graphJSON = json.dumps(fig_btc, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/vfutur_btc.js', 'w') as file:
        file.write('var vfutur_btc = {};'.format(graphJSON))

    fig_eth = coinglass_fuch('https://open-api.coinglass.com/api/pro/v1/futures/vol/chart?&symbol=ETH')
    graphJSON = json.dumps(fig_eth, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/vfutur_eth.js', 'w') as file:
        file.write('var vfutur_eth = {};'.format(graphJSON))

    fig_xrp = coinglass_fuch('https://open-api.coinglass.com/api/pro/v1/futures/vol/chart?&symbol=XRP')
    graphJSON = json.dumps(fig_xrp, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/vfutur_xrp.js', 'w') as file:
        file.write('var vfutur_xrp = {};'.format(graphJSON))

    # return render(request, 'change_activ.html')

def change_activ2(request):

    # ------------ Общее количество монет, переданных по цепочке - БТС и ЕТН. Учитываются только успешные переводы.  -------------------------
    formdat = 'humanized'  # unix or humanized
    url = '/v1/metrics/transactions/transfers_volume_sum'
    toks = ['btc', 'eth']
    # ------------ Общее количество монет - по  часам, короткий период.  -------------------------
    start = '1640000000'  # s интервал дат ОТ в формате unix timestamp
    interval = '1h'  # frequency interval: 1h, 24h, 10m, 1w, 1month

    fig_transfers = make_subplots(specs=[[{"secondary_y": True}]])

    color_list = ["#0d6efd", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7", "#e9700b"]
    col = [x for x in color_list]
    c = 0
    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        fig_transfers.add_trace(go.Bar(x=df["t"], y=df["v"], marker=dict(color=col[c]), name=k))
        c += 1

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_transfers.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_transfers)
    fig_transfers.update_layout(barmode='stack')
    graphJSON = json.dumps(fig_transfers, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/transfers_exch1h.js', 'w') as file:
        file.write('var transfers_exch1h = {};'.format(graphJSON))

    # ------------ Общее количество монет - по  ДНЯМ.  -------------------------
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month

    fig_transfers = make_subplots(specs=[[{"secondary_y": True}]])

    color_list = ["#0d6efd", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7", "#e9700b"]
    col = [x for x in color_list]
    c = 0
    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        fig_transfers.add_trace(go.Bar(x=df["t"], y=df["v"], marker=dict(color=col[c]), name=k))
        c += 1

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_transfers.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_transfers)
    fig_transfers.update_layout(barmode='stack')
    graphJSON = json.dumps(fig_transfers, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/transfers_exch.js', 'w') as file:
        file.write('var transfers_exch = {};'.format(graphJSON))

    # ------------ BTC индекс волатильности  -------------------------
    url = '/v1/metrics/indicators/bvin'
    toks = ['btc']

    fig_bvin = make_subplots(specs=[[{"secondary_y": True}]])

    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        fig_bvin.add_trace(go.Scatter(x=df["t"], y=df["v"], name='Индекс волатильности BTC', line=dict(color='#fd7e14', width=3)))

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_bvin.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_bvin)
    graphJSON = json.dumps(fig_bvin, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/bvin.js', 'w') as file:
        file.write('var bvin = {};'.format(graphJSON))

    # ------------  Futures Estimated Leverage Ratio - All Exchanges ------------
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1596668800'  # s интервал дат ОТ в формате unix timestamp
    url = '/v1/metrics/derivatives/futures_estimated_leverage_ratio'
    pul = {
        'BTC': 'btc',
        'ETH': 'eth',
    }

    fig_out = make_subplots(specs=[[{"secondary_y": True}]])

    color_list = ["#0d6efd", "#1f764d", "#a4bd03", "#D55E00", "#0072B2", "#CC79A7", "#e9700b"]
    col = [x for x in color_list]
    c = 0
    for key, value in pul.items():
        print(key, '- ', value)
        df = pd.read_json(glassnode_api(value, interval, formdat, start, url))
        fig_out.add_trace(go.Bar(x=df["t"], y=df["v"], marker=dict(color=col[c]), name=key))
        c += 1

    # dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    # dates = [d for d in dfp["t"]]
    # values = [l for l in dfp["v"]]
    # fig_out.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_out)
    fig_out.update_layout(barmode='stack')
    graphJSON = json.dumps(fig_out, cls=plotly.utils.PlotlyJSONEncoder)

    with open('media/futmarginkredit.js', 'w') as file:
        file.write('var futmarginkredit = {};'.format(graphJSON))

    # return render(request, 'change_activ2.html')

def change_adr(request):
# ------------ начитка адресов -------------------------
    # ------------ Адреса не 0 баланс -------------------------
    interval = '24h'  # frequency interval: 1h, 24h, 10m, 1w, 1month
    formdat = 'humanized'  # unix or humanized
    start = '1496668800'  # s интервал дат ОТ в формате unix timestamp

    url = '/v1/metrics/addresses/non_zero_count'
    toks = ['btc', 'eth']

    fig_nonzero = make_subplots(specs=[[{"secondary_y": True}]])

    for k in toks:
        df = pd.read_json(glassnode_api(k, interval, formdat, start, url))
        fig_nonzero.add_trace(go.Scatter(x=df["t"], y=df["v"], name=k))

    dfp = pd.read_json(glassnode_api('btc', interval, formdat, start, '/v1/metrics/market/price_usd_close'))
    dates = [d for d in dfp["t"]]
    values = [l for l in dfp["v"]]
    fig_nonzero.add_trace(go.Scatter(x=dates, y=values, name='price BTC', line=dict(color='#343a40', width=1)), secondary_y=True)

    fig_mode(fig_nonzero)
    graphJSON = json.dumps(fig_nonzero, cls=plotly.utils.PlotlyJSONEncoder)
    with open('media/nonzero.js', 'w') as file:
        file.write('var nonzero = {};'.format(graphJSON))

    # ------------начитка всего пула кошельков -------------------
    glassnode_adress('btc')
    glassnode_adress('eth')

    #  начитка кошельков по BTC суммарными пулами (было изначатьно, далее разделено на каждый отедльно) -------------------
    toks = 'btc'
    pul1 = {
        '0.01-0.1': '/v1/metrics/addresses/min_point_zero_1_count',
        '0.1-1': '/v1/metrics/addresses/min_point_1_count',
        '1-10': '/v1/metrics/addresses/min_1_count',
        '10-100': '/v1/metrics/addresses/min_10_count',
    }
    graphJSON = glassnode_adress_pul(toks, pul1)
    with open('media/adr10.js', 'w') as file:
        file.write('var adr10 = {};'.format(graphJSON))

    pul1 = {
        '100-1000': '/v1/metrics/addresses/min_100_count',
        '1000-10k': '/v1/metrics/addresses/min_1k_count',
        '>10k': '/v1/metrics/addresses/min_10k_count',
    }
    graphJSON = glassnode_adress_pul(toks, pul1)
    with open('media/adr10k.js', 'w') as file:
        file.write('var adr10k = {};'.format(graphJSON))

    #  начитка кошельков по ETH -------------------
    toks = 'eth'
    pul2 = {
        '0.01-0.1': '/v1/metrics/addresses/min_point_zero_1_count',
        '0.1-1': '/v1/metrics/addresses/min_point_1_count',
        '1-10': '/v1/metrics/addresses/min_1_count',
        '10-100': '/v1/metrics/addresses/min_10_count',
    }
    graphJSON = glassnode_adress_pul(toks, pul2)
    with open('media/adreth10.js', 'w') as file:
        file.write('var adreth10 = {};'.format(graphJSON))

    pul1 = {
        '100-1000': '/v1/metrics/addresses/min_100_count',
        '1000-10k': '/v1/metrics/addresses/min_1k_count',
        '>10k': '/v1/metrics/addresses/min_10k_count',
    }
    graphJSON = glassnode_adress_pul(toks, pul1)
    with open('media/adreth10k.js', 'w') as file:
        file.write('var adreth10k = {};'.format(graphJSON))


    #  ЗАКРЫТО видать пока или Т3   # ------------ Адреса ETH in Loss / In Profit -------------------------
    # toks = 'eth'
    # pul2 = {
    #     'In Profit': '/v1/metrics/addresses/profit_count',
    #     'In Loss': '/v1/metrics/addresses/loss_count',
    # }
    # graphJSON = glassnode_adress(toks, pul2)
    # with open('media/ethprofit.js', 'w') as file:
    #     file.write('var ethprofit = {};'.format(graphJSON))
    #
    #     # ------------ Адреса BTC in Loss / In Profit  -------------------------
    # toks = 'btc'
    # pul2 = {
    #     'In Profit': '/v1/metrics/addresses/profit_count',
    #     'In Loss': '/v1/metrics/addresses/loss_count',
    # }
    # graphJSON = glassnode_adress(toks, pul2)
    # with open('media/btcprofit.js', 'w') as file:
    #     file.write('var btcprofit = {};'.format(graphJSON))

    # return render(request, 'change_adr.html')

def change_ex(request):
    # ------------ биржи монеты -------------------------
    # ------------ Изменение баланса на биржах за 30 дней -------------------------
    url = '/v1/metrics/distribution/exchange_net_position_change'
    pul1 = {
        'BTC': 'btc',
    }
    graphJSON = glassnode_exchage(url, pul1)
    with open('media/btc_change.js', 'w') as file:
        file.write('var btc_change = {};'.format(graphJSON))

    pul2 = {
        'ETH': 'eth',
    }
    graphJSON = glassnode_exchage(url, pul2)
    with open('media/eth_change.js', 'w') as file:
        file.write('var eth_change = {};'.format(graphJSON))

    # ------------ Чистый поток=Приток-отток (монет на биржу) -------------------------
    url = '/v1/metrics/transactions/transfers_volume_exchanges_net'
    symbol = 'btc'
    graphJSON = glassnode_one_value(url, symbol)
    with open('media/btc_transfers.js', 'w') as file:
        file.write('var btc_transfers = {};'.format(graphJSON))

    # ------------ баланс общий, без разбивки по биржам (пака не нужен) -------------------------
    # pul4 = {
    #     'ETH': 'eth',
    # }
    # graphJSON = glassnode_exchage(url, pul4)
    # with open('media/eth_balance.js', 'w') as file:
    #     file.write('var eth_balance = {};'.format(graphJSON))

    # ------------ Exchange Balance  -------------------------
    url = '/v1/metrics/distribution/balance_exchanges_all'
    symbol = 'btc'
    graphJSON = glassnode_balance(url, symbol)
    with open('media/btc_balance_exch.js', 'w') as file:
        file.write('var btc_balance_exch = {};'.format(graphJSON))

    url = '/v1/metrics/distribution/balance_exchanges_all'
    symbol = 'eth'
    graphJSON = glassnode_balance(url, symbol)
    with open('media/eth_balance_exch.js', 'w') as file:
        file.write('var eth_balance_exch = {};'.format(graphJSON))

    url = '/v1/metrics/distribution/balance_exchanges_all'
    symbol = 'usdt'
    graphJSON = glassnode_balance(url, symbol)
    with open('media/usdt_balance_exch.js', 'w') as file:
        file.write('var usdt_balance_exch = {};'.format(graphJSON))

    url = '/v1/metrics/distribution/balance_exchanges_all'
    symbol = 'usdc'
    graphJSON = glassnode_balance(url, symbol)
    with open('media/usdc_balance_exch.js', 'w') as file:
        file.write('var usdc_balance_exch = {};'.format(graphJSON))

    # ------------ финиш обнов по биржам-------------------------
    # return render(request, 'change_ex.html')

def o120522(request):
    pages = Page.objects.filter(id_page=101).order_by('sort')
    return render(request, 'o120522.html', {'pages': pages})

def o170522(request):
    pages = Page.objects.filter(id_page=102).order_by('sort')
    return render(request, 'o170522.html', {'pages': pages})

def home(request):
    pages_c = Page.objects.filter(id_page=11, column=1).order_by('sort')
    pages_r = Page.objects.filter(id_page=11, column=2).order_by('sort')
    return render(request, 'home.html', {'pages_c': pages_c, 'pages_r': pages_r})

def profloss(request):
    pages = Page.objects.filter(id_page=3).order_by('sort')
    return render(request, 'profloss.html', {'pages': pages})

def exchange(request):
    pages = Page.objects.filter(id_page=1).order_by('sort')
    return render(request, 'exchange.html', {'pages': pages})

def addresses(request):
    pages = Page.objects.filter(id_page=2).order_by('sort')
    return render(request, 'addresses.html', {'pages': pages})

def activity(request):
    pages = Page.objects.filter(id_page=4).order_by('sort')
    return render(request, 'activity.html', {'pages': pages})

def bigtrans(request):
    dtu = datetime.now().timestamp() - 50000
    tranzs = Tranzact.objects.filter(time_trz__gt=dtu).order_by('-id')
    return render(request, 'bigtrans.html', {'tranzs': tranzs})

def bigtrans_filter(request):
    dtu = datetime.now().timestamp() - 43200
    tranzs = Tranzact.objects.filter(time_trz__gt=dtu).order_by('-id')
    return render(request, 'bigtrans_filter.html', {'tranzs': tranzs})

def bigtrans_sum(request):
    pages = Page.objects.filter(id_page=12).order_by('sort')
    return render(request, 'bigtrans_sum.html', {'pages': pages})

def alertgraph(tranzs):

    datesTochange = []
    datesFromchange = []
    valuesTochange = []
    valuesFromchange = []
    for k in tranzs:
        datetrz = str(k['intval'].astimezone(pytz.timezone('Europe/Kiev')))

        if k['from_owner_type'] == 'unknown' and k['to_owner_type'] == 'exchange':
            datesTochange.append(datetrz)
            valuesTochange.append(k['amount__sum'])

        if k['from_owner_type'] == 'exchange' and k['to_owner_type'] == 'unknown':
            datesFromchange.append(datetrz)
            valuesFromchange.append(-k['amount__sum'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=datesTochange, y=valuesTochange, name="TO exchange", marker=dict(color='#0d6efd')))
    fig.add_trace(go.Bar(x=datesFromchange, y=valuesFromchange, name="FROM exchange", marker=dict(color='#09830f')))
    fig_mode(fig)
    fig.update_layout(barmode='overlay')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def alertExgraph(tranzs):

    datesExchange = []
    # datesFromchange = []
    valuesExchange = []
    # valuesFromchange = []
    for k in tranzs:
        datetrz = str(k['intval'].astimezone(pytz.timezone('Europe/Kiev')))

        if k['from_owner_type'] == 'exchange' and k['to_owner_type'] == 'exchange':
            datesExchange.append(datetrz)
            valuesExchange.append(k['amount__sum'])

        # if k['from_owner_type'] == 'exchange' and k['to_owner_type'] == 'unknown':
        #     datesFromchange.append(datetrz)
        #     valuesFromchange.append(-k['amount__sum'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=datesExchange, y=valuesExchange, name="TO exchange", marker=dict(color='#0d6efd')))
    # fig.add_trace(go.Bar(x=datesFromchange, y=valuesFromchange, name="FROM exchange", marker=dict(color='#09830f')))
    fig_mode(fig)
    fig.update_layout(barmode='overlay')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def alertOneEx(tranzs, exchnge):

    datesToOne = []
    datesFromOne = []
    valuesToOne = []
    valuesFromOne = []
    for k in tranzs:
        datetrz = str(k['intval'].astimezone(pytz.timezone('Europe/Kiev')))

        if k['from_owner'].lower() != exchnge.lower() and k['to_owner'].lower() == exchnge.lower():
            datesToOne.append(datetrz)
            valuesToOne.append(k['amount__sum'])

        if k['from_owner'].lower() == exchnge.lower() and k['to_owner'].lower() != exchnge.lower():
            datesFromOne.append(datetrz)
            valuesFromOne.append(-k['amount__sum'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=datesToOne, y=valuesToOne, name="TO exchange", marker=dict(color='#0d6efd')))
    fig.add_trace(go.Bar(x=datesFromOne, y=valuesFromOne, name="FROM exchange", marker=dict(color='#09830f')))
    fig_mode(fig)
    fig.update_layout(barmode='overlay')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def bigtrans_agr(request):
    dtu = datetime.now().timestamp() - 100000000 # ограничение по времени для дневок
    tranzsday = Tranzact.objects.filter(time_trz__gt=dtu, symbol='btc').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzsday)
    with open('media/alertday.js', 'w') as file:
        file.write('var alertday = {};'.format(graphJSON))

    dtuh = datetime.now().timestamp() - 1123200  # 13 дней для почасовки
    tranzshour = Tranzact.objects.filter(time_trz__gt=dtuh, symbol='btc').annotate(intval=TruncHour('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('-intval')
    graphJSON = alertgraph(tranzshour)
    with open('media/alerthour.js', 'w') as file:
        file.write('var alerthour = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='eth').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alertdayeth.js', 'w') as file:
        file.write('var alertdayeth = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtuh, symbol='eth').annotate(intval=TruncHour('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alerthoureth.js', 'w') as file:
        file.write('var alerthoureth = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='usdt').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alertdayusd.js', 'w') as file:
        file.write('var alertdayusd = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtuh, symbol='usdt').annotate(intval=TruncHour('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alerthourusd.js', 'w') as file:
        file.write('var alerthourusd = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='busd').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alertdaybusd.js', 'w') as file:
        file.write('var alertdaybusd = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='usdc').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alertdayusdc.js', 'w') as file:
        file.write('var alertdayusdc = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='trx').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alertdaytrx.js', 'w') as file:
        file.write('var alertdaytrx = {};'.format(graphJSON))

    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='xrp').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertgraph(tranzs)
    with open('media/alertdayxrp.js', 'w') as file:
        file.write('var alertdayxrp = {};'.format(graphJSON))

    tranzexday = Tranzact.objects.filter(time_trz__gt=dtu, symbol='btc').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner_type', 'to_owner_type').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertExgraph(tranzexday)
    with open('media/alertexday.js', 'w') as file:
        file.write('var alertexday = {};'.format(graphJSON))

    tranzoneday = Tranzact.objects.filter(time_trz__gt=dtu, symbol='btc').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner', 'to_owner').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertOneEx(tranzoneday, 'Binance')
    with open('media/alertone.js', 'w') as file:
        file.write('var alertone = {};'.format(graphJSON))
    graphJSON = alertOneEx(tranzoneday, 'Bitfinex')
    with open('media/alertonebf.js', 'w') as file:
        file.write('var alertonebf = {};'.format(graphJSON))
    graphJSON = alertOneEx(tranzoneday, 'Coinbase')
    with open('media/alertonecb.js', 'w') as file:
        file.write('var alertonecb = {};'.format(graphJSON))
    graphJSON = alertOneEx(tranzoneday, 'Gemini')
    with open('media/alertonegm.js', 'w') as file:
        file.write('var alertonegm = {};'.format(graphJSON))

    tranzoneday = Tranzact.objects.filter(time_trz__gt=dtu, symbol='eth').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner', 'to_owner').annotate(Sum('amount'), Sum('amount_usd')).order_by('symbol', '-intval')
    graphJSON = alertOneEx(tranzoneday, 'bitfinex')
    with open('media/alertoneet.js', 'w') as file:
        file.write('var alertoneet = {};'.format(graphJSON))

def bigtrans_full(request):
    # item['timeTrz'] = pd.to_datetime(item['timestamp'], unit="s") - преобразование UNIX в дату-время
    # item['amount_usd_int'] = ("{:12.0f}".format(item['amount_usd'])) - форматирование сумм
    dtu = datetime.now().timestamp() - 43200 # минус пол-сутки
    tranzs = Tranzact.objects.filter(time_trz__gt=dtu).order_by('-id')
    cursors = Cursor.objects.latest('timeapi')
    return render(request, 'bigtrans_full.html', {'tranzs': tranzs, 'cursors': cursors})

def bigtrans_szn(request):
    dtu = datetime.now().timestamp() - 586400
    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='btc').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner', 'to_owner', 'from_owner_type', 'to_owner_type').annotate(Avg('amount'), Count('amount'), Sum('amount'), Sum('amount_usd')).order_by('from_owner', 'to_owner', '-intval' )
    return render(request, 'bigtrans_szn.html', {'tranzs': tranzs, 'symb': 'BTC'})

def bigtranseth_szn(request):
    dtu = datetime.now().timestamp() - 586400
    tranzs = Tranzact.objects.filter(time_trz__gt=dtu, symbol='eth').annotate(intval=TruncDay('date_trz')).values('intval', 'symbol', 'from_owner', 'to_owner', 'from_owner_type', 'to_owner_type').annotate(Avg('amount'), Count('amount'), Sum('amount'), Sum('amount_usd')).order_by('from_owner', 'to_owner', '-intval' )
    return render(request, 'bigtrans_szn.html', {'tranzs': tranzs, 'symb': 'ETH'})


def telegram_bot_sendtext(token, chat_id, message):
    # photo_tel = 'https://bon-dvor.ru/image/catalog/tel_out.jpg'
    url = f'https://api.telegram.org/bot{token}/sendmessage?chat_id={chat_id}&parse_mode=HTML&text={message}'
    response = requests.get(url)
    # response2 = requests.get('https://api.telegram.org/bot' + token + '/sendPhoto?chat_id=' + chat_id + '&photo=' + photo_tel)
    # response3 = requests.get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&text=<b><i>Вам Малява: </i></b>\n\r - пропустили, шельмы, звонок то? \n\r - значица так?&parse_mode=HTML')    вариант &parse_mode=Markdown
    return response.json()

def sendBottest(request):
    token = '1859314561:AAFll5liYVo_pnNLfRIDxIMwAVaB9SciJr4'
    chat_id = '469352039'

    monet = 50000
    if monet >= 100000:
        numfire = '🔥🔥🔥'
    elif monet >= 65000:
        numfire = '🔥🔥'
    elif monet >= 30000:
        numfire = '🔥'
    else:
        numfire = ''

    textmes = numfire + '️🎯🎯🎯 <b><i>ПРОВЕРКА Бота</i></b>\n\r' + 'и шо мы имеем?'
    telegram_bot_sendtext(token, chat_id, textmes)
    return render(request, 'testbot.html')

# функция записи полученных данных в БД, и отправка в телеграм сообщений при срабатывании условий
def dump_alert(response_data):

    cur = Cursor()
    cur.cursorapi = response_data['cursor']
    cur.resultapi = response_data['result']
    cur.timeapi = datetime.now(timezone.utc)
    cur.countapi = response_data['count']

    cur.save(force_insert=True)

    lasttrz = Tranzact.objects.latest('time_trz')
    lastIdtrz = lasttrz.id_trz
    print(lastIdtrz)
    c = 1
    for item in response_data['transactions']:
        if int(item['id']) > lastIdtrz:

            if 'owner' not in item['from']:
                item['birFrom'] = 'out'
            else:
                item['birFrom'] = item['from']['owner']

            if 'owner' not in item['to']:
                item['birTo'] = 'out'
            else:
                item['birTo'] = item['to']['owner']
            item['n'] = c
            c += 1

            trzs = Tranzact()
            trzs.symbol = item['symbol']
            trzs.amount = item['amount']
            trzs.amount_usd = item['amount_usd']
            trzs.blockchain = item['blockchain']
            trzs.from_address = item['from']['address']
            trzs.from_owner = item['birFrom']
            trzs.from_owner_type = item['from']['owner_type']
            trzs.to_address = item['to']['address']
            trzs.to_owner = item['birTo']
            trzs.to_owner_type = item['to']['owner_type']
            trzs.hash = item['hash']
            trzs.id_trz = item['id']
            trzs.time_trz = item['timestamp']
            trzs.transaction_type = item['transaction_type']
            trzs.transaction_count = item['transaction_count']
            trzs.date_trz = pd.to_datetime(item['timestamp'], unit="s")

            trzs.save(force_insert=True)

        # Бот оповещения в телеграм о крупных и необычных транзакциях
            formraz = "{:,d}"

            if item['amount_usd'] >= 150_000_000:
                amfire = '🔥🔥🔥'
            elif item['amount_usd'] >= 100_000_000:
                amfire = '🔥🔥'
            elif item['amount_usd'] >= 50_000_000:
                amfire = '🔥'
            else:
                amfire = ''

            token = '1859314561:AAFll5liYVo_pnNLfRIDxIMwAVaB9SciJr4'
            chat_id = '469352039'

            messInf = '<b>' + item['symbol'].upper() + ' - ' + formraz.format(round(item['amount'])) + ' монет' + '</b>\n\rсумма в $ - ' + formraz.format(round(item['amount_usd'])) + '\n\rаккурат в: ' + str(pd.to_datetime((item['timestamp']+10800), unit="s"))
            if 'bit' in item['blockchain']:
                messLink = '<a href="https://bitinfocharts.com/ru/bitcoin/tx/' + item['hash'] + '">\n\rдетали транзакции</a>'
            elif item['blockchain'] == 'ethereum':
                messLink = '<a href="https://etherscan.io/tx/0x' + item['hash'] + '"> .</a>'
            elif item['blockchain'] == 'ripple':
                messLink = '<a href="https://bithomp.com/explorer/' + item['hash'] + '">\n\rдетали транзакции</a>'
            elif item['blockchain'] == 'tron':
                messLink = '<a href="https://tronscan.org/#/transaction/' + item['hash'] + '"> .</a>'
            else:
                messLink = ''
            print(messLink)

            # самые толстые небиржевые кошели
            if item['from']['address'] == '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ' or item['to']['address'] == '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ':
                textbig1 = '🎯🎯🎯 <b><i>Движ на КИТЕ-1 (MicroStrategy вроде)</i></b>\n\r' + messInf + messLink
                telegram_bot_sendtext(token, chat_id, textbig1)

            # сюда прошел переток с Кита-1 (возможно себе же)
            if item['from']['address'] == '1LQoWist8KkaUXSPKZHNvEyfrEkPHzSsCd' or item['to']['address'] == '1LQoWist8KkaUXSPKZHNvEyfrEkPHzSsCd':
                textbig1 = '🎯🎯🎯 <b><i>Движ на КИТЕ-2 (сюда ушло все с MicroStrategy)</i></b>\n\r' + messInf + messLink
                telegram_bot_sendtext(token, chat_id, textbig1)

            if item['from']['address'] == 'bc1qazcm763858nkj2dj986etajv6wquslv8uxwczt' or item['to']['address'] == 'bc1qazcm763858nkj2dj986etajv6wquslv8uxwczt':
                textbig1 = '🎯🎯🎯 <b><i>Движ на КИТЕ-3</i></b>\n\r' + messInf + messLink
                telegram_bot_sendtext(token, chat_id, textbig1)

            if item['from']['address'] == '1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF' or item['to']['address'] == '1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF':
                textbig1 = '🎯🎯🎯 <b><i>Движ на КИТЕ-4</i></b>\n\r' + messInf + messLink
                telegram_bot_sendtext(token, chat_id, textbig1)

            # вне бирж
            if item['birFrom'] == 'unknown' and item['birTo'] == 'unknown' and item['amount_usd'] > 200_000_000:
                if item['amount_usd'] >= 800_000_000:
                    amfireout = '🔥🔥🔥'
                elif item['amount_usd'] >= 500_000_000:
                    amfireout = '🔥🔥'
                elif item['amount_usd'] >= 300_000_000:
                    amfireout = '🔥'
                else:
                    amfireout = ''
                textmess = amfireout + ' <i>Транзакция вне бирж</i>\n\r' + messInf + messLink
            # внутренние
            elif item['birFrom'] != 'unknown' and item['birFrom'] == item['birTo'] and item['amount_usd'] > 21_000_000:
                textmess = amfire + ' <i>ВНУТРИ <b>' + item['birFrom'].upper() + '</b></i>\n\r' + messInf + messLink
            # между бирж
            elif item['birFrom'] != 'unknown' and item['birTo'] != 'unknown' and item['birFrom'] != item['birTo'] and item['amount_usd'] > 10_000_000:
                textmess = amfire + ' <i>Перевод с <b>' + item['birFrom'] + ' на ' + item['birTo'] + '</b></i>\n\r' + messInf + messLink
            # заводы на биржи
            elif item['birFrom'] == 'unknown' and item['birTo'] == 'Binance' and item['amount_usd'] > 21_000_000:
                textmess = amfire + ' <b><i>ЗАХОД на ' + item['birTo'].upper() + '</i></b>\n\r' + messInf + messLink
            elif item['birFrom'] == 'unknown' and item['birTo'] == 'Bitfinex' and item['amount_usd'] > 15_000_000:
                textmess = amfire + ' <b><i>ЗАХОД на ' + item['birTo'].upper() + '</i></b>\n\r' + messInf + messLink
            elif item['birFrom'] == 'unknown' and item['birTo'] == 'Coinbase' and item['amount_usd'] > 15_000_000:
                textmess = amfire + ' <b><i>ЗАХОД на ' + item['birTo'].upper() + '</i></b>\n\r' + messInf + messLink
            elif item['birFrom'] == 'unknown' and item['birTo'] == 'Gemini' and item['amount_usd'] > 15_000_000:
                textmess = amfire + ' <i>ЗАХОД на ' + item['birTo'] + '</i>\n\r' + messInf + messLink
            # заход на другие биржи и на основные меньше основного порога
            elif item['birFrom'] == 'unknown' and item['birTo'] != 'unknown' and item['amount_usd'] > 15_000_000:
                textmess = '<b><i>ЗАХОД на ' + item['birTo'] + '</i></b>\n\r' + messInf + messLink
            # выводы с бирж
            elif item['birFrom'] == 'Binance' and item['birTo'] == 'unknown' and item['amount_usd'] > 21_000_000:
                textmess = amfire + ' <b><i>ВЫВОД с ' + item['birFrom'].upper() + '</i></b>\n\r' + messInf + messLink
            elif item['birFrom'] == 'Bitfinex' and item['birTo'] == 'unknown' and item['amount_usd'] > 15_000_000:
                textmess = amfire + ' <i>ВЫВОД с ' + item['birFrom'].upper() + '</i>\n\r' + messInf + messLink
            elif item['birFrom'] == 'Coinbase' and item['birTo'] == 'unknown' and item['amount_usd'] > 15_000_000:
                textmess = amfire + ' <i>ВЫВОД с ' + item['birFrom'].upper() + '</i>\n\r' + messInf + messLink
            elif item['birFrom'] == 'Gemini' and item['birTo'] == 'unknown' and item['amount_usd'] > 15_000_000:
                textmess = amfire + ' <i>ВЫВОД с ' + item['birFrom'] + '</i>\n\r' + messInf + messLink
            # вывод на другие биржи и на основные меньше основного порога
            elif item['birFrom'] != 'unknown' and item['birTo'] == 'unknown' and item['amount_usd'] > 15_000_000:
                textmess = '<i>ВЫВОД с ' + item['birFrom'] + '</i>\n\r' + messInf + messLink
            # маловато будет
            else:
                textmess = ''
                print('ниче интересного')

            if textmess != '':
                print(textmess)
                telegram_bot_sendtext(token, chat_id, textmess)

def alert(request):
    i = 0
    while i < 5:
        headers = {
            'X-WA-API-KEY': 'XZVEZdTNoRIlNWtVGwTpEDqv0OoXDyU0'
        }
        cursors = Cursor.objects.latest('timeapi')
        time59 = datetime.now(timezone.utc) - timedelta(minutes=59)
        if cursors.timeapi > time59:
            cursorend = cursors.cursorapi
        else:
            cursorend = ''

        url = 'https://api.whale-alert.io/v1/transactions?cursor=' + cursorend
        df = requests.request("GET", url, headers=headers)
        response_data = df.json()

        result = response_data['result']
        count_trz = response_data['count']

        if count_trz > 0 and result == 'success':
            dump_alert(response_data)
            # tranzacts = response_data['transactions']
            # cursor_end = response_data['cursor']
            # print('новый курсор -', cursor_end)
            break
        else:
            print("НЕТУ новых, ждем-с")
            time.sleep(11)
        i += 1
        continue

def posts(request):
    posts = Post.objects

    toks = 'eth'
    pul2 = {
        '10-100': '/v1/metrics/addresses/min_10_count',
    }
    graphJSON = glassnode_adress_pul(toks, pul2)
    with open('media/prob.js', 'w') as file:
        file.write('var prob = {};'.format(graphJSON))
    #  ----------- всячина пробы вывода  ----------------------------
    bl = {
        'bi1': 'шош ты милай голову скланил та...',
        'values': ['123', 'se spis;', 'отож'],
        'posts': posts,
    }
    print(bl)
    return render(request, 'posts.html', {'posts': posts})

def proto(request):
    posts = Post.objects
    graphs = Graph.objects.filter(id__in=[26, 14])
    print(graphs)
    return render(request, 'proto.html', {'graphs': graphs, 'posts': posts})


def proto_bd_adr(request):
    pages = Page.objects.filter(id=11)
    return render(request, 'proto_bd_adr.html', {'pages': pages})

def proto_bd_pl(request):
    pages = Page.objects.filter(id_page=4)
    return render(request, 'proto_bd_pl.html', {'pages': pages})

def specific_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'specific_post.html', {'post': post})


# --------------- запасные и образцовые страницы ------------------------
def chartsapexcharts(request):
    return render(request, 'chartsapexcharts.html')

def chartschartjs(request):
    return render(request, 'chartschartjs.html')

def chartsecharts(request):
    return render(request, 'chartsecharts.html')

def tablesgeneral(request):
    return render(request, 'tablesgeneral.html')

def iconsbootstrap(request):
    return render(request, 'iconsbootstrap.html')

def iconsboxicons(request):
    return render(request, 'iconsboxicons.html')

def iconsremix(request):
    return render(request, 'iconsremix.html')

def tablesdata(request):
    return render(request, 'tablesdata.html')

def pagesblank(request):
    return render(request, 'pagesblank.html')
