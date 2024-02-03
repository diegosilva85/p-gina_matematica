from flask import Flask, render_template, request, redirect, url_for
from pandas import DataFrame
from sendcsv import Email
from mural import Mural
import numpy as np
from scipy.stats import mode
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    prova1: Mapped[float] = mapped_column(nullable=True)
    prova2: Mapped[float] = mapped_column(nullable=True)
    prova3: Mapped[float] = mapped_column(nullable=True)
    prova4: Mapped[float] = mapped_column(nullable=True)
    prova5: Mapped[float] = mapped_column(nullable=True)
    prova6: Mapped[float] = mapped_column(nullable=True)
    prova7: Mapped[float] = mapped_column(nullable=True)
    prova8: Mapped[float] = mapped_column(nullable=True)
    pm: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    boss_vitoria: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    boss_total: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_ouro: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_prata: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_bronze: Mapped[int] = mapped_column(nullable=True, server_default=str(0))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI ", "sqlite:///database_2024.db")

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Terceiro_A(db.Model):
    __tablename__ = 'Terceiro_A'


class Terceiro_B(db.Model):
    __tablename__ = 'Terceiro_B'


class Terceiro_C(db.Model):
    __tablename__ = 'Terceiro_C'


class Primeiro_D(db.Model):
    __tablename__ = 'Primeiro_D'


with app.app_context():
    db.create_all()

lista_turmas_db = [Terceiro_A, Terceiro_B, Terceiro_C, Primeiro_D]

senha = os.environ.get("senha_professor").strip("")

login, prova, nota, turma, pm, id_aluno, id_class = None, None, None, None, None, None, None

# Dados das turmas
with open('nomes_1D.txt', 'r', encoding='ISO-8859-1') as arquivo:
    primeiro_d = arquivo.readlines()
with open('nomes_3A.txt', 'r', encoding='ISO-8859-1') as arquivo:
    terceiro_a = arquivo.readlines()
with open('nomes_3B.txt', 'r', encoding='ISO-8859-1') as arquivo:
    terceiro_b = arquivo.readlines()
with open('nomes_3C.txt', 'r', encoding='ISO-8859-1') as arquivo:
    terceiro_c = arquivo.readlines()


def selecionar_turma(valor):
    if valor == 'a' or valor == '3ºA':
        return lista_turmas_db[0]
    elif valor == 'b' or valor == '3ºB':
        return lista_turmas_db[1]
    elif valor == 'c' or valor == '3ºC':
        return lista_turmas_db[2]
    elif valor == 'd' or valor == '1ºD':
        return lista_turmas_db[3]


def criar_turmas():
    global lista_turmas_db, terceiro_a, terceiro_b, terceiro_c, primeiro_d

    for aluno_a in terceiro_a:
        novo_aluno = Terceiro_A(nome=aluno_a)
        db.session.add(novo_aluno)
        db.session.commit()

    for aluno_b in terceiro_b:
        novo_aluno = Terceiro_B(nome=aluno_b)
        db.session.add(novo_aluno)
        db.session.commit()

    for aluno_c in terceiro_c:
        novo_aluno = Terceiro_C(nome=aluno_c)
        db.session.add(novo_aluno)
        db.session.commit()

    for aluno_d in primeiro_d:
        novo_aluno = Primeiro_D(nome=aluno_d)
        db.session.add(novo_aluno)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    classes = {
        '3ºA': '3ºA',
        '3ºB': '3ºB',
        '3ºC': '3ºC',
        '1ºD': '1ºD'
    }
    if request.method == 'POST':
        if "aluno_id_input" in request.form:
            aluno_nome = request.form['aluno_id_input']
            return redirect(url_for('busca', aluno_id=aluno_nome))
    return render_template('home.html', classes=classes)


@app.route('/aluno/<turma_aluno>/<aluno_nome>', methods=['GET', 'POST'])
def aluno(aluno_nome, turma_aluno):
    turma_selecionada = selecionar_turma(turma_aluno)
    resultados_busca = db.session.query(turma_selecionada).filter(turma_selecionada.nome.like(f'%{aluno_nome}%')).all()

    return render_template('aluno.html', search_results=resultados_busca)


@app.route('/busca/<aluno_id>', methods=['GET', 'POST'])
def busca(aluno_id):
    search_term = aluno_id
    aluno_turma = {'3ºA': [], '3ºB': [], '3ºC': [], '1ºD': []}
    for chave in aluno_turma.keys():
        turma_busca = selecionar_turma(chave)
        resultados_busca = db.session.query(turma_busca.nome).filter(turma_busca.nome.like(f'%{search_term}%')).all()
        for resultados in resultados_busca:
            aluno_turma[chave].append(resultados[0].strip('\n'))

    return render_template('busca.html', resultados_busca=aluno_turma)


def adicionar_aluno(turma_to_add, aluno_adicional):
    turma_selecionada = selecionar_turma(turma_to_add)
    novo_aluno = turma_selecionada(nome=aluno_adicional)
    db.session.add(novo_aluno)
    db.session.commit()


def deletar_aluno(id_delete, turma_delete):
    turma_selecionada = selecionar_turma(turma_delete)
    aluno_delete = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_delete)).scalar()
    db.session.delete(aluno_delete)
    db.session.commit()


def atualizar_nota(prova_update, nota_update, id_update, turma_update):
    turma_selecionada = selecionar_turma(turma_update)
    aluno_update = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_update)).scalar()
    num_prova = f'prova{prova_update}'
    setattr(aluno_update, num_prova, nota_update)
    db.session.commit()


def atualizar_pm(pm_adicional, id_pm=None, turma_pm=None, aluno_nome=None):
    aluno_update = None
    turma_selecionada = selecionar_turma(turma_pm)
    if id_pm is not None:
        aluno_update = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_pm)).scalar()
    elif aluno_nome is not None:
        aluno_update = db.session.execute(
            db.select(turma_selecionada).where(turma_selecionada.nome == aluno_nome)).scalar()
    pm_atualizado = int(pm_adicional) + int(aluno_update.pm)
    setattr(aluno_update, "pm", pm_atualizado)
    db.session.commit()


def boss(pm_boss, turma_boss, id_boss):
    turma_selecionada = selecionar_turma(turma_boss)
    aluno_boss = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_boss)).scalar()
    total_boss = int(aluno_boss.boss_total) + 1
    if pm_boss == '15':
        numero_vitorias = 1 + int(aluno_boss.boss_vitoria)
        setattr(aluno_boss, "boss_vitoria", numero_vitorias)
        atualizar_pm(15, id_pm=id_boss, turma_pm=turma_boss)
    elif pm_boss == '5':
        atualizar_pm(5, id_pm=id_boss, turma_pm=turma_boss)
    setattr(aluno_boss, "boss_total", total_boss)
    db.session.commit()


def atualizar_coroas(nome_coroa, turma_coroa, valor_coroa):
    turma_selecionada = selecionar_turma(turma_coroa)
    aluno_coroa = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.nome == nome_coroa)).scalar()
    if valor_coroa == 0:
        total_selecionada = int(aluno_coroa.coroa_ouro) + 1
        setattr(aluno_coroa, "coroa_ouro", total_selecionada)
    elif valor_coroa == 1:
        total_selecionada = int(aluno_coroa.coroa_prata) + 1
        setattr(aluno_coroa, "coroa_prata", total_selecionada)
    elif valor_coroa == 2:
        total_selecionada = int(aluno_coroa.coroa_bronze) + 1
        setattr(aluno_coroa, "coroa_bronze", total_selecionada)
    db.session.commit()


@app.route('/professor', methods=['GET', 'POST'])
def professor():
    global login, prova, nota, turma, pm, id_aluno, id_class, senha
    if request.method == 'POST':
        if 'Password' in request.form:
            password = request.form['Password']
            if password == senha:
                login = True
    if 'add' in request.form:
        aluno_adicionar = request.form['Id']
        turma_adicionar = request.form['class']
        adicionar_aluno(turma_adicionar, aluno_adicionar)
    if 'delete' in request.form:
        id_delete = request.form['Id']
        turma_deletar = request.form['turma']
        deletar_aluno(id_delete, turma_deletar)
    if 'start' in request.form:
        prova = request.form['prova']
        turma = request.form['turma']
    if 'nota' in request.form:
        nota = request.form['nota']
        pm = request.form['pm']
        id_aluno = request.form['id_aluno']
        atualizar_nota(prova, nota, id_aluno, turma)
        atualizar_pm(pm, id_pm=id_aluno, turma_pm=turma)
    if 'ranking' in request.form:
        id_class = request.form['ranking']
        return redirect(url_for('ranking', class_id=id_class))
    if 'mural_id_input' in request.form:
        mural_turma = request.form['mural_id_input']
        prova_mural = request.form['prova_input']
        return redirect(url_for('mural', mural_turma=mural_turma, prova_mural=prova_mural))
    if 'exportar' in request.form:
        exportar = request.form['exportar']
        exportar_csv(exportar)
    if 'criar' in request.form:
        criar_turmas()
    if 'boss' in request.form:
        boss_pm = request.form['boss_pm']
        boss_turma = request.form['boss_turma']
        boss_id = request.form['boss_id']
        boss(boss_pm, boss_turma, boss_id)
    return render_template('professor.html', login=login, prova=prova, class_id=id_class)


@app.route('/mural/<mural_turma>/<prova_mural>', methods=['GET', 'POST'])
def mural(mural_turma, prova_mural):
    prova_mural_banco = f'prova{prova_mural}'
    turma_selecionada = selecionar_turma(mural_turma)
    resultados_mural = db.session.query(turma_selecionada.nome, getattr(turma_selecionada, prova_mural_banco)).order_by(
        getattr(turma_selecionada, prova_mural_banco).desc()).all()
    pm_prova = db.session.query(getattr(turma_selecionada, 'pm')).all()
    notas = [resultado[1] for resultado in resultados_mural if resultado[1] is not None]
    notas.sort(reverse=True)
    pm_prova_lista = [valor[0] for valor in pm_prova if valor[0] is not None]

    media = np.mean(notas)
    moda = mode(notas)
    mediana = np.median(notas)
    desvio = np.std(notas)
    pm_medio = np.mean(pm_prova_lista)
    nota_outro = None
    nota_prata = None
    lista_ouro = []
    lista_prata = []
    lista_bronze = []
    for i in range(10, 5, -1):
        lista_ouro = [item[0] for item in resultados_mural if item[1] == i]
        if lista_ouro:
            for estudante in lista_ouro:
                atualizar_pm(9, aluno_nome=estudante, turma_pm=mural_turma)
                atualizar_coroas(nome_coroa=estudante, turma_coroa=mural_turma, valor_coroa=0)
            nota_outro = i
            break
    for i in range(nota_outro - 1, 5, -1):
        lista_prata = [item[0] for item in resultados_mural if item[1] == i]
        if lista_prata:
            for estudante_2 in lista_prata:
                atualizar_pm(6, aluno_nome=estudante_2, turma_pm=mural_turma)
                atualizar_coroas(nome_coroa=estudante_2, turma_coroa=mural_turma, valor_coroa=1)
            nota_prata = i
            break
    for i in range(nota_prata - 1, 5, -1):
        lista_bronze = [item[0] for item in resultados_mural if item[1] == i]
        if lista_bronze:
            for estudante_3 in lista_bronze:
                atualizar_pm(3, aluno_nome=estudante_3, turma_pm=mural_turma)
                atualizar_coroas(nome_coroa=estudante_3, turma_coroa=mural_turma, valor_coroa=2)
            break
    imagem_mural = Mural(mural_turma, prova_mural, round(media, 2), int(moda[0]), mediana, round(desvio, 2),
                         round(pm_medio, 2), lista_ouro, lista_prata, lista_bronze)

    return render_template('mural.html', imagem=imagem_mural.caminho_static)


@app.route('/<class_name>')
def class_page(class_name):
    turma_selecionada = selecionar_turma(class_name)

    resultados_class_page = (db.session.query(turma_selecionada.id, turma_selecionada.nome, turma_selecionada.prova1,
                                              turma_selecionada.prova2, turma_selecionada.prova3,
                                              turma_selecionada.prova4,
                                              turma_selecionada.prova5, turma_selecionada.prova6,
                                              turma_selecionada.prova7,
                                              turma_selecionada.prova8, turma_selecionada.pm).all())
    lista_de_provas = []

    for i in range(1, 9):
        atributo = getattr(turma_selecionada, f"prova{i}")
        dados = db.session.query(atributo).all()
        notas_validas = [nota[0] for nota in dados if nota[0] is not None]
        if notas_validas:
            media = round(np.mean(notas_validas), 2)
            mediana = np.median(notas_validas)
            moda = int(mode(notas_validas)[0])
            desvio = round(np.std(notas_validas), 2)
            lista_prova = [media, mediana, moda, desvio]
            lista_de_provas.append(lista_prova)

    tamanho = len(lista_de_provas)

    return render_template('class_page.html', class_name=class_name, data=resultados_class_page,
                           estatisticas=lista_de_provas, tamanho=tamanho)


@app.route('/ranking/<class_id>', methods=['GET', 'POST'])
def ranking(class_id):
    turma_selecionada = selecionar_turma(class_id)
    resultados_ranking = db.session.query(turma_selecionada.nome, getattr(turma_selecionada, 'pm')).order_by(
        getattr(turma_selecionada, 'pm').desc()).all()

    return render_template('ranking.html', data=resultados_ranking, class_id=class_id)


def exportar_csv(valor):
    turma_selecionada = selecionar_turma(valor)
    with app.app_context():
        resultados_csv = (db.session.query(turma_selecionada.nome, turma_selecionada.prova1, turma_selecionada.prova2,
                                           turma_selecionada.prova3, turma_selecionada.prova4, turma_selecionada.prova5,
                                           turma_selecionada.prova6, turma_selecionada.prova7, turma_selecionada.prova8,
                                           turma_selecionada.pm).all())

    dataframe = DataFrame.from_records(resultados_csv,
                                       columns=['Nome', '1°', '2°', '3°', '4°', '5°', '6°', '7°', '8°', 'PM'])
    dataframe.to_csv(f'Turma_{valor}.csv', index=False)

    email = Email(valor)


if __name__ == '__main__':
    app.run(debug=True)
