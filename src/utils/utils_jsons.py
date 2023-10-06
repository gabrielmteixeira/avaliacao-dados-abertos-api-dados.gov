import json
import re
import os
from datetime import datetime


def processa_metadados(conjunto_de_dados: dict):
  recursos = conjunto_de_dados.get('resources')
  presenca_tokens = True
  tokens = []
  presenca_url_arquivo_metadados_anexos = False
  urls_arquivos_metadados_anexos = []
  titulo = conjunto_de_dados['title']
  email_responsavel = conjunto_de_dados['conjuntoDadosEdicao']['emailResponsavel']
  data_publicacao = conjunto_de_dados['metadata_created']
  data_ultima_modificacao = conjunto_de_dados['metadata_modified']

  if recursos:
    for recurso in recursos:
      url_recurso = recurso.get('url')
      if url_recurso:
        presenca_url_arquivo_metadados_anexos = True
        urls_arquivos_metadados_anexos.append(url_recurso)

  if email_responsavel == '':
    email_responsavel = []

  if presenca_url_arquivo_metadados_anexos:
    tokens.append('URI')
  if titulo:
    tokens.append('titulo')
  if email_responsavel:
    tokens.append('autor')
  if data_publicacao:
    tokens.append('data')
  if data_ultima_modificacao:
    tokens.append('ultima atualizacao')

  metadados = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens,
    'presencaURLsArquivosMetadadosAnexos' : presenca_url_arquivo_metadados_anexos,
    'URLsArquivosMetadadosAnexos' : urls_arquivos_metadados_anexos,
    'titulo' : titulo,
    'emails' : email_responsavel,
    'dataPublicacao' : data_publicacao,
    'dataUltimaModificacao' : data_ultima_modificacao
  }

  return metadados


def processa_licenca(conjunto_de_dados: dict):
  presenca_tokens = False
  licencas = conjunto_de_dados['conjuntoDadosForm']['licenca']
  tokens = []

  if licencas:
    presenca_tokens = True
    tokens = ['licenca']

  licenca = {
    'presencaTokens' : presenca_tokens,
    'licencas' : licencas,
    'tokens' : tokens
  }

  return licenca


def processa_procedencia_dados(conjunto_de_dados: dict):
  presenca_tokens = False
  tokens = []
  organizacao_responsavel = conjunto_de_dados['conjuntoDadosEdicao']['responsavel']

  if organizacao_responsavel:
    presenca_tokens = True
    tokens.append('responsavel')

  procedencia_dados = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens,
    'organizacaoResponsavel' : organizacao_responsavel
  }

  return procedencia_dados


def processa_qualidade_dados(conjunto_de_dados: dict):
  presenca_tokens = False
  tokens = []
  existe_avalicao = conjunto_de_dados.get('avaliacaoDTO')

  if existe_avalicao:
    presenca_tokens = True
    tokens = ['metrica']

  qualidade_dados = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens
  }

  return qualidade_dados


def processa_versionamento_dados(conjunto_de_dados: dict):
  presenca_tokens = False
  tokens = []
  data_ultima_modificacado = conjunto_de_dados['metadata_modified']

  if data_ultima_modificacado:
    presenca_tokens = True
    tokens = ['ultima atualizacao']

  versionamento_dados = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens,
    'dataUltimaModificacao' : data_ultima_modificacado
  }

  return versionamento_dados


def processa_feedback(conjunto_de_dados: dict):
  presenca_tokens = True
  tokens = ['fale com']
  email = conjunto_de_dados['conjuntoDadosEdicao']['emailResponsavel']

  if email == '':
    email = []
    presenca_tokens = False
    tokens = []

  feedback = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens,
    'emails' : email
  }

  return feedback


def processa_atributo_download(conjunto_de_dados: dict):
  recursos = conjunto_de_dados.get('resources')
  urls_volume_dados = []
  presenca_tokens_urls_dados_atualizados = False
  tokens_urls_dados_atualizados = []
  extensoes_download_massivo = []

  if recursos:
    for recurso in recursos:
      url_recurso = recurso.get('url')
      if url_recurso: 
        formatos_recurso = recurso.get('format').split('+')
        for formato in formatos_recurso:
          extensao = (f".{formato}").lower()
          if extensao in url_recurso and extensao in ['.zip', '.tar', '.rar', '.gz', '7z']:
            urls_volume_dados.append(url_recurso)
            if extensoes_download_massivo not in extensoes_download_massivo:
              extensoes_download_massivo.append(extensao)

  regex_tokens = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                                        r'(data|atualiza[cç][aã]o|[uú]ltima|frequ[eê]ncia|criado' \
                                        r'|cria[cç][aã]o|atualizado|cobertura|temporal|validade)' \
                                        r'(?:[\s.,;:!?_\'\"/]+|\b)'
  conjunto_de_dados_string = json.dumps(conjunto_de_dados)
  tokens_encontrados_urls_dados_atualizados = re.findall(regex_tokens, conjunto_de_dados_string, re.IGNORECASE)
  tokens_urls_dados_atualizados.extend(set(tokens_encontrados_urls_dados_atualizados))
  if tokens_urls_dados_atualizados:
    presenca_tokens_urls_dados_atualizados = True

  download = {
    'extensoesUrlsVolumeDados' : bool(extensoes_download_massivo),
    'urlsVolumeDados' : urls_volume_dados,
    'presencaTokensUrlsDadosAtualizados' : presenca_tokens_urls_dados_atualizados,
    'tokensUrlsDadosAtualizados' : tokens_urls_dados_atualizados,
    'extensoesDownloadMassivo' : extensoes_download_massivo
  }

  return download

def processa_atributo_apis(conjunto_de_dados: dict):
  recursos = conjunto_de_dados.get('resources')
  presenca_tokens_pagina_api = False
  tokens_pagina_api = []
  presenca_doc_api = False
  url_doc_api = []
  presenca_tokens_urls_doc = False

  regex_tokens_pagina_api = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                            r'(API|documenta[cç][aã]o|documenta[cç][aã]o da API|manual|descri[cç][aã]o' \
                            r'|par[aâ]metros|especifica[cç][aã]o|webservice|REST|RESTful|consumo' \
                            r'|retorno|resultados|m[eé]todo|GET|URL|URI|cabe[cç]alhos|headers)' \
                            r'(?:[\s.,;:!?_\'\"/]+|\b)'
  regex_tokens_doc_api = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                            r'(API|documenta[cç][aã]o|swagger|docs|io-docs|openApis)' \
                            r'(?:[\s.,;:!?_\'\"/]+|\b)'
  for recurso in recursos:
    formato_recurso = recurso.get('format')
    formato_recurso_string = json.dumps(formato_recurso)
    recurso_string = json.dumps(recurso)
    tokens_pagina_api_formato_recurso = re.findall(regex_tokens_pagina_api, formato_recurso_string, re.IGNORECASE)
    tokens_doc_api_formato_recurso = re.findall(regex_tokens_doc_api, formato_recurso_string, re.IGNORECASE)
    if tokens_pagina_api_formato_recurso or tokens_doc_api_formato_recurso:
      tokens_encontrados_pagina_api = re.findall(regex_tokens_pagina_api, recurso_string, re.IGNORECASE)
      tokens_encontrados_doc_api = re.findall(regex_tokens_doc_api, recurso_string, re.IGNORECASE)
      if tokens_encontrados_pagina_api:
        presenca_tokens_pagina_api = True
        tokens_pagina_api.extend(tokens_encontrados_pagina_api)
        presenca_doc_api = True
        url_recurso = recurso.get('url')
        url_doc_api.append(url_recurso)
      if tokens_encontrados_doc_api:
        presenca_tokens_urls_doc = True
  tokens_pagina_api = list(set(tokens_pagina_api))
    

  apis = {
    'presencaTokensPaginaAPI' : presenca_tokens_pagina_api,
    'tokensPaginaAPI' : tokens_pagina_api,
    'presencaDocAPI' : presenca_doc_api,
    'URLDocAPI' : url_doc_api,
    'presencaTokensURLsDoc' : presenca_tokens_urls_doc
  }

  return apis

def processa_garantir_acesso_aos_dados(conjunto_de_dados: dict):
  garantir_acesso_aos_dados = {
    'download' : processa_atributo_download(conjunto_de_dados),
    'APIs' : processa_atributo_apis(conjunto_de_dados)
  }

  return garantir_acesso_aos_dados


def processa_identificadores_dados(conjunto_de_dados: dict):
  recursos = conjunto_de_dados.get('resources')
  urls_subdominios_adm_separados_principal = []
  tokens_url = []
  formatos_dados = []
  urls_com_formato_dados = []

  if recursos:
    for recurso in recursos:
      url_recurso = recurso.get('url')
      if url_recurso: 
        urls_subdominios_adm_separados_principal.append(url_recurso)
        formatos_recurso = recurso.get('format').split('+')
        for formato in formatos_recurso:
          extensao = (f".{formato}").lower()
          if extensao not in formatos_dados:
            formatos_dados.append(extensao)
          if extensao in url_recurso:
            urls_com_formato_dados.append(url_recurso)
            if extensao not in tokens_url:
              tokens_url.append(extensao)

  identificadores_dados = {
    'presencaDeURLsPersistentes' : {
      'URLsSubdominiosAdmSeparadosPrincipal' : urls_subdominios_adm_separados_principal,
      'indicativosURLsConjDados' : {
        'presencaTokensURL' : bool(tokens_url),
        'tokensURL' : tokens_url,
        'presencaFormatoDados' : bool(formatos_dados),
        'formatosDados' : formatos_dados,
        'urlsComFormatoDados' : urls_com_formato_dados
      }
    }
  }

  return identificadores_dados


def processa_formatos_de_dados(conjunto_de_dados: dict):
  recursos = conjunto_de_dados.get('resources')
  presencaTokens = False
  tokens = []
  if recursos:
    for recurso in recursos:
      if 'format' in recurso:
        presencaTokens = True
        tokens = 'formato'

  formatos_de_dados = {
    'presencaTokens' : presencaTokens,
    'tokens' : tokens
  }

  return formatos_de_dados


def processa_preservacao_dos_dados(conjunto_de_dados: dict):
  presenca_tokens = False
  tokens = []

  regex_tokens = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                  r'(Manuten[cç][aã]o|Breve|arquivado|arquivamento|c[oó]pia' \
                  r'|substitui[cç][aã]o|substitu[ií]do|removido|remo[cç][aã]o)' \
                  r'(?:[\s.,;:!?_\'\"/]+|\b)'
  conjunto_de_dados_string = json.dumps(conjunto_de_dados)
  tokens_encontrados = re.findall(regex_tokens, conjunto_de_dados_string, re.IGNORECASE)
  tokens.extend(set(tokens_encontrados))
  if tokens:
    presenca_tokens = True

  preservacao_dos_dados = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens
  }

  return preservacao_dos_dados


def processa_republicacao_dos_dados(conjunto_de_dados: dict):
  presenca_tokens = False
  tokens = []
  publicacao_original = ''
  link_publicacao_original = ''

  regex_tokens = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                  r'(fonte original|proced[eê]ncia|cita[cç][aã]o|publica[cç][aã]o original|licen[cç]a|publicador)' \
                  r'(?:[\s.,;:!?_\'\"/]+|\b)'
  conjunto_de_dados_string = json.dumps(conjunto_de_dados)
  tokens_encontrados = re.findall(regex_tokens, conjunto_de_dados_string, re.IGNORECASE)
  tokens.extend(set(tokens_encontrados))
  if tokens:
    presenca_tokens = True

  republicacao_de_dados = {
    'presencaTokens' : presenca_tokens,
    'tokens' : tokens,
    'publicacaoOriginal' : publicacao_original,
    'linkPublicacaoOriginal' : link_publicacao_original
  }

  return republicacao_de_dados


def processa_regras(conjunto_de_dados: dict):
  regras = {
    'informacoesSobreMetadados' : processa_metadados(conjunto_de_dados),
    'informacoesSobreLicenca' : processa_licenca(conjunto_de_dados),
    'informacoesSobreProcedenciaDados' : processa_procedencia_dados(conjunto_de_dados),
    'informacoesSobreQualidadeDados' : processa_qualidade_dados(conjunto_de_dados),
    'informacoesSobreVersionamentoDados' : processa_versionamento_dados(conjunto_de_dados),
    'informacoesSobreFeedback' : processa_feedback(conjunto_de_dados),
    'informacoesSobreGarantirAcessoAosDados' : processa_garantir_acesso_aos_dados(conjunto_de_dados),
    'informacoesSobreIdentificadoresDeDados' : processa_identificadores_dados(conjunto_de_dados),
    'informacoesSobreFormatosDeDados' : processa_formatos_de_dados(conjunto_de_dados),
    'informacoesSobrePreservacaoDosDados' : processa_preservacao_dos_dados(conjunto_de_dados),
    'informacoesSobreRepublicacaoDosDados' : processa_republicacao_dos_dados(conjunto_de_dados)
  }

  return regras


def processa_completos(regras: dict):
  completos = {
    'regras' : {
      'informacoesSobreMetadados' : regras['informacoesSobreMetadados'],
      'informacoesSobreLicenca' : regras['informacoesSobreLicenca'],
      'informacoesSobreProcedenciaDados' : regras['informacoesSobreProcedenciaDados'],
      'informacoesSobreQualidadeDados' : regras['informacoesSobreQualidadeDados'],
      'informacoesSobreVersionamentoDados' : regras['informacoesSobreVersionamentoDados'],
      'informacoesSobreFeedback' : regras['informacoesSobreFeedback']
    }
  }

  return completos


def processa_primarios(regras: dict):
  primarios = {
    'regras' : {
      'informacoesSobreProcedenciaDados' : regras['informacoesSobreProcedenciaDados'],
      'informacoesSobreQualidadeDados' : regras['informacoesSobreQualidadeDados'],
      'informacoesSobreFeedback' : regras['informacoesSobreFeedback']
    }
  }

  return primarios


def processa_atuais(regras: dict):
  atuais = {
    'regras' : {
      'informacoesSobreGarantirAcessoAosDados' : regras['informacoesSobreGarantirAcessoAosDados']
    }
  }

  return atuais


def processa_facilidade_acesso_fisico_ou_eletronico(regras: dict):
  facilidade_acesso_fisico_ou_eletronico = {
    'regras' : {
      'informacoesSobreGarantirAcessoAosDados' : regras['informacoesSobreGarantirAcessoAosDados']
    }
  }

  return facilidade_acesso_fisico_ou_eletronico


def processa_processaveis_por_marquina(regras: dict):
  processaveis_por_marquina = {
    'regras' : {
      'informacoesSobreIdentificadoresDeDados' : regras['informacoesSobreIdentificadoresDeDados'],
      'informacoesSobreFormatosDeDados' : regras['informacoesSobreFormatosDeDados']
    }
  }

  return processaveis_por_marquina


def processa_nao_descriminatorio(regras: dict):
  nao_descriminatorio = {
    'regras' : {
      'informacoesSobreGarantirAcessoAosDados' : regras['informacoesSobreGarantirAcessoAosDados'],
      'informacoesSobrePreservacaoDosDados' : regras['informacoesSobrePreservacaoDosDados'],
      'informacoesSobreLicenca' : regras['informacoesSobreLicenca'],
      'informacoesSobreMetadados' : regras['informacoesSobreMetadados'],
      'informacoesSobreFeedback' : regras['informacoesSobreFeedback']
    }
  }

  return nao_descriminatorio


def processa_formatos_de_propriedade_comum_ou_aberto(regras: dict):
  formatos_de_propriedade_comum_ou_aberto = {
    'regras' : {
      'informacoesSobreFormatosDeDados' : regras['informacoesSobreFormatosDeDados'],
      'informacoesSobreLicenca' : regras['informacoesSobreLicenca'],
      'informacoesSobreGarantirAcessoAosDados' : regras['informacoesSobreGarantirAcessoAosDados']
      
    }
  }

  return formatos_de_propriedade_comum_ou_aberto


def processa_licencas_livres(regras: dict):
  licencas_livres = {
    'regras' : {
      'informacoesSobreRepublicacaoDosDados' : regras['informacoesSobreRepublicacaoDosDados'],
      'informacoesSobreLicenca' : regras['informacoesSobreLicenca']
    }
  }

  return licencas_livres


def processa_permanencia(regras: dict):
  permanencia = {
    'regras' : {
      'informacoesSobreIdentificadoresDeDados' : regras['informacoesSobreIdentificadoresDeDados'],
      'informacoesSobrePreservacaoDosDados' : regras['informacoesSobrePreservacaoDosDados'],
      'informacoesSobreGarantirAcessoAosDados' : regras['informacoesSobreGarantirAcessoAosDados'],
      'informacoesSobreRepublicacaoDosDados' : regras['informacoesSobreRepublicacaoDosDados'],
      'informacoesSobreVersionamentoDados' : regras['informacoesSobreVersionamentoDados']
    }
  }

  return permanencia


def processa_custos_de_utilizacao(regras: dict):
  custos_de_utilizacao = {
    'regras' : {
      'informacoesSobreGarantirAcessoAosDados' : regras['informacoesSobreGarantirAcessoAosDados'],
      'informacoesSobreFeedback' : regras['informacoesSobreFeedback'],
    }
  }

  return custos_de_utilizacao


def processa_principios_governanca(conjunto_de_dados: dict):
  regras = processa_regras(conjunto_de_dados)

  principios_governanca = {
    'completos' : processa_completos(regras),
    'primarios' : processa_primarios(regras),
    'atuais' : processa_atuais(regras),
    'facilidadeAcessoFisicoOuEletronico' : processa_facilidade_acesso_fisico_ou_eletronico(regras),
    'processaveisPorMaquina' : processa_processaveis_por_marquina(regras),
    'naoDiscriminatorio' : processa_nao_descriminatorio(regras),
    'formatosDePropriedadeComumOuAberto' : processa_formatos_de_propriedade_comum_ou_aberto(regras),
    'licencasLivres' : processa_licencas_livres(regras),
    'permanencia' : processa_permanencia(regras),
    'custosDeUtilizacao' : processa_custos_de_utilizacao(regras)
  }
  
  return principios_governanca


def processa_conjunto_de_dados(caminho_conjunto_de_dados: str):
  conjunto_de_dados = {}

  try:
    with open(caminho_conjunto_de_dados, 'r', encoding='utf-8') as arquivo_conjunto_de_dados:
      conjunto_de_dados = json.load(arquivo_conjunto_de_dados)
  except json.JSONDecodeError as e:
    print(f"Erro no parsing do JSON no arquivo {caminho_conjunto_de_dados}: {e}")
  try:
    with open('modelo_saida.json', 'r', encoding='utf-8') as arquivo_modelo_saida:
      saida_json = json.load(arquivo_modelo_saida)
  except json.JSONDecodeError as e:
    print(f"Erro no parsing do JSON no arquivo modelo_saida.json: {e}")

  principios_de_governanca = processa_principios_governanca(conjunto_de_dados)

  saida_json = {
    'urlPaginaPrincipal' : 'https://dados.gov.br/dados/conjuntos-dados/{}'.format(conjunto_de_dados['name']),
    'dataAvaliacao' : datetime.now().strftime('%d/%m/%Y'),
    'presencaTokensComuns' : None,
    'tokensComuns' : [],
    'presencaTokensEspecificosDadosAbertos' : None,
    'tokensEspecificosDadosAbertos' : [],
    'presencaURLsDownloadDados' : principios_de_governanca['completos']['regras']['informacoesSobreMetadados']['presencaURLsArquivosMetadadosAnexos'],
    'possivelFalsoPositivo' : False,
    'possivelAPI' : False,
    'principiosGovernanca' : principios_de_governanca
  }

  return saida_json


def gera_saidas_json(diretorio_dados: str, diretorio_saidas_json: str):
  os.makedirs(diretorio_saidas_json, exist_ok=True)

  for nome_arquivo in os.listdir(diretorio_dados):
    caminho_arquivo = os.path.join(diretorio_dados, nome_arquivo)
    
    if os.path.isfile(caminho_arquivo) and caminho_arquivo.endswith('.json'):
      saida_json = processa_conjunto_de_dados(caminho_arquivo)

      caminho_saida = os.path.join(diretorio_saidas_json, nome_arquivo)
      with open(caminho_saida, 'w', encoding='utf-8') as arquivo_saida:
        arquivo_saida.write(json.dumps(saida_json, ensure_ascii=False, indent=2))