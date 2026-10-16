from encodings import normalize_encoding

from flask import Flask, render_template, request, redirect, url_for, session, flash
import fdb

app = Flask(__name__)
app.secret_key = ''
# ESTA PARTE ESTÁ FAZENDO A CONEXÃO COM O BANCO DE DADOS
def conectar():
    banco = fdb.connect(
        host= r'C:\Users\Aluno\Downloads\BANCO\BANCOGYMFLOW.FDB',
        user='SYSDBA',
        password='sysdba',
    )
    return banco

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if not senha_forte(senha):
            flash('A senha não atende aos criterios necesários')
            return redirect(url_for('cadastro'))

        banco = conectar()
        cursor = banco.cursor()

        cursor.execute('SELECT ID_USUARIO FROM WHERE EMAIL = ?', (email,))

        if cursor.fetchone():
            banco.close()
            flash('E-mail já cadastrado')
            return redirect(url_for('cadastro'))

        senha_hash = criar_hash(senha)

        cursor.execute("""INSERT INTO USUARIOS(NOME,EMAIL,SENHA,ATIVO,TENTATIVAS_LOGIN,BLOQUEADO) VALUES (?,?,?,1,0,0,0)""", (nome, email, senha_hash))

        banco.commit()
        banco.close()

        flash('Cadastro realizado com sucesso')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

def senha_forte(senha):
    maiuscula = False
    minuscula = False
    numero = False
    especial = False

    if len(senha) < 8:
        return False

    for caractere in senha:
        if caractere.isupper():
            maiuscula = True
        elif caractere.islower():
            minuscula = True
        elif caractere.isdigit():
            numero = True
        else:
            especial = True

    if maiuscula and minuscula and numero and especial:
        return True
    else:
        return False


@app.route('/entrar')
def entrar():
    email = request.form['email']
    senha = request.form['senha']

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""SELECT ID_USUARIO,NOME,SENHA,ATIVO,TENTATIVAS_LOGIN,BLOQUEADO FROM USUARIOS WHERE EMAIL = ?""", (email,))

    usuario = cursor.fetchone()

    if usuario is None:
        banco.close()
        flash('E-mail ou senha incorretos')
        return redirect(url_for('login'))

    if bloqueado:
        banco.close()
        flash('Usuário Bloqueado')
        return redirect(url_for('login'))

    if not ativo:
        banco.close()
        flash('Usuário Inativo')
        return redirect(url_for('login'))

    if criar_hash(senha) != senha_hash:
        tentativas +=1
        bloqueado = 1 if tentativas >= 3 else 0

        cursor.execute("""UPDATE USUARIOS SET TENTATIVAS_LOGIN = ?, BLOQUEADO = ? WHERE ID_USUARIO = ?""", (tentativas,bloqueado,id_usuario))

        banco.commit()
        banco.close()
        flash('Senha incorreta')
        return redirect(url_for('login'))

    cursor.execute("""UPDATE USUARIOS SET TENTATIVAS_LOGIN = 0 WHERE ID_USUARIO = ?""", (id_usuario))

    banco.commit()
    banco.close()


    session.clear()
    session['id_usuario'] = usuario
    session['usuario'] = nome

    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    if 'id_usuario' in session:
        return redirect(url_for('login'))

    session.clear()
    flash('Você saiu da sua conta.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


