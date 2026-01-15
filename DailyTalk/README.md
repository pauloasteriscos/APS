# DailyTalk.pt <br>
Aluno: Paulo Silva - Nº 2501478  <br>
Ano letivo: 2025  <br>
2501478@estudante.uab.pt  <br>

GIT:<br>
https://github.com/pauloasteriscos/APS<br>

URL do serviço ativo:  <br>
https://aps-68v8.onrender.com<br>

6 - Padrões de comportamento: Padrão implementado: **Strategy**

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

## Endpoints implementados (Unidade 1)


/config                | GET | Devolve a página HTML de configuração da atividade (sem guardar informação).<br>
/json-params           | GET | Lista JSON com os parâmetros configuráveis definidos na página de configuração.<br>
/deploy?activityID=... | GET | Prepara a instância da atividade e devolve o URL de acesso para o aluno.<br>
/analytics-list        | GET | Devolve a lista de analytics recolhidos pela atividade.<br>
/analytics             | POST | Recebe o ID da atividade e devolve dados analíticos de exemplo.<br>


## Padrões de Software Aplicados
### Factory Method (GoF — Padrão de Criação)

O padrão **Factory Method** é utilizado para encapsular a criação das diferentes atividades pedagógicas, permitindo que o sistema seja extensível sem depender de classes concretas.

- `Activity` define o *Product* abstrato
- `DialogActivity`, `QuizActivity` e `ScenarioActivity` são *Concrete Products*
- `ActivityFactory` define o *Creator* abstrato
- Cada tipo de atividade possui a sua fábrica concreta
- A seleção da fábrica adequada é feita com base no tipo de atividade solicitado

Este padrão permite adicionar novos tipos de atividade sem alterar o código cliente.


### Facade (GoF — Padrão Estrutural)

O padrão estrutural **Facade** foi introduzido através da classe `ActivityProviderFacade`.

Esta classe fornece um **ponto de entrada unificado** para o subsistema interno do Activity Provider, coordenando o fluxo de criação da atividade e encapsulando o acesso ao Factory Method.

O Facade:
- reduz o acoplamento entre os endpoints REST e a lógica interna;
- centraliza a orquestração do fluxo;
- não implementa lógica de negócio, apenas delega responsabilidades.

Desta forma, os endpoints REST permanecem simples e desacoplados da complexidade do subsistema.


## Tecnologia utilizada:

**Python 3**  
**Flask** (microframework para implementação dos Web Services)  
**Gunicorn** (servidor WSGI utilizado no Render)  
**Render.com** (Cloud para webservice)


## Implementação do Padrão de Criação (Factory Method) - (Unidade 4)
Nesta entrega foi implementado o padrão **Factory Method**, aplicado ao processo de criação das atividades pedagógicas no contexto do DailyTalk.

O endpoint `/deploy` recebe o tipo de atividade a instanciar (`dialog`, `quiz` ou `scenario`), e delega essa responsabilidade ao componente:

**ActivityFactory** – classe criadora (Creator)

A fábrica instancia dinamicamente um dos produtos concretos:
- `DialogActivity`  
- `QuizActivity`  
- `ScenarioActivity`  


----------------------------------------------------------------------------------------------------------------------------------
## Implementação do Padrão Estrutural (Facade) - (Unidade 5)

Na Semana 5 foi aplicado o padrão estrutural **Facade** para organizar o acesso aos subsistemas internos do Activity Provider.

A classe **ActivityProviderFacade** atua como ponto de entrada único para os casos de uso do sistema, nomeadamente para o processo de deploy das atividades.

Em vez dos endpoints REST comunicarem diretamente com fábricas, atividades e lógica interna, toda a orquestração é delegada ao Facade, que:
- seleciona a fábrica correta;
- cria a atividade;
- devolve o URL de acesso ao aluno.

Desta forma, o Facade simplifica o uso do sistema, reduz o acoplamento e protege os detalhes de implementação do subsistema interno.


----------------------------------------------------------------------------------------------------------------------------------
## Implementação do Padrão Comportamental (Strategy) - (Unidade 6)

Na Semana 6 foi introduzido o padrão **Strategy** para resolver a variabilidade da lógica de avaliação pedagógica das atividades.

Embora todas as atividades sigam o mesmo fluxo geral  
(*submissão » avaliação » feedback » registo » resposta*),  
o modo de calcular o **score**, o **feedback** e as **métricas** varia conforme o tipo de atividade:

- Num **Quiz**, depende sobretudo dos acertos;
- Num **Diálogo**, depende das escolhas e do percurso;
- Num **Cenário**, depende das decisões e penalizações.

Para evitar um método central cheio de `if/else` (o chamado "método deus"), onde começa pequeno e depois, esta variação foi encapsulada no padrão Strategy.

Foi definida a interface:

`EvaluationStrategy`

com implementações concretas:

- `QuizEvaluationStrategy`  
- `DialogEvaluationStrategy`  
- `ScenarioEvaluationStrategy`

Cada objeto `Activity` recebe a sua estratégia no momento da criação (via Factory Method), e delega nela a avaliação da submissão do aluno.

Desta forma:
- o serviço principal mantém o fluxo comum;
- a lógica que realmente varia fica isolada nas estratégias;
- novos tipos de avaliação podem ser adicionados sem modificar o código existente.
