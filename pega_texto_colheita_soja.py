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

def trabalhos_campo(colheita_mt_soja_porcento, colheita_mt_soja_compara_ano):
    if colheita_mt_soja_porcento < colheita_mt_soja_compara_ano:
        return "Os trabalhos de campo estão atrasados ante igual período do ano passado"
    if colheita_mt_soja_porcento > colheita_mt_soja_compara_ano:
        return "Os trabalhos de campo estão adiantados ante igual período do ano passado"
    if colheita_mt_soja_porcento == colheita_mt_soja_compara_ano:
        return "Os trabalhos de campo estão no mesmo nível ante igual período do ano passado"



def cria_texto_soja_colheita(table):


    import re
    data_inicio = datas()[1]
    ano_safra = re.findall(r'\d\d\/\d\d', table[0][0])
    colheita_mt_soja_porcento = float((table[-4][-1]).strip().replace("%", "").replace(",", "."))
    dia_semana = datas()[0]
    colheita_mt_soja_avanco_semana = (table[-3][-1]).strip()
    colheita_mt_soja_compara_ano = float((table[-2][-1]).strip().replace("%", "").replace(",", "."))
    texto_compara = trabalhos_campo(colheita_mt_soja_porcento, colheita_mt_soja_compara_ano)
    area_mt_soja = (table[0][-1]).strip()

    colheita_mt_soja_oeste = (table[-4][-3]).strip()
    colheita_mt_soja_medionorte = (table[-4][-7]).strip()
    colheita_mt_soja_nordeste = (table[-4][-6]).strip()
    colheita_mt_soja_sudeste = (table[-4][-2]).strip()


    titulo = f'Soja/MT: Colheita avança {colheita_mt_soja_avanco_semana} em uma semana e atinge {str(colheita_mt_soja_porcento).replace(".", ",")}% da área, diz IMEA\n\n'

    texto = f'São Paulo, {data_inicio} - A colheita da safra de soja 20{ano_safra[0]} de Mato Grosso atingiu {str(colheita_mt_soja_porcento).replace(".", ",")}% da área plantada, apontou o Instituto Mato-grossense de Economia Agropecuária (Imea) nesta {dia_semana}. O avanço na semana foi de {colheita_mt_soja_avanco_semana}. {texto_compara} ({str(colheita_mt_soja_compara_ano).replace(".", ",")}). A área cultivada com soja em Mato Grosso chega a {area_mt_soja} hectares, segundo o Imea.\n\nEntre as regiões, o oeste do Estado já concluiu {colheita_mt_soja_oeste} da colheita e o médio-norte, {colheita_mt_soja_medionorte}. No nordeste, o ritmo está em {colheita_mt_soja_nordeste}, enquanto no sudeste mato-grossenses a retirada dos grãos do campo foi realizada em {colheita_mt_soja_sudeste} da área semeada. (Equipe Broadcast Agro)\n\n\n\n'

    return titulo, texto



def go_getIt(url_busca):
    table = extrai_tabela(url_busca)
    titulo = cria_texto_soja_colheita(table)[0]
    texto = cria_texto_soja_colheita(table)[1]
    
    return titulo, texto


if __name__ == '__main__':
    main()

