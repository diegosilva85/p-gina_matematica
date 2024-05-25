from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pandas import DataFrame
from mural import Mural
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from math import floor
from pathlib import Path
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pyarrow
from base import Base, BaseProfessor
from acesso_database import adicionar_aluno, alunos_elite, atualizar_coroas, acrescentar_pm, media_alunos, \
    deletar_aluno, inserir_dados_prova, boss, estatisticas
from base_gastos import BaseGastos, Banco_de_dados

senha_sessao_flask = os.environ.get("senha_professor").strip("")
app = Flask(__name__)
app.config['SECRET_KEY'] = senha_sessao_flask
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///database_2024.db")
app.config['UPLOAD_FOLDER'] = 'static/upload'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

banco_gastos = Banco_de_dados()


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


class Gastos(BaseGastos):
    __tablename__ = 'gastos'


lista_turmas_db = [Terceiro_A, Terceiro_B, Terceiro_C, Primeiro_D]
senha = os.environ.get("senha_professor").strip("")

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
    classes = {'3ºA': '3ºA', '3ºB': '3ºB', '3ºC': '3ºC', '1ºD': '1ºD'}
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


@app.route('/boss/<class_id>', methods=['GET', 'POST'])
def lista_boss(class_id):
    turma_selecionada = selecionar_turma(class_id)
    lista_alunos = db.session.query(turma_selecionada.nome, turma_selecionada.coroa_ouro,
                                    turma_selecionada.coroa_prata, turma_selecionada.coroa_bronze,
                                    turma_selecionada.boss_vitoria, turma_selecionada.boss_total).order_by(
        turma_selecionada.nome)
    lista_turma = []
    for estudante in lista_alunos:
        coroas = sum(estudante[1:4])
        if coroas != 0:
            nome = estudante[0]
            boss_vitorias = estudante[4]
            boss_total = estudante[5]
            lista_estudante = [nome, coroas, boss_vitorias, boss_total]
            lista_turma.append(lista_estudante)

    return render_template("boss.html", estudantes=lista_turma)


@app.route('/boss_registro/<boss_turma>/<elite>', methods=['GET', 'POST'])
@login_required
def registro_boss(boss_turma, elite='não'):
    turma_tabela = selecionar_turma(boss_turma)
    alunos_registro = db.session.query(turma_tabela.nome, turma_tabela.coroa_ouro,
                                       turma_tabela.coroa_prata, turma_tabela.coroa_bronze,
                                       turma_tabela.boss_total, turma_tabela.id, turma_tabela.boss_elite,
                                       turma_tabela.coroas_elite)

    lista_alunos = []
    for aluno in alunos_registro:
        coroas = sum(aluno[1:4]) - aluno.boss_total
        if coroas != 0:
            if elite == 'sim' and aluno.boss_elite < aluno.coroas_elite:
                nome = aluno[0]
                dados = [nome, aluno[5]]
                lista_alunos.append(dados)
            elif elite == 'não':
                nome = aluno[0]
                dados = [nome, aluno[5]]
                lista_alunos.append(dados)

    if request.method == 'POST':
        if 'boss_pm' in request.form:
            boss_pm = request.form['boss_pm']
            boss_id = request.form['boss_id']
            boss(pm=boss_pm, turma=turma_tabela, id_boss=boss_id, db=db)
        if 'voltar' in request.form:
            return redirect(url_for('professor'))

    return render_template('boss_registro.html', lista_alunos=lista_alunos)


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
    if request.method == 'POST':
        if 'add' in request.form:
            aluno_adicionar = request.form['Id']
            turma_adicionar = request.form['class']
            turma_tabela = selecionar_turma(turma_adicionar)
            adicionar_aluno(turma=turma_tabela, nome=aluno_adicionar, db=db)
        if 'delete' in request.form:
            id_delete = request.form['Id']
            turma_deletar = request.form['turma']
            turma_tabela = selecionar_turma(turma_deletar)
            deletar_aluno(id_delete=id_delete, turma=turma_tabela, db=db)
        if 'start' in request.form:
            prova = request.form['prova']
            turma = request.form['turma']
            elite = request.form['elite']
            return redirect(url_for('notas_prova', prova=prova, turma=turma, elite=elite))
        if 'turma_mural' in request.form:
            mural_turma = request.form['turma_mural']
            prova_mural = request.form['prova_mural']
            imagem_mural = request.form['imagem_mural']
            elite_mural = request.form['elite_mural']
            return redirect(url_for('mural', mural_turma=mural_turma, prova_mural=prova_mural,
                                    imagem=imagem_mural, elite=elite_mural))
        if 'exportar_turma' in request.form:
            exportar = request.form['exportar_turma']
            exportar_csv(exportar)
        if 'criar_turmas' in request.form:
            criar_turmas(request.form['criar_turmas'])
        if 'alunos_elite' in request.form:
            elite = request.form['alunos_elite']
            turma_tabela = selecionar_turma(elite)
            alunos_elite(turma=turma_tabela, db=db)
        if 'boss_turma' in request.form:
            boss_turma = request.form['boss_turma']
            boss_elite = request.form['boss_elite']
            return redirect(url_for('registro_boss', boss_turma=boss_turma, elite=boss_elite))
        if 'arquivo' in request.form:
            return redirect(url_for('upload_arquivo'))
    return render_template('professor.html', logged_in=current_user.is_authenticated)


@app.route('/prova/<prova>/<turma>/<elite>', methods=['GET', 'POST'])
@login_required
def notas_prova(prova, turma, elite):
    turma_tabela = selecionar_turma(turma)
    if elite == "sim":
        resultados = db.session.query(turma_tabela.id, turma_tabela.nome).filter(
            turma_tabela.elite == "sim").order_by(turma_tabela.nome)
    else:
        resultados = db.session.query(turma_tabela.id, turma_tabela.nome).order_by(turma_tabela.nome)
    if request.method == 'POST':
        if "nota" in request.form:
            nota = request.form['nota']
            pm = request.form['pm']
            id_aluno = request.form['id']
            beneficios = request.form['beneficios']
            elite_form = request.form['elite']
            inserir_dados_prova(prova, nota, id_aluno, turma=turma_tabela, pm=pm, beneficio=beneficios,
                                elite=elite_form, db=db)
            acrescentar_pm(pm, id_pm=id_aluno, turma=turma_tabela, db=db)
        if "voltar" in request.form:
            return redirect(url_for("professor"))
    return render_template('prova.html', resultados=resultados, elite=elite)


@app.route('/mural/<mural_turma>/<prova_mural>/<imagem>/<elite>', methods=['GET', 'POST'])
def mural(mural_turma, prova_mural, imagem, elite="não"):
    turma_tabela = selecionar_turma(mural_turma)
    atributo_prova = getattr(turma_tabela, f'prova{prova_mural}')
    atributo_pm = getattr(turma_tabela, f'pm{prova_mural}')
    atributo_elite = getattr(turma_tabela, f"elite{prova_mural}")
    resultados_mural = db.session.query(turma_tabela.nome, atributo_prova, atributo_pm).filter(
        atributo_elite == elite).order_by(atributo_prova.desc()).all()
    if elite == "sim":
        fator = 1
        pm_adicional_ouro, pm_adicional_prata, pm_adicional_bronze = 9, 6, 3
    else:
        fator = 1 / 2
        pm_adicional_ouro, pm_adicional_prata, pm_adicional_bronze = 6, 4, 2

    lista_ouro, lista_prata, lista_bronze = [], [], []
    notas_mural = {'10': [], '9': [], '8': [], '7': [], '6': []}
    for aluno in resultados_mural:
        for chave in notas_mural.keys():
            nota = aluno[1] if aluno[1] is not None else 0
            if nota >= int(chave) and aluno[2] >= floor(fator * int(chave)) + 2 * fator:
                notas_mural[chave].append(aluno.nome)
                break

    for chave in notas_mural.keys():
        if notas_mural[chave] and not lista_ouro:
            lista_ouro = notas_mural[chave]
        elif notas_mural[chave] and not lista_prata:
            lista_prata = notas_mural[chave]
        elif notas_mural[chave] and not lista_bronze:
            lista_bronze = notas_mural[chave]

    if imagem == "Não":
        for estudante in lista_ouro:
            acrescentar_pm(pm_adicional_ouro, nome=estudante, turma=turma_tabela, db=db)
            atualizar_coroas(nome=estudante, turma=turma_tabela, valor=0,
                             prova=prova_mural, elite=elite, db=db)
        for estudante in lista_prata:
            acrescentar_pm(pm_adicional_prata, nome=estudante, turma=turma_tabela, db=db)
            atualizar_coroas(nome=estudante, turma=turma_tabela, valor=1,
                             prova=prova_mural, elite=elite, db=db)
        for estudante in lista_bronze:
            acrescentar_pm(pm_adicional_bronze, nome=estudante, turma=turma_tabela, db=db)
            atualizar_coroas(nome=estudante, turma=turma_tabela, valor=2,
                             prova=prova_mural, elite=elite, db=db)

    notas = [resultado[1] for resultado in resultados_mural if resultado[1] is not None]
    notas.sort(reverse=True)

    pm_prova = db.session.query(getattr(turma_tabela, 'pm')).all()
    pm_prova_lista = [valor[0] for valor in pm_prova if valor[0] is not None]
    dados = estatisticas(notas, pm_prova_lista)

    imagem_mural = Mural(mural_turma, prova_mural, dados[0], dados[2], dados[1], dados[3],
                         dados[4], lista_ouro, lista_prata, lista_bronze, elite)

    return render_template('mural.html', imagem=imagem_mural.caminho_static)


@app.route('/<class_name>', methods=['GET', 'POST'])
def class_page(class_name):
    turma_tabela = selecionar_turma(class_name)

    resultados_class_page = (db.session.query(turma_tabela.nome, turma_tabela.prova1, turma_tabela.prova2,
                                              turma_tabela.prova3, turma_tabela.prova4, turma_tabela.prova5,
                                              turma_tabela.prova6, turma_tabela.prova7, turma_tabela.prova8).order_by(
        turma_tabela.id).all())
    lista_de_provas = []

    for i in range(1, 9):
        atributo = getattr(turma_tabela, f"prova{i}")
        dados_turma = db.session.query(atributo).all()
        notas_validas = [dado[0] for dado in dados_turma if dado[0] is not None]
        if notas_validas:
            lista_de_provas.append(estatisticas(notas_validas))

    tamanho = len(lista_de_provas)
    medias = []
    for resultado in resultados_class_page:
        media_aluno = media_alunos(resultado)
        medias.append(media_aluno)
    return render_template('class_page.html', class_name=class_name, data=resultados_class_page,
                           estatisticas=lista_de_provas, tamanho=tamanho, media_alunos=medias)


@app.route('/ranking/<class_id>', methods=['GET', 'POST'])
def ranking(class_id):
    turma_tabela = selecionar_turma(class_id)
    resultados_ranking = db.session.query(turma_tabela.nome, getattr(turma_tabela, 'pm')).order_by(
        getattr(turma_tabela, 'pm').desc()).all()

    return render_template('ranking.html', data=resultados_ranking, class_id=class_id)


@app.route('/ranking_geral', methods=['GET', 'POST'])
def ranking_geral():
    turmas = [
        (Terceiro_A, Terceiro_A.pm),
        (Terceiro_B, Terceiro_B.pm),
        (Terceiro_C, Terceiro_C.pm)
    ]
    ranking_final = []
    for turma, atributo in turmas:
        ranking_turma = db.session.query(turma.nome, atributo).order_by(atributo).all()
        ranking_final.extend(ranking_turma)
    ordenados = sorted(ranking_final, key=lambda x: x[1], reverse=True)

    return render_template('ranking_geral.html', dados=ordenados)


@app.route("/manual", methods=['GET', 'POST'])
@login_required
def manual():
    manual_ajuste = None
    resultado = None
    if request.method == 'POST':
        if 'manual' in request.form:
            manual_ajuste = request.form['manual']
            if manual_ajuste:
                turma_selecionada = selecionar_turma(manual_ajuste)
                resultado = db.session.query(turma_selecionada).order_by(turma_selecionada.id).all()
        if 'voltar' in request.form:
            return redirect(url_for('professor'))
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
        if 'voltar' in request.form:
            return redirect(url_for('professor'))
        setattr(resultados, dado_alterar, request.form['valor'])
        db.session.commit()
        return render_template("aluno_alterar.html", nome=nome)
    return render_template("aluno_alterar.html", nome=nome)


def exportar_csv(valor):
    turma_sel = selecionar_turma(valor)
    resultados_csv = db.session.query(turma_sel.id, turma_sel.nome, turma_sel.prova1,
                                      turma_sel.prova2, turma_sel.prova3, turma_sel.prova4,
                                      turma_sel.prova5, turma_sel.prova6, turma_sel.prova7,
                                      turma_sel.prova8, turma_sel.pm1, turma_sel.pm2, turma_sel.pm3, turma_sel.pm4,
                                      turma_sel.pm5, turma_sel.pm6, turma_sel.pm7, turma_sel.pm8, turma_sel.pm,
                                      turma_sel.coroa1, turma_sel.coroa2, turma_sel.coroa3, turma_sel.coroa4,
                                      turma_sel.coroa5, turma_sel.coroa6, turma_sel.coroa7, turma_sel.coroa8,
                                      turma_sel.beneficios1, turma_sel.beneficios2, turma_sel.beneficios3,
                                      turma_sel.beneficios4, turma_sel.beneficios5, turma_sel.beneficios6,
                                      turma_sel.beneficios7, turma_sel.beneficios8, turma_sel.boss_vitoria,
                                      turma_sel.boss_total, turma_sel.coroa_ouro, turma_sel.coroa_prata,
                                      turma_sel.coroa_bronze).order_by(turma_sel.id).all()

    dataframe = DataFrame.from_records(resultados_csv, columns=['Id', 'Nome', '1°', '2°', '3°', '4°', '5°', '6°', '7°',
                                                                '8°', 'pm1', 'pm2', 'pm3', 'pm4', 'pm5', 'pm6', 'pm7',
                                                                'pm8', 'PM', "coroa1", "coroa2", "coroa3", "coroa4",
                                                                'coroa5', 'coroa6', 'coroa7', 'coroa8', 'beneficios1',
                                                                'beneficios2', 'beneficios3', 'beneficios4',
                                                                'beneficios5', 'beneficios6', 'beneficios7',
                                                                'beneficios8', 'BossV', 'BossT', 'Ouro', 'Prata',
                                                                'Bronze'])
    dataframe.to_csv(f'./static/Turma_{valor}.csv', index=False)

    # email = Email(valor)


# --------------------------------------- Servidor da aplicação Controle de gastos ----------------------------------- #
@app.route('/controle_gastos/add', methods=['GET', 'POST'])
def controle_gastos_add():
    dados = request.get_json()
    try:
        banco_gastos.adicionar(tabela=Gastos, gasto=dados)
        return jsonify({'status': 'Adição de registro bem sucedida!'}), 200
    except Exception as e:
        return jsonify({'status': str(e)}), 500


def gerar_lista_dicionarios(dados):
    linhas = []
    for item in dados:
        dados_gasto = {
            'id': item.id,
            'valor': item.valor,
            'data': item.data,
            'categoria': item.categoria,
            'parcelas': 1,
            'descricao': item.descricao,
            'mes_ano': item.mes_ano,
            'pagamento': item.pagamento
        }
        linhas.append(dados_gasto)
    return linhas


@app.route('/controle_gastos/categorias', methods=['GET', 'POST'])
def controle_gastos_categorias():
    dado = request.get_json()
    response = banco_gastos.linhas_categoria(tabela=Gastos, parametro=dado['parametro'])
    linhas = gerar_lista_dicionarios(response)
    return jsonify(linhas)


@app.route('/controle_gastos/mes', methods=['GET', 'POST'])
def controle_gastos_mes():
    dado = request.get_json()
    response = banco_gastos.linhas_mes(tabela=Gastos, mes_ano=dado['mes'])
    linhas = gerar_lista_dicionarios(response)
    return jsonify(linhas)


@app.route('/controle_gastos/total_mes', methods=['GET', 'POST'])
def controle_gastos_total_mes():
    dado = request.get_json()
    response = banco_gastos.total_mes(tabela=Gastos, mes_ano=dado['mes'])
    return jsonify(response)


@app.route('/controle_gastos/total_categoria', methods=['GET', 'POST'])
def controle_gastos_total_categoria():
    dado = request.get_json()
    response = banco_gastos.total_categoria(tabela=Gastos, parametro=dado['parametro'])
    return jsonify(response)


@app.route('/controle_gastos/deletar', methods=['GET', 'POST'])
def controle_gastos_delete():
    dados = request.get_json()
    banco_gastos.deletar(tabela=Gastos, id_gasto=int(dados['id_delete']))

@app.route('controle_gastos/todos', methods=['GET', 'POST'])
def controle_gastos_todos():
    dados = request.get_json()
    todos_gastos = banco_gastos.todos_gastos(tabela=Gastos)
    return jsonify(todos_gastos)


if __name__ == '__main__':
    app.run(debug=True)
