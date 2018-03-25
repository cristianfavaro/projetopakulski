import requests
from bs4 import BeautifulSoup as bs
import smtplib
import itertools
import pendulum


### arquivos com senhas

import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

airtable_api = os.environ.get('AIRTABLE_KEY')
gmail_acc = os.environ.get('G-MAIL_ACC')
gmail_pass = os.environ.get('G-MAIL_KEY')

airtable_fonte_api_url = os.environ.get('AIR_FONTE_URL')
base_k = os.environ.get('BASE')
table_n = "Table 1"


#sexta
colheita_soja = 4, 8
colheita_milho = 3, 8
colheita_algodao = 1, 8

semeadura_soja = 4, 7
semeadura_milho = 3, 7
semeadura_algodao = 1, 7

#segunda
boletim_soja = 4, 2
boletim_milho = 3, 2
boletim_algodao = 1, 2

#todos os dias
estimativa_safra_soja = 4, 9
estimativa_safra_milho = 3, 9
estimativa_safra_algodao = 1, 9


#Dia da semana

def dia_semana():
	today = pendulum.today()
	dia_semana = today.day_of_week 
	return dia_semana


#Pegar o html

def get_data(cat, sub):

	
	html = requests.get(f"http://www.imea.com.br/imea-site/relatorios-mercado-detalhe/buscarPublicacoes?categoria={cat}&subcategoria={sub}&page=1")
	xpto = html.json()
	return xpto["data"]["rows"]


def limpa_pega(arquivo_json):
	lista_compara = []
	for d in arquivo_json:
		lista_compara.append(f"{d['data'].strip()} {d['nome'].strip()} | {d['arquivo'].strip()}")
	return lista_compara

#importando csv e transformando em dicionário

def csv_import(base_k, table_n):
	from airtable import Airtable
	base_key = base_k
	table_name = table_n
	airtable = Airtable(base_key, table_name, api_key=airtable_api)
	records = airtable.get_all()
	base_de_relatorio = []
	for v in records:
		base_de_relatorio.append(v['fields']['publicacao'])

	return base_de_relatorio


#adicionar linha no Airtable
def adicionar_linha(novos_dados):
	airtable_destino_api_url = airtable_fonte_api_url
	headers = {"Authorization": f'Bearer {airtable_api}'}
	new_content = {"fields": {"publicacao": novos_dados}}
	s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)


def novidade(base_de_relatorio, lista_compara):
	novidade = []
	for item in lista_compara:
		if item in base_de_relatorio:
			pass
		else:
			novidade.append(item)
			adicionar_linha(item)
	return novidade

def enviar_email(novidade, textos=""):
	if novidade == []:
		pass
	else:
		subject = 'Relatorio disponivel no site do Imea'
		msg = 'Subject:{}\n\nSeguem relatórios disponíveis:\n\n\n'.format(subject)
		for linha in novidade:
			msg+= f"Relatório {linha.split(' | ')[0]} está disponível. http://www.imea.com.br/upload/publicacoes/arquivos/{linha.split(' | ')[1]}\n"
		
		if textos == "":
			pass
		else:
			msg += "\n\n"
			msg += "Textos automatizados (conferir com tabela!):\n\n\n"
			msg += textos
			
		gmail_sender = 'cfc.jornalista@gmail.com'

		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.login(gmail_acc, gmail_pass)

		para = os.environ.get('DESTINO_EMAIL')

		corpo = msg.encode('utf8')
		server.sendmail(gmail_sender, para.split(","), corpo)

		server.quit()


def main():
	#pesquisando todos os dias 

	#Estimativa safra de soja
	data = get_data(estimativa_safra_soja[0], estimativa_safra_soja[1])
	lista_compara = limpa_pega(data)
	base_de_relatorio = csv_import(base_k, table_n)
	relatorios_novos = novidade(base_de_relatorio, lista_compara)
	e_mail = enviar_email(relatorios_novos)

	#Estimativa safra de milho

	data = get_data(estimativa_safra_milho[0], estimativa_safra_milho[1])
	lista_compara = limpa_pega(data)
	base_de_relatorio = csv_import(base_k, table_n)
	relatorios_novos = novidade(base_de_relatorio, lista_compara)
	e_mail = enviar_email(relatorios_novos)

	#Estimativa safra de algodão

	data = get_data(estimativa_safra_algodao[0], estimativa_safra_algodao[1])
	lista_compara = limpa_pega(data)
	base_de_relatorio = csv_import(base_k, table_n)
	relatorios_novos = novidade(base_de_relatorio, lista_compara)
	e_mail = enviar_email(relatorios_novos)

	#Relatórios específicos 

	dia = dia_semana()
	if dia == 0:
		import pega_texto_colheita_soja
		
		#colheita de soja
		data = get_data(colheita_soja[0], colheita_soja[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		textos = ""

		for item in relatorios_novos:
			url_tabela = item.split(" | ")[1]
			titulo, text = pega_texto_colheita_soja.go_getIt(url_tabela)
			textos += titulo
			textos += text

		e_mail = enviar_email(relatorios_novos, textos)

		#colheita de milho
		data = get_data(colheita_milho[0], colheita_milho[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

		#colheita de algodão
		data = get_data(colheita_algodao[0], colheita_algodao[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

		#semeadura de soja
		data = get_data(semeadura_soja[0], semeadura_soja[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

		#semeadura de milho
		data = get_data(semeadura_milho[0], semeadura_milho[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

		#semeadura de algodão
		data = get_data(semeadura_algodao[0], semeadura_algodao[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

	if dia == 1:
		#boletim de soja 
		data = get_data(boletim_soja[0], boletim_soja[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

		#boletim de milho 
		data = get_data(boletim_milho[0], boletim_milho[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)

		#boletim de algodão
		data = get_data(boletim_algodao[0], boletim_algodao[1])
		lista_compara = limpa_pega(data)
		base_de_relatorio = csv_import(base_k, table_n)
		relatorios_novos = novidade(base_de_relatorio, lista_compara)
		e_mail = enviar_email(relatorios_novos)


if __name__ == '__main__':
	main()
