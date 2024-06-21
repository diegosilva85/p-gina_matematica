# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import mode


def checar_mural(tabela, turma, prova, db):
    if turma == 'a':
        turma = 'Terceiro_A'
    elif turma == 'b':
        turma = 'Terceiro_B'
    elif turma == 'c':
        turma = 'Terceiro_C'
    elif turma == 'd':
        turma = 'Primeiro_D'
    turma_tabela = getattr(tabela, 'turma')
    resposta = db.session.query(tabela).filter(turma_tabela == turma).all()
    for item in resposta:
        valor = getattr(item, f'prova{prova}')
        print(f"TABELA MURAIS: {valor}")
        if valor == 'x':
            return False
    return True

def registrar_prova(tabela, turma, prova, db):
    turma_tabela= {'a': 'Terceiro_A', 'b': 'Terceiro_B', 'c': 'Terceiro_C', 'd': 'Primeiro_D'}
    turma_mural = getattr(tabela, 'turma')    
    mural = db.session.query(tabela).filter(turma_mural == turma_tabela[turma]).scalar()
    setattr(mural, f'prova{prova}', 'x')
    db.session.commit()
    db.session.close()


def adicionar_aluno(turma, nome, db):
    novo_aluno = turma(nome=nome)
    db.session.add(novo_aluno)
    db.session.commit()


def deletar_aluno(id_delete, turma, db):
    aluno_delete = db.session.execute(db.select(turma).where(turma.id == id_delete)).scalar()
    db.session.delete(aluno_delete)
    db.session.commit()


def inserir_dados_prova(prova, nota, id_update, turma, pm, beneficio, db, elite):
    aluno = db.session.execute(db.select(turma).where(turma.id == id_update)).scalar()
    setattr(aluno, f"prova{prova}", nota)
    setattr(aluno, f"pm{prova}", pm)
    setattr(aluno, f"elite{prova}", elite)
    if beneficio == "calc":
        acrescentar_pm(-5, id_pm=id_update, turma=turma, db=db)
        setattr(aluno, f'beneficios{prova}', "Calculadora")
    if beneficio == "anular":
        acrescentar_pm(-10, id_pm=id_update, turma=turma, db=db)
        setattr(aluno, f'beneficios{prova}', "Anular")
    if beneficio == "formula":
        acrescentar_pm(-10, id_pm=id_update, turma=turma, db=db)
        setattr(aluno, f'beneficios{prova}', "Formulas")
    if beneficio == "caderno":
        acrescentar_pm(-15, id_pm=id_update, turma=turma, db=db)
        setattr(aluno, f'beneficios{prova}', "Caderno")
    db.session.commit()


def acrescentar_pm(pm_adicional, db, id_pm=None, turma=None, nome=None):
    aluno = None
    if id_pm is not None:
        aluno = db.session.execute(db.select(turma).where(turma.id == id_pm)).scalar()
    elif nome is not None:
        aluno = db.session.execute(db.select(turma).where(turma.nome == nome)).scalar()
    print(f"ALUNO: {aluno.nome} PM: {aluno.pm}")
    pm_atualizado = int(pm_adicional) + int(aluno.pm)
    print(f"PM_ATUALIZADO: {pm_atualizado}")
    setattr(aluno, "pm", pm_atualizado)
    db.session.commit()
    # db.session.close()


def boss(pm, turma, id_boss, db):
    aluno = db.session.execute(db.select(turma).where(turma.id == id_boss)).scalar()
    if pm == '15':
        aluno.boss_vitoria += 1
        aluno.boss_elite += 1
        acrescentar_pm(15, id_pm=id_boss, turma=turma, db=db)
    elif pm == '10':
        aluno.boss_vitoria += 1
        acrescentar_pm(10, id_pm=id_boss, turma=turma, db=db)
    elif pm == '5':
        aluno.boss_elite += 1
        acrescentar_pm(5, id_pm=id_boss, turma=turma, db=db)
    aluno.boss_total += 1
    db.session.commit()


def atualizar_coroas(nome, turma, valor, prova, elite, db):
    aluno = db.session.execute(db.select(turma).where(turma.nome == nome)).scalar()
    print(f"----- COROA ----- ALUNO: {aluno.nome}")
    if valor == 0:
        aluno.coroa_ouro += 1
        setattr(aluno, f"coroa{prova}", "ouro")
    elif valor == 1:
        aluno.coroa_prata += 1
        setattr(aluno, f"coroa{prova}", "prata")
    elif valor == 2:
        aluno.coroa_bronze += 1
        setattr(aluno, f"coroa{prova}", "bronze")
    if elite == 'sim':
        aluno.coroas_elite += 1
    db.session.commit()
    db.session.close()


def alunos_elite(turma, db):
    resultado_query = db.session.query(turma.nome, turma.prova1, turma.prova2, turma.prova3, turma.prova4, turma.prova5,
                                       turma.prova6, turma.prova7, turma.prova8).order_by(turma.id).all()
    medias = []
    nome_elite = None
    for resultado in resultado_query:
        media_aluno = media_alunos(resultado)
        medias.append(media_aluno)
    for dado in medias:
        for key, value in dado.items():
            if key != "media":
                nome_elite = db.session.execute(
                    db.select(turma).where(turma.nome == key)).scalar()
            else:
                if value >= 7:
                    nome_elite.elite = "sim"
                else:
                    nome_elite.elite = "não"
    db.session.commit()


def media_alunos(lista: tuple) -> dict:
    notas = {
        lista[0]: [],
        "media": 0
    }
    for nota in lista:
        if isinstance(nota, str):
            continue
        nota = nota or 0  # Se None, atribui 0 à nota
        notas[lista[0]].append(nota)

    notas[lista[0]].sort()
    notas[lista[0]] = notas[lista[0]][2:]

    notas["media"] = round(sum(notas[lista[0]]) / len(notas[lista[0]]), 2)
    return notas


def estatisticas(notas: list, pm=None) -> list:
    media = round(np.mean(notas), 2)
    try:
        moda = int(mode(notas)[0])
    except ValueError:
        moda = 0
    mediana = np.median(notas)
    desvio = round(np.std(notas), 2)
    if pm:
        pm_medio = round(np.mean(pm), 2)
        return [media, mediana, moda, desvio, pm_medio]

    return [media, mediana, moda, desvio]
