# DailyTalk.pt
Aluno: Paulo Silva - Nº 2501478  
Ano letivo: 2025
2501478@estudante.uab.pt

GIT:
https://github.com/pauloasteriscos/APS

URL do serviço ativo:  
https://aps-68v8.onrender.com

----------------------------------------------------------------------------------------------------------------------------------
# Unidade Curricular: APS - Arquitetura e Padrões de Software, da Universidade Aberta.
## Descrição:

**Activity Provider**
O objetivo é implementar os Web Services RESTful necessários para que a plataforma **Inven!RA** possa:

- Obter a página de configuração da atividade;  
- Recolher os parâmetros configuráveis;  
- Efetuar o deploy da atividade;  
- Consultar a lista de analytics;   
- Obter os analytics registados por nós estudantes.  

O serviço está alojado na plataforma **Render.com**, conforme recomendado nos recursos da UC.

## Endpoints implementados (Semana 1)


/config                | GET | Devolve a página HTML de configuração da atividade (sem guardar informação).<br>
/json-params           | GET | Lista JSON com os parâmetros configuráveis definidos na página de configuração.<br>
/deploy?activityID=... | GET | Prepara a instância da atividade e devolve o URL de acesso para o aluno.<br>
/analytics-list        | GET | Devolve a lista de analytics recolhidos pela atividade.<br>
/analytics             | POST | Recebe o ID da atividade e devolve dados analíticos de exemplo.<br>

## Tecnologia utilizada:

**Python 3**
**Flask** (microframework para implementação dos Web Services)
**Gunicorn** (servidor WSGI utilizado no Render)
**Render.com** (Cloud para webservice)
