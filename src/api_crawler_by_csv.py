import pandas as pd
from api_crawler import colhe_conjuntos_de_dados

def produz_arquivo_nomes_conjuntos_de_dados(arquivo_csv: str, arquivo_destino: str):
  df = pd.read_csv(arquivo_csv)
  with open(arquivo_destino, 'w', encoding='utf-8') as arquivo:
    for _, row in df.iterrows():
        nome_conjunto_de_dados = str(row['sublinks dados.gov']).split('/')[-1]
        arquivo.write(f'{nome_conjunto_de_dados}\n')
  

arquivo_csv = 'lista_portais.csv'
arquivo_nomes_conjuntos_de_dados = 'nomes_registros.txt'
diretorio_destino = 'conjuntos_de_dados'

produz_arquivo_nomes_conjuntos_de_dados(arquivo_csv, arquivo_nomes_conjuntos_de_dados)
colhe_conjuntos_de_dados(arquivo_nomes_conjuntos_de_dados, diretorio_destino)