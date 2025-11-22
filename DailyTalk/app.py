from flask import Flask, request, jsonify, Response

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <h1>DailyTalk.pt - Activity Provider (Inven!RA)</h1>
    <p>Serviço de teste - Semana 1 (APS).</p>
    <ul>
      <li><strong>config_url</strong>: <code>/config</code></li>
      <li><strong>json_params_url</strong>: <code>/json-params</code></li>
      <li><strong>user_url (deploy)</strong>: <code>/deploy?activityID=DTALK-DEMO-001</code></li>
      <li><strong>analytics_url</strong>: <code>/analytics</code> (POST JSON)</li>
      <li><strong>analytics_list_url</strong>: <code>/analytics-list</code></li>
    </ul>
    """, 200, {"Content-Type": "text/html; charset=utf-8"}

# -------------------------------------------------------
# Página de configuração da atividade (config_url) -  GET /config  » HTML embutível
# -------------------------------------------------------

@app.route("/config")
def config_page():
    # HTML para leitura na Inven!RA
    html = """
    <div id="dailytalk-config">
      <h2>Configuração da atividade DailyTalk.pt</h2>

      <label for="scenario">Cenário DailyTalk</label><br>
      <input type="text" id="scenario" name="scenario"
             value="Chegada ao hostel em Lisboa"><br><br>

      <label for="language">Idioma principal</label><br>
      <input type="text" id="language" name="language"
             value="pt-PT"><br><br>

      <!-- Exemplo de parâmetro não visível, mas com name -->
      <input type="hidden" name="difficulty" value="normal">
    </div>
    """
    return Response(html, mimetype="text/html")


# --------------------------------------------------------------------------------------------------------------
# Lista de parâmetros da página de configuração - GET /json-params  » JSON [ { "name", "type" }, ... ]
# --------------------------------------------------------------------------------------------------------------
@app.route("/json-params")
def json_params():
    params = [
        {"name": "scenario",   "type": "text/plain"},
        {"name": "language",   "type": "text/plain"},
        {"name": "difficulty", "type": "text/plain"}
    ]
    return jsonify(params)


# --------------------------------------------------------------------------------------------------------------
# Deploy de atividade (user_url) » GET /deploy?activityID=... Resposta: URL (texto simples) para aceder à atividade
# --------------------------------------------------------------------------------------------------------------
@app.route("/deploy")
def deploy():
    activity_id = request.args.get("activityID", "DTALK-DEMO-001")

    # Base do serviço atual (ex.: https://aps-68v8.onrender.com/)
    base_url = request.url_root.rstrip("/")

    # URL que a Inven!RA usará depois para POST "Provide activity"
    launch_url = f"{base_url}/activity/{activity_id}"

    # Especificação diz que é um URL, não JSON » devolvemos text/plain
    return Response(launch_url, mimetype="text/plain")

# --------------------------------------------------------------------------------------------------------------
# Lista de analytics da atividade (analytics_list_url) - GET /analytics-list  → JSON com qualAnalytics e quantAnalytics
# --------------------------------------------------------------------------------------------------------------
@app.route("/analytics-list")
def analytics_list():
    data = {
        "qualAnalytics": [
            {"name": "Student activity profile", "type": "text/plain"},
            {"name": "Activity heat map",        "type": "URL"}
        ],
        "quantAnalytics": [
            {"name": "Total interações",                 "type": "integer"},
            {"name": "Tempo na atividade (segundos)",    "type": "integer"}
        ]
    }
    return jsonify(data)

# --------------------------------------------------------------------------------------------------------------
# Analytics de atividade (analytics_url) - POST /analytics  com  { "activityID": "..." }
#    » devolve lista de alunos com quantAnalytics e qualAnalytics
# --------------------------------------------------------------------------------------------------------------
@app.route("/analytics", methods=["POST"])
def analytics():
    payload = request.get_json(silent=True) or {}
    activity_id = payload.get("activityID", "DTALK-DEMO-001")

    # Dados de EXEMPLO – estáticos, só para a Semana 1
    response = [
        {
            "inveniraStdID": 1001,
            "quantAnalytics": [
                {
                    "name": "Total interações",
                    "type": "integer",
                    "value": 12
                },
                {
                    "name": "Tempo na atividade (segundos)",
                    "type": "integer",
                    "value": 210
                }
            ],
            "qualAnalytics": [
                {
                    "name": "Student activity profile",
                    "type": "text/plain",
                    "value": "Participou em todas as etapas do diálogo."
                },
                {
                    "name": "Activity heat map",
                    "type": "URL",
                    "value": "https://dailytalk.pt/APS/heatmap/1001"
                }
            ]
        },
        {
            "inveniraStdID": 1002,
            "quantAnalytics": [
                {
                    "name": "Total interações",
                    "type": "integer",
                    "value": 5
                },
                {
                    "name": "Tempo na atividade (segundos)",
                    "type": "integer",
                    "value": 95
                }
            ],
            "qualAnalytics": [
                {
                    "name": "Student activity profile",
                    "type": "text/plain",
                    "value": "Abandonou a atividade a meio do diálogo."
                },
                {
                    "name": "Activity heat map",
                    "type": "URL",
                    "value": "https://dailytalk.pt/APS/heatmap/1002"
                }
            ]
        }
    ]

    return jsonify(response)


# -------------------------------------------------------
# Entrada padrão para o gunicorn (Render usa: gunicorn app:app)
# -------------------------------------------------------
if __name__ == "__main__":
    # Para testes locais: 
    #   python -m venv venv
    #   pip install -r requirements.txt
    #   python app.py
    #     Running on http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
