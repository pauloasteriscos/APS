from __future__ import annotations
from abc import ABC, abstractmethod
from strategies import EvaluationStrategy, EvaluationResult

class Activity(ABC):
    """
    Entidade de domínio que representa uma atividade DailyTalk.

    Responsabilidade:
    - Identidade da atividade (ID)
    - Geração do launch URL específico do tipo
    - Delegação da avaliação para a Strategy correspondente
    """
    def __init__(self, activity_id: str, base_url: str, evaluator: EvaluationStrategy):
        self.activity_id = activity_id
        # Remove barra final do base_url para consistência
        self.base_url = base_url.rstrip("/")
        self.evaluator = evaluator

    @abstractmethod
    def get_launch_url(self) -> str:
        """Retorna o URL de lançamento desta atividade."""
        raise NotImplementedError

    def evaluate_submission(self, submission: dict) -> EvaluationResult:
        """Avalia uma submissão delegando para a Strategy associada."""
        return self.evaluator.evaluate(submission=submission, activity_id=self.activity_id)

class DialogActivity(Activity):
    """Atividade de diálogo guiado."""
    def get_launch_url(self) -> str:
        return f"{self.base_url}/activity/dialog/{self.activity_id}"

class QuizActivity(Activity):
    """Atividade de questionário (quiz)."""
    def get_launch_url(self) -> str:
        return f"{self.base_url}/activity/quiz/{self.activity_id}"

class ScenarioActivity(Activity):
    """Atividade baseada em cenário (Erasmus+)."""
    def get_launch_url(self) -> str:
        return f"{self.base_url}/activity/scenario/{self.activity_id}"
