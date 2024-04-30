from math import floor
from main import acrescentar_pm, atualizar_coroas


def mural_antigo(resultados_mural, fator, imagem, mural_turma, elite, prova_mural, pm_adicional_ouro,
                 pm_adicional_prata, pm_adicional_bronze):
    nota_ouro, nota_prata = None, None
    lista_ouro, lista_prata, lista_bronze = [], [], []
    lista_nao_ouro, lista_nao_ouro_2 = [], []
    lista_nao_prata, lista_nao_prata_2 = [], []

    for i in range(10, 5, -1):
        if lista_nao_ouro:
            for nao_ouro in lista_nao_ouro:
                if int(nao_ouro[2]) >= floor(i * fator + 1):
                    lista_ouro.append(nao_ouro[0])
                else:
                    lista_nao_ouro_2.append(nao_ouro)
            lista_nao_ouro = lista_nao_ouro_2
        lista_ouro.extend([item[0] for item in resultados_mural if item[1] == i and item[2] >= floor(i * fator + 1)])
        lista_nao_ouro.extend([item for item in resultados_mural if item[1] == i and item[2] < floor(i * fator + 1)])
        if lista_ouro:
            if imagem == "Não":  # Se o professor optou por apenas gerar a imagem, ou para atribuir os pms.
                for estudante in lista_ouro:
                    acrescentar_pm(pm_adicional_ouro, nome=estudante, turma=mural_turma)
                    atualizar_coroas(nome=estudante, turma=mural_turma, valor=0,
                                     prova=prova_mural, elite=elite)
            nota_ouro = i
            break
    if nota_ouro is None:
        pass
    else:
        lista_nao_ouro_2 = []
        for j in range(nota_ouro - 1, 5, -1):
            if lista_nao_prata:
                for nao_prata in lista_nao_prata:
                    if int(nao_prata[2]) >= floor(fator + 1):
                        lista_prata.append(nao_prata[0])
                        lista_nao_prata.remove(nao_prata)
                    else:
                        lista_nao_prata_2.append(nao_prata)
                lista_nao_prata = lista_nao_prata_2
            lista_prata.extend(
                [item[0] for item in resultados_mural if item[1] == j and item[2] >= floor(j * fator + 1)])
            lista_nao_prata.extend(
                [item for item in resultados_mural if item[1] == j and item[2] < floor(j * fator + 1)])
            if lista_prata:
                for nao_ouro in lista_nao_ouro:
                    if int(nao_ouro[2]) >= floor(fator + 1):
                        lista_prata.append(nao_ouro[0])
                    else:
                        lista_nao_ouro_2.append(nao_ouro)
                lista_nao_ouro = lista_nao_ouro_2
                if imagem == "Não":  # Se o professor optou por apenas gerar a imagem, ou para atribuir os pms.
                    for estudante_2 in lista_prata:
                        acrescentar_pm(pm_adicional_prata, nome=estudante_2, turma=mural_turma)
                        atualizar_coroas(nome=estudante_2, turma=mural_turma, valor=1,
                                         prova=prova_mural, elite=elite)
                nota_prata = j
                break
        if nota_prata is None:
            pass
        else:
            for k in range(nota_prata - 1, 5, -1):
                lista_bronze = [item[0] for item in resultados_mural if
                                item[1] == k and item[2] >= floor(k * fator + 1)]
                if lista_bronze:
                    for nao_ouro in lista_nao_ouro:
                        if int(nao_ouro[2]) >= floor(fator + 1):
                            lista_bronze.append(nao_ouro[0])
                    for nao_prata in lista_nao_prata:
                        if int(nao_prata[2]) >= floor(fator + 1):
                            lista_bronze.append(nao_prata[0])
                    if imagem == "Não":  # Se o professor optou por apenas gerar a imagem, ou para atribuir os pms.
                        for estudante_3 in lista_bronze:
                            acrescentar_pm(pm_adicional_bronze, nome=estudante_3, turma=mural_turma)
                            atualizar_coroas(nome=estudante_3, turma=mural_turma, valor=2,
                                             prova=prova_mural, elite=elite)
                    break
