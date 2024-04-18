# avaliacao-dados-abertos-api-dados.gov
Este repositório é destinado à ferramenta de avaliação da API do site dados.gov.br quanto ao cumprimento dos 10 princípios de governança de dados abertos, estipulados com base no documento de recomendações de Boas Práticas para Dados na Web (DWBP - https://www.w3.org/TR/dwbp/), para a pesquisa TIC Web Dados Abertos, do DCC/UFMG.

# passos para execução
- Projeto construído com Python3.10
- Instalar as bibliotecas essenciais para a execução do projeto, com o comando "pip install -r requirements.txt".
- No diretório "src", executar o crawler da api do portal "dados.gov", com o comando "python3.10 api_crawler.py"
Ao fim da execução do "api_crawler.py", terão sido criados: o arquivo "nomes_registros.txt", contendo o nome de todos os conjuntos de dados colhidos; O diretório "conjuntos_de_dados", que armazena todos os conjuntos de dados colhidos; o arquivo "log_conjuntos_json_improprio.txt", que registra o nome de todos os conjuntos de dados cujo JSON recebido da API do dados.gov estava em formato impróprio para ser utilizado e, portanto, foram ignorados.
- No diretório "src", executar o script de processamento dos conjuntos de dados colhidos, "data_parser.py", com o comando "python3.10 data_parser.py". 
Ao fim da execução do "data_parser.py", terão sido criados: o diretório "saida_json", contendo todos os JSONs resultantes do processamento dos conjuntos de dados colhidos; o diretório "saida_csv", contento o CSV "resultado_bruto_dados.gov.csv", que apresenta uma visão geral da coleta de conjuntos de dados realizados. Vale ressaltar que, nessa etapa, o CSV "resultado_bruto_dados.gov.csv" ainda não recebeu tratamento quanto à presença de caracteres especiais.
- No diretório "src", executar o script "text_to_html_csv_parser.py". Ele irá tratar os dados presentes no CSV "resultado_bruto_dados.gov.csv" com relação à presença de caracteres especiais, substituindo-os pelo correspondente encoding HTML. O resultado desse processamento é armazenado em "resultado_dados.gov.csv".
- "resultado_dados.gov.csv" representa a saída final da aplicação.
