from flask import Flask, render_template_string, request, session, g
import random, sqlite3, os

app = Flask(__name__)
app.secret_key = "forca-unama-maria"

PALAVRAS = ["PYTHON", "UNAMA", "COMPUTADOR", "CODIGO", "FORCA", "ALUNO", "PROFESSOR", "BRASIL", "PARA", "SANTAREM"]

DB = "banco.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.execute("CREATE TABLE IF NOT EXISTS ranking (id INTEGER PRIMARY KEY, nome TEXT, resultado TEXT, tentativas_usadas INTEGER)")
        g.db.commit()
    return g.db

@app.teardown_appcontext
def fechar(e=None):
    db = g.pop("db", None)
    if db: db.close()

def novo_jogo():
    session["palavra"] = random.choice(PALAVRAS)
    session["certas"] = []
    session["erradas"] = []
    session["tentativas"] = 6
    session["nome"] = ""

HTML = """
<!DOCTYPE html>
<style>
body{font-family:Arial;text-align:center;background:linear-gradient(135deg,#aee2ff,#ffc0d9);padding:15px;margin:0;min-height:100vh}
.caixa{background:white;max-width:450px;margin:auto;padding:25px;border-radius:20px;box-shadow:0 10px 25px rgba(255,111,174,0.3);border:3px solid #ffb3d1}
.logo{font-size:50px}
.palavra{font-size:34px;letter-spacing:8px;margin:20px 0;color:#3a9ad9}
button{background:#ff6fae;color:white;border:none;padding:12px 20px;border-radius:10px;font-size:16px;width:100%;cursor:pointer}
button:hover{background:#ff8fbf}
input{font-size:18px;padding:10px;border:2px solid #aee2ff;border-radius:10px;text-align:center}
table{width:100%;margin-top:15px;border-collapse:collapse;font-size:14px}
th,td{padding:8px;border-bottom:1px solid #ffe0ee}
th{background:#e0f3ff;color:#ff6fae}
h1{color:#ff6fae}
</style>
<body>
<div class="caixa">
<div class="logo"></div>
<h1 style="margin:5px">Jogo da Forca</h1>
<div style="text-align:center;">
<svg width="180" height="210" viewBox="0 0 180 210">
<line x1="10" y1="200" x2="100" y2="200" stroke="#333" stroke-width="5"/>
<line x1="30" y1="200" x2="30" y2="10" stroke="#333" stroke-width="5"/>
<line x1="30" y1="10" x2="120" y2="10" stroke="#333" stroke-width="5"/>
<line x1="120" y1="10" x2="120" y2="40" stroke="#333" stroke-width="3"/>
{% if tentativas >= 1 %}<circle cx="120" cy="55" r="15" fill="none" stroke="#333" stroke-width="3"/>{% endif %}
{% if tentativas >= 2 %}<line x1="120" y1="70" x2="120" y2="120" stroke="#333" stroke-width="3"/>{% endif %}
{% if tentativas >= 3 %}<line x1="120" y1="85" x2="95" y2="105" stroke="#333" stroke-width="3"/>{% endif %}
{% if tentativas >= 4 %}<line x1="120" y1="85" x2="145" y2="105" stroke="#333" stroke-width="3"/>{% endif %}
{% if tentativas >= 5 %}<line x1="120" y1="120" x2="100" y2="155" stroke="#333" stroke-width="3"/>{% endif %}
{% if tentativas >= 6 %}<line x1="120" y1="120" x2="140" y2="155" stroke="#333" stroke-width="3"/>{% endif %}
</svg>
</div>
</div>
<!-- BONEQUINHO PENDURADO -->
<hr>
<h2 class="palavra">{{ exibida }}</h2>
<p> Tentativas: <b>{{ tentativas }}</b> | Letras usadas: {{ usadas }}</p>
<p><b>{{ mensagem }}</b></p>
{% if precisa_nome %}
<form method="post"><input name="nome" placeholder="Seu nome" required><br><br><button>Salvar no Ranking</button></form>
{% elif fim %}
<a href="/novo"><button>Jogar Novamente</button></a>
{% else %}
<form method="post"><input name="letra" maxlength="1" required autofocus placeholder="Letra" style="text-transform:uppercase;width:80px"><br><br><button>Tentar Letra</button></form>
{% endif %}
<h3> Ranking - Banco de Dados</h3>
<table><tr><th>Nome</th><th>Resultado</th><th>Tentativas</th></tr>
{% for r in ranking %}<tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td></tr>{% endfor %}
</table>
</div></body></html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    if "palavra" not in session: novo_jogo()
    db = get_db()
    palavra = session["palavra"]
    mensagem = ""
    fim = False
    precisa_nome = False

    if request.method == "POST":
        if "nome" in request.form and session.get("ganhou") is not None:
            resultado = "Ganhou " if session["ganhou"] else "Perdeu "
            usadas = 6 - session["tentativas"]
            db.execute("INSERT INTO ranking (nome, resultado, tentativas_usadas) VALUES (?,?,?)", (request.form["nome"], resultado, usadas))
            db.commit()
            session.pop("ganhou", None)
            session["nome"] = request.form["nome"]
        elif "letra" in request.form:
            letra = request.form.get("letra","").upper()
            if letra and letra not in session["certas"] + session["erradas"]:
                if letra in palavra:
                    session["certas"].append(letra)
                else:
                    session["erradas"].append(letra)
                    session["tentativas"] -= 1
                session.modified = True

    exibida = " ".join([l if l in session["certas"] else "_" for l in palavra])

    if "_" not in exibida.replace(" ",""):
        mensagem = " Você ganhou! Era " + palavra
        fim = True
        if "ganhou" not in session and not session.get("nome"):
            session["ganhou"] = True
            precisa_nome = True
    elif session["tentativas"] <= 0:
        mensagem = " Você perdeu! Era " + palavra
        exibida = " ".join(palavra)
        fim = True
        if "ganhou" not in session and not session.get("nome"):
            session["ganhou"] = False
            precisa_nome = True

    ranking = db.execute("SELECT nome, resultado, tentativas_usadas FROM ranking ORDER BY id DESC LIMIT 10").fetchall()
    return render_template_string(HTML, exibida=exibida, tentativas=session["tentativas"], usadas=", ".join(session["certas"]+session["erradas"]) or "Nenhuma", mensagem=mensagem, fim=fim, precisa_nome=precisa_nome, ranking=ranking)

@app.route("/novo")
def novo():
    novo_jogo()
    return index()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
