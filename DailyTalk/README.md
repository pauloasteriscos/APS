# DailyTalk.pt <br>
Aluno: Paulo Silva - Nº 2501478  <br>
Ano letivo: 2025  <br>
2501478@estudante.uab.pt  <br>

GIT:<br>
https://github.com/pauloasteriscos/APS<br>

URL do serviço ativo:  <br>
https://aps-68v8.onrender.com<br>

7 - Antipadrões: AntiPadrão implementado: **BLOB (God Object)**

----------------------------------------------------------------------------------------------------------------------------------
# Unidade Curricular: APS - Arquitetura e Padrões de Software, da Universidade Aberta.
## Descrição:

Este projeto implementa os Web Services RESTful necessários para que a plataforma **Inven!RA** possa:

- Obter a página de configuração da atividade;
- Recolher os parâmetros configuráveis;
- Efetuar o deploy da atividade;
- Consultar a lista de analytics;
- Obter os analytics registados por nós estudantes.

O serviço está alojado na plataforma **Render.com**, conforme recomendado nos recursos da UC.

---

## Endpoints implementados

| Endpoint                | Método | Descrição |
|------------------------|--------|-----------|
| `/config`              | GET    | Devolve a página HTML de configuração da atividade |
| `/json-params`         | GET    | Lista JSON com os parâmetros configuráveis |
| `/deploy?activityID=...&type=...` | GET    | Prepara a instância da atividade e devolve o URL de acesso |
| `/analytics-list`      | GET    | Devolve a lista de analytics disponíveis |
| `/analytics`           | POST   | Recebe o ID da atividade e devolve dados analíticos simulados |
| `/submit`              | POST   | Recebe submissão de aluno e devolve avaliação |

---

## Padrões de Software Aplicados

### Strategy (Comportamental)

Usado para encapsular diferentes lógicas de avaliação pedagógica, conforme o tipo de atividade.

- Interface: `EvaluationStrategy`
- Estratégias concretas:
  - `QuizEvaluationStrategy`
  - `DialogEvaluationStrategy`
  - `ScenarioEvaluationStrategy`

Cada atividade recebe sua estratégia no momento da criação (via Factory Method), e delega a ela a avaliação da submissão. Isso evita métodos monolíticos (`if/else`) e facilita extensão futura.

### Factory Method (Criação)

Usado para instanciar dinamicamente diferentes tipos de atividades.

- `Activity` (Product abstrato)
- `DialogActivity`, `QuizActivity`, `ScenarioActivity` (Concrete Products)
- `ActivityFactory` (Creator com lógica de decisão baseada no tipo)

Esse padrão permite adicionar novos tipos de atividade sem alterar o código cliente.

### Facade (Estrutural)

Usado para orquestrar o processo de deploy de atividades através de um ponto único de entrada:

- Classe: `ActivityProviderFacade`
- Oculta os detalhes internos do processo de deploy e permite futura integração com subsistemas externos

#### Extensão implementada:
Embora o Facade não tivesse lógica real inicialmente, agora simula integração externa com logs do tipo:

```python
[Facade] Atividade 'TEST-QUIZ-001' registrada no sistema externo.
[Facade] URL da atividade: http://...
```

Essa estrutura permite futura inclusão de notificações, banco de dados, ou serviços de analytics externos.

---

## Arquitetura em Camadas

- `app.py`: Camada de apresentação (Flask endpoints)
- `services/`: Camada de aplicação (coordenam fluxo de lógica)
- `domain/`: Camada de domínio (representação das entidades)
- `strategies.py`: Estratégias de avaliação por tipo
- `factories/`: Instancia os objetos adequados (Factory)
- `facade/`: Exposição simplificada para integração

---

## Tecnologias Utilizadas

- Python 3
- Flask (Web Framework)
- Gunicorn (WSGI server)
- Render.com (cloud hosting)
- colorlog (para logging colorido e legível)

---

## Logs e Rastreabilidade

Para rastrear a execução e garantir a passagem por cada camada:

- Todos os componentes possuem `logging.debug()` estruturado
- Os logs são coloridos com `colorlog` para melhor leitura
- Cada estratégia, serviço, factory e facade imprime mensagens ao ser usado

Exemplo:
```bash
[DEBUG] [ActivityFactory] Criando atividade 'TEST-QUIZ-001'
[DEBUG] [SubmissionService] Iniciando avaliação da atividade
[DEBUG] [QuizEvaluation] Avaliando atividade TEST-QUIZ-001 com dados: {...}
```

---

## Avaliação do Projeto: Versão ANTES vs. DEPOIS
Antipadrão Identificado - The Blob (God Object)

No projeto original (ANTES), é evidente a ocorrência do antipadrão The Blob, também conhecido como God Object. 
Em termos práticos, o arquivo principal app.py concentrava múltiplas responsabilidades distintas: 
 - Ddefinia os endpoints Flask (camada de interface HTTP)
 - Continha lógica de orquestração de negócios (deploy de atividades, avaliação de submissões)
 - Mantinha estado global das atividades (DEPLOYED_ACTIVITIES), e até declarava classes de domínio e uma facade. 
 
Ou seja, grande parte do comportamento do sistema estava aglomerado em um único módulo controlador, enquanto outras classes eram principalmente estruturas de dados auxiliares. 

Foi concebido desta forma para o começo do protótipo. Este cenário corresponde à definição clássica do Blob, onde "um componente monopoliza o processamento, e a maioria dos outros objetos apenas encapsula dados". 
Na prática, o estilo de implementação procedimental levou a um objeto central com inúmeras responsabilidades, violando o Single Responsibility Principle (SRP) e comprometendo a coesão do projeto.

Por que isso é um antipadrão? 
Segundo a literatura desta UC, o Blob tende a gerar classes excessivamente grandes, de baixa coesão, com alto acoplamento e difícil manutenção. 

De facto, na versão "ANTES", o app.py atuava como um "canivete suíço" da aplicação. 
Qualquer alteração nessa parte central (por exemplo, na lógica de deploy ou validação de submissões) poderia impactar múltiplos aspectos do sistema, dada a sua dependência generalizada. 

Além disso, essa abordagem dificulta a evolução, pois à medida que novas funcionalidades fossem adicionadas, a tendência seria continuar inflando o mesmo módulo, levando a código frágil e potencial duplicação de lógica. 

Resumindo, a versão inicial apresentava um ponto único de forte acoplamento e muitas razões de mudança, características típicas do antipadrão Blob.

### Solução de Refatoração Aplicada
Na versão refatorada (DEPOIS), o antipadrão Blob foi eliminado através da redistribuição das responsabilidades em camadas e componentes especializados. 
A solução seguiu as recomendações clássicas para esse antipadrão, separando o "Modo Deus" em várias entidades coesas. 

Especificamente, foram introduzidas as seguintes mudanças arquiteturais:
 - Camada de Serviços de Aplicação: 
   Foram criadas classes de serviço (ex.: ActivityService, SubmissionService) para coordenar as operações de negócio. 
   Por exemplo, a lógica de deploy de uma atividade (antes realizada diretamente no endpoint) agora está encapsulada em ActivityService.deploy(), que internamente usa o Factory para criar a atividade e registra-a, chamando a facade apenas para ações externas (log/integração). 
   De forma similar, a validação de submissão e cálculo de avaliação ocorrem em SubmissionService.submit(). 
   Essa camada age como um Controller especializado, reduzindo a carga do app.py.

  - Camada de Domínio e Estratégias: 
    As classes de domínio (como Activity e suas derivadas) e as estratégias de avaliação (QuizEvaluationStrategy, etc.) permanecem responsáveis por regras específicas, mas agora residem em módulos próprios (domain/, strategies.py). 
	O padrão Strategy foi mantido para encapsular diferentes lógicas de avaliação pedagógica, evitando condicionais extensos.

  - Factory Unificado: A criação das atividades, antes distribuída em múltiplas fábricas concretas, foi simplificada com um Factory Method central (ActivityFactory.create(...)) que decide o tipo adequado com base em parâmetros. 
  Isso eliminou duplicação de código na escolha de factories específicas e tornou mais fácil adicionar novos tipos de atividades sem modificar o código cliente.

  - Facade Refinada: 
    A classe facade (ActivityProviderFacade) foi extraída para seu próprio módulo (facade/) e sua responsabilidade ficou focada em integração externa (simulação de registro/log de deploy). 
  Antes, a facade também criava a atividade. Agora, aplica-se o princípio da única responsabilidade: Quem cria é o Factory/Service, enquanto a Facade apenas realiza passos complementares (por exemplo, poderia notificar um sistema externo sem conhecer detalhes internos da criação).

  - Camada de Apresentação Enxuta: 
    O app.py final ficou bem mais simples e coeso. 
	Ele apenas define os endpoints e delega o processamento às camadas de serviço. 
	Por exemplo, no endpoint /deploy a função agora faz: launch_url = activity_service.deploy(...) e retorna a resposta; no /submit, simplesmente chama result, status = submission_service.submit(payload) e devolve o JSON. 
	Toda a validação de dados e chamadas de lógica complexa estão fora do módulo Flask, tornando-o apenas uma fina camada de roteamento.

Em resumo, a refatoração aplicou princípios de modularização e encapsulamento, dividindo aquele objeto central em unidades menores e bem definidas. 
Essa abordagem alinha se a Padrões Arquiteturais estudados nesta disciplina de Arquitetura e Padrões de Software, conhecidos como "MVC/Camadas", e que também formam estudados em Programação Web Avaçada neste curso, onde há separação clara entre controle de fluxo, lógica de negócio e detalhes de implementação.

### Efeitos da Refatoração (Versão DEPOIS)
Os resultados dessa refatoração são bastante positivos e cumprem os requisitos da entrega:
  - Eliminação do Blob e Melhoria de Coesão: 
    Cada classe/módulo agora tem responsabilidade única e bem definida, atendendo ao SRP, Single Responsibility Principle, ou em português, Princípio da Responsabilidade Única, onde cada classe ou módulo do sistema deve ser responsável por apenas uma coisa, ou seja, ter uma única função clara e bem delimitada.
	O código está mais coeso, por exemplo, SubmissionService lida somente com submissões/avaliações, ActivityService apenas com ciclo de vida de atividades. 
	Não existe mais uma classe dominante fazendo "de tudo", o que distribui as responsabilidades de forma uniforme.

  - Redução de Acoplamento: 
    Ao dividir funcionalidades em camadas (apresentação - serviços - domínio), diminuiu-se o acoplamento entre partes do sistema. 
	Mudanças internas em como uma atividade é criada ou avaliada agora não afetam o código de interface (Flask) desde que a interface do serviço permaneça igual. 
	Isso isola o efeito das mudanças e torna a arquitetura mais resiliente a evoluções.

  - Facilidade de Manutenção e Extensibilidade: 
    O código ficou mais fácil de manter e extensível, pois novas funcionalidades podem ser incorporadas criando novos serviços ou novas estratégias, sem editar um God Object central. 
	A compreensão do fluxo também melhora, pois está claro em qual camada cada lógica reside (por exemplo, qualquer desenvolvedor sabe que regras de negócio estarão nos serviços ou domínio, não perdidas em meio a código de interface). 
	Essas melhorias mostram que refatorar um Blob em unidades modulares aumenta a flexibilidade e robustez da arquitetura.

  - Reutilização e Testabilidade: 
    Com componentes separados, é possível testar cada parte de forma isolada (p. ex., testar ActivityService ou uma estratégia de avaliação independentemente do Flask). 
	Na versão anterior, testar a lógica implicaria simular requests HTTP ou mexer no objeto gigante com muito estado compartilhado. 
	Agora há claras fronteiras de módulo. 
	Isso também favorece reutilização de componentes em outros contextos, por exemplo, as estratégias de avaliação ou o factory podem ser reutilizados se outro módulo precisar instanciar atividades. 
	Esses ganhos de reuso e teste são consequência direta da maior modularidade alcançada.

  - Código Mais Limpo (Menos Dupicação): 
    A refatoração eliminou código duplicado ou redundante. 
	Por exemplo, a lógica de validação de payload que aparecia no endpoint /submit agora está centralizada em SubmissionService.submit(). 
	Da mesma forma, concentrar a lógica de criação no ActivityFactory.create evitou repetição de código de escolha de fábrica. 
	Com menos trechos repetidos, o código fica menos propenso a erros e mais fácil de ajustar.

Há de ressaltar, que nesta entrega foi escolhido apenas um AntiPadrão para refatorar, aquele que identifiquei com maior relevância face ao estado atual do projeto, embora outros AntiPadrões tenham sido observados e que serão refatorados a seguir o cronograma das melhorias estruturais, que está em fase de definição.

Para esta entrega, foram analisados os 14 AntiPadrões, optando-se por escolher o Blob e aplicar a correção específica para ele, conforme orientações teóricas da disciplina.

##Conclusão: 
A comparação entre as versões evidencia que o antipadrão identificado (Blob) foi corrigido com sucesso, onde solução aplicada, baseada em refatoração para camadas e padrões de projeto adequados, resolveu o problema de sobrecarga de responsabilidades. 
Os efeitos são altamente benéficos: 
  - O projeto DailyTalk ganhou em organização, modularidade e facilidade de evolução. 
  - Em resumo, a entrega DEPOIS apresenta um código bem arquitetado sobre o processo de refatoração e aprendizagem obtida.

Referências Bibliográficas:
  PAREDES, Hugo; MORGADO, Leonel. Antipadrões: Reinventar más soluções para problemas comuns. Unidade Curricular de Arquitetura e Padrões de Software (APS) - Universidade Aberta, 2020. Material de apoio interno.
  GAMMA, Erich et al. Padrões de Projetos: Soluções Reutilizáveis de Software Orientado a Objetos. 1. ed. Porto Alegre: Bookman, 2008.
