from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3
from ai import perguntar  # Sua função que chama a API da Claude

app = Flask(__name__)
app.secret_key = "segredo"

# =========================
# BANCO DE DADOS
# =========================
def conectar():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def criar_banco():
    conn = conectar()
    # Usuários
    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    # Histórias
    conn.execute("""
    CREATE TABLE IF NOT EXISTS historias(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        titulo TEXT,
        conteudo TEXT
    )
    """)
    # Capítulos
    conn.execute("""
    CREATE TABLE IF NOT EXISTS capitulos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        historia_id INTEGER,
        titulo TEXT,
        conteudo TEXT
    )
    """)
    conn.commit()
    conn.close()

criar_banco()

# =========================
# ROTAS DE LOGIN / REGISTRO
# =========================
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("chat.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_user", methods=["POST"])
def login_user():
    username = request.form["username"]
    password = request.form["password"]
    conn = conectar()
    user = conn.execute("SELECT * FROM usuarios WHERE username=? AND password=?",
                        (username, password)).fetchone()
    conn.close()
    if user:
        session["user"] = username
        return redirect("/")
    return "Login inválido"

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    conn = conectar()
    try:
        conn.execute("INSERT INTO usuarios(username,password) VALUES(?,?)",
                     (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Usuário já existe"
    conn.close()
    session["user"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# ROTAS DE IA
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    resposta = perguntar(msg)
    return jsonify({"response": resposta})

@app.route("/ideia", methods=["POST"])
def ideia():
    tema = request.json.get("tema","")
    prompt = f"""
Crie uma ideia original para uma história.
Tema: {tema}
Inclua:
- sinopse
- protagonista
- conflito principal
"""
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/continuar", methods=["POST"])
def continuar():
    texto = request.json["texto"]
    prompt = f"""
Continue a história abaixo mantendo coerência narrativa:

{texto}
"""
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/melhorar", methods=["POST"])
def melhorar():
    texto = request.json["texto"]
    prompt = f"""
Melhore o estilo literário do texto abaixo, sem mudar o significado:

{texto}
"""
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/traduzir_literal", methods=["POST"])
def traduzir_literal():
    texto = request.json["texto"]
    prompt = f"""
Traduza o texto abaixo para inglês.
Regras:
- Traduza exatamente como está
- Não melhore o estilo
- Não explique nada
- Não adicione comentários

Texto:
{texto}
"""
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/personagem", methods=["POST"])
def personagem():
    descricao = request.json.get("descricao","")
    prompt = f"""
Crie um personagem detalhado para uma história.
Descrição: {descricao}
Inclua:
- nome
- idade
- aparência
- personalidade
- história de fundo
"""
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

# =========================
# ROTAS DE HISTÓRIAS E CAPÍTULOS
# =========================
@app.route("/salvar_historia", methods=["POST"])
def salvar_historia():
    titulo = request.json["titulo"]
    conteudo = request.json["conteudo"]
    usuario = session.get("user","")
    conn = conectar()
    conn.execute("INSERT INTO historias(usuario,titulo,conteudo) VALUES(?,?,?)",
                 (usuario,titulo,conteudo))
    conn.commit()
    conn.close()
    return jsonify({"mensagem":"História salva com sucesso!"})

@app.route("/salvar_capitulo", methods=["POST"])
def salvar_capitulo():
    historia_id = request.json["historia_id"]
    titulo = request.json["titulo"]
    conteudo = request.json["conteudo"]
    conn = conectar()
    conn.execute("INSERT INTO capitulos(historia_id,titulo,conteudo) VALUES(?,?,?)",
                 (historia_id,titulo,conteudo))
    conn.commit()
    conn.close()
    return jsonify({"mensagem":"Capítulo salvo com sucesso!"})

@app.route("/listar_historias")
def listar_historias():
    usuario = session.get("user","")
    conn = conectar()
    rows = conn.execute("SELECT id,titulo FROM historias WHERE usuario=?",(usuario,)).fetchall()
    conn.close()
    historias = [{"id":r["id"], "titulo":r["titulo"]} for r in rows]
    return jsonify({"historias": historias})

@app.route("/listar_capitulos", methods=["POST"])
def listar_capitulos():
    historia_id = request.json["historia_id"]
    conn = conectar()
    rows = conn.execute("SELECT id,titulo,conteudo FROM capitulos WHERE historia_id=?",
                        (historia_id,)).fetchall()
    conn.close()
    capitulos = [{"id":r["id"], "titulo":r["titulo"], "conteudo":r["conteudo"]} for r in rows]
    return jsonify({"capitulos": capitulos})

# =========================
# RODAR SERVIDOR
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
