import json
import os
import pandas as pd
from datetime import datetime
from utils.utils_jsons import colhe_tokens_especificos_dados_abertos


def verifica_metadata(saida_json: dict):
  provide_metadata = 0
  provide_descriptive_metadata = 0
  informacoes_sobre_metadados = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreMetadados']

  presenca_tokens = informacoes_sobre_metadados['presencaTokens']
  presenca_urls_arquivos_metadados_anexos = informacoes_sobre_metadados['presencaURLsArquivosMetadadosAnexos']
  
  if presenca_tokens and presenca_urls_arquivos_metadados_anexos:
    provide_metadata = 1
    
  if provide_metadata:
    possibilidade_contato = 0
    emails = informacoes_sobre_metadados['emails']
    if emails:
      for email in emails:
        if '@' in email:
          possibilidade_contato = 1

    titulo = 1 if informacoes_sobre_metadados['titulo'] else 0
    data_ultima_modificacao = 1 if informacoes_sobre_metadados['dataUltimaModificacao'] else 0
    data_publicacao = 1 if informacoes_sobre_metadados['dataPublicacao'] else 0

    agregador = [titulo, data_publicacao, possibilidade_contato, data_ultima_modificacao]
    soma_agregador = sum(agregador)
    if soma_agregador >= 2:
      provide_descriptive_metadata = 1
  
  return provide_metadata, provide_descriptive_metadata


def verifica_data_license_information(saida_json: dict):
  provide_data_license_information = 0
  informacoes_sobre_licenca = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreLicenca']
  presenca_tokens = informacoes_sobre_licenca['presencaTokens']

  licensas = True if informacoes_sobre_licenca['licencas'] else False
  if presenca_tokens and licensas:
    provide_data_license_information = 1
  
  return provide_data_license_information


def verifica_data_provenance_information(saida_json: dict):
  provide_data_provenance_information = 0
  informacoes_sobre_metadados = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreMetadados']
  informacoes_sobre_procedencia_dos_dados = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreProcedenciaDados']  

  presenca_tokens = informacoes_sobre_procedencia_dos_dados['presencaTokens']
  data_publicacao = True if informacoes_sobre_metadados['dataPublicacao'] else False
  responsavel = True if informacoes_sobre_procedencia_dos_dados['organizacaoResponsavel'] else False
  if presenca_tokens and (data_publicacao or responsavel):
    provide_data_provenance_information = 1 

  return provide_data_provenance_information


def verifica_version_indicator(saida_json: dict):
  provide_a_version_indicator = 0
  informacoes_sobre_versionamento_dados = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreVersionamentoDados']

  presenca_tokens = informacoes_sobre_versionamento_dados['presencaTokens']
  data_de_versao = True if informacoes_sobre_versionamento_dados['dataUltimaModificacao'] else False

  if presenca_tokens and data_de_versao:
    provide_a_version_indicator = 1  

  return provide_a_version_indicator


def verifica_feedback_from_data_consumers(saida_json: dict):
  gather_feedback_from_data_consumers = 0
  informacoes_sobre_feedback = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreFeedback']

  presenca_tokens = informacoes_sobre_feedback['presencaTokens']
  emails = True if informacoes_sobre_feedback['emails'] else False
  
  if presenca_tokens and emails:
    gather_feedback_from_data_consumers = 1
  
  return gather_feedback_from_data_consumers


def verifica_bulk_download(saida_json: dict):
  provide_bulk_download = 0
  informacoes_sobre_garantir_acesso_aos_dados = saida_json['principiosGovernanca']['atuais']['regras']['informacoesSobreGarantirAcessoAosDados']
  
  arquivos_download_massivo = informacoes_sobre_garantir_acesso_aos_dados['download']['extensoesUrlsVolumeDados']

  if arquivos_download_massivo:
    provide_bulk_download = 1

  return provide_bulk_download


def confere_data_atualizada(data: str):
  data_atualizada = False
  formato_data = '%d/%m/%Y %H:%M:%S'
  data_formatada = datetime.strptime(data, formato_data)
  ano_corrente = datetime.now().year
  
  if data_formatada.year == ano_corrente:
    data_atualizada = True

  return data_atualizada

def verifica_data_up_to_date(saida_json: dict):
  provide_data_up_to_date = 0
  informacoes_sobre_garantir_acesso_aos_dados = saida_json['principiosGovernanca']['atuais']['regras']['informacoesSobreGarantirAcessoAosDados']
  informacoes_sobre_metadados = saida_json['principiosGovernanca']['completos']['regras']['informacoesSobreMetadados']
  data_publicacao = informacoes_sobre_metadados['dataPublicacao']
  data_ultima_modificacao = informacoes_sobre_metadados['dataUltimaModificacao']
  data_publicacao_atualizada = False
  data_ultima_modificacao_atualizada = False

  presenca_tokens_urls_dados_atualizados = informacoes_sobre_garantir_acesso_aos_dados['download']['presencaTokensUrlsDadosAtualizados']

  if data_publicacao:
    data_publicacao_atualizada = confere_data_atualizada(data_publicacao)
  if data_ultima_modificacao:
    data_ultima_modificacao_atualizada = confere_data_atualizada(data_ultima_modificacao)
  data_atualizada = data_publicacao_atualizada or data_ultima_modificacao_atualizada

  if presenca_tokens_urls_dados_atualizados and data_atualizada:
    provide_data_up_to_date = 1

  return provide_data_up_to_date


def verifica_persistent_uris_as_identifiers_of_datasets(saida_json: dict):
  use_persistent_uris_as_identifiers_of_datasets = 0
  informacoes_sobre_identificadores_de_dados = saida_json['principiosGovernanca']['processaveisPorMaquina']['regras']['informacoesSobreIdentificadoresDeDados']
  
  urls_com_formato_dados = informacoes_sobre_identificadores_de_dados['presencaDeURLsPersistentes']['indicativosURLsConjDados']['urlsComFormatoDados']
  presenca_tokens = bool(colhe_tokens_especificos_dados_abertos({'urls' : urls_com_formato_dados}))
  url_dominio_diferente = False
  dominio_portal = 'dados.gov.br'
  
  for url in urls_com_formato_dados:
    if dominio_portal not in url:
      url_dominio_diferente = True
  if presenca_tokens and url_dominio_diferente:
    use_persistent_uris_as_identifiers_of_datasets = 1

  return use_persistent_uris_as_identifiers_of_datasets


def verifica_machine_readable_standardized_data_formats(saida_json: dict):
  use_machine_readable_standardized_data_formats = 0
  informacoes_sobre_formatos_de_dados = saida_json['principiosGovernanca']['processaveisPorMaquina']['regras']['informacoesSobreFormatosDeDados']
  informacoes_sobre_identificadores_de_dados = saida_json['principiosGovernanca']['processaveisPorMaquina']['regras']['informacoesSobreIdentificadoresDeDados']

  presenca_tokens = informacoes_sobre_formatos_de_dados['presencaTokens']
  urls_extensoes_legiveis = informacoes_sobre_identificadores_de_dados['presencaDeURLsPersistentes']['indicativosURLsConjDados']['presencaFormatoDados']

  if presenca_tokens and urls_extensoes_legiveis:
    use_machine_readable_standardized_data_formats = 1  

  return use_machine_readable_standardized_data_formats


def verifica_data_in_multiple_formats(saida_json: dict):
  provide_data_in_multiple_formats = 0
  informacoes_sobre_formatos_de_dados = saida_json['principiosGovernanca']['processaveisPorMaquina']['regras']['informacoesSobreFormatosDeDados']
  informacoes_sobre_identificadores_de_dados = saida_json['principiosGovernanca']['processaveisPorMaquina']['regras']['informacoesSobreIdentificadoresDeDados']

  presenca_tokens = informacoes_sobre_formatos_de_dados['presencaTokens']
  formatos_dados = informacoes_sobre_identificadores_de_dados['presencaDeURLsPersistentes']['indicativosURLsConjDados']['formatosDados']
  formatos_variados = True if len(formatos_dados) > 1 else False

  if presenca_tokens and formatos_variados:
    provide_data_in_multiple_formats = 1

  return provide_data_in_multiple_formats


def verifica_cite_the_original_publication(saida_json: dict):
  cite_the_original_publication = 0
  informacoes_sobre_republicacao_dos_dados = saida_json['principiosGovernanca']['licencasLivres']['regras']['informacoesSobreRepublicacaoDosDados']

  presenca_publicacao_original = informacoes_sobre_republicacao_dos_dados['publicacaoOriginal']

  if presenca_publicacao_original:
    cite_the_original_publication = 1  

  return cite_the_original_publication


def processa_saida_json(saida_json: dict, id_json: int):
  site = saida_json['urlPaginaPrincipal']
  data_avaliacao = saida_json['dataAvaliacao']
  provide_metadata, provide_descriptive_metadata = verifica_metadata(saida_json)

  boas_praticas_dados_web = {
    'idJson' : id_json,
    'site' : site,
    'data_avaliacao' : data_avaliacao,
    'possivel_falso_positivo' : saida_json['possivelFalsoPositivo'],
    'provide_metadata' : provide_metadata,
    'provide_descriptive_metadata' : provide_descriptive_metadata,
    'provide_data_license_information' : verifica_data_license_information(saida_json),
    'provide_data_provenance_information' : verifica_data_provenance_information(saida_json),
    'provide_a_version_indicator' : verifica_version_indicator(saida_json),
    'gather_feedback_from_data_consumers' : verifica_feedback_from_data_consumers(saida_json),
    'provide_bulk_download' : verifica_bulk_download(saida_json),
    'provide_data_up_to_date' : verifica_data_up_to_date(saida_json),
    'use_persistent_URIs_as_identifiers_of_datasets' : verifica_persistent_uris_as_identifiers_of_datasets(saida_json),
    'use_machine_readable_standardized_data_formats' : verifica_machine_readable_standardized_data_formats(saida_json),
    'provide_data_in_multiple_formats' : verifica_data_in_multiple_formats(saida_json),
    'cite_the_original_publication' : verifica_cite_the_original_publication(saida_json)
  }

  boas_praticas_dados_web = pd.DataFrame([boas_praticas_dados_web])
  
  return boas_praticas_dados_web


def gera_csv_dwbp(diretorio_saidas_json: str, diretorio_saida_csv: str):
  analise_boas_praticas = pd.DataFrame()

  for nome_arquivo in os.listdir(diretorio_saidas_json):
    caminho_arquivo_json = os.path.join(diretorio_saidas_json, nome_arquivo)
    id_json = int(nome_arquivo.split('.')[0])
    with open(caminho_arquivo_json, 'r', encoding='utf-8') as arquivo_json:
      saida_json = json.load(arquivo_json)
      nova_linha_analise_boas_praticas = processa_saida_json(saida_json, id_json)
      analise_boas_praticas = pd.concat([analise_boas_praticas, nova_linha_analise_boas_praticas], ignore_index=True)

  os.makedirs(diretorio_saida_csv, exist_ok=True)
  caminho_csv = os.path.join(diretorio_saida_csv, 'resultado.csv')
  analise_boas_praticas.to_csv(caminho_csv, index=False)
