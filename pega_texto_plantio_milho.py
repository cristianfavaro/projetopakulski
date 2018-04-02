import io
import re

import requests
import rows


def extrai_tabela(url):
    url_final = f"http://www.imea.com.br/upload/publicacoes/arquivos/{url}"
    response = requests.get(url_final)
    return rows.import_from_pdf(
        io.BytesIO(response.content),
        ends_before=re.compile(r'\* ?Variação em .*'),
    )


#definindo o dia da semana

def datas():
    import pendulum
    from pendulum import Date

    today = pendulum.today()
    extenso = ""
    if today.day_of_week == 1: 
        extenso = "segunda-feira"
    if today.day_of_week == 2: 
        extenso = "terça-feira"
    if today.day_of_week == 3: 
        extenso = "quarta-feira"
    if today.day_of_week == 4: 
        extenso = "quinta-feira"
    if today.day_of_week == 5: 
        extenso = "sexta-feira"

    date = Date.today()
    data_inicio = f"{date.day}/{date.month}/{date.year}"

    return extenso, data_inicio


#funcao para ajudar a construir meu texto

def trabalhos_campo(plantio_mt_milho_porcento, plantio_mt_milho_compara_ano):
    if plantio_mt_milho_porcento < plantio_mt_milho_compara_ano:
        return "Os trabalhos de campo estão atrasados ante igual período do ano passado"
    if plantio_mt_milho_porcento > plantio_mt_milho_compara_ano:
        return "Os trabalhos de campo estão adiantados ante igual período do ano passado"
    if plantio_mt_milho_porcento == plantio_mt_milho_compara_ano:
        return "Os trabalhos de campo estão no mesmo nível ante igual período do ano passado"



def cria_texto_milho_plantio(table):


    import re
    data_inicio = datas()[1]
    ano_safra = re.findall(r'\d\d\/\d\d', table[0][0])
    plantio_mt_milho_porcento = float((table[-4][-1]).split("\n")[1].replace("%", "").replace(",", "."))
    dia_semana = datas()[0]
    plantio_mt_milho_avanco_semana = (table[-3][-1]).strip()
    plantio_mt_milho_compara_ano = float((table[-2][-1]).strip().replace("%", "").replace(",", "."))
    texto_compara = trabalhos_campo(plantio_mt_milho_porcento, plantio_mt_milho_compara_ano)
    area_mt_milho = (table[0][-1]).strip()
    

#   PARTE IMPORTANTE DO CÓDIGO. VOCÊ FEZ ISSO PORQUE A TABELA ESTAVA DANDO UM ERRO NA ÚLTIMA LINHA. 

    plantio_mt_milho_oeste = (table[-4][-3]).strip()
    if "\n" in plantio_mt_milho_oeste:
        plantio_mt_milho_oeste = plantio_mt_milho_oeste.split("\n")[1].replace("%", "").replace(",", ".")
    
    plantio_mt_milho_medionorte = (table[-4][-7]).strip()
    if "\n" in plantio_mt_milho_medionorte:
        plantio_mt_milho_medionorte = plantio_mt_milho_medionorte.split("\n")[1].replace("%", "").replace(",", ".")
    
    plantio_mt_milho_nordeste = (table[-4][-6]).strip()
    if "\n" in plantio_mt_milho_nordeste:
        plantio_mt_milho_nordeste = plantio_mt_milho_nordeste.split("\n")[1].replace("%", "").replace(",", ".")

    plantio_mt_milho_sudeste = (table[-4][-2]).strip()
    if "\n" in plantio_mt_milho_sudeste:
        plantio_mt_milho_sudeste = plantio_mt_milho_sudeste.split("\n")[1].replace("%", "").replace(",", ".")



    titulo = f'Milho/MT: Plantio ______da safrinha?_______ avança {plantio_mt_milho_avanco_semana} em uma semana e atinge {str(plantio_mt_milho_porcento).replace(".", ",")}% da área, diz IMEA\n\n'




    texto = f'São Paulo, {data_inicio} - O plantio da ______primeira ou segunda safra?_____ safra de milho 20{ano_safra[0]} de Mato Grosso atingiu {str(plantio_mt_milho_porcento).replace(".", ",")}% da área prevista para a cultura, apontou o Instituto Mato-grossense de Economia Agropecuária (Imea) nesta {dia_semana}. O avanço na semana foi de {plantio_mt_milho_avanco_semana}. {texto_compara} ({str(plantio_mt_milho_compara_ano).replace(".", ",")}%). A área cultivada com milho em Mato Grosso chega a {area_mt_milho} hectares, segundo o Imea.\n\nEntre as regiões, o oeste do Estado já concluiu {(plantio_mt_milho_oeste).replace(".", ",")}% do plantio e o médio-norte, {(plantio_mt_milho_medionorte).replace(".", ",")}%. No nordeste, o ritmo está em {(plantio_mt_milho_nordeste).replace(".", ",")}%, enquanto no sudeste mato-grossenses a retirada dos grãos do campo foi realizada em {(plantio_mt_milho_sudeste).replace(".", ",")}% da área semeada. (Equipe Broadcast Agro)\n\n\n\n'

    return titulo, texto



def go_getIt(url_busca):
    table = extrai_tabela(url_busca)
    titulo = cria_texto_milho_plantio(table)[0]
    texto = cria_texto_milho_plantio(table)[1]
    
    return titulo, texto


if __name__ == '__main__':
    main()
