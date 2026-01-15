from __future__ import annotations

from abc import ABC, abstractmethod
from flask import Flask, request, jsonify, Response

from strategies import (
    EvaluationStrategy,
    QuizEvaluationStrategy,
    DialogEvaluationStrategy,
    ScenarioEvaluationStrategy,
    EvaluationResult,
)

app = Flask(__name__)

# Registry simples (memória) para armazenar atividades "deployed"
DEPLOYED_ACTIVITIES: dict[str, "Activity"] = {}


# ======================================================================
# PADRÃO DE CRIAÇÃO: FACTORY METHOD + STRATEGY
# ======================================================================
# Product abstrato: representa uma atividade DailyTalk
class Activity(ABC):
    def __init__(self, activity_id: str, base_url: str, evaluator: EvaluationStrategy):
        self.activity_id = activity_id
        self.base_url = base_url.rstrip("/")
        self.evaluator = evaluator  # Strategy

    @abstractmethod
    def get_launch_url(self) -> str:
        """Devolve o URL de lançamento desta atividade."""
        raise NotImplementedError

    def evaluate_submission(self, submission: dict) -> EvaluationResult:
        """Delegação para a Strategy: avalia e produz resultado."""
        return self.evaluator.evaluate(submission=submission, activity_id=self.activity_id)


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
        raise NotImplementedError


# Concrete Creators: cada fábrica sabe criar um tipo concreto de Activity e injetar a Strategy
class DialogActivityFactory(ActivityFactory):
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        return DialogActivity(activity_id, base_url, evaluator=DialogEvaluationStrategy())


class QuizActivityFactory(ActivityFactory):
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        return QuizActivity(activity_id, base_url, evaluator=QuizEvaluationStrategy())


class ScenarioActivityFactory(ActivityFactory):
    def create_activity(self, activity_id: str, base_url: str) -> Activity:
        return ScenarioActivity(activity_id, base_url, evaluator=ScenarioEvaluationStrategy())


# Função auxiliar para escolher a fábrica adequada
def get_factory(activity_type: str) -> ActivityFactory:
    """
    Seleciona a fábrica concreta com base no tipo de atividade.
    Se o tipo não for reconhecido, usa DialogActivityFactory como padrão.
    """
    activity_type = (activity_type or "").lower().strip()

    if activity_type == "quiz":
        return QuizActivityFactory()
    if activity_type == "scenario":
        return ScenarioActivityFactory()

    # "dialog" é o tipo por omissão (tolerante)
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

    def deploy_activity(self, activity_id: str, activity_type: str, base_url: str) -> Activity:
        # Seleciona a fábrica adequada
        factory = get_factory(activity_type)

        # Cria a atividade concreta (já com Strategy injetada)
        activity = factory.create_activity(activity_id, base_url)
        return activity


# ======================================================================
# ENDPOINTS EXISTENTES
# ======================================================================
@app.route("/")
def index():
    return """
    <h1>DailyTalk.pt - Activity Provider (Inven!RA)</h1>
    <p>Serviço de teste - Unidade 6 - Strategy method (APS)</p>
    <ul>
      <li><strong>config_url</strong>: <code>/config</code></li>
      <li><strong>json_params_url</strong>: <code>/json-params</code></li>
      <li><strong>user_url (deploy)</strong>: <code>/deploy?activityID=DTALK-DEMO-001&type=dialog</code></li>
      <li><strong>submit</strong>: <code>/submit</code> (POST JSON)</li>
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
        {"name": "difficulty", "type": "text/plain"},
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
    activity = facade.deploy_activity(activity_id, activity_type, base_url)

    # guarda no registry para permitir submissão/avaliação
    DEPLOYED_ACTIVITIES[activity_id] = activity

    launch_url = activity.get_launch_url()
    return Response(launch_url, mimetype="text/plain")


# ======================================================================
# NOVO ENDPOINT: SUBMISSÃO / AVALIAÇÃO (Strategy em funcionamento real)
# ======================================================================
@app.route("/submit", methods=["POST"])
def submit():
    """
    Payload esperado:
    {
      "activityID": "DTALK-DEMO-001",
      "submission": { ... }    # varia conforme o tipo da atividade
    }
    """
    payload = request.get_json(silent=True) or {}
    activity_id = payload.get("activityID")
    submission = payload.get("submission", {})

    if not activity_id:
        return jsonify({"error": "Missing activityID"}), 400

    # Tolerância: submission pode vir None / tipo errado
    if submission is None:
        submission = {}
    if not isinstance(submission, dict):
        return jsonify({"error": "Invalid submission: must be an object/dict"}), 400

    activity = DEPLOYED_ACTIVITIES.get(activity_id)
    if not activity:
        return jsonify({"error": f"Unknown activityID: {activity_id}. Deploy first."}), 404

    # Avaliação via Strategy (já passa activity_id internamente)
    result = activity.evaluate_submission(submission)

    # * Implementar aqui: registar analytics/progresso/logs
    return jsonify(
        {
            "activityID": activity_id,
            "score": result.score,
            "feedback": result.feedback,
            "metrics": result.metrics,
        }
    ), 200


@app.route("/analytics-list")
def analytics_list():
    data = {
        "qualAnalytics": [
            {"name": "Student activity profile", "type": "text/plain"},
            {"name": "Activity heat map",        "type": "URL"},
        ],
        "quantAnalytics": [
            {"name": "Total interações",              "type": "integer"},
            {"name": "Tempo na atividade (segundos)", "type": "integer"},
        ],
    }
    return jsonify(data)


# --------------------------------------------------------------------------------------------------------------
# Analytics de atividade (analytics_url) - POST /analytics  com  { "activityID": "..." }
#    » devolve lista de alunos com quantAnalytics e qualAnalytics
# --------------------------------------------------------------------------------------------------------------
@app.route("/analytics", methods=["POST"])
def analytics():
    payload = request.get_json(silent=True) or {}
    _activity_id = payload.get("activityID", "DTALK-DEMO-001")

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
