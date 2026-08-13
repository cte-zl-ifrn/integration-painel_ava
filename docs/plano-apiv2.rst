=========================================
Plano de Implementação da Nova API v2
=========================================

Este documento estabelece o plano detalhado de desenvolvimento e testes para a versão 2 da API do Painel AVA (``/api/v2/``), considerando as especificações oficiais do **SUAP** e a evolução do plugin Moodle **``tool_painelava``**.

.. note::
   O objetivo é implementar os 22 endpoints da API v2 mantendo a cobertura de testes em **100%**. Os servidores mock serão autônomos (desenvolvimento paralelo offline) e utilizados também em testes automatizados.


1. Especificação de Integração Externa (SUAP e Moodle)
======================================================

1.1. Integração com o SUAP (Sem Gestão Externa)
------------------------------------------------
* **Fonte da Verdade**: `https://suap.ifrn.edu.br/api/openapi.json`
* **Endpoints Reais do SUAP Mapeados**:
  * **Autenticação**:
    * ``POST /api/token/pair`` (Emissão do token JWT do SUAP com ``username`` e ``password``)
    * ``POST /api/token/refresh`` (Renovação de token JWT do SUAP)
    * ``POST /api/token/verify`` (Validação de token JWT do SUAP)
  * **Informações de Servidores (RH)**:
    * ``GET /api/rh/meus-dados/`` (Dados pessoais, cargo, setor, foto)
    * ``GET /api/rh/meus-vinculos/`` (Lista de vínculos de servidor)
  * **Informações de Alunos (Ensino)**:
    * ``GET /api/ensino/meus-dados-aluno/`` (Dados do aluno, curso, matriz, IRA, foto)
    * ``GET /api/ensino/meus-diarios/`` (Diários e turmas do aluno)
* **Servidor Mock do SUAP (``run_mock_suap``)**:
  * Emulará estritamente a especificação oficial do OpenAPI do SUAP.

1.2. Evolução da API no Plugin Moodle ``tool_painelava`` (Com Autonomia e Retrocompatibilidade)
------------------------------------------------------------------------------------------------
* **Repositório**: `/home/kelson/projetos/IFRN/sas/tool_painelava`
* **Estratégia de Retrocompatibilidade**:
  * Manter a versão v1 (``admin/tool/painelava/api/index.php``) 100% funcional sem breaking changes.
  * Criar/Expandir suporte para a **API v2 no ``tool_painelava``** para atender aos novos requisitos de:
    * Notificações (sumário, listagem, leitura/não lida).
    * Conversas / Mensagens (sumário, conversas por AVA, histórico, leitura).
    * Salas e Cursos (favoritar, visibilidade, progresso percentual).
    * Revogação/Renovação de tokens em cascata no Moodle.
* **Servidor Mock do Moodle (``run_mock_moodle``)**:
  * Emulará tanto a v1 quanto a nova v2 do plugin ``tool_painelava`` com estado persistente em memória e carga de dados em JSON.


2. Arquitetura dos Servidores Mock Standalone
=============================================

2.1. Execução no Ambiente Local
-------------------------------
* **SUAP Mock**: ``python manage.py run_mock_suap --port 8001`` (baseado no OpenAPI do SUAP).
* **Moodle Mock**: ``python manage.py run_mock_moodle --port 8002`` (baseado na v2 do ``tool_painelava``).
* O Painel AVA local em desenvolvimento apontará para as portas dos mocks via variáveis de ambiente/settings.

2.2. Execução na Suíte de Testes (Pytest)
-----------------------------------------
* Fixtures em Pytest subirão os servidores mock em portas livres para validação HTTP de 100% da cobertura de código.


3. Estrutura dos Arquivos da API v2 no Painel AVA
=================================================

* **Roteamento**:
  * ``src/urls.py``: registro de ``path("api/v2/", api_v2.urls)``.
* **Controladores e Schemas**:
  * ``src/painel/api_v2.py``: rotas NinjaAPI (22 endpoints).
  * ``src/painel/schemas_v2.py``: esquemas Pydantic para validação e serialização.
* **Camada de Serviços BFF e Brokers**:
  * ``src/painel/services_v2.py``: orquestração entre SUAP e Moodle AVAs.
  * Corrigir `SuapBroker` em ``src/painel/brokers.py`` para consumir `/api/rh/meus-dados/` e `/api/ensino/meus-dados-aluno/` do SUAP oficial.
* **Aplicação Raiz Django dos Mocks (`src/mocks/`)**:
  * `src/mocks/apps.py` (App Django independente configurado em `INSTALLED_APPS`)
  * `src/mocks/suap_server.py`
  * `src/mocks/moodle_server.py`
  * `src/mocks/management/commands/run_mock_suap.py`
  * `src/mocks/management/commands/run_mock_moodle.py`


4. Detalhamento dos 22 Endpoints da API v2 no Painel AVA
========================================================

4.1. Módulo Autenticação (4 endpoints)
---------------------------------------
1. ``POST /api/v2/token/pair/``: Emissão de par JWT no Painel via autenticação com o SUAP real/mock.
2. ``POST /api/v2/token/refresh/``: Renovação em cascata no Painel AVA e no ``tool_painelava`` dos AVAs.
3. ``POST /api/v2/token/verify/``: Validação do token JWT.
4. ``POST /api/v2/token/revoke/``: Revogação em cascata no Painel e nos AVAs.

4.2. Módulo Usuário (3 endpoints)
----------------------------------
5. ``GET /api/v2/usuario/info/``: Unificação de dados de perfil obtidos via SUAP (RH/Ensino).
6. ``GET /api/v2/usuario/preferencia/``: Leitura de preferências no Painel.
7. ``PATCH /api/v2/usuario/preferencia/``: Atualização de preferências.

4.3. Módulo Sala de Aula (7 endpoints)
---------------------------------------
8. ``GET /api/v2/sala/tipo/`` e ``GET /api/v2/sala/tipo/<ava>/``: Lista de tipos de sala.
9. ``GET /api/v2/sala/tipo/<tipo>/``: Metadados, filtros e ordenações por tipo de sala.
10. ``GET /api/v2/sala/tipo/quantidades/``: Quantidades por tipo.
11. ``GET /api/v2/sala/tipo/<tipo>/<ava>/``: Cursos/salas do usuário obtidos via ``tool_painelava`` v2.
12. ``GET /api/v2/sala/progresso/<ava>/<ids>/``: Progresso percentual retornado pelo ``tool_painelava``.
13. ``PATCH /api/v2/sala/favorito/<ava>/<id>/``: Altera favorito via ``tool_painelava``.
14. ``PATCH /api/v2/sala/visivel/<ava>/<id>/``: Altera visibilidade via ``tool_painelava``.

4.4. Módulo Notificação (4 endpoints)
--------------------------------------
15. ``GET /api/v2/notificacao/``: Contadores de não lidas via ``tool_painelava`` v2.
16. ``GET /api/v2/notificacao/<ava>/``: Lista de notificações.
17. ``GET /api/v2/notificacao/<ava>/<ids>/``: Detalhes da notificação.
18. ``PATCH /api/v2/notificacao/<ava>/<ids>/``: Atualização de leitura no Moodle.

4.5. Módulo Conversa (4 endpoints)
-----------------------------------
19. ``GET /api/v2/conversa/``: Contadores de conversas via ``tool_painelava`` v2.
20. ``GET /api/v2/conversa/<ava>/``: Lista de conversas.
21. ``GET /api/v2/conversa/<ava>/<ids>/``: Mensagens da conversa.
22. ``PATCH /api/v2/conversa/<ava>/<id>/``: Marcação de leitura da conversa.


5. Estratégia de Testes Automatizados e Cobertura (100%)
======================================================

* Criação de ``src/painel/tests_apiv2.py`` exercitando todos os 22 endpoints.
* Integração completa com os mocks HTTP do SUAP (OpenAPI real) e Moodle (``tool_painelava`` v2).
* Verificação com ``sas test painel`` garantindo **100% de cobertura de código**.


6. Fases de Execução
====================

1. **Aprovação do Plano**: Aguardar autorização do usuário.
2. **Atualização da v2 no Moodle Plugin (`tool_painelava`)**:
   * Adicionar suporte aos novos serviços v2 em `/home/kelson/projetos/IFRN/sas/tool_painelava` preservando a v1.
3. **Construção dos Mocks Standalone**:
   * `run_mock_suap` (fiel ao `https://suap.ifrn.edu.br/api/openapi.json`).
   * `run_mock_moodle` (fiel à API v2 do `tool_painelava`).
4. **Atualização dos Brokers e Desenvolvimento da API v2 no Painel AVA**:
   * Atualizar `SuapBroker` com os endpoints oficiais do SUAP.
   * Desenvolver os 22 endpoints em `src/painel/api_v2.py`.
5. **Testes Automatizados e Garantia de 100% de Cobertura**:
   * Implementação dos testes em `tests_apiv2.py` e validação com `sas test painel`.
