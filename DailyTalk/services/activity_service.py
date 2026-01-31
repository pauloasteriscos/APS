from factories.activity_factory import ActivityFactory
from facade.activity_provider_facade import ActivityProviderFacade

class ActivityService:
    """
    Application Service responsável por:
    - Criar Activities concretas (utilizando o Factory)
    - Manter o registo das Activities deployadas
    - Coordenar o processo de deploy com o ActivityProviderFacade

    Remove do app.py a lógica de coordenação direta, evitando o antipadrão Blob (God Object).
    """
    def __init__(self):
        # Armazena atividades atualmente deployadas, por ID
        self._activities = {}
        self._facade = ActivityProviderFacade()

    def deploy(self, activity_id: str, activity_type: str, base_url: str) -> str:
        if not activity_id or not activity_type:
            raise ValueError("Missing activity_id or type")
        # Garante base_url sem barra final
        base_url = base_url.rstrip("/")

        # Cria a atividade concreta apropriada (Strategy injetada)
        activity = ActivityFactory.create(
            activity_type=activity_type,
            activity_id=activity_id,
            base_url=base_url
        )
        # Armazena a atividade criada no registro interno
        self._activities[activity_id] = activity

        # Usa o Facade para efetuar o deploy (extensível para outras operações)
        self._facade.deploy_activity(activity_id, activity)

        # Retorna o URL de lançamento da atividade criada
        return activity.get_launch_url()

    def get_activity(self, activity_id: str):
        """Recupera uma atividade previamente deployada pelo ID."""
        return self._activities.get(activity_id)
