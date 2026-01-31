from domain.activity import DialogActivity, QuizActivity, ScenarioActivity
from strategies import DialogEvaluationStrategy, QuizEvaluationStrategy, ScenarioEvaluationStrategy

class ActivityFactory:
    """
    Factory Method para criação de Activities.
    Encapsula a lógica de instanciação e associação de estratégias.
    """
    @staticmethod
    def create(activity_type: str, activity_id: str, base_url: str):
        # Normaliza o tipo para caixa baixa e remove espaços
        normalized_type = (activity_type or "").strip().lower()

        if normalized_type == "quiz":
            return QuizActivity(
                activity_id=activity_id,
                base_url=base_url,
                evaluator=QuizEvaluationStrategy()
            )
        if normalized_type == "scenario":
            return ScenarioActivity(
                activity_id=activity_id,
                base_url=base_url,
                evaluator=ScenarioEvaluationStrategy()
            )
        # Por omissão ou tipo não reconhecido, utiliza DialogActivity
        return DialogActivity(
            activity_id=activity_id,
            base_url=base_url,
            evaluator=DialogEvaluationStrategy()
        )
