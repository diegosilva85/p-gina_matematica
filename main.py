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

turmas = [Terceiro_A, Terceiro_B, Terceiro_C, Primeiro_D]

senha = os.environ.get("senha_professor").strip("")

database = 'database_2024.db'
login, prova, nota, turma, pm, id_aluno, id_class = None, None, None, None, None, None, None


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
    resultados = db.session.query(Terceiro_A).filter(Terceiro_A.nome.like(f'%{search_term}%')).all()

    return render_template('aluno.html', search_results=resultados)


def add_entry(turma_to_add, aluno):
    novo_aluno = None
    if turma_to_add == "a":
        novo_aluno = Terceiro_A(nome=aluno)
    elif turma_to_add == "b":
        novo_aluno = Terceiro_B(nome=aluno)
    elif turma_to_add == "c":
        novo_aluno = Terceiro_C(nome=aluno)
    elif turma_to_add == "d":
        novo_aluno = Primeiro_D(nome=aluno)
    db.session.add(novo_aluno)
    db.session.commit()


def delete_entry(id_delete, turma_delete):
    aluno_delete = None
    if turma_delete == "a":
        aluno_delete = db.session.execute(db.select(Terceiro_A).where(Terceiro_A.id == id_delete)).scalar()
    elif turma_delete == "b":
        aluno_delete = db.session.execute(db.select(Terceiro_B).where(Terceiro_B.id == id_delete)).scalar()
    elif turma_delete == "c":
        aluno_delete = db.session.execute(db.select(Terceiro_C).where(Terceiro_C.id == id_delete)).scalar()
    if turma_delete == 'd':
        aluno_delete = db.session.execute(db.select(Primeiro_D).where(Primeiro_D.id == id_delete)).scalar()
    db.session.delete(aluno_delete)
    db.session.commit()


def update_entry(prova, pm, nota, id_aluno, turma):
    aluno_update = None
    if turma == 'a':
        aluno_update = db.session.execute(db.select(Terceiro_A).where(Terceiro_A.id == id_aluno)).scalar()
    elif turma == 'b':
        aluno_update = db.session.execute(db.select(Terceiro_B).where(Terceiro_B.id == id_aluno)).scalar()
    elif turma == 'c':
        aluno_update = db.session.execute(db.select(Terceiro_C).where(Terceiro_C.id == id_aluno)).scalar()
    elif turma == 'd':
        aluno_update = db.session.execute(db.select(Primeiro_D).where(Primeiro_D.id == id_aluno)).scalar()
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
    return render_template('professor.html', login=login, prova=prova, class_id=id_class)


@app.route('/mural/<mural_turma>/<prova_mural>', methods=['GET', 'POST'])
def mural(mural_turma, prova_mural):
    resultados = None
    prova_mural_banco = f'prova{prova_mural}'
    pm_prova = None

    if mural_turma == 'a':
        resultados = db.session.query(Terceiro_A.nome, getattr(Terceiro_A, prova_mural_banco)).order_by(
            getattr(Terceiro_A, prova_mural_banco).desc()).all()
        pm_prova = db.session.query(getattr(Terceiro_A, 'pm')).all()
    elif mural_turma == 'b':
        resultados = db.session.query(Terceiro_B.nome, getattr(Terceiro_B, prova_mural_banco)).order_by(
            getattr(Terceiro_B, prova_mural_banco).desc()).all()
        pm_prova = db.session.query(getattr(Terceiro_B, 'pm')).all()
    elif mural_turma == 'c':
        resultados = db.session.query(Terceiro_C.nome, getattr(Terceiro_C, prova_mural_banco)).order_by(
            getattr(Terceiro_C, prova_mural_banco).desc()).all()
        pm_prova = db.session.query(getattr(Terceiro_C, 'pm')).all()
    elif mural_turma == 'd':
        resultados = db.session.query(Primeiro_D.nome, getattr(Primeiro_D, prova_mural_banco)).order_by(
            getattr(Primeiro_D, prova_mural_banco).desc()).all()
        pm_prova = db.session.query(getattr(Primeiro_D, 'pm')).all()

    notas = [resultado[1] for resultado in resultados if resultado[1] is not None]
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
        lista_ouro = [item[0] for item in resultados if item[1] == i]
        if lista_ouro:
            nota_outro = i
            break
        else:
            pass
    for i in range(nota_outro - 1, 5, -1):
        lista_prata = [item[0] for item in resultados if item[1] == i]
        if lista_prata:
            nota_prata = i
            break
        else:
            pass
    for i in range(nota_prata - 1, 5, -1):
        lista_bronze = [item[0] for item in resultados if item[1] == i]
        if lista_bronze:
            break
        else:
            pass
    imagem_mural = Mural(mural_turma, prova_mural, round(media, 2), int(moda[0]), mediana, round(desvio, 2),
                         round(pm_medio, 2), lista_ouro, lista_prata, lista_bronze)

    return render_template('mural.html', imagem=imagem_mural.caminho_static)


@app.route('/<class_name>')
def class_page(class_name):
    global turmas
    resultados, turma_selecionada = None, turmas[3]
    if class_name == '3ºA':
        turma_selecionada = turmas[0]
    elif class_name == '3ºB':
        turma_selecionada = turmas[1]
    elif class_name == '3°C':
        turma_selecionada = turmas[2]
    elif class_name == '1°D':
        turma_selecionada = turmas[3]

    with app.app_context():
        resultados = (db.session.query(turma_selecionada.nome, turma_selecionada.prova1, turma_selecionada.prova2,
                                       turma_selecionada.prova3, turma_selecionada.prova4, turma_selecionada.prova5,
                                       turma_selecionada.prova6, turma_selecionada.prova7, turma_selecionada.prova8,
                                       turma_selecionada.pm).all())
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
    return render_template('class_page.html', class_name=class_name, data=resultados,
                           estatisticas=lista_de_provas, tamanho=tamanho)


@app.route('/ranking/<class_id>', methods=['GET', 'POST'])
def ranking(class_id):
    resultados, turma_h1 = None, None
    if class_id == 'a':
        turma_h1 = "3° A"
        resultados = db.session.query(Terceiro_A.nome, getattr(Terceiro_A, 'pm')).order_by(
            getattr(Terceiro_A, 'pm').desc()).all()
    elif class_id == 'b':
        turma_h1 = "3° B"
        resultados = db.session.query(Terceiro_B.nome, getattr(Terceiro_B, 'pm')).order_by(
            getattr(Terceiro_B, 'pm').desc()).all()
    elif class_id == 'c':
        turma_h1 = "3° C"
        resultados = db.session.query(Terceiro_C.nome, getattr(Terceiro_C, 'pm')).order_by(
            getattr(Terceiro_C, 'pm').desc()).all()
    elif class_id == 'd':
        turma_h1 = "1° D"
        resultados = db.session.query(Primeiro_D.nome, getattr(Primeiro_D, 'pm')).order_by(
            getattr(Primeiro_D, 'pm').desc()).all()

    return render_template('ranking.html', data=resultados, class_id=class_id, turma_h1=turma_h1)


def exportar_csv(valor):
    global turmas
    turma_selecionada = turmas[3]
    if valor == 'a':
        turma_selecionada = turmas[0]
    elif valor == 'b':
        turma_selecionada = turmas[1]
    elif valor == 'c':
        turma_selecionada = turmas[2]
    elif valor == 'd':
        turma_selecionada = turmas[3]

    with app.app_context():
        resultados = (db.session.query(turma_selecionada.nome, turma_selecionada.prova1, turma_selecionada.prova2,
                                       turma_selecionada.prova3, turma_selecionada.prova4, turma_selecionada.prova5,
                                       turma_selecionada.prova6, turma_selecionada.prova7, turma_selecionada.prova8,
                                       turma_selecionada.pm).all())
    dataframe = DataFrame.from_records(resultados,
                                       columns=['Nome', '1°', '2°', '3°', '4°', '5°', '6°', '7°', '8°', 'PM'])
    dataframe.to_csv(f'Turma_{valor}.csv', index=False)

    email = Email(valor)


if __name__ == '__main__':
    app.run(debug=True)
