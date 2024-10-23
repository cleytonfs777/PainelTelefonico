import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# import from folders/theme changer
from dash_bootstrap_templates import ThemeSwitchAIO

# ========== Styles ============ #
tab_card = {'height': '100%'}

main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor": "top",
               "y": 0.9,
               "xanchor": "left",
               "x": 0.1,
               "title": {"text": None},
               "font": {"color": "white"},
               "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l": 10, "r": 10, "t": 10, "b": 10}
}

config_graph = {"displayModeBar": True, "showTips": False}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

# ===== Reading and cleaning File ====== #
df_geral = pd.read_csv('assets/df_geral.csv', sep=',')
# Converter 'Tempo' para datetime
df_geral['Tempo'] = pd.to_datetime(df_geral['Tempo'])
df_geral['dia'] = df_geral['Tempo'].dt.day  # Extrair o dia para o gráfico
# Extrair o mês a partir de 'Tempo'
df_geral['Mês'] = df_geral['Tempo'].dt.month
df_geral['Ano'] = df_geral['Tempo'].dt.year  # Extrair o ano

# Função para definir a faixa horária


def definir_faixa_horaria(hora):
    if 0 <= hora < 2:
        return '00:00-02:00'
    elif 2 <= hora < 4:
        return '02:00-04:00'
    elif 4 <= hora < 6:
        return '04:00-06:00'
    elif 6 <= hora < 8:
        return '06:00-08:00'
    elif 8 <= hora < 10:
        return '08:00-10:00'
    elif 10 <= hora < 12:
        return '10:00-12:00'
    elif 12 <= hora < 14:
        return '12:00-14:00'
    elif 14 <= hora < 16:
        return '14:00-16:00'
    elif 16 <= hora < 18:
        return '16:00-18:00'
    elif 18 <= hora < 20:
        return '18:00-20:00'
    elif 20 <= hora < 22:
        return '20:00-22:00'
    else:
        return '22:00-00:00'


# Adicionar a nova coluna 'faixa_horaria' ao DataFrame
df_geral['faixa_horaria'] = df_geral['Tempo'].dt.hour.apply(
    definir_faixa_horaria)

# Dicionário para mapear os valores de COB para os nomes das regiões
cob_legend = {
    21: '2ºCOB - Uberlândia',
    22: '2ºCOB - Uberaba',
    31: '3ºCOB - Juiz de Fora',
    32: '3ºCOB - Barbacena',
    4: '4ºCOB - Montes Claros',
    51: '5ºCOB - Governador Valadares',
    52: '5ºCOB - Ipatinga',
    61: '6ºCOB - Varginha'
}

# Substituir os valores da coluna 'COB' pelos nomes das regiões
df_geral['COB_nome'] = df_geral['COB'].map(cob_legend)

# Função para converter os números dos meses em texto


def convert_to_text(month):
    months_dict = {
        0: 'Ano Todo',
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }
    return months_dict.get(month, "")


# Gerar opções de meses com base no DataFrame
options_month = [{'label': convert_to_text(
    mes), 'value': mes} for mes in df_geral['Mês'].unique()]
options_month = sorted(options_month, key=lambda x: x['value'])
# Adicionar "Todos"
# options_month.insert(0, {'label': 'Todos', 'value': 'all'})

# Gerar opções de COBs com base no dicionário cob_legend
options_cob = [{'label': cob_legend[key], 'value': key} for key in cob_legend]
# options_cob.insert(0, {'label': 'Todos', 'value': 'all'})  # Adiciona "Todos"

# Layout do Dashboard
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# =========  Layout  =========== #
app.layout = dbc.Container(children=[

    # Primeira Linha com Imagem, textos, toggle e filtros
    dbc.Row([
        # Coluna 1: Imagem, textos e o botão toggle
        dbc.Col([
            html.Div([
                html.Img(src='/assets/icon.png',  # Imagem da logo
                         style={'width': '100px', 'height': '100px', 'object-fit': 'contain'})
            ], style={'text-align': 'center'}),
            html.Legend("Centrais Telefônicas", style={
                'text-align': 'center', 'font-weight': 'bold', 'font-size': '1.5rem'}),
            html.Legend("CBMMG", style={'text-align': 'center'}),
            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])
        ], sm=12, md=4),  # Coluna 1 (Imagem e botões) ocupa 4/12 espaços

        # Coluna 2: Filtro por mês
        dbc.Col([
            dbc.CardBody([
                html.H3("Filtro por mês:", style={
                    'text-align': 'center', 'font-weight': 'bold', 'font-size': '1rem', 'margin-bottom': '1rem', 'background-color': '#00244BFF', 'color': 'white', 'border': '1px solid black'}),
                dcc.Checklist(
                    id='filter-buttons',
                    options=options_month,
                    value=[option['value']
                           for option in options_month if option['value'] != 'all'],
                    inline=False,  # Permitir grid
                )
            ], style={'text-align': 'center', 'font-weight': 'bold', 'font-size': '.7rem', 'border': '1px solid black', 'height': '14rem'})
        ], sm=12, md=4),  # Coluna 2 (Filtro por mês) ocupa 4/12 espaços

        # Coluna 3: Filtro por COB
        dbc.Col([
            dbc.CardBody([
                html.H3("Filtro por COB:", style={
                    'text-align': 'center', 'font-weight': 'bold', 'font-size': '1rem', 'margin-bottom': '1rem', 'background-color': '#00244BFF', 'color': 'white', 'border': '1px solid black'}),
                dcc.Checklist(
                    id='cob-filter-buttons',
                    options=options_cob,
                    value=[key for key in cob_legend],
                    inline=False,
                )
            ], style={'text-align': 'center', 'font-weight': 'bold', 'font-size': '.8rem', 'border': '1px solid black', 'height': '14rem'})
        ], sm=12, md=4),  # Coluna 3 (Filtro por COB) ocupa 4/12 espaços
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Segunda Linha com Gráfico 1
    dbc.Row([
        dbc.Col([dbc.Card([
            dbc.CardBody([
                dcc.Graph(id='graph1', className='dbc', config=config_graph)
            ])
        ], style=tab_card)
        ]),  # Ocupar toda a linha
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Terceira Linha com Gráficos 2 e 3
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph2', className='dbc',
                              config=config_graph)  # Gráfico 2
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph3', className='dbc',
                              config=config_graph)  # Gráfico 3
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Quarta Linha com Gráfico 4
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph4', className='dbc',
                              config=config_graph)  # Gráfico 4 sozinho
                ])
            ], style=tab_card)
        ], sm=12, lg=12),  # Ocupar toda a linha
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Quinta Linha com Gráficos 5 e 6
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Gráfico 5 ocupa 6 espaços
                    dcc.Graph(id='graph5', className='dbc',
                              config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Gráfico 6 ocupa 6 espaços
                    dcc.Graph(id='graph6', className='dbc',
                              config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Sexta Linha com Gráficos 7 e 8
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Gráfico 7 ocupa 6 espaços
                    dcc.Graph(id='graph7', className='dbc',
                              config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Gráfico 8 ocupa 6 espaços
                    dcc.Graph(id='graph8', className='dbc',
                              config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=6),
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

], fluid=True, style={'height': '100vh'})

# Callback para Graficos
# Callback para atualizar os filtros


@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('graph3', 'figure'),
     Output('graph4', 'figure'),
     Output('graph5', 'figure'),
     Output('graph6', 'figure'),
     Output('graph7', 'figure'),
     Output('graph8', 'figure')],
    [Input('filter-buttons', 'value'),
     Input('cob-filter-buttons', 'value'),
     Input(ThemeSwitchAIO.ids.switch("theme"), "value")]
)
def update_graphs(month, cobs, toggle):
    template = template_theme1 if toggle else template_theme2

    # Filtrar dados com base nos meses e COBs selecionados
    if 'all' not in month:
        df_filtered = df_geral[df_geral['Mês'].isin(month)]
    else:
        df_filtered = df_geral.copy()

    if 'all' not in cobs:
        df_filtered = df_filtered[df_filtered['COB'].isin(cobs)]

    # Gráfico 1 - Quantidade de Ligações por Dia
    chamadas_por_dia_cob = df_filtered.groupby(
        [df_filtered['Tempo'].dt.date, 'COB_nome']).size().reset_index(name='Quantidade')
    fig1 = px.bar(chamadas_por_dia_cob, x='Tempo', y='Quantidade', color='COB_nome',
                  labels={'Quantidade': 'Número de Chamadas', 'Tempo': 'Dia', 'COB_nome': 'Região (COB)'})
    fig1.update_layout(legend_title_text='Região (COB)',
                       legend=dict(traceorder='normal'), template=template, height=400)

    # Gráfico 2 - Ligações Atendidas e Não Atendidas por COB
    atendidas_nao_atendidas = df_filtered.groupby(
        ['COB_nome', 'Status']).size().reset_index(name='Quantidade')
    status_mapping = {0: 'Não Atendido', 1: 'Atendido'}
    atendidas_nao_atendidas['Status'] = atendidas_nao_atendidas['Status'].map(
        status_mapping)
    fig2 = px.bar(atendidas_nao_atendidas, x='COB_nome', y='Quantidade', color='Status',
                  labels={'Quantidade': 'Número de Chamadas', 'COB_nome': 'Região (COB)', 'Status': 'Atendimento'})
    fig2.update_layout(legend_title_text='Atendimento',
                       legend=dict(traceorder='normal'), template=template)

    # Gráfico 3 - Ligações por Faixa Horária e COB
    chamadas_por_faixa_horaria = df_filtered.groupby(
        ['faixa_horaria', 'COB_nome']).size().reset_index(name='Quantidade')
    faixa_horaria_ordem = ['00:00-02:00', '02:00-04:00', '04:00-06:00', '06:00-08:00', '08:00-10:00',
                           '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00', '18:00-20:00',
                           '20:00-22:00', '22:00-00:00']
    chamadas_por_faixa_horaria['faixa_horaria'] = pd.Categorical(chamadas_por_faixa_horaria['faixa_horaria'],
                                                                 categories=faixa_horaria_ordem, ordered=True)
    fig3 = px.bar(chamadas_por_faixa_horaria, x='faixa_horaria', y='Quantidade', color='COB_nome',
                  labels={'Quantidade': 'Número de Chamadas', 'faixa_horaria': 'Faixa Horária', 'COB_nome': 'Região (COB)'})
    fig3.update_layout(legend_title_text='Região (COB)',
                       legend=dict(traceorder='normal'), template=template)

    # Gráfico 4 - Picos de Ligações por Faixa Horária e COB
    chamadas_por_faixa_cob = df_filtered.groupby(
        ['faixa_horaria', 'COB_nome']).size().reset_index(name='Quantidade')
    fig4 = px.line(chamadas_por_faixa_cob, x='faixa_horaria', y='Quantidade', color='COB_nome',
                   labels={'faixa_horaria': 'Faixa Horária', 'Quantidade': 'Número de Chamadas', 'COB_nome': 'Região (COB)'})
    fig4.update_layout(legend_title_text='Região (COB)',
                       legend=dict(traceorder='normal'), template=template)

    # Gráfico 5 - Distribuição de ligações atendidas por COB
    chamadas_atendidas = df_filtered[df_filtered['Status'] == 1]
    atendidas_por_cob = chamadas_atendidas.groupby(
        'COB_nome').size().reset_index(name='Quantidade')
    fig5 = px.pie(atendidas_por_cob, values='Quantidade', names='COB_nome',
                  title='Distribuição de ligações atendidas por COB (Região)',
                  labels={'COB_nome': 'Região (COB)', 'Quantidade': 'Número de Chamadas'})
    fig5.update_layout(template=template)

    # Gráfico 6 - Top Atendente por número de ligações
    chamadas_atendidas = df_filtered[(df_filtered['Status'] == 1) & (
        df_filtered['Teleatendente'] != '0')]
    atendidas_por_atendente = chamadas_atendidas.groupby(
        ['Teleatendente', 'COB_nome']).size().reset_index(name='Quantidade')
    atendidas_por_atendente.sort_values(
        by='Quantidade', ascending=False, inplace=True)
    media_atendidas = atendidas_por_atendente['Quantidade'].mean()

    fig6 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{atendidas_por_atendente['Teleatendente'].iloc[0]} - Top Atendente</span><br>"
            f"<span style='font-size:90%'>COB: {atendidas_por_atendente['COB_nome'].iloc[0]}</span><br>"
            f"<span style='font-size:90%'>Ligações atendidas - em relação à média</span>"
        },
        value=atendidas_por_atendente['Quantidade'].iloc[0],
        number={'suffix': " ligações", 'font': {'size': 50}},
        delta={'relative': True, 'valueformat': '.1%','reference': media_atendidas, 'position': "bottom", 'font': {'size': 30}}
    ))

    # Atualizando o layout para ocupar todo o espaço
    fig6.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),  # Ajustar margens para zero
        height=None,  # Remover a definição de altura
        width=None,   # Remover a definição de largura
        template=template,
        autosize=True  # Permitir que o gráfico ajuste automaticamente o tamanho
    )

    # Gráfico 7 - Top COB por número de ligações atendidas
    atendidas_por_cob = chamadas_atendidas.groupby(
        'COB_nome').size().reset_index(name='Quantidade')
    atendidas_por_cob.sort_values(
        by='Quantidade', ascending=False, inplace=True)
    media_atendidas_por_cob = atendidas_por_cob['Quantidade'].mean()

    fig7 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{atendidas_por_cob['COB_nome'].iloc[0]} - Top COB</span><br>"
            f"<span style='font-size:90%'>Região com mais ligações atendidas</span><br>"
            f"<span style='font-size:90%'>Ligações atendidas - em relação à média</span>"
        },
        value=atendidas_por_cob['Quantidade'].iloc[0],
        number={'suffix': " ligações", 'font': {'size': 50}},
        delta={'relative': True, 'valueformat': '.1%','reference': media_atendidas_por_cob, 'position': "bottom", 'font': {'size': 30}}
    ))

    # Atualizando o layout para ocupar todo o espaço
    fig7.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),  # Ajustar margens para zero
        height=None,  # Remover a definição de altura
        width=None,   # Remover a definição de largura
        template=template,
        autosize=True  # Permitir que o gráfico ajuste automaticamente o tamanho
    )

    # Gráfico 8 - Top COB por número de ligações não atendidas
    chamadas_nao_atendidas = df_filtered[df_filtered['Status'] == 0]
    nao_atendidas_por_cob = chamadas_nao_atendidas.groupby(
        'COB_nome').size().reset_index(name='Quantidade')
    nao_atendidas_por_cob.sort_values(
        by='Quantidade', ascending=False, inplace=True)
    media_nao_atendidas_por_cob = nao_atendidas_por_cob['Quantidade'].mean()

    fig8 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{nao_atendidas_por_cob['COB_nome'].iloc[0]} - Top COB</span><br>"
            f"<span style='font-size:90%'>Região com mais ligações não atendidas</span><br>"
            f"<span style='font-size:90%'>Ligações não atendidas - em relação à média</span>"
        },
        value=nao_atendidas_por_cob['Quantidade'].iloc[0],
        number={'suffix': " ligações", 'font': {'size': 50}},
        delta={'relative': True, 'valueformat': '.1%','reference': media_nao_atendidas_por_cob, 'position': "bottom", 'font': {'size': 30}}
    ))

    # Atualizando o layout para ocupar todo o espaço
    fig8.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),  # Ajustar margens para zero
        height=None,  # Remover a definição de altura
        width=None,   # Remover a definição de largura
        template=template,
        autosize=True  # Permitir que o gráfico ajuste automaticamente o tamanho
    )

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8


if __name__ == '__main__':
    app.run_server(debug=True)
