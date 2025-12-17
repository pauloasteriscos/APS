from flask import Flask, request, jsonify, Response
from abc import ABC, abstractmethod  # Para o padrão Factory Method

app = Flask(__name__)

# ======================================================================
# PADRÃO DE CRIAÇÃO: FACTORY METHOD
# ======================================================================
# Product abstrato: representa uma atividade DailyTalk
class Activity(ABC):
    def __init__(self, activity_id: str, base_url: str):
        self.activity_id = activity_id
        self.base_url = base_url.rstrip("/")

    @abstractmethod
    def get_launch_url(self) -> str:
        """Devolve o URL de lançamento desta atividade."""
        pass


# Concrete Products: diferentes tipos de atividade
class DialogActivity(Activity):
    def get_launch_url(self) -> str:
        # Exemplo de URL para diálogo guiado
        return f"{self.base_url}/activity/dialog/{self.activity_id}"


class QuizActivity(Activity):
    def get_launch_url(self) -> str:
        # Exemplo de URL para atividade de escolhas múltiplas
        return f"{self.base_url}/activity/quiz/{self.activity_id}"


class ScenarioActivity(Activity):
    def get_launch_url(self) -> str:
        # Exemplo de URL para cenário Erasmus+ genérico
        return f"{self.base_url}/activity/scenario/{self.activity_id}"


# Creator abstrato: define o factory method
class ActivityFactory(ABC):
    @abstractmethod
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        """Factory Method: cria uma Activity concreta."""
        pass


# Concrete Creators: cada fábrica sabe criar um tipo concreto de Activity
class DialogActivityFactory(ActivityFactory):
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        return DialogActivity(activity_id, base_url)


class QuizActivityFactory(ActivityFactory):
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        return QuizActivity(activity_id, base_url)


class ScenarioActivityFactory(ActivityFactory):
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        return ScenarioActivity(activity_id, base_url)


# Função auxiliar para escolher a fábrica adequada
def get_factory(activity_type: str) -> ActivityFactory:
    """
    Seleciona a fábrica concreta com base no tipo de atividade.
    Se o tipo não for reconhecido, usa DialogActivityFactory como padrão.
    """
    activity_type = (activity_type or "").lower()

    if activity_type == "quiz":
        return QuizActivityFactory()
    elif activity_type == "scenario":
        return ScenarioActivityFactory()
    else:
        # "dialog" é o tipo por omissão
        return DialogActivityFactory()


# ======================================================================
# PADRÃO ESTRUTURAL: FACADE (GoF)
# ======================================================================
# Fornece uma interface unificada para um conjunto de interfaces no subsistema,
# desacoplando a camada REST da lógica de criação de atividades.
class ActivityProviderFacade:
    """
    Facade que fornece um ponto de entrada unificado para o Activity Provider,
    coordenando serviços internos sem implementar lógica de negócio.
    """

    def deploy_activity(self, activity_id: str, activity_type: str, base_url: str) -> str:
        # Seleciona a fábrica adequada
        factory = get_factory(activity_type)

        # Cria a atividade concreta
        activity = factory.create_activity(activity_id, base_url)

        # Obtém o URL de lançamento
        return activity.get_launch_url()

# ======================================================================
# ENDPOINTS EXISTENTES
# ======================================================================
@app.route("/")
def index():
    return """
    <h1>DailyTalk.pt - Activity Provider (Inven!RA)</h1>
    <p>Serviço de teste - Secção 5 - Facade (APS).</p>
    <ul>
      <li><strong>config_url</strong>: <code>/config</code></li>
      <li><strong>json_params_url</strong>: <code>/json-params</code></li>
      <li><strong>user_url (deploy)</strong>: <code>/deploy?activityID=DTALK-DEMO-001&type=dialog</code></li>
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
    activity_type = request.args.get("type", "dialog")
    base_url = request.url_root.rstrip("/")

    # Usa o Facade
    facade = ActivityProviderFacade()
    launch_url = facade.deploy_activity(activity_id, activity_type, base_url)

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

    # Dados de EXEMPLO – estáticos, para Semana 4 - Factory Method
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
                    "value": "http://dailytalk.pt/APS/heatmap/1001"
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
                    "value": "http://dailytalk.pt/APS/heatmap/1002"
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
