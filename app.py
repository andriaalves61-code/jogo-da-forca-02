from flask import Flask, render_template, request, session, redirect, url_for
import random
import os

app = Flask(name)
app.secret_key = "wathy22"

palavras_por_categoria = {
  "Filme": {
    "TITANIC": "Navio gigante que afundou no filme",
    "AVATAR": "Filme com pessoas azuis em outro planeta",
    "SHREK": "Ogro verde que mora no pantano",
    "FROZEN": "Filme da Elsa que canta Let It Go",
    "BARBIE": "Boneca loira que virou filme rosa",
    "VINGADORES": "Grupo de herois da Marvel"
  },
  "Serie": {
    "STRANGER": "Serie da Netflix com o mundo invertido",
    "WANDINHA": "Menina da Familia Addams na Netflix",
    "DARK": "Serie alema sobre viagem no tempo",
    "ROUND": "Serie coreana com jogo, nome em ingles e 1 palavra"
  },
  "Musica": {
    "ANITTA": "Cantora brasileira famosa no mundo todo",
    "BEYONCE": "Cantora de Single Ladies",
    "SHAKIRA": "Cantora de Waka Waka",
    "SERTANEJO": "Estilo musical muito tocado no Para"
  },
  "Comida": {
    "PIPOCA": "A gente come vendo filme",
    "ACAI": "Fruta roxa muito famosa no Para",
    "PIZZA": "Comida redonda com queijo",
    "BRIGADEIRO": "Docinho de chocolate de festa"
  },
  "Animal": {
    "CACHORRO": "Melhor amigo do homem",
    "GATO": "Animal que mia e gosta de dormir",
    "ELEFANTE": "Maior animal terrestre, tem tromba",
    "TUCANO": "Passarinho com bico colorido"
  },
  "Curso": {
    "PYTHON": "Linguagem de programacao do curso",
    "UNAMA": "Sua faculdade",
    "CODING": "Outro nome para programacao",
    "COMPUTADOR": "Maquina que usamos para programar"
  }
}

ranking = []

def novo_jogo():
    categoria = random.choice(list(palavras_por_categoria.keys()))
    palavra = random.choice(list(palavras_por_categoria[categoria].keys()))
    dica = palavras_por_categoria[categoria][palavra]
    session["categoria"] = categoria
    session["palavra"] = palavra
    session["dica"] = dica
    session["tentativas"] = 6
    session["certas"] = []
    session["erradas"] = []
    session["msg"] = ""
    session["fim"] = False

@app.route("/", methods=["GET", "POST"])
def index():
    if "nome" not in session:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            cor = request.form.get("cor", "Rosa")
            if nome:
                session["nome"] = nome
                session["cor"] = cor
                novo_jogo()
                return redirect(url_for("index"))
        return render_template("index.html", logado=False)

    if request.form.get("acao") == "novo":
        novo_jogo()
        return redirect(url_for("index"))
    if request.form.get("acao") == "sair":
        session.clear()
        return redirect(url_for("index"))

    if request.method == "POST" and not session.get("fim"):
        letra = request.form.get("letra", "").upper()
        palavra = session["palavra"]
        certas = session.get("certas", [])
        erradas = session.get("erradas", [])
        if letra and letra not in certas and letra not in erradas:
            if letra in palavra:
                certas.append(letra)
                session["certas"] = certas
                session["msg"] = "Acertou!"
            else:
                erradas.append(letra)
                session["erradas"] = erradas
                session["tentativas"] -= 1
                session["msg"] = "Errou! Tente de novo"
            ganhou = all(l in certas for l in palavra)
            if ganhou:
                session["msg"] = f"Parabens, {session['nome']}! Voce ganhou!"
                session["fim"] = True
                ranking.insert(0, {"nome": session["nome"], "resultado": "Ganhou", "palavra": palavra})
            elif session["tentativas"] <= 0:
                session["msg"] = f"Perdeu! A palavra era: {palavra}"
                session["fim"] = True
                ranking.insert(0, {"nome": session["nome"], "resultado": "Perdeu", "palavra": palavra})
        return redirect(url_for("index"))

    palavra = session.get("palavra", "")
    certas = session.get("certas", [])
    exibicao = " ".join([l if l in certas else "_" for l in palavra])
    return render_template("index.html", logado=True, nome=session.get("nome"), cor=session.get("cor"),
        categoria=session.get("categoria"), dica=session.get("dica"), exibicao=exibicao,
        tentativas=session.get("tentativas", 6), erradas=session.get("erradas", []),
        msg=session.get("msg", ""), fim=session.get("fim", False), ranking=ranking)

if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
