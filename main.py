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
    pm: Mapped[int] = mapped_column(nullable=True)


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

database = 'database_2024.db'
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
            aluno_id = request.form['aluno_id_input']
            return redirect(url_for('aluno', aluno_id=aluno_id))
    return render_template('home.html', classes=classes)


@app.route('/aluno/<aluno_id>', methods=['GET', 'POST'])
def aluno(aluno_id):
    search_term = aluno_id
    # TODO: Colocar a busca para as demais turmas.
    resultados_busca = db.session.query(Terceiro_A).filter(Terceiro_A.nome.like(f'%{search_term}%')).all()

    return render_template('aluno.html', search_results=resultados_busca)


def add_entry(turma_to_add, aluno):
    turma_selecionada = selecionar_turma(turma_to_add)
    novo_aluno = turma_selecionada(nome=aluno)
    db.session.add(novo_aluno)
    db.session.commit()


def delete_entry(id_delete, turma_delete):
    turma_selecionada = selecionar_turma(turma_delete)
    aluno_delete = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_delete)).scalar()
    db.session.delete(aluno_delete)
    db.session.commit()


def update_entry(prova, pm, nota, id_aluno, turma):
    turma_selecionada = selecionar_turma(turma)
    aluno_update = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_aluno)).scalar()
    num_prova = f'prova{prova}'
    if aluno_update.pm is None:
        pm_atualizado = int(pm) + 0
    else:
        pm_atualizado = int(pm) + int(aluno_update.pm)
    setattr(aluno_update, num_prova, nota)
    setattr(aluno_update, "pm", pm_atualizado)
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
        aluno = request.form['Id']
        turma = request.form['class']
        add_entry(turma, aluno)
    if 'delete' in request.form:
        id_delete = request.form['Id']
        turma = request.form['turma']
        delete_entry(id_delete, turma)
    if 'start' in request.form:
        prova = request.form['prova']
        turma = request.form['turma']
    if 'nota' in request.form:
        nota = request.form['nota']
        pm = request.form['pm']
        id_aluno = request.form['id_aluno']
        update_entry(prova, pm, nota, id_aluno, turma)
    if 'class_id_input' in request.form:
        id_class = request.form['class_id_input']
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
            nota_outro = i
            break
        else:
            pass
    for i in range(nota_outro - 1, 5, -1):
        lista_prata = [item[0] for item in resultados_mural if item[1] == i]
        if lista_prata:
            nota_prata = i
            break
        else:
            pass
    for i in range(nota_prata - 1, 5, -1):
        lista_bronze = [item[0] for item in resultados_mural if item[1] == i]
        if lista_bronze:
            break
        else:
            pass
    imagem_mural = Mural(mural_turma, prova_mural, round(media, 2), int(moda[0]), mediana, round(desvio, 2),
                         round(pm_medio, 2), lista_ouro, lista_prata, lista_bronze)

    return render_template('mural.html', imagem=imagem_mural.caminho_static)


@app.route('/<class_name>')
def class_page(class_name):
    turma_selecionada = selecionar_turma(class_name)

    resultados_class_page = (db.session.query(turma_selecionada.id, turma_selecionada.nome, turma_selecionada.prova1,
                                              turma_selecionada.prova2, turma_selecionada.prova3, turma_selecionada.prova4,
                                              turma_selecionada.prova5, turma_selecionada.prova6, turma_selecionada.prova7,
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
        else:
            pass

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
