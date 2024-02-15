import html
import os
import pandas as pd 

def converter(texto: str):
    entidades_html = []
    for char in texto:
        ponto_codigo = ord(char)
        nome_entidade = html.entities.codepoint2name.get(ponto_codigo)
        if nome_entidade:
            entidades_html.append('&{};'.format(nome_entidade))
        else:
            entidades_html.append(char)

    palavra_convertida = ''.join(entidades_html)
    return palavra_convertida

diretorio_saida_csv = "saida_csv"
caminho_csv_entrada = os.path.join(diretorio_saida_csv, 'resultado_bruto_dados.gov.csv')
caminho_csv_saida = os.path.join(diretorio_saida_csv, 'resultado_dados.gov.csv')

df = pd.read_csv(caminho_csv_entrada, na_filter=False, keep_default_na=False)
title = []
description = []

for index, row in df.iterrows():
    title.append(converter(row['title']))
    description.append(converter(row['description']))

df['title'] = pd.Series(title)
df['description'] = pd.Series(description)
df.to_csv(caminho_csv_saida, index=False)