from flask import Flask, render_template, request, redirect, url_for, send_file
from pandas import DataFrame
from sendcsv import Email
from mural import Mural
import numpy as np
from scipy.stats import mode
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from math import floor
from pathlib import Path
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pyarrow


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
    pm1: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm2: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm3: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm4: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm5: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm6: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm7: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm8: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa1: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa2: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa3: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa4: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa5: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa6: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa7: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa8: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios1: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios2: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios3: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios4: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios5: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios6: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios7: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios8: Mapped[str] = mapped_column(nullable=True, server_default="-")
    boss_vitoria: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    boss_total: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_ouro: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_prata: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_bronze: Mapped[int] = mapped_column(nullable=True, server_default=str(0))


class BaseProfessor(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


senha_sessao_flask = os.environ.get("senha_professor").strip("")
app = Flask(__name__)
app.config['SECRET_KEY'] = senha_sessao_flask
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///database_2024.db")
app.config['UPLOAD_FOLDER'] = 'static/upload'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Terceiro_A(db.Model):
    __tablename__ = 'Terceiro_A'


class Terceiro_B(db.Model):
    __tablename__ = 'Terceiro_B'


class Terceiro_C(db.Model):
    __tablename__ = 'Terceiro_C'


class Primeiro_D(db.Model):
    __tablename__ = 'Primeiro_D'


class Professor(BaseProfessor, UserMixin):
    __tablename__ = 'professor'
    nome: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()


lista_turmas_db = [Terceiro_A, Terceiro_B, Terceiro_C, Primeiro_D]
senha = os.environ.get("senha_professor").strip("")
prova, nota, turma, pm, id_aluno, id_class = None, None, None, None, None, None

with app.app_context():
    db.create_all()
    # senha_hash = hash_and_salted_password = generate_password_hash(password=senha, method='pbkdf2:sha256',
    #                                                                salt_length=8)
    # professor = Professor(nome="diego", password=senha_hash)
    # db.session.add(professor)
    # db.session.commit()

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


def criar_turmas(letra_turma):
    global lista_turmas_db, terceiro_a, terceiro_b, terceiro_c, primeiro_d

    if letra_turma == 'a':
        for aluno_a in terceiro_a:
            novo_aluno = Terceiro_A(nome=aluno_a)
            db.session.add(novo_aluno)
            db.session.commit()
    elif letra_turma == 'b':
        for aluno_b in terceiro_b:
            novo_aluno = Terceiro_B(nome=aluno_b)
            db.session.add(novo_aluno)
            db.session.commit()
    elif letra_turma == 'c':
        for aluno_c in terceiro_c:
            novo_aluno = Terceiro_C(nome=aluno_c)
            db.session.add(novo_aluno)
            db.session.commit()
    else:
        for aluno_d in primeiro_d:
            novo_aluno = Primeiro_D(nome=aluno_d)
            db.session.add(novo_aluno)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Professor, user_id)


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
    search_term = aluno_id.upper()
    aluno_turma = {'3ºA': [], '3ºB': [], '3ºC': [], '1ºD': []}
    for chave in aluno_turma.keys():
        turma_busca = selecionar_turma(chave)
        resultados_busca = db.session.query(turma_busca.nome).filter(turma_busca.nome.like(f'%{search_term}%')).all()
        for resultados in resultados_busca:
            aluno_turma[chave].append(resultados[0].strip('\n'))

    return render_template('busca.html', resultados_busca=aluno_turma)


@app.route('/downloads', methods=['GET', 'POST'])
def downloads():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('downloads.html', files=files)


@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        return send_file(file_path, mimetype='application/octet-stream', as_attachment=True)
    except FileNotFoundError:
        file_path = Path("./static") / filename

    return send_file(file_path, mimetype='application/octet-stream', as_attachment=True)


@app.route('/upload_arquivo', methods=['GET', 'POST'])
def upload_arquivo():
    mensagem = ''
    if request.method == 'POST':
        file = request.files['arquivo']
        file.save(f'./static/upload/{file.filename}')
        mensagem = 'Arquivo enviado com sucesso!'
    return render_template('upload.html', mensagem=mensagem)


@app.route('/download_professor', methods=['GET', 'POST'])
@login_required
def download_professor():
    # files = os.listdir("./static")
    directory = "./static"
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return render_template('download_professor.html', files=files)


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


def inserir_dados_prova(prova_update, nota_update, id_update, turma_update, pm_update, calc=None, anular=None,
                        caderno=None, formula=None):
    turma_selecionada = selecionar_turma(turma_update)
    aluno_update = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_update)).scalar()
    setattr(aluno_update, f"prova{prova_update}", nota_update)
    setattr(aluno_update, f"pm{prova_update}", pm_update)
    if calc is not None:
        acrescentar_pm(-5, id_pm=id_update, turma_pm=turma_update)
        setattr(aluno_update, f'beneficios{prova_update}', "Calculadora")
    if anular is not None:
        acrescentar_pm(-10, id_pm=id_update, turma_pm=turma_update)
        setattr(aluno_update, f'beneficios{prova_update}', "Anular")
    if formula is not None:
        acrescentar_pm(-10, id_pm=id_update, turma_pm=turma_update)
        setattr(aluno_update, f'beneficios{prova_update}', "Fórmulas")
    if caderno is not None:
        acrescentar_pm(-15, id_pm=id_update, turma_pm=turma_update)
        setattr(aluno_update, f'beneficios{prova_update}', "Caderno")
    db.session.commit()


def acrescentar_pm(pm_adicional, id_pm=None, turma_pm=None, aluno_nome=None):
    aluno_pm = None
    turma_selecionada = selecionar_turma(turma_pm)
    if id_pm is not None:
        aluno_pm = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_pm)).scalar()
    elif aluno_nome is not None:
        aluno_pm = db.session.execute(
            db.select(turma_selecionada).where(turma_selecionada.nome == aluno_nome)).scalar()
    pm_atualizado = int(pm_adicional) + int(aluno_pm.pm)
    setattr(aluno_pm, "pm", pm_atualizado)
    db.session.commit()


def boss(pm_boss, turma_boss, id_boss):
    turma_selecionada = selecionar_turma(turma_boss)
    aluno_boss = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.id == id_boss)).scalar()
    total_boss = int(aluno_boss.boss_total) + 1
    if pm_boss == '15':
        numero_vitorias = 1 + int(aluno_boss.boss_vitoria)
        setattr(aluno_boss, "boss_vitoria", numero_vitorias)
        acrescentar_pm(15, id_pm=id_boss, turma_pm=turma_boss)
    elif pm_boss == '5':
        acrescentar_pm(5, id_pm=id_boss, turma_pm=turma_boss)
    setattr(aluno_boss, "boss_total", total_boss)
    db.session.commit()


def atualizar_coroas(nome_coroa, turma_coroa, valor_coroa, prova_coroa):
    turma_selecionada = selecionar_turma(turma_coroa)
    aluno_coroa = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.nome == nome_coroa)).scalar()
    if valor_coroa == 0:
        total_selecionada = int(aluno_coroa.coroa_ouro) + 1
        setattr(aluno_coroa, "coroa_ouro", total_selecionada)
        setattr(aluno_coroa, f"coroa{prova_coroa}", "ouro")
    elif valor_coroa == 1:
        total_selecionada = int(aluno_coroa.coroa_prata) + 1
        setattr(aluno_coroa, "coroa_prata", total_selecionada)
        setattr(aluno_coroa, f"coroa{prova_coroa}", "prata")
    elif valor_coroa == 2:
        total_selecionada = int(aluno_coroa.coroa_bronze) + 1
        setattr(aluno_coroa, "coroa_bronze", total_selecionada)
        setattr(aluno_coroa, f"coroa{prova_coroa}", "bronze")
    db.session.commit()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        if 'Password' in request.form:
            professor_login = db.session.execute(db.select(Professor).where(Professor.nome == "diego")).scalar()
            password = request.form['Password']
            if check_password_hash(professor_login.password, password):
                login_user(professor_login)
                return redirect(url_for("professor"))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/professor', methods=['GET', 'POST'])
@login_required
def professor():
    calculadora, anular, formula, caderno = None, None, None, None
    global prova, nota, turma, pm, id_aluno, id_class, senha
    if request.method == 'POST':
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
            if 'calc' in request.form:
                calculadora = request.form['calc']
            if 'anular' in request.form:
                anular = request.form['anular']
            if 'formula' in request.form:
                formula = request.form['formula']
            if 'caderno' in request.form:
                caderno = request.form['caderno']
            inserir_dados_prova(prova, nota, id_aluno, turma, pm, calc=calculadora, anular=anular, formula=formula,
                                caderno=caderno)
            acrescentar_pm(pm, id_pm=id_aluno, turma_pm=turma)
        if 'ranking' in request.form:
            id_class = request.form['ranking']
            return redirect(url_for('ranking', class_id=id_class))
        if 'turma_mural' in request.form:
            mural_turma = request.form['turma_mural']
            prova_mural = request.form['prova_mural']
            return redirect(url_for('mural', mural_turma=mural_turma, prova_mural=prova_mural))
        if 'exportar_turma' in request.form:
            exportar = request.form['exportar_turma']
            exportar_csv(exportar)
        if 'criar_turmas' in request.form:
            criar_turmas(request.form['criar_turmas'])
        if 'boss_turma' in request.form:
            boss_pm = request.form['boss_pm']
            boss_turma = request.form['boss_turma']
            boss_id = request.form['boss_id']
            boss(boss_pm, boss_turma, boss_id)
        if 'arquivo' in request.form:
            return redirect(url_for('upload_arquivo'))
    return render_template('professor.html', prova=prova, class_id=id_class,
                           logged_in=current_user.is_authenticated)


@app.route('/mural/<mural_turma>/<prova_mural>', methods=['GET', 'POST'])
def mural(mural_turma, prova_mural):
    prova_mural_banco = f'prova{prova_mural}'
    turma_selecionada = selecionar_turma(mural_turma)
    resultados_mural = db.session.query(turma_selecionada.nome, getattr(turma_selecionada, prova_mural_banco),
                                        getattr(turma_selecionada, f'pm{prova_mural}')).order_by(
        getattr(turma_selecionada, prova_mural_banco).desc()).all()

    notas = [resultado[1] for resultado in resultados_mural if resultado[1] is not None]
    notas.sort(reverse=True)

    nota_ouro = None
    nota_prata = None
    lista_ouro = []
    lista_nao_ouro = []
    lista_prata = []
    lista_nao_prata = []
    lista_bronze = []
    for i in range(10, 5, -1):
        if lista_nao_ouro:
            for nao_ouro in lista_nao_ouro:
                if int(nao_ouro[2]) >= floor(i / 2 + 1):
                    lista_ouro.append(nao_ouro[0])
                    lista_nao_ouro.remove(nao_ouro)
        lista_ouro.extend([item[0] for item in resultados_mural if item[1] == i and item[2] >= floor(i / 2 + 1)])
        lista_nao_ouro.extend([item for item in resultados_mural if item[1] == i and item[2] < floor(i / 2 + 1)])
        if lista_ouro:
            for estudante in lista_ouro:
                acrescentar_pm(9, aluno_nome=estudante, turma_pm=mural_turma)
                atualizar_coroas(nome_coroa=estudante, turma_coroa=mural_turma, valor_coroa=0, prova_coroa=prova_mural)
            nota_ouro = i
            break
    if nota_ouro is None:
        pass
    else:
        for j in range(nota_ouro - 1, 5, -1):
            if lista_nao_prata:
                for nao_prata in lista_nao_prata:
                    if int(nao_prata[2]) >= floor(j / 2 + 1):
                        lista_prata.append(nao_prata[0])
                        lista_nao_prata.remove(nao_prata)
            lista_prata.extend([item[0] for item in resultados_mural if item[1] == j and item[2] >= floor(j / 2 + 1)])
            lista_nao_prata.extend([item for item in resultados_mural if item[1] == j and item[2] < floor(j / 2 + 1)])
            if lista_prata:
                for nao_ouro in lista_nao_ouro:
                    if int(nao_ouro[2]) >= floor(j / 2 + 1):
                        lista_prata.append(nao_ouro[0])
                        lista_nao_ouro.remove(nao_ouro)
                for estudante_2 in lista_prata:
                    acrescentar_pm(6, aluno_nome=estudante_2, turma_pm=mural_turma)
                    atualizar_coroas(nome_coroa=estudante_2, turma_coroa=mural_turma, valor_coroa=1,
                                     prova_coroa=prova_mural)
                nota_prata = j
                break
        if nota_prata is None:
            pass
        else:
            for k in range(nota_prata - 1, 5, -1):
                lista_bronze = [item[0] for item in resultados_mural if item[1] == k and item[2] >= floor(k / 2 + 1)]
                if lista_bronze:
                    for nao_ouro in lista_nao_ouro:
                        if int(nao_ouro[2]) >= floor(k / 2 + 1):
                            lista_bronze.append(nao_ouro[0])
                    for nao_prata in lista_nao_prata:
                        if int(nao_prata[2]) >= floor(k / 2 + 1):
                            lista_bronze.append(nao_prata[0])
                    for estudante_3 in lista_bronze:
                        acrescentar_pm(3, aluno_nome=estudante_3, turma_pm=mural_turma)
                        atualizar_coroas(nome_coroa=estudante_3, turma_coroa=mural_turma, valor_coroa=2,
                                         prova_coroa=prova_mural)
                    break

    pm_prova = db.session.query(getattr(turma_selecionada, 'pm')).all()
    pm_prova_lista = [valor[0] for valor in pm_prova if valor[0] is not None]
    media = round(np.mean(notas), 2)
    try:
        moda = int(mode(notas)[0])
    except ValueError:
        moda = 0
    mediana = np.median(notas)
    desvio = round(np.std(notas), 2)
    pm_medio = round(np.mean(pm_prova_lista), 2)

    imagem_mural = Mural(mural_turma, prova_mural, media, moda, mediana, desvio,
                         pm_medio, lista_ouro, lista_prata, lista_bronze)

    return render_template('mural.html', imagem=imagem_mural.caminho_static)


@app.route('/<class_name>', methods=['GET', 'POST'])
def class_page(class_name):
    turma_selecionada = selecionar_turma(class_name)

    resultados_class_page = (db.session.query(turma_selecionada.id, turma_selecionada.nome, turma_selecionada.prova1,
                                              turma_selecionada.prova2, turma_selecionada.prova3,
                                              turma_selecionada.prova4, turma_selecionada.prova5,
                                              turma_selecionada.prova6,
                                              turma_selecionada.prova7, turma_selecionada.prova8,
                                              turma_selecionada.pm).order_by(turma_selecionada.id).all())
    lista_de_provas = []

    for i in range(1, 9):
        atributo = getattr(turma_selecionada, f"prova{i}")
        dados_turma = db.session.query(atributo).all()
        notas_validas = [dado[0] for dado in dados_turma if dado[0] is not None]
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


@app.route("/manual", methods=['GET', 'POST'])
@login_required
def manual():
    manual_ajuste = None
    resultado = None
    if request.method == 'POST':
        manual_ajuste = request.form['manual']
        if manual_ajuste:
            turma_selecionada = selecionar_turma(manual_ajuste)
            resultado = db.session.query(turma_selecionada).order_by(turma_selecionada.id).all()
    return render_template("manual.html", manual=manual_ajuste, resultados=resultado, logged_in=True)


@app.route("/aluno_alterar/<nome>/<turma>", methods=['GET', 'POST'])
@login_required
def aluno_alterar(nome, turma):
    turma_selecionada = selecionar_turma(turma)
    resultados = db.session.execute(db.select(turma_selecionada).where(turma_selecionada.nome == nome)).scalar()
    nome = resultados.nome
    dado_alterar = None
    if request.method == 'POST':
        if 'prova_aluno' in request.form and request.form['prova_aluno'] != "":
            dado_alterar = request.form['prova_aluno']
        if 'pm_aluno' in request.form and request.form['pm_aluno'] != "":
            dado_alterar = request.form['pm_aluno']
        if 'coroa_aluno' in request.form and request.form['coroa_aluno'] != "":
            dado_alterar = request.form['coroa_aluno']
        if 'beneficio_aluno' in request.form and request.form['beneficio_aluno'] != "":
            dado_alterar = request.form['beneficio_aluno']
        if 'boss_aluno' in request.form and request.form['boss_aluno'] != "":
            dado_alterar = request.form['boss_aluno']
        if "coroas_aluno" in request.form and request.form['coroas_aluno'] != "":
            dado_alterar = request.form['coroas_aluno']

        setattr(resultados, dado_alterar, request.form['valor'])
        db.session.commit()
        return render_template("aluno_alterar.html", nome=nome)
    return render_template("aluno_alterar.html", nome=nome)


def exportar_csv(valor):
    turma_sel = selecionar_turma(valor)
    resultados_csv = db.session.query(turma_sel).order_by(turma_sel.id).all()
    dataframe = DataFrame([resultado.__dict__ for resultado in resultados_csv])
    dataframe = dataframe.drop(columns=['_sa_instance_state'], errors='ignore')
    # dataframe = DataFrame(resultados_csv.__dict__)
    # resultados_csv = db.session.query(turma_sel.id, turma_sel.nome, turma_sel.prova1,
    #                                   turma_sel.prova2, turma_sel.prova3, turma_sel.prova4,
    #                                   turma_sel.prova5, turma_sel.prova6, turma_sel.prova7,
    #                                   turma_sel.prova8, turma_sel.pm1, turma_sel.pm2, turma_sel.pm3, turma_sel.pm4,
    #                                   turma_sel.pm5, turma_sel.pm6, turma_sel.pm7, turma_sel.pm8, turma_sel.pm,
    #                                   turma_sel.coroa1, turma_sel.coroa2, turma_sel.coroa3, turma_sel.coroa4,
    #                                   turma_sel.coroa5, turma_sel.coroa6, turma_sel.coroa7, turma_sel.coroa8,
    #                                   turma_sel.beneficios1, turma_sel.beneficios2, turma_sel.beneficios3,
    #                                   turma_sel.beneficios4, turma_sel.beneficios5, turma_sel.beneficios6,
    #                                   turma_sel.beneficios7, turma_sel.beneficios8, turma_sel.boss_vitoria,
    #                                   turma_sel.boss_total, turma_sel.coroa_ouro, turma_sel.coroa_prata,
    #                                   turma_sel.coroa_bronze).all()
    #
    # dataframe = DataFrame.from_records(resultados_csv, columns=['Id', 'Nome', '1°', '2°', '3°', '4°', '5°', '6°', '7°',
    #                                                             '8°', 'pm1', 'pm2', 'pm3', 'pm4', 'pm5', 'pm6', 'pm7',
    #                                                             'pm8', 'PM', "coroa1", "coroa2", "coroa3", "coroa4",
    #                                                             'coroa5', 'coroa6', 'coroa7', 'coroa8', 'beneficios1',
    #                                                             'beneficios2', 'beneficios3', 'beneficios4',
    #                                                             'beneficios5', 'beneficios6', 'beneficios7',
    #                                                             'beneficios8', 'BossV', 'BoosT', 'Ouro', 'Prata',
    #                                                             'Bronze'])
    dataframe.to_csv(f'Turma_{valor}.csv', index=False)

    email = Email(valor)


if __name__ == '__main__':
    app.run(debug=True)
