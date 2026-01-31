import logging
from domain.activity import Activity

# Ativa logging se ainda não estiver configurado
logging.basicConfig(level=logging.DEBUG)

class ActivityProviderFacade:
    """
    Facade que fornece um ponto de entrada unificado para o provedor de atividades,
    coordenando serviços internos sem expor detalhes de implementação.
    """
    def deploy_activity(self, activity_id: str, activity: Activity) -> None:
        """
        Executa o processo de deploy da atividade.
        Aqui, simula uma integração com subsistemas externos,
        como notificação de criação ou coleta de métricas.
        """
        launch_url = activity.get_launch_url()
        logging.debug(f"[Facade] Atividade '{activity_id}' registrada no sistema externo.")
        logging.debug(f"[Facade] URL da atividade: {launch_url}")

        # Aqui poderia futuramente: enviar e-mail, registrar em banco, etc.
        # PARA TESTES:
        # self.email_service.send_activity_created(activity_id, launch_url)
        # self.analytics_client.register_new_activity(activity_id)
