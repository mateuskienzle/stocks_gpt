from menu_styles import *
from functions import *
from app import *

from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd


import openai
from dotenv import load_dotenv
import os

load_dotenv()

#definicao da chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")


try:
    df_historico_wallet = pd.read_csv('historical_msgs_wallet.csv', index_col=0)

except:
    df_historico_wallet = pd.DataFrame(columns=['user', 'chatGPT'])

try:
    df_historico_sector = pd.read_csv('historical_msgs_sector.csv', index_col=0)
except:
    df_historico_sector = pd.DataFrame(columns=['user', 'chatGPT'])


df_historico_wallet.to_csv('historical_msgs_wallet.csv')
df_historico_sector.to_csv('historical_msgs_sector.csv')


df_data_wallet = pd.read_csv('book_data.csv')
df_data_wallet.drop('exchange', axis=1, inplace=True)
df_data_wallet['date'] = df_data_wallet['date'].str.replace('T00:00:00', '')


def generate_card_gpt(pesquisa):
    cardNovo =  dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-desktop', style={"fontSize": '85%'}), " ChatGPT: "], className='textoQuartenario'),
                                        html.H5(str(pesquisa), className='textoQuartenarioBranco')
                                    ], md=12, style={'text-align' : 'left'}),                              
                                ]),
                            ], md=11, xs=6, style={'text-align' : 'left'}),
                        ])
                    ])
                ], className='card_chatgpt')
            ])
        ], className='g-2 my-auto')

    return cardNovo
def generate_card_user(pesquisa):
    cardNovo =  dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-user-circle', style={"fontSize": '85%'}), " User: "], className='textoQuartenario'),
                                        html.H5(str(pesquisa), className='textoQuartenarioBranco')
                                    ], md=12, style={'text-align' : 'left'}),                              
                                ]),
                            ], md=11, xs=6, style={'text-align' : 'left'}),
                        ])
                    ])
                ], className='card_chatgpt')
            ])
        ], className='g-2 my-auto')

    return cardNovo

def generateCardsList(card_pergunta, card_resposta):

    cardAgrupado = dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    card_pergunta
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    card_resposta
                ])
            ]),
        ])
    ]),

    return cardAgrupado


def gerar_resposta(messages):
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        #model="gpt-3.5-turbo-0301", ## ate 1 junho 2023
        messages=messages,
        max_tokens=1024,
        temperature=1,
        # stream=True
        )
        retorno = response.choices[0].message.content
    except:
        retorno = 'Não foi possível pesquisar. ChatGPT fora do ar'
    return retorno

def clusterCards(df_msgs_store):

    df_historical_msgs = pd.DataFrame(df_msgs_store)
    cardsList = []
    
    for line in df_historical_msgs.iterrows():
        card_pergunta = generate_card_user(line[1]['user'])
        card_resposta = generate_card_gpt(line[1]['chatGPT'])

        cardsList.append(card_pergunta)
        cardsList.append(card_resposta)


    return cardsList

layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col("Wallet Chat", className='textoPrincipal', style={'margin-top' : '10px'}, md=12),
                ], className= 'g-2 my-auto'),

                dbc.Row([
                    dbc.Col([
                        dbc.Input(id="msg_user_wallet", type="text", placeholder="Insira uma mensagem")
                    ], md=10),
                    dbc.Col([
                        dbc.Button("Pesquisa", id="botao_search_wallet")
                    ], md=2),
                ], className= 'g-2 my-auto'),

                dbc.Row([
                    dbc.Col([

                    ],md=12, id='cards_respostas_wallet', style={"height": "100%", "maxHeight": "25rem", "overflow-y": "auto"}),
                ], className= 'g-2 my-auto'),
            ], md=6),

            dbc.Col([
                dbc.Row([
                    dbc.Col("Sector Chat", className='textoPrincipal', style={'margin-top' : '10px'}, md=12)
                ], className= 'g-2 my-auto'),

                dbc.Row([
                    dbc.Col([
                        dbc.Input(id="msg_user_sector", type="text", placeholder="Insira uma mensagem")
                    ], md=10),
                    dbc.Col([
                        dbc.Button("Pesquisa", id="botao_search_sector")
                    ], md=2)
                ], className= 'g-2 my-auto'),

                dbc.Row([
                    dbc.Col([

                    ],md=12, id='cards_respostas_sector', style={"height": "100%", "maxHeight": "25rem", "overflow-y": "auto"}),
                ], className= 'g-2 my-auto'),
            ], md=6),

        ], className= 'g-2 my-auto')

],fluid=True),


@app.callback(
 
    Output('cards_respostas_wallet', 'children'),
    Input('botao_search_wallet', 'n_clicks'),
    State('msg_user_wallet', 'value'),

)

def add_msg_wallet(n, msg_user):

    df_historical_msgs_wallet = pd.read_csv('historical_msgs_wallet.csv', index_col=0)

    if msg_user == None:
        lista_cards = clusterCards(df_historical_msgs_wallet)
        return lista_cards


    mensagem = f'{df_data_wallet}, considerando somente os dados existentes dentro do dataframe, qual é a resposta exata para a pergunta: ' + msg_user

    mensagens = []
    mensagens.append({"role": "user", "content": str(mensagem)})

    pergunta_user = mensagens[0]['content']
    resposta_chatgpt = gerar_resposta(mensagens)


    if pergunta_user == 'None' or  pergunta_user == '':
        lista_cards = clusterCards(df_historical_msgs_wallet)
        return lista_cards

    new_line = pd.DataFrame([[pergunta_user, resposta_chatgpt]], columns=['user', 'chatGPT'])

    new_line['user'] = new_line['user'].str.split(':')
    new_line['user'] = new_line['user'][0][-1]
    df_historical_msgs_wallet = pd.concat([new_line, df_historical_msgs_wallet], ignore_index = True)


    df_historical_msgs_wallet.to_csv('historical_msgs_wallet.csv')
    
    lista_cards = clusterCards(df_historical_msgs_wallet)



    return lista_cards


@app.callback(
 
    Output('cards_respostas_sector', 'children'),
    Input('botao_search_sector', 'n_clicks'),
    State('msg_user_sector', 'value'),

)

def add_msg_sector(n, msg_user):

    df_historical_msgs_sector = pd.read_csv('historical_msgs_sector.csv', index_col=0)

    if msg_user == None:
        lista_cards = clusterCards(df_historical_msgs_sector)
        return lista_cards


    mensagem = f'{df_data_wallet}, considerando somente os dados existentes dentro do dataframe, qual é a resposta exata para a pergunta: ' + msg_user

    mensagens = []
    mensagens.append({"role": "user", "content": str(mensagem)})

    pergunta_user = mensagens[0]['content']
    resposta_chatgpt = gerar_resposta(mensagens)


    if pergunta_user == 'None' or  pergunta_user == '':
        lista_cards = clusterCards(df_historical_msgs_sector)
        return lista_cards

    new_line = pd.DataFrame([[pergunta_user, resposta_chatgpt]], columns=['user', 'chatGPT'])

    new_line['user'] = new_line['user'].str.split(':')
    new_line['user'] = new_line['user'][0][-1]
    df_historical_msgs_sector = pd.concat([new_line, df_historical_msgs_sector], ignore_index = True)


    df_historical_msgs_sector.to_csv('historical_msgs_sector.csv')
    
    lista_cards = clusterCards(df_historical_msgs_sector)



    return lista_cards
