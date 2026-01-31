class SubmissionService:
    """
    Application Service responsável por tratar submissões de atividades,
    delegando a avaliação e agregando informações de retorno.
    """
    def __init__(self, activity_service):
        self.activity_service = activity_service

    def submit(self, payload: dict):
        activity_id = payload.get("activityID")
        if not activity_id:
            return {"error": "Missing activityID"}, 400

        # Garante que submission seja um dicionário válido
        submission = payload.get("submission", {})
        if submission is None:
            submission = {}
        if not isinstance(submission, dict):
            return {"error": "Invalid submission: must be an object/dict"}, 400

        activity = self.activity_service.get_activity(activity_id)
        if activity is None:
            return {"error": f"Unknown activityID: {activity_id}. Deploy first."}, 404

        # Avalia a submissão usando a Strategy da atividade
        result_obj = activity.evaluate_submission(submission)

        # Prepara a resposta com os dados de resultado
        result = {
            "activityID": activity_id,
            "score": result_obj.score,
            "feedback": result_obj.feedback,
            "metrics": result_obj.metrics,
        }
        return result, 200
