import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

# Configura o nível de logging
logging.basicConfig(level=logging.DEBUG)

@dataclass(frozen=True)
class EvaluationResult:
    score: int
    feedback: str
    metrics: Dict[str, Any]

class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate(self, submission: Dict[str, Any], activity_id: str) -> EvaluationResult:
        """Calcula score, feedback e métricas para uma submissão."""
        raise NotImplementedError

class QuizEvaluationStrategy(EvaluationStrategy):
    def evaluate(self, submission: Dict[str, Any], activity_id: str) -> EvaluationResult:
        logging.debug(f"[QuizEvaluation] Avaliando atividade {activity_id} com dados: {submission}")
        # Conta acertos e tempo
        correct = int(submission.get("correct", 0))
        total = int(submission.get("total", max(correct, 1)))
        seconds = int(submission.get("seconds", 0))

        score = int((correct / total) * 100)
        feedback = f"Quiz: {correct}/{total} corretas."
        metrics = {"correct": correct, "total": total, "seconds": seconds, "kind": "quiz"}
        return EvaluationResult(score=score, feedback=feedback, metrics=metrics)

class DialogEvaluationStrategy(EvaluationStrategy):
    def evaluate(self, submission: Dict[str, Any], activity_id: str) -> EvaluationResult:
        logging.debug(f"[DialogEvaluation] Avaliando atividade {activity_id} com dados: {submission}")
        # Passos concluídos e escolhas corretas
        completed_steps = int(submission.get("completed_steps", 0))
        total_steps = int(submission.get("total_steps", max(completed_steps, 1)))
        good_choices = int(submission.get("good_choices", 0))

        score = min(100, int((completed_steps / total_steps) * 70 + good_choices * 10))
        feedback = "Diálogo: percurso concluído e escolhas avaliadas."
        metrics = {
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "good_choices": good_choices,
            "kind": "dialog",
        }
        return EvaluationResult(score=score, feedback=feedback, metrics=metrics)

class ScenarioEvaluationStrategy(EvaluationStrategy):
    def evaluate(self, submission: Dict[str, Any], activity_id: str) -> EvaluationResult:
        logging.debug(f"[ScenarioEvaluation] Avaliando atividade {activity_id} com dados: {submission}")
        # Decisões corretas e penalizações
        decisions_ok = int(submission.get("decisions_ok", 0))
        penalties = int(submission.get("penalties", 0))
        steps = int(submission.get("steps", 0))

        score = max(0, min(100, decisions_ok * 20 - penalties * 10))
        feedback = "Cenário: decisões e penalizações aplicadas."
        metrics = {"decisions_ok": decisions_ok, "penalties": penalties, "steps": steps, "kind": "scenario"}
        return EvaluationResult(score=score, feedback=feedback, metrics=metrics)
