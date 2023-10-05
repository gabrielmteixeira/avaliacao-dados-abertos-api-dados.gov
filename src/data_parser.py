import json
import os
import time
from utils.utils_jsons import gera_saidas_json
from utils.utils_csv import gera_csv_dwbp

inicio_cronometro = time.time()

diretorio_dados = 'conjuntos_de_dados'
diretorio_saidas_json = 'saidas_json'
diretorio_saida_csv = 'saida_csv'

gera_saidas_json(diretorio_dados, diretorio_saidas_json)
gera_csv_dwbp(diretorio_saidas_json, diretorio_saida_csv)

fim_cronometro = time.time()
tempo_execucao = fim_cronometro - inicio_cronometro
print(tempo_execucao)