### SALA DE SINAIS ###

# Faz conexao websocket na corretora - V
# Escolhas random - V
# Espera horario - V
# Envia sticker de início - V
# Simula aposta - V
# Faz martingale (se necessário) - V
# Envia sinal (3 a 4 máximo) - V
# Envia sticker de win ou mensagem de loss - V
# Envia relatório ao final da sessão - V
# Arquivo config para personalizacões - V
# Adicionar o ID do canal no arquivo config - V
# Criar sessão de sinais e escolher quantidade de sinais no arquivo config - V
# Editar mensagens dos sinais/relatórios no config - V
# Adicionar mais texto na mensagem no config - V
# Novas moedas - V
# Texto com Acima/Abaixo - V
# Retirar (M1) - V

import asyncio
import websockets
import time
import json
import datetime
from pathlib import Path
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import os
import requests
import ast
import re

def intro():
    text = "AVALON SINAIS"
    dev = "Vitor A. DEV"
    ctttel = 31991914820
    cttdiscord = "Vitu1761"

    print('{:=^40}'.format(text))
    print('{:=^40}'.format(f" Desenvolvedor : {dev} "))
    print('{:=^40}'.format(f" Telefone : {ctttel} "))
    print('{:=^40}'.format(f" Discord : {cttdiscord} "))

    print()
    print('[0] - Prosseguir \n')
    input("Insira uma opção: ")

def enviar_mensagem(msg):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=HTML'

    try:
        requests.post(url)
        print("Mensagem enviada!")
    except Exception as e:
        print("Erro: ", e)

def gerar_sinal(moeda, objetivo):
    link_corretora = config['link_corretora']

    if(objetivo == 'COMPRA'):
        emoji_resultado = '🟢'
        direcao = '(Acima)'
    else:
        emoji_resultado = '🔴'
        direcao = '(Abaixo)'

    hora_agora = datetime.datetime.now()
    entrada_hora = hora_agora + datetime.timedelta(minutes=2)
    proximo_1minuto = entrada_hora + datetime.timedelta(minutes=1)
    proximo_2minuto = entrada_hora + datetime.timedelta(minutes=2)

    msg = f'''
{config['mensagens_sinais']['frase_1']} {moeda}
{config['mensagens_sinais']['frase_2']} 1 Minuto
{emoji_resultado} {objetivo.capitalize()} {direcao}
{config['mensagens_sinais']['frase_4']} {entrada_hora.strftime("%H:%M")}

{config['mensagens_sinais']['frase_5']}
{config['mensagens_sinais']['frase_6']} {proximo_1minuto.strftime("%H:%M")}
{config['mensagens_sinais']['frase_7']} {proximo_2minuto.strftime("%H:%M")}
🔗 [Clique aqui para abrir a corretora!]({link_corretora})'''
    
    if(len(config['mensagem_adicional']['texto']) > 0):
        msg2 = f"\n\n[{config['mensagem_adicional']['texto']}]({config['mensagem_adicional']['link']})"
        msg = msg + msg2

    params = {
    'chat_id': chat_id,
    'text': msg,
    'parse_mode': 'Markdown',  # Usando HTML, mas o link será interpretado como texto
    'disable_web_page_preview': True
}

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    try:
        requests.get(url, params=params)
        print("Mensagem enviada!")
    except Exception as e:
        print("Erro: ", e)

    horario_2_segundos_antes = entrada_hora.replace(second = 0, microsecond = 0) - datetime.timedelta(seconds=1)
    #print(horario_2_segundos_antes.strftime("%H:%M:%S"))

    return horario_2_segundos_antes, entrada_hora.strftime("%H:%M")





def enviar_sticker(sticker_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendSticker?chat_id={chat_id}&sticker={sticker_id}'

    try:
        requests.post(url)
        print("Sticker enviado!")
    except Exception as e:
        print("Erro: ", e)


def is_horario_valido():
    sessoes = config['sessao_sinais']

    while(True):
        for item in sessoes:
            if(datetime.datetime.now().strftime('%H:%M') == item['horario']):
                print('Horario válido!')

                # Envia sticker
                enviar_sticker(config['start_sticker_id'])
                print('Esperando 10 minutos...')
                time.sleep(10 * 60)

                return item['min_sinais'], item['max_sinais']
        
def is_horario(h1,m1,h2,m2, printar = False):
    agora = datetime.datetime.now().time()
    hora_inicio = datetime.time(h1, m1)  
    hora_fim = datetime.time(h2, m2)     
    
    if hora_inicio <= agora <= hora_fim:
        if(printar == True):
            print("Horário válido!")
        return True
    else:
        return False

def extrair_config():
    config = {}

    with open("Config/config.txt", "r", encoding="UTF-8") as file:
        mensagem = file.readlines()

        for linha in mensagem:
            linha = linha.strip()
            splited = linha.split('=', 1)
            config[f'{splited[0]}'] = splited[1]

            if('{' in splited[1]):
                config[f'{splited[0]}'] = ast.literal_eval(splited[1])

    return config

def gerar_relatorio(list_geral):
    wins = 0
    losses = 0
    resultado_final = ''
    msg1 = ''
    msg2 = ''
    msg3 = ''

    for item in list_geral:
        if(item[3] == '✅️'):
            wins += 1
        elif(item[3] == '❌'):
            losses += 1

    if (wins > losses):
        resultado_final = '✅️💰'
    elif(losses > wins):
        resultado_final = '❌'
    else:
        resultado_final = ''

    msg1 = f'''{config['mensagens_relatorio']['frase_1']}

'''

    for item in list_geral:
        msg2 += f'''{item[0]} | {item[1]} | {item[2]} | {item[3]}\n'''

    msg3 = f'''
{config['mensagens_relatorio']['frase_3']} {wins} x {losses} {resultado_final}'''

    msg_final = msg1 + msg2 + msg3

    print(msg_final)

    enviar_mensagem(msg_final)

# Headers
headers = {
"Host": "ws.trade.polariumbroker.com",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
"Accept": "*/*",
"Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate, br, zstd",
"Sec-WebSocket-Version": 13,
"Origin": "https://trade.polariumbroker.com",
"Sec-WebSocket-Extensions": "permessage-deflate",
"Sec-WebSocket-Key": "rM+/nQLxakEYmLySorhpaw==",
"Connection": "keep-alive, Upgrade",
"Cookie": "web_rules=; landing=trade.polariumbroker.com; lang=pt_PT; pll_language=pt; _vid_t=CEP93tNZn8NxzQgzG5DsVjFFCFwl/K3UDrX1mbpW/5hFTNaqi6rj4MTd7FLnAvW1HDluvXeFmFOBMw==; ssid=606e1174cb99d096ae56f109c5759a6e; _gcl_au=1.1.653231827.1731029116; _ga_BH1SENMS6L=GS1.1.1731191955.2.1.1731194653.50.0.0; _ga=GA1.2.8543462.1731029117; _ym_uid=173102911818916524; _ym_d=1731029118; _hjSessionUser_3225446=eyJpZCI6ImI4ZjhiNDFlLTFlMDktNWI1My1iNzE1LWI3NzNmNGExZDFlYSIsImNyZWF0ZWQiOjE3MzEwMjkxMTg0OTksImV4aXN0aW5nIjp0cnVlfQ==; afUserId=8a4971c1-38bf-4ef0-b384-c455946fb142-p; AF_SYNC=1731029121977; cto_bundle=zXxCqF8lMkJXYiUyQlNxSTBQSnNpRmlScCUyRm8lMkJJZ2Q2dktyZzZybEtLVm1QN0l4UVJVQnl6bG95UyUyQkR6ek1GSkZqYzQ0NWdHbXRqb096YUdNWDBIM1lNYW9mYWElMkJlMGJlRUJ1V2ZtNk1TODJ6WENxaUtrbVRiRjQ2eHRPSmowUnF2QnQ5bE1oaFpJaTBDQ1FNV01qQkFhVWNwVnBPTUh1YTUya0RQdG1DU0tPS0paYWM0Z0ElM0Q; __adroll_fpc=84718ddd00e55d0406c19472b9845aaa-1731029125146; __ar_v4=TASDBBMXPNBF3EY5FCLEZ4%3A20241108%3A21%7C4PVPFLGGBVA63KG73JCRKB%3A20241108%3A21%7CYVLLQ2ZQ2BHSZIRBNHADA7%3A20241108%3A21; platform=315; device_id=KlxiS8zeNlvn4CmvUMxv; device_id=KlxiS8zeNlvn4CmvUMxv; _hjSession_3225446=eyJpZCI6IjllOTk4MmUyLTA2NjgtNDMyMC1hMWY0LTgwNThiNjY2M2ZmNSIsImMiOjE3MzExOTE5NTc2MzksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _gid=GA1.2.1623199711.1731191958; _ym_isad=2; _ym_visorc=b; platform_version=3369.5.8010.release; device_locale=pt; _gat_UA-44367767-1=1; _dc_gtm_UA-44367767-1=1",
"Sec-Fetch-Dest": "empty",
"Sec-Fetch-Mode": "websocket",
"Sec-Fetch-Site": "same-site",
"Pragma": "no-cache",
"Cache-Control": "no-cache"
}

horario_manhã = (0,0,23,00)   # 1H e 10
horario_tarde = (14,50,16,00)  # 1H e 10
horario_noite = (19,50,23,00)  # 1H e 10

websocket_data = []

moedas = {
    'USD/BRL (OTC)' : 1546,
    'EUR/USD (OTC)' : 1345,
    'EUR/JPY (OTC)' : 1346,
    'PEN/USD (OTC)' : 1545,
    'AUD/CAD (OTC)' : 1348, 
    'EUR/GBP (OTC)' : 1347,
    'USD/MXN (OTC)' : 1548
}

escolha_objetivo = ['COMPRA', 'VENDA']
escolha_cooldown = [3, 4]
escolha_quantidade_sinais = [3, 4]

config = extrair_config()
chat_id = config['chat_id']
bot_token = config['bot_token']

async def comunicacao():
    # Variáveis
    uri = "wss://ws.trade.polariumbroker.com/echo/websocket"
    achou_moeda = False
    tentativas_martingale = 2
    i = 0
    tentativa_conexao = 0
    sinal_atual = 0
    horario_inicial = time.time()
    list_relatorio = []
    list_geral = []
    listas = []

    # Checa se está no horário
    min_sinais, max_sinais = is_horario_valido()

    # Escolhe randomicamente
    quantidade_sinais = random.randint(min_sinais, max_sinais)
    print(f"[{quantidade_sinais}] - Sinais")

    while(sinal_atual < quantidade_sinais):
        # Escolhe randomicamente
        objetivo = random.choice(escolha_objetivo)
        cooldown = random.choice(escolha_cooldown)
        tipo_moeda, moeda_id = random.choice(list(moedas.items()))
        
        async with websockets.connect(uri) as websocket:
            # Criar a mensagem de autenticação
            mensagem = {"name":"authenticate","request_id":"1732221414_387380317","local_time":11135,"msg":{"ssid":"71219081b1bf62d302648427c1fdba01","protocol":3,"session_id":"","client_session_id":""}}

            # Criar a mensagem de gerar velas
            mensagem_velas = {"name":"subscribeMessage","request_id":"s_233","local_time":27876,"msg":{"name":"candle-generated","params":{"routingFilters":{"active_id":moeda_id,"size":1}}}}
            
            # Enviar a mensagem como JSON
            await websocket.send(json.dumps(mensagem))
            print("Mensagem de autenticação enviada!")

            # Enviar a mensagem como JSON
            await websocket.send(json.dumps(mensagem_velas))
            print("Mensagem de gerar enviada!")

            # Tenta conexão até conectar
            print('Estabelecendo conexão...')
            for j in range(5):
                await websocket.send(json.dumps(mensagem))
                await websocket.send(json.dumps(mensagem_velas))
                time.sleep(3)

            # Printar objetivo e moeda
            print(f'[{objetivo}]')
            print(f'Moeda {tipo_moeda}, ID {moeda_id}')

            # Gera sinal
            horario_sinal, hora_relatorio = gerar_sinal(tipo_moeda, objetivo)

            # Espera horário do sinal
            while(True):
                if(datetime.datetime.now().strftime("%H:%M:%S") == horario_sinal.strftime("%H:%M:%S")):
                    print('[INICIANDO ENTRADA...]')
                    break

            # Simula aposta
            while (i <= tentativas_martingale):
                # Pega valor da moeda antes
                while(True):
                    try:
                        resposta = await websocket.recv()
                        resposta = json.loads(resposta)
                        tentativa_conexao += 1

                        if (resposta.get('name') != 'timeSync'):
                            try:
                                print(f"{tipo_moeda}: [{resposta['msg']['open']}]")
                                moeda = resposta['msg']['open']

                                horario_antes = time.time()
                                print('Espera de 60 segundos...')

                                achou_moeda = True

                                break
                            except:
                                achou_moeda = False

                    except websockets.ConnectionClosed:
                        print("Conexão fechada pelo servidor")
                        async with websockets.connect(uri) as websocket:
                                message = await websocket.recv()

                # Pega valor da moeda depois
                if(achou_moeda == True):
                    moeda_antes = float(moeda)

                    while(True):
                        try:
                            resposta = await websocket.recv()
                            resposta = json.loads(resposta)
                            if (resposta.get('name') != 'timeSync'):
                                websocket_data.append(resposta['msg']['open'])
                                #print(len(websocket_data))

                                try:
                                    if(len(websocket_data) % 60 == 0):
                                        print(f"{tipo_moeda}: [{resposta['msg']['open']}]")
                                        nova_moeda = resposta['msg']['open']

                                        break
                                except:
                                    print(f"Mensagem recebida do servidor: {resposta}")
                        except websockets.ConnectionClosed:
                            print("Conexão fechada pelo servidor")
                            async with websockets.connect(uri) as websocket:
                                    message = await websocket.recv()

                    moeda_depois = float(nova_moeda)

                    # Checa resultado
                    if(moeda_antes > moeda_depois):
                        print('CAIU!!!')

                        if(objetivo == 'VENDA'):
                            resultado = 'WIN'
                        elif(objetivo == 'COMPRA'):
                            resultado = 'LOSS'
                        else:
                            resultado = 'WIN' 

                    elif(moeda_antes < moeda_depois):
                        print('SUBIU!!!')

                        if(objetivo == 'VENDA'):
                            resultado = 'LOSS'
                        elif(objetivo == 'COMPRA'):
                            resultado = 'WIN'
                        else:
                            resultado = 'WIN'

                    else:
                        print('PERMANECEU!!!')

                        resultado = 'WIN'

                    if(resultado == 'WIN'):
                        print(f'Resultado : {resultado}')
                        print('Encerrando entrada...')
                        i = tentativas_martingale
                    elif(resultado == 'LOSS' and i < tentativas_martingale):
                        print(f'Iniciando martingale {i+1}...')
                    else:
                        print(f'Resultado : {resultado}')
                        print('Encerrando entrada...')

                    achou_moeda = False
                    i += 1

            # Garantir que o índice sinal_atual existe na lista listas
            if sinal_atual >= len(listas):
                # Adiciona uma nova sublista (lista interna) para o índice sinal_atual
                listas.append([])

            # Adiciona resultados para relatório
            listas[sinal_atual].append(hora_relatorio)
            listas[sinal_atual].append(tipo_moeda)
            listas[sinal_atual].append(objetivo.capitalize())
            if(resultado == 'WIN'):
                emoji = '✅️'
            elif(resultado == 'LOSS'):
                emoji = '❌'
            listas[sinal_atual].append(emoji)
            list_geral.append(listas[sinal_atual])

            # Envia resultado no Telegram
            if(resultado == 'WIN'):
                enviar_sticker(config['win_sticker_id'])
            elif(resultado == 'LOSS'):
                enviar_mensagem('Loss')

            # Atualiza/Reseta variáveis (sinal_atual e i)
            sinal_atual += 1
            i = 0
            websocket_data.clear()

            if(sinal_atual >= quantidade_sinais):
                # Gera relatório
                time.sleep(2 * 60)
                gerar_relatorio(list_geral)

                # Print
                print('Esperando próxima sessão...')

                # Reseta variáveis
                listas.clear()
                list_geral.clear()
            else:
                # Espera tempo aleatório (3 ou 4 min)
                print(f'Espera de [{cooldown}] minutos até o próximo sinal...')
                time.sleep(cooldown * 60)



# Intro
intro()
print('Aguardando horário...')

# Executar a função
while(True):
    asyncio.run(comunicacao())



# Retira time.sleep de 10 min
# Retirar comandos de teste