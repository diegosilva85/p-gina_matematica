import sqlite3
import csv
from flask import Flask, render_template, request, redirect, url_for
from mural import Mural
import numpy as np
from scipy.stats import mode
import os

app = Flask(__name__)
senha = os.environ.get("senha_professor").strip("")
print(senha)
database = 'database_2024.db'
login, prova, nota, turma, pm, id_aluno, id_class = None, None, None, None, None, None, None


def db_connection(function):  # Decorator Function to handle connections with the database
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        result = function(conn, cursor, *args, **kwargs)
        conn.commit()
        cursor.close()
        conn.close()
        return result

    return wrapper


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

    # Connect to the SQLite database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Perform a search query
    cursor.execute('SELECT * FROM Terceiro_A WHERE Nome LIKE ?', ('%' + search_term + '%',))
    search_results = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('aluno.html', search_results=search_results)


@db_connection
def add_entry(conn, cursor, turma_to_add, aluno):
    if 'turma' == 'd':
        turma_add = f'Primeiro_{turma_to_add.upper()}'
    else:
        turma_add = f'Terceiro_{turma_to_add.upper()}'
    add_query = f'INSERT INTO {turma_add} (Nome) VALUES (?)'
    data_to_insert = aluno
    cursor.execute(add_query, (data_to_insert,))


@db_connection
def delete_entry(conn, cursor, id_delete, turma_delete):
    if turma_delete == 'd':
        turma_delete = f'Primeiro_{turma_delete.upper()}'
    else:
        turma_delete = f'Terceiro_{turma_delete.upper()}'
    delete_query = f"DELETE FROM {turma_delete} WHERE id = ?"
    cursor.execute(delete_query, (id_delete,))


@db_connection
def update_entry(conn, cursor, prova, pm, nota, id_aluno, turma):
    num_prova = f'prova{prova}'
    if turma == 'd':
        turma_update = f'Primeiro_{turma.upper()}'
    else:
        turma_update = f'Terceiro_{turma.upper()}'
    cursor.execute(f"SELECT PM FROM {turma_update} WHERE id = ?", (id_aluno,))
    get_pm = cursor.fetchone()
    pm = int(pm) + get_pm[0]
    update_query = f"UPDATE {turma_update} SET {num_prova} = ?, PM = ? WHERE id = ?"
    cursor.execute(update_query, (nota, pm, id_aluno))


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
    return render_template('professor.html', login=login, prova=prova, class_id=id_class)


@app.route('/mural/<mural_turma>/<prova_mural>', methods=['GET', 'POST'])
def mural(mural_turma, prova_mural):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if mural_turma == 'd':
        turma_rnk = f'Primeiro_{mural_turma}'
    else:
        turma_rnk = f'Terceiro_{mural_turma}'
    cursor.execute(f'SELECT Nome, prova{prova_mural}, PM FROM {turma_rnk} ORDER BY {prova_mural} DESC')
    data = cursor.fetchall()
    notas = [notas[1] for notas in data if notas[1] is not None]
    pm_prova = [notas[2] for notas in data]
    media = np.mean(notas)
    moda = mode(notas)
    mediana = np.median(notas)
    desvio = np.std(notas)
    pm_medio = np.mean(pm_prova)
    nota_outro = None
    nota_prata = None
    lista_ouro = []
    lista_prata = []
    lista_bronze = []
    for i in range(10, 5, -1):
        lista_ouro = [item[0] for item in data if item[1] == i]
        if lista_ouro:
            nota_outro = i
            break
        else:
            pass
    for i in range(nota_outro - 1, 5, -1):
        lista_prata = [item[0] for item in data if item[1] == i]
        if lista_prata:
            nota_prata = i
            break
        else:
            pass
    for i in range(nota_prata - 1, 5, -1):
        lista_bronze = [item[0] for item in data if item[1] == i]
        if lista_bronze:
            break
        else:
            pass
    imagem_mural = Mural(mural_turma, prova_mural, round(media, 2), int(moda[0]), mediana, round(desvio, 2),
                         round(pm_medio, 2), lista_ouro, lista_prata, lista_bronze)
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('mural.html', imagem=imagem_mural.caminho_static)


@app.route('/<class_name>')
def class_page(class_name):
    global numeros
    # Connect to the SQLite database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if class_name == '1ºD':
        table = "Primeiro_D"
    else:
        table = f"Terceiro_{class_name[-1].upper()}"
    # Fetch data from the table
    cursor.execute(f'SELECT * FROM {table}')
    data = cursor.fetchall()
    lista_de_provas = []
    for i in range(1, 9):
        cursor.execute(f'SELECT prova{str(i)} FROM {table}')
        notas = cursor.fetchall()
        notas_validas = [item[0] for item in notas if item[0] is not None]
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
    return render_template('class_page.html', class_name=class_name, data=data,
                           estatisticas=lista_de_provas, tamanho=tamanho)


@app.route('/ranking/<class_id>', methods=['GET', 'POST'])
def ranking(class_id):
    if class_id == 'd':
        turma_rnk = f'Primeiro_{class_id}'
        turma_h1 = f'1º{class_id.upper()}'
    else:
        turma_rnk = f'Terceiro_{class_id}'
        turma_h1 = f'3º{class_id.upper()}'
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(f'SELECT Nome, PM FROM {turma_rnk} ORDER BY PM DESC')
    data = cursor.fetchall()
    return render_template('ranking.html', data=data, class_id=class_id, turma_h1=turma_h1)


if __name__ == '__main__':
    app.run(debug=True)
