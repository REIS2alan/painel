from flask import Flask, render_template, request, redirect, url_for, jsonify
import os

app = Flask(__name__)

# Lista de notificações em memória
notificacoes = []

# 🔹 Primeira tela -> escolher depósito
@app.route("/", methods=["GET", "POST"])
def escolher():
    if request.method == "POST":
        deposito = request.form["deposito"]
        return redirect(url_for("painel", deposito=deposito))
    return render_template("escolher.html")

# 🔹 Painel por depósito
@app.route("/painel/<deposito>")
def painel(deposito):
    todas = []
    for n in notificacoes:
        # Carro/Empilhadeira aparecem em todos os painéis
        if n["nome"].lower() in ["carro", "empilhadeira"]:
            todas.append(n)
        # Entrada/Saída aparecem apenas no depósito correspondente
        elif n["local"] == deposito:
            todas.append(n)

    todas_ordenadas = sorted(todas, key=lambda x: x["id"], reverse=True)
    return render_template("index.html", notificacoes=todas_ordenadas, deposito=deposito)

# 🔹 Escritório envia notificações
@app.route("/escritorio", methods=["GET", "POST"])
def escritorio():
    mensagem = ""
    if request.method == "POST":
        nome = request.form["nome"]  # Entrada, Saída, Carro, Empilhadeira
        local = request.form["local"]
        setor = request.form.get("setor", "")
        notificacoes.append({
            "id": len(notificacoes) + 1,
            "nome": nome,
            "local": local,
            "setor": setor,
            "visto": False,
            "status": None,
            "aceito": False
        })
        mensagem = f"✅ Notificação de {nome} para {local} enviada com sucesso!"

    nao_vistos = [n for n in notificacoes if not n["visto"]]
    return render_template("escritorio.html", notificacoes=nao_vistos, mensagem=mensagem)

# 🔹 API para adicionar notificações via fetch
@app.route("/nova", methods=["POST"])
def nova():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida"}), 400

    nome = data.get("nome")
    local = data.get("local")
    setor = data.get("setor", "")

    notificacoes.append({
        "id": len(notificacoes) + 1,
        "nome": nome,
        "local": local,
        "setor": setor,
        "visto": False,
        "status": None,
        "aceito": False
    })

    return jsonify({"success": True, "mensagem": f"✅ Notificação de {nome} para {local} enviada com sucesso!"})

# 🔹 Marcar Entrada/Saída como visto
@app.route("/visto/<int:notificacao_id>/<deposito>", methods=["POST"])
def marcar_visto(notificacao_id, deposito):
    for n in notificacoes:
        if n["id"] == notificacao_id:
            n["visto"] = True
            break
    return redirect(url_for("painel", deposito=deposito))

# 🔹 Atualizar status de Carro/Empilhadeira
@app.route("/atualizar_status/<int:notificacao_id>/<status>", methods=["POST"])
def atualizar_status(notificacao_id, status):
    deposito_redirect = None
    for n in notificacoes:
        if n["id"] == notificacao_id:
            n["status"] = status
            if status == "aceito":
                n["aceito"] = True  # Sinal para parar o áudio no front-end
            if status == "entregue":
                n["visto"] = True
            deposito_redirect = n["local"]
            break
    # Redireciona para o painel correto do depósito da notificação
    if not deposito_redirect:
        deposito_redirect = "D-06"  # fallback
    return redirect(url_for("painel", deposito=deposito_redirect))

if __name__ == "__main__":
    # 🔹 Usar porta do Render ou 5000 como padrão
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
