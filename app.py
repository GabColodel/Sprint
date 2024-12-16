import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import numpy as np
from flask import Flask, send_from_directory

# Caminho para o arquivo Excel
caminho_arquivo = r"C:/Users/colod/OneDrive/Desktop/Dispersao/Dispersao.xlsx"

# Ler o arquivo Excel
df = pd.read_excel(caminho_arquivo)

# Resetar o índice para que ele se torne uma coluna
df = df.reset_index()

# Caminho para a pasta de vídeos
caminho_videos = r"C:/Users/colod/OneDrive/Desktop/Dispersao"

# Configurar Flask para servir os vídeos
server = Flask(__name__)

@server.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(caminho_videos, filename)

# Iniciar o app Dash com o servidor Flask
app = dash.Dash(__name__, server=server)

# Layout do app
app.layout = html.Div(
    style={
        'backgroundColor': '#1e1e1e',  # Cor de fundo escura
        'color': 'white',  # Cor do texto
        'padding': '10px',
        'fontFamily': 'Arial, sans-serif'
    },
    children=[
        html.H1(
            "Análise de Sprint",
            style={'textAlign': 'center', 'color': 'white'}
        ),
        # Filtros em uma única linha
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Label("Posições:", style={'fontSize': '14px', 'marginBottom': '5px'}),
                        dcc.Checklist(
                            id='position-filter',
                            options=[{'label': pos, 'value': pos} for pos in df['Posição'].unique()],
                            value=df['Posição'].unique().tolist(),
                            style={'color': 'white'}
                        )
                    ],
                    style={'width': '19%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
                html.Div(
                    children=[
                        html.Label("Partes:", style={'fontSize': '14px', 'marginBottom': '5px'}),
                        dcc.Checklist(
                            id='part-filter',
                            options=[{'label': part, 'value': part} for part in df['Parte'].unique()],
                            value=df['Parte'].unique().tolist(),
                            style={'color': 'white'}
                        )
                    ],
                    style={'width': '19%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
                html.Div(
                    children=[
                        html.Label("Datas:", style={'fontSize': '14px', 'marginBottom': '5px'}),
                        dcc.Checklist(
                            id='date-filter',
                            options=[{'label': date, 'value': date} for date in df['Data'].unique()],
                            value=df['Data'].unique().tolist(),
                            style={'color': 'white'}
                        )
                    ],
                    style={'width': '19%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
                html.Div(
                    children=[
                        html.Label("Adversários:", style={'fontSize': '14px', 'marginBottom': '5px'}),
                        dcc.Checklist(
                            id='opponent-filter',
                            options=[{'label': opp, 'value': opp} for opp in df['Adversário'].unique()],
                            value=df['Adversário'].unique().tolist(),
                            style={'color': 'white'}
                        )
                    ],
                    style={'width': '19%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
                html.Div(
                    children=[
                        html.Label("Fases:", style={'fontSize': '14px', 'marginBottom': '5px'}),
                        dcc.Checklist(
                            id='phase-filter',
                            options=[{'label': phase, 'value': phase} for phase in df['Fase'].unique()],
                            value=df['Fase'].unique().tolist(),
                            style={'color': 'white'}
                        )
                    ],
                    style={'width': '19%', 'display': 'inline-block', 'verticalAlign': 'top'}
                ),
            ],
            style={
                'marginBottom': '20px',
                'display': 'flex',
                'justifyContent': 'space-between'
            }
        ),
        dcc.Graph(id='scatter-plot'),
        html.Div(
            id='equation-container',
            style={
                'marginTop': '20px',
                'textAlign': 'right',
                'color': 'white',
                'fontSize': '16px',
                'paddingRight': '20px'
            }
        ),
        html.Div(id='video-container', style={'marginTop': '20px', 'textAlign': 'center'})
    ]
)

# Callback para atualizar o gráfico e a equação
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('equation-container', 'children')],
    [Input('position-filter', 'value'),
     Input('part-filter', 'value'),
     Input('date-filter', 'value'),
     Input('opponent-filter', 'value'),
     Input('phase-filter', 'value')]
)
def update_scatter(selected_positions, selected_parts, selected_dates, selected_opponents, selected_phases):
    # Filtrar o DataFrame com base nas seleções
    filtered_df = df[
        df['Posição'].isin(selected_positions) &
        df['Parte'].isin(selected_parts) &
        df['Data'].isin(selected_dates) &
        df['Adversário'].isin(selected_opponents) &
        df['Fase'].isin(selected_phases)
    ]

    # Criar o gráfico de dispersão
    fig = px.scatter(
        filtered_df,
        x="Distancia",
        y="Tempo",
        size="VelocidadeMaxima",
        hover_name="Nome",
        title="Gráfico de Dispersão: Distância vs Tempo",
        labels={
            "Distancia": "Distância (m)",
            "Tempo": "Tempo (s)",
            "Ação": "Tipo de Ação"
        },
        color="Ação",
        custom_data=['index']  # Inclui o índice original no hoverData
    )

    # Tema escuro
    fig.update_layout(template="plotly_dark")

    # Adicionar linha de tendência
    if not filtered_df.empty:
        x = filtered_df["Distancia"].values
        y = filtered_df["Tempo"].values

        # Regressão linear para calcular a linha de tendência
        coef = np.polyfit(x, y, 1)
        poly1d_fn = np.poly1d(coef)
        fig.add_scatter(
            x=x,
            y=poly1d_fn(x),
            mode='lines',
            name='Linha de Tendência',
            line=dict(dash='dot', color='white', width=1)
        )

        # Gerar a equação da linha de tendência
        equation = f"Equação da linha: y = {coef[0]:.2f}x + {coef[1]:.2f}"
    else:
        equation = "Nenhuma linha de tendência disponível."

    # Adicionar os nomes como anotações abaixo dos marcadores
    annotations = []
    for i, row in filtered_df.iterrows():
        annotations.append(
            dict(
                x=row["Distancia"],
                y=row["Tempo"] - 0.5,
                text=row["Nome"],
                showarrow=False,
                font=dict(size=10, color="white"),
            )
        )
    fig.update_layout(annotations=annotations)

    return fig, equation


# Callback para atualizar o vídeo ao passar o mouse sobre um ponto
@app.callback(
    Output('video-container', 'children'),
    [Input('scatter-plot', 'hoverData'),
     Input('position-filter', 'value'),
     Input('part-filter', 'value'),
     Input('date-filter', 'value'),
     Input('opponent-filter', 'value'),
     Input('phase-filter', 'value')]
)
def update_video(hoverData, selected_positions, selected_parts, selected_dates, selected_opponents, selected_phases):
    if hoverData is None:
        return html.Div("Passe o mouse sobre um marcador para ver o vídeo.")

    # Filtrar o DataFrame com base nas seleções
    filtered_df = df[
        df['Posição'].isin(selected_positions) &
        df['Parte'].isin(selected_parts) &
        df['Data'].isin(selected_dates) &
        df['Adversário'].isin(selected_opponents) &
        df['Fase'].isin(selected_phases)
    ]

    # Obter o índice original da linha no DataFrame principal
    point_index = hoverData['points'][0]['customdata'][0]

    # Usar o índice original para localizar a linha no DataFrame original
    video_filename = df.loc[point_index, 'Video']

    # Construir o URL do vídeo
    video_url = f"/videos/{video_filename}"

    # Renderizar o vídeo
    return html.Video(
        src=video_url,
        controls=True,
        autoPlay=True,
        style={'width': '600px', 'height': '400px'}
    )

# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True)
