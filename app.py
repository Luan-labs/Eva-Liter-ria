from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3
from ai import perguntar
import os
from werkzeug.utils import secure_filename
import docx
import PyPDF2

app = Flask(__name__)
app.secret_key = "segredo"

# -------------------------
# Configuração de uploads
# -------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt","pdf","docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------
# Banco de dados
# -------------------------
def conectar():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def criar_banco():
    conn = conectar()
    conn.execute("""CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS historias(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        titulo TEXT,
        conteudo TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS capitulos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        historia_id INTEGER,
        titulo TEXT,
        conteudo TEXT
    )""")
    conn.commit()
    conn.close()

criar_banco()

# -------------------------
# Login e registro
# -------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("editor.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_user", methods=["POST"])
def login_user():
    username = request.form["username"]
    password = request.form["password"]
    conn = conectar()
    user = conn.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username,password)).fetchone()
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
        conn.execute("INSERT INTO usuarios(username,password) VALUES(?,?)",(username,password))
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

# -------------------------
# Funções Literária
# -------------------------
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
Inclua: sinopse, protagonista e conflito principal
"""
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/continuar", methods=["POST"])
def continuar():
    texto = request.json["texto"]
    prompt = f"Continue a história abaixo mantendo coerência narrativa:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/melhorar", methods=["POST"])
def melhorar():
    texto = request.json["texto"]
    prompt = f"Melhore o estilo literário do texto abaixo, sem mudar o significado:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/traduzir_literal", methods=["POST"])
def traduzir_literal():
    texto = request.json["texto"]
    prompt = f"Traduza o texto abaixo para inglês exatamente como está:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/personagem", methods=["POST"])
def personagem():
    descricao = request.json.get("descricao","")
    prompt = f"Crie um personagem detalhado:\nDescrição: {descricao}\nInclua nome, idade, aparência, personalidade e história de fundo."
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

# -------------------------
# Funções Engenharia de Textos
# -------------------------
@app.route("/reformatar", methods=["POST"])
def reformatar():
    texto = request.json["texto"]
    prompt = f"Reformate o texto abaixo para melhor clareza e coesão:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/simplificar", methods=["POST"])
def simplificar():
    texto = request.json["texto"]
    prompt = f"Simplifique o texto abaixo mantendo o significado:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/expandir", methods=["POST"])
def expandir():
    texto = request.json["texto"]
    prompt = f"Expanda o texto abaixo adicionando detalhes e descrições:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

@app.route("/resumir", methods=["POST"])
def resumir():
    texto = request.json["texto"]
    prompt = f"Resuma o texto abaixo mantendo as ideias principais:\n{texto}"
    resposta = perguntar(prompt)
    return jsonify({"response": resposta})

# -------------------------
# Upload de arquivos
# -------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"mensagem":"Nenhum arquivo enviado"})
    
    file = request.files['file']
    if file.filename == "":
        return jsonify({"mensagem":"Nenhum arquivo selecionado"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conteudo = ""
        ext = filename.rsplit(".",1)[1].lower()
        
        try:
            if ext == "txt":
                with open(filepath, "r", encoding="utf-8") as f:
                    conteudo = f.read()
            elif ext == "docx":
                doc = docx.Document(filepath)
                conteudo = "\n".join([p.text for p in doc.paragraphs])
            elif ext == "pdf":
                with open(filepath,"rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    conteudo = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception as e:
            return jsonify({"mensagem":f"Erro ao ler o arquivo: {e}"})

        return jsonify({"conteudo":conteudo})
    else:
        return jsonify({"mensagem":"Formato de arquivo não permitido"})

# -------------------------
# Salvar e listar histórias e capítulos
# -------------------------
@app.route("/salvar_historia", methods=["POST"])
def salvar_historia():
    titulo = request.json["titulo"]
    conteudo = request.json["conteudo"]
    usuario = session.get("user","")
    conn = conectar()
    conn.execute("INSERT INTO historias(usuario,titulo,conteudo) VALUES(?,?,?)",(usuario,titulo,conteudo))
    conn.commit()
    conn.close()
    return jsonify({"mensagem":"História salva com sucesso!"})

@app.route("/salvar_capitulo", methods=["POST"])
def salvar_capitulo():
    historia_id = request.json["historia_id"]
    titulo = request.json["titulo"]
    conteudo = request.json["conteudo"]
    conn = conectar()
    conn.execute("INSERT INTO capitulos(historia_id,titulo,conteudo) VALUES(?,?,?)",(historia_id,titulo,conteudo))
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
    rows = conn.execute("SELECT id,titulo,conteudo FROM capitulos WHERE historia_id=?",(historia_id,)).fetchall()
    conn.close()
    capitulos = [{"id":r["id"], "titulo":r["titulo"], "conteudo":r["conteudo"]} for r in rows]
    return jsonify({"capitulos": capitulos})

# -------------------------
# Rodar servidor
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
