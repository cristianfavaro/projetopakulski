import requests
from bs4 import BeautifulSoup as bs
import smtplib
import itertools
import pendulum



sextaf = False

def eh_sexta():
    today = pendulum.today()
    if today.day_of_week == 4: 
        return True
    else:
        return False


sextaf = eh_sexta()


if sextaf == True:
    #parte 1 - Buscar os relatórios
    import os
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())

    airtable_api = os.environ.get('AIRTABLE_KEY')
    gmail_acc = os.environ.get('G-MAIL_ACC')
    gmail_pass = os.environ.get('G-MAIL_KEY')


    airtable_api = "keyOX7ztvDK09NIWr"
    airtable_fonte_api_url = "https://api.airtable.com/v0/appP6G7OJmLzUCoUt/Table%201"


    pag_semeadura = requests.get("http://www.imea.com.br/imea-site/relatorios-mercado-detalhe/buscarPublicacoes?categoria=4&subcategoria=2&page=1")
    xpto_semeadura = pag_semeadura.json()

    arquivos = xpto_semeadura["data"]["rows"]


    #Parte 2 - Criar a lista para comparar

    lista_compara = []

    def limpa_pega(json):
        for d in arquivos:
            #relatorio = (f"{d['nome'].strip()} -- {d['data'].strip()}")
            #lista_compara.append(f"{[relatorio]}")
            lista_compara.append(d['data'].strip())
        return lista_compara

    limpa_pega(arquivos)


    #Parte 3 - importar o csv
    url = f'{airtable_fonte_api_url}?api_key={airtable_api}'
    requisicao = requests.get(url)
    nuvem = requisicao.json()

    #transformando em dicionário
    base_de_relatorio = []
    for v in nuvem['records']:
        base_de_relatorio.append(v['fields']['publicacao'])


    #Inserindo no Airtable
    def adicionar_linha(novos_dados):
        airtable_destino_api_url = "https://api.airtable.com/v0/appP6G7OJmLzUCoUt/Table%201"
        headers = {"Authorization": f'Bearer {airtable_api}'}
        new_content = {"fields": {"publicacao": novos_dados}}
        s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)


    #Parte 4 - Procura se tem novidade

    novidade = []
    for item in lista_compara:
        if item in base_de_relatorio:
            pass
        else:
            novidade.append(item)
            adicionar_linha(item)


    #Parte 4 - Criar a mensagem avisando os dias disponíveis, se tiver novidade.

    ativar_email = False

    if novidade == []:
        pass
    else:
        ativar_email = True
        subject = 'Relatório de Soja disponível no site do Imea' 
        msg = 'Subject:{}\n\nSegue relatórios disponíveis de soja,\n\n\n'.format(subject)
        for linha in novidade:
            msg+= f"Relatório do dia {linha} está disponível\n"




    #Parte 6 - Enviar e-mail

    if ativar_email == True:    
        gmail_sender = 'cristianfavaroo@gmail.com'

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_acc, gmail_pass)

        para = 'cfc.jornalista@gmail.com,cristianfavaroo@gmail.com'

        corpo = msg.encode('utf8')
        server.sendmail(gmail_sender, para.split(","), corpo)

        server.quit()
