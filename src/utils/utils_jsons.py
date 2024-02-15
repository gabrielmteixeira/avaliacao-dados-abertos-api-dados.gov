import json
import re
import os
from datetime import datetime


def reduz_descricao(texto_bruto_descricao: str | None) -> str  | None:
  padrao_regex = re.compile(r'^(.*?)(?:,|\.(?!.*?,)|\n(?!.*[,.]))')
  match = padrao_regex.match(texto_bruto_descricao)
  if match:
    descricao_reduzida = match.group(1)
    return descricao_reduzida
  else:
    return texto_bruto_descricao


def remove_alerta_padrao_da_api(descricao: str | None) -> str  | None:
  # a API do dados.gov insere, em alguns campos de descrição, um alerta padrão de formato. Tal alerta não é interessante para o projeto
  match = re.search(r'(.*?) \* \* \*', descricao)
  if match:
    descricao_sem_alerta = match.group(1)
    return descricao_sem_alerta
  else:
    return descricao


def processa_atributo_descricao(texto_bruto_descricao: str | None) -> str | None:
  descricao_reduzida = None
  if texto_bruto_descricao:
    descricao_sem_alerta = remove_alerta_padrao_da_api(texto_bruto_descricao)
    descricao_limpa = descricao_sem_alerta.strip().replace("\n", "").replace("\r", "")
    descricao_limpa = re.sub(r'\s+', ' ', descricao_limpa) # Substituí ocorrências de múltiplos espaços susequentes por um único espaço.
    descricao_reduzida = reduz_descricao(descricao_limpa)
  return descricao_reduzida


def processa_metadados(conjunto_de_dados: dict):
  recursos = conjunto_de_dados.get('resources')
  presenca_tokens = True
  tokens = []
  presenca_url_arquivo_metadados_anexos = False
  urls_arquivos_metadados_anexos = []
  titulo = conjunto_de_dados['title']
  descricao = processa_atributo_descricao(conjunto_de_dados.get('notes'))
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
    'descricao' : descricao,
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
    if isinstance(licencas, list) or licencas != "notspecified":
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
          formato = str(formato).lower()
          if formato in ['zip', 'tar', 'rar', 'gz', '7z']:
            urls_volume_dados.append(url_recurso)
            if formato not in extensoes_download_massivo:
              extensoes_download_massivo.append(formato)

  regex_tokens = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                                        r'(data|atualiza[cç][aã]o|[uú]ltima|frequ[eê]ncia|criado' \
                                        r'|cria[cç][aã]o|atualizado|cobertura|temporal|validade)' \
                                        r'(?:[\s.,;:!?_\'\"/]+|\b)'
  conjunto_de_dados_string = json.dumps(conjunto_de_dados, ensure_ascii=False, indent=2)
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
    formato_recurso_string = json.dumps(formato_recurso, ensure_ascii=False, indent=2)
    recurso_string = json.dumps(recurso, ensure_ascii=False, indent=2)
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
          formato = str(formato).lower()

          regex_formato = r'(?:[\s.,;:!?_\'\"/]+|\b)({})(?:[\s.,;:!?_\'\"/]+|\b)'.format(formato)
          url_com_formato = re.search(regex_formato, url_recurso, re.IGNORECASE)
          if formato not in formatos_dados:
            formatos_dados.append(formato)
          if url_com_formato:
            urls_com_formato_dados.append(url_recurso)
            if formato not in tokens_url:
              tokens_url.append(formato)

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
  conjunto_de_dados_string = json.dumps(conjunto_de_dados, ensure_ascii=False, indent=2)
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
  conjunto_de_dados_string = json.dumps(conjunto_de_dados, ensure_ascii=False, indent=2)
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


def colhe_tokens_comuns(conjunto_de_dados: dict):
  tokens = []
  regex_tokens = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                  r'(informa[cç][oõ]es|adicionais|dados' \
                  r'|crit[eé]rios|conjunto|t[ií]tulo|palavra|palavras|chave' \
                  r'|data|publica[cç][aã]o|cria[cç][aã]o|atualiza[cç][aã]o|contato' \
                  r'|refer[eê]ncia|refer[eê]ncias|respons[aá]vel|respons[aá]veis|idioma' \
                  r'|fonte|fontes|vers[aã]o|tema|metadado' \
                  r'|estrutural|estruturais|campo|campos|tipo' \
                  r'|[uú]ltima|modifica[cç][aã]o|geogr[aá]fica|temporal|escopo|geopol[ií]tico|autor|autores|criado' \
                  r'|entidade|ponto|per[ií]odo|temas|categorias|formatos|m[ií]dia|licen[cç]a' \
                  r'|licen[cç]as|conte[uú]do|recursos|termos|restri[cç][oõ]es|restri[cç][aã]o|criador|criadores|[aá]rea' \
                  r'|editor|editora|editores|editoras|qualidade|disponibilidade|atual|hist[oó]rico|obsoleto|mudan[cç]as' \
                  r'|modifica[cç][oõ]es|[uú]ltimas|feedback|formul[aá]rio|rank|ranqueamento|esperado|avalia[cç][aã]o|avalia[cç][oõ]es|bot[aã]o' \
                  r'|bot[oõ]es|coment[aá]rio|questionamento|classifica|classifica[cç][aã]o|corre[cç][aã]o|revis[aã]o|compartilhar|compartilhe|informe|fale' \
                  r'|entre|sugest[oõ]es|original|proced[eê]ncia|cita[cç][aã]o|publicador|atualizado|validade|documenta[cç][aã]o' \
                  r'|manual|par[aâ]metros|especifica[cç][aã]o|webservice|REST|RESTful|consumo|retorno|resultados|m[eé]todo|GET' \
                  r'|URL|cabe[cç]alhos|headers|linguagem|padr[aã]o|exportar|explorar' \
                  r'|estrutura|escolher|manuten[cç][aã]o|breve|arquivado|arquivamento|c[oó]pia|substitui[cç][aã]o|substitu[ií]do|removido' \
                  r'|remo[cç][aã]o|tempo|adotado|dispon[ií]vel)' \
                  r'(?:[\s.,;:!?_\'\"/]+|\b)'

  conjunto_de_dados_string = json.dumps(conjunto_de_dados, ensure_ascii=False, indent=2)
  tokens_encontrados = re.findall(regex_tokens, conjunto_de_dados_string, re.IGNORECASE)
  tokens.extend(set(tokens_encontrados))

  return tokens

def colhe_tokens_especificos_dados_abertos(conjunto_de_dados: dict):
  tokens = []
  regex_tokens = r'(?:[\s.,;:!?_\'\"/]+|\b)' \
                  r'(metadados|dicion[aá]rio|dicion[aá]rios|dicion[aá]rio dados|taxonomia|crit[eé]rio|crit[eé]rios|descri[cç][aã]o conjunto dados' \
                  r'|URI|frequ[eê]ncia|granularidade|mantenedor|mantenedores|formato data|metadado estrutural|metadados estruturais' \
                  r'|tipo dados|m[eé]trica|[uú]ltima modifica[cç][aã]o|[uú]ltima atualiza[cç][aã]o|descri[cç][aã]o|cobertura geogr[aá]fica' \
                  r'|cobertura temporal|escopo geopol[ií]tico|entidade respons[aá]vel|ponto contato|per[ií]odo temporal|data [uú]ltima modifica[cç][aã]o' \
                  r'|formato|formato m[ií]dia|identificador|rela[cç][aã]o|tipo conte[uú]do|qualidade dados|integridade|integridade dados' \
                  r'|disponibilidade dados|hist[oó]rico mudanças|hist[oó]rico modifica[cç][oõ]es|hist[oó]rico modifica[cç][aã]o|[uú]ltimas modifica[cç][oõ]es' \
                  r'|periodicidade|API|APIs|documenta[cç][aã]o API|csv|xml|json|rdf|dados|estruturados|dados abertos)' \
                  r'(?:[\s.,;:!?_\'\"/]+|\b)'

  conjunto_de_dados_string = json.dumps(conjunto_de_dados, ensure_ascii=False, indent=2)
  tokens_encontrados = re.findall(regex_tokens, conjunto_de_dados_string, re.IGNORECASE)
  tokens.extend(set(tokens_encontrados))

  return tokens

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

  tokens_comuns = colhe_tokens_comuns(conjunto_de_dados)
  tokens_especificos_dados_abertos = colhe_tokens_especificos_dados_abertos(conjunto_de_dados)

  principios_de_governanca = processa_principios_governanca(conjunto_de_dados)
  possivel_api = principios_de_governanca['atuais']['regras']['informacoesSobreGarantirAcessoAosDados']['APIs']['presencaTokensPaginaAPI']

  saida_json = {
    'urlPaginaPrincipal' : 'https://dados.gov.br/dados/conjuntos-dados/{}'.format(conjunto_de_dados['name']),
    'dataAvaliacao' : datetime.now().strftime('%d/%m/%Y'),
    'presencaTokensComuns' : bool(tokens_comuns),
    'tokensComuns' : tokens_comuns,
    'presencaTokensEspecificosDadosAbertos' : bool(tokens_especificos_dados_abertos),
    'tokensEspecificosDadosAbertos' : tokens_especificos_dados_abertos,
    'presencaURLsDownloadDados' : principios_de_governanca['completos']['regras']['informacoesSobreMetadados']['presencaURLsArquivosMetadadosAnexos'],
    'possivelFalsoPositivo' : False,
    'possivelAPI' : possivel_api,
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