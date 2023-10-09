import json
import requests
import os


def colhe_nomes_conjuntos_de_dados(arquivo_destino: str):
  offset = 0
  tamanho_pagina = 50

  request_base = f'https://dados.gov.br/api/publico/conjuntos-dados/buscar?offset={0}&tamanhoPagina={1}'
  response_base = requests.get(request_base)
  response_json_object = json.loads(response_base.text) 
  quantidade_registros_restantes = response_json_object["totalRegistros"]

  with open(arquivo_destino, 'w', encoding='utf-8') as arquivo:
    while quantidade_registros_restantes > 0:
      if quantidade_registros_restantes <= tamanho_pagina:
        tamanho_pagina = quantidade_registros_restantes
      request = f'https://dados.gov.br/api/publico/conjuntos-dados/buscar?offset={offset}&tamanhoPagina={tamanho_pagina}'
      response = requests.get(request)
      response_json_object = json.loads(response.text)
      registros = response_json_object.get('registros')
      if registros is not None:
        for registro in registros:
          arquivo.write(registro['name'] + '\n')
      offset += tamanho_pagina
      quantidade_registros_restantes -= tamanho_pagina


def colhe_conjuntos_de_dados(arquivo_nomes_conjuntos_de_dados: str, diretorio_destino: str):
  with open(arquivo_nomes_conjuntos_de_dados, 'r') as arquivo:
    id_conjunto = 0
    for nome_conjunto_de_dados in arquivo:
      nome_conjunto_de_dados = nome_conjunto_de_dados.strip()
      request_conjunto_de_dados = f'https://dados.gov.br/api/publico/conjuntos-dados/{nome_conjunto_de_dados}'
      response_conjunto_de_dados = requests.get(request_conjunto_de_dados)
      try:
        conjunto_de_dados = json.loads(response_conjunto_de_dados.text)
        conjunto_de_dados_valido = conjunto_de_dados.get('id') is not None
        if conjunto_de_dados_valido:
          caminho_arquivo = os.path.join(diretorio_destino, f'{id_conjunto}.json')
          with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo_conjunto_de_dados:
            conjunto_de_dados_json = json.dumps(conjunto_de_dados, ensure_ascii=False, indent=2)
            arquivo_conjunto_de_dados.write(conjunto_de_dados_json)
            id_conjunto += 1
      except json.JSONDecodeError as e:
        with open('log_conjuntos_json_improprio.txt', 'a', encoding='utf-8') as arquivo_log_json_improprio:
          arquivo_log_json_improprio.write(nome_conjunto_de_dados + '\n')

          
arquivo_nomes_conjuntos_de_dados = 'nomes_registros.txt'
diretorio_destino = 'conjuntos_de_dados'
os.makedirs(diretorio_destino, exist_ok=True)  
colhe_nomes_conjuntos_de_dados(arquivo_nomes_conjuntos_de_dados)
colhe_conjuntos_de_dados(arquivo_nomes_conjuntos_de_dados, diretorio_destino)