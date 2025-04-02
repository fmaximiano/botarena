import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import os

def limpar_texto(texto):
    if isinstance(texto, str):
        return texto.replace('\n', ' ').replace(';', '.').strip()
    return texto

def extrair_dados_servico(url, i):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    dados = {}

    dados['id_servico'] = url.split("/")[-1]

    titulo = soup.find('span', {'class': 'field--name-title'})
    dados['titulo'] = limpar_texto(titulo.text.strip()) if titulo else 'Não informado'


    print(f"Scraping: {i} de 1225 serviços({(i/1225)*100}%)")


    # O que é?
    descricao = soup.find('div', {'class': 'field--name-field-descricao'})
    dados['descricao'] = limpar_texto(descricao.text.strip()) if descricao else 'Não informado'

    # Órgão Responsável
    orgao = soup.find('div', {'class': 'field--name-field-filiacao'})
    if orgao:
        orgao_nome = orgao.find('div', {'class': 'field__item'})
        dados['orgao_responsavel'] = limpar_texto(orgao_nome.text.strip()) if orgao_nome else 'Não informado'
    else:
        dados['orgao_responsavel'] = 'Não informado'

    # Etapas, custos e documentos
    etapas = []
    etapas_div = soup.find_all('div', {'class': 'paragraph--type--etapas-do-servico'})
    for etapa in etapas_div:
        etapa_info = {}
        etapa_numero = etapa.find('div', {'class': 'field--name-field-etapa-numero'})
        etapa_nome = etapa.find('div', {'class': 'field--name-field-etapa-nome'})
        etapa_descricao = etapa.find('div', {'class': 'field--name-field-etapa-descricao'})
        etapa_documentacao = etapa.find('div', {'class': 'field--name-field-etapa-documentacao'})
        etapa_valor = etapa.find('div', {'class': 'field--name-field-etapa-valor'})
        
        etapa_info['numero'] = limpar_texto(etapa_numero.text.strip()) if etapa_numero else ''
        etapa_info['nome'] = limpar_texto(etapa_nome.text.strip()) if etapa_nome else ''
        etapa_info['descricao'] = limpar_texto(etapa_descricao.text.strip()) if etapa_descricao else ''
        etapa_info['documentacao'] = limpar_texto(etapa_documentacao.text.strip()) if etapa_documentacao else ''
        etapa_info['valor'] = limpar_texto(etapa_valor.text.strip()) if etapa_valor else ''
        
        etapas.append(etapa_info)
    
    dados['etapas'] = etapas
    print("Etapas inseridas no serviço")

    # Quanto tempo leva?
    prazo = soup.find('div', {'class': 'field--name-field-quanto-tempo-leva'})
    dados['prazo'] = limpar_texto(prazo.text.strip()) if prazo else 'Não informado'

    # Quem pode utilizar este serviço?
    publico = soup.find('div', {'class': 'field--name-field-quem-pode-utilizar-servico'})
    dados['publico'] = limpar_texto(publico.text.strip()) if publico else 'Não informado'

    # Arquivos
    arquivos = []
    arquivos_div = soup.find_all('span', {'class': 'file--application-pdf'})
    for arquivo in arquivos_div:
        arquivo_info = {}
        arquivo_link = arquivo.find('a')
        arquivo_info['titulo'] = limpar_texto(arquivo_link.text.strip()) if arquivo_link else ''
        arquivo_info['link'] = arquivo_link['href'] if arquivo_link else ''
        arquivos.append(arquivo_info)
    
    dados['arquivos'] = arquivos

    # Legislação
    legislacao = soup.find('div', {'class': 'field--name-field-legislacao'})
    dados['legislacao'] = limpar_texto(legislacao.text.strip()) if legislacao else 'Não informado'

    # Dúvidas frequentes
    faq = soup.find('div', {'class': 'field--name-field-duvidas-frequentes'})
    dados['faq'] = limpar_texto(faq.text.strip()) if faq else 'Não informado'

    # Outras informações
    observacoes = soup.find('div', {'class': 'field--name-field-outras-informacoes'})
    dados['observacoes'] = limpar_texto(observacoes.text.strip()) if observacoes else 'Não informado'

    return dados

""" # Função para extrair unidades de uma página específica
def extrair_dados_unidades(soup):
    unidades = []
    unidades_table = soup.find('table', {'class': 'table-hover'})
    if unidades_table:
        rows = unidades_table.find_all('tr')[1:]  # Ignora o cabeçalho
        for row in rows:
            cols = row.find_all('td')
            municipio = limpar_texto(cols[0].text.strip()) if cols[0] else ''
            unidade = limpar_texto(cols[1].text.strip()) if cols[1] else ''
            unidades.append({'municipio': municipio, 'unidade': unidade})
    return unidades

# Função para iterar por todas as páginas e coletar todas as unidades
def extrair_todas_unidades(url_base, max_workers=10):
    unidades_totais = []
    pagina = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while True:
            url = f"{url_base}?page={pagina}"
            futures.append(executor.submit(fetch_unidades_page, url))
            pagina += 1

            # Checa a última página sem novas unidades
            if not fetch_unidades_page(url):
                break

        for future in as_completed(futures):
            unidades = future.result()
            if unidades:
                unidades_totais.extend(unidades)

    return unidades_totais

# Função auxiliar para requisição das páginas de unidades
def fetch_unidades_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  # Força a codificação correta
    soup = BeautifulSoup(response.text, 'html.parser')
    return extrair_dados_unidades(soup) """


# Função para ler a última URL processada
def ler_ultima_url_processada():
    try:
        with open('progresso.txt', 'r') as file:
            return file.readline().strip()
    except FileNotFoundError:
        return None

# Função para salvar a última URL processada
def salvar_ultima_url_processada(url):
    with open('progresso.txt', 'w') as file:
        file.write(url)

# Função principal para coletar e salvar todos os serviços em JSON
def coletar_e_salvar_servicos(urls):

    ultima_url = ler_ultima_url_processada()
    iniciar_processamento = False if ultima_url else True

    # Abertura do arquivo JSON para gravação incremental
    json_file_path = 'servicos.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            servicos = json.load(json_file)
    else:
        servicos = {}


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    i=1

    for url in urls:
        if not iniciar_processamento:
            if url == ultima_url:
                iniciar_processamento = True
            continue

        dados_servico = extrair_dados_servico(url, i)
        # unidades_totais = extrair_todas_unidades(url)

        # dados_servico['unidades'] = unidades_totais  # Adiciona as unidades ao serviço
        # print("Unidades inseridas no serviço")

        # Usa o ID do serviço como chave no dicionário
        servico_id = dados_servico['id_servico']
        servicos[servico_id] = dados_servico

        i+=1

        # Grava todos os serviços em um único arquivo JSON
        with open('servicos.json', 'w', encoding='utf-8') as json_file:
            json.dump(servicos, json_file, ensure_ascii=False, indent=4)

        salvar_ultima_url_processada(url)

# Carregar URLs da planilha Excel
excel_file_path = 'urls_srvs.xlsx'
coluna_urls = 'URL'
df = pd.read_excel(excel_file_path)
urls = df[coluna_urls].dropna().tolist() 

coletar_e_salvar_servicos(urls)
