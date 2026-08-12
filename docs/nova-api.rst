============================
Especificação da Nova API v2
============================


O documento especifica a v2 da API para atuar como uma camada BFF (Backend For Frontend) do Painel AVA (``/api/v2/``),
integrando os frontends (web e mobile) e as diferentes instâncias do Moodle (AVAs). A API utiliza autenticação
baseada em JWT (``Authorization: Bearer <token>``) com suporte a revogação e renovação em cascata para quando for
mobile e session para quando for web.

Estrutura dos Módulos e Endpoints (22 Endpoints)
================================================


.. list-table::
   :header-rows: 1
   :widths: auto

   * - Módulo
     - Endpoints
     - Descrição Resumida
   * - **Autenticação**
     - ``POST /token/pair/`` ``POST /token/refresh/`` ``POST /token/verify/`` ``POST /token/revoke/``
     - Gerenciamento de ciclo de vida do JWT (emissão, refresh, verificação e revogação em cascata no Painel e nos AVAs).
   * - **Usuário**
     - ``GET /usuario/info/`` ``GET /usuario/preferencia/`` ``PATCH /usuario/preferencia/``
     - Informações de perfil e preferências globais do usuário no Painel.
   * - **Sala de Aula**
     - ``GET /sala/tipo/`` ``GET /sala/tipo/<tipo>/`` ``GET /sala/tipo/quantidades/`` ``GET /sala/tipo/<tipo>/<ava>/`` ``GET /sala/progresso/...`` ``PATCH /sala/favorito/...`` ``PATCH /sala/visivel/...``
     - Listagem de tipos de salas (Home, Diários, Coordenações, Laboratórios, Auto-inscrições, Backups), filtros dinâmicos, progresso e ações de favoritar/ocultar salas.
   * - **Notificação**
     - ``GET /notificacao/`` ``GET /notificacao/<ava>/`` ``GET /notificacao/<ava>/<ids>`` ``PATCH /notificacao/<ava>/<ids>``
     - Sumário por AVA, listagem, detalhamento e marcação de lido/não lido.
   * - **Conversa**
     - ``GET /conversa/`` ``GET /conversa/<ava>/`` ``GET /conversa/<ava>/<ids>`` ``PATCH /conversa/<ava>/<id>/``
     - Sumário por AVA, conversas, mensagens e alteração de status de leitura.


Autenticação
============


1. ``POST /token/pair/``
------------------------


Gera um novo par de tokens

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "password": "string",
     "username": "string"
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "username": "string",
     "refresh": "jwt",
     "access": "jwt"
   }


.. code-block:: json

   {
     "detail": "No active account found with the given credentials",
     "code": "authentication_failed"
   }


.. code-block:: json

   {
     "detail": "Invalid input.",
     "code": "invalid",
     "username": "username is required",
     "password": "password is required"
   }


2. ``POST /token/refresh/``
---------------------------


Gera um novo par de tokens no Painel AVA e nos AVA em que ocorreu a autenticação usando este token

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "refresh": "string"
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "refresh": "string",
     "access": "string"
   }


.. code-block:: json

   {
     "detail": "Token is invalid or expired",
     "code": "token_not_valid"
   }


.. code-block:: json

   {
     "detail": "Invalid input.",
     "code": "invalid",
     "refresh": "token is required"
   }


3. ``POST /token/verify/``
--------------------------


Verifica se o token é válido

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "token": "string"
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "refresh": "jwt",
     "access": "jwt"
   }


.. code-block:: json

   {
     "detail": "Token is invalid or expired",
     "code": "token_not_valid"
   }


.. code-block:: json

   {
     "detail": "Invalid input.",
     "code": "invalid",
     "token": "token is required"
   }


4. ``POST /token/revoke/``
--------------------------


Revoga o token no Painel AVA e nos AVA em que ocorreu a autenticação usando este token

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "token": "jwt"
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
       "detail": "Token revoked",
       "revoke_list": [
           {"service_name": "<string>", "url": "<string>", "revoked": true, "duration": "<duration in ISO 8601 format>"}
       ]
   }


.. code-block:: json

   {
     "detail": "Token is invalid or expired",
     "code": "token_not_valid"
   }


.. code-block:: json

   {
     "detail": "Invalid input.",
     "code": "invalid",
     "token": "token is required"
   }


Usuário
=======


5. ``GET /usuario/info/``
-------------------------


Retorna informações do usuário

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "id": 0,
     "matricula": "",
     "identificacao": "",
     "nome_social": "",
     "nome_registro": "",
     "ultimo_nome": "",
     "nome_usual": "",
     "cpf": "",
     "rg": "",
     "passaporte": "",
     "filiacao": [
       "",
       ""
     ],
     "sexo": "",
     "data_nascimento": "",
     "data_de_nascimento": "",
     "naturalidade": "",
     "email": "",
     "email_secundario": "",
     "email_google_classroom": "",
     "email_academico": "",
     "email_preferencial": "",
     "foto": "",
     "url_foto_75x100": "",
     "url_foto_150x200": "",
     "tipo_vinculo": "Servidor",
     "tipo_usuario": "Servidor (Técnico-Administrativo)",
     "vinculo": {
       "turno": "",
       "campus_curso": "ZL: 123456 - ASDF",
       "campus": "",
       "curso": "123456 - ASDF",
       "matriz": "000 - ASDF",
       "cargo": "",
       "ingresso": "2015/2",
       "ira": "100,00",
       "categoria": "tecnico_administrativo",
       "situacao": "",
       "situacao_sistemica": "",
       "matricula_regular": false
     },
     "vinculos": [
       {
         "detalhamento": {
           "modalidade": "",
           "nivel_ensino": "",
           "ativo": false,
           "cargo": "",
           "categoria": "Técnico Administrativo"
         },
         "estrangeiro": false
       }
     ]
   }


6. ``GET /usuario/preferencia/``
--------------------------------


Retorna preferências do usuário

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "zoom" : "100%",
     "configuracao" : "Padrão"
   }


7. ``PATCH /usuario/preferencia/``
----------------------------------


Atualiza preferências do usuário

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "zoom" : "100%"
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "zoom" : "100%"
   }


Sala de aula virtual
====================


8. ``GET /sala/tipo/``
----------------------


Retorna os tipos de sala, sendo que ``/sala/tipo/*/`` é o mesmo que ``/sala/tipo/`` e ``/sala/tipo/<ava>/`` é o
mesmo que ``/sala/tipo/`` com o campo ``<ava>`` sempre ``*``. Se for informado o campo ``<ava>`` serão consultados
apenas os dados daquele AVA pelo ``slug`` informado, ``inicio``, ``backup`` e ``autoinscricoes`` ignoram este filtro
e sempre mostrarão todos os dados.

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
     {
       "slug": "inicio",
       "rotulo_curto": "Início",
       "rotulo_longo": "Início",
       "dica": "Continue de onde você parou",
       "icon": "fa-regular fa-house",
       "ordem": 0,
       "selecionado": false,
       "ativo": true,
     },
     {
       "slug": "diario",
       "rotulo_curto": "Diários",
       "rotulo_longo": "Meus diários",
       "dica": "Diários de classe",
       "icon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" class=\"lucide lucide-book-open h-4 w-4\" aria-hidden=\"true\" data-tsd-source=\"/src/components/govbr/BrNavbar.tsx:42:17\"><path d=\"M12 7v14\"></path><path d=\"M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z\"></path></svg>",
       "ordem": 1,
       "selecionado": true,
       "ativo": true,
     },
     {
       "slug": "coordenacao",
       "rotulo_curto": "Coordenações",
       "rotulo_longo": "Salas de coordenações",
       "dica": "Salas de coordenações dos cursos",
       "icon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" class=\"lucide lucide-book-open h-4 w-4\" aria-hidden=\"true\" data-tsd-source=\"/src/components/govbr/BrNavbar.tsx:42:17\"><path d=\"M12 7v14\"></path><path d=\"M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z\"></path></svg>",
       "ordem": 2,
       "selecionado": false,
       "ativo": true,
     },
     {
       "slug": "laboratorio",
       "rotulo_curto": "Laboratórios",
       "rotulo_longo": "Laboratórios de EaD",
       "dica": "Laboratórios para práticas de EaD disponibilizados no Ambiente Virtual de Aprendizagem",
       "icon": "fa-solid fa-flask",
       "ordem": 3,
       "selecionado": false,
       "ativo": true,
     },
     {
       "slug": "autoinscricoes",
       "rotulo_curto": "Auto-inscrições",
       "rotulo_longo": "Auto-inscrições",
       "dica": "Cursos para auto-inscrição",
       "subtitulo": "Cursos abertos em que você pode se inscrever sem aprovação prévia.",
       "icon": "fa-brands fa-stripe-s",
       "ordem": 4,
       "selecionado": false,
       "ativo": true,
     },
     {
       "slug": "backup",
       "rotulo_curto": "Backups",
       "rotulo_longo": "Meus backups",
       "dica": "Backups",
       "subtitulo": "Backups dos seus diários ou compartilhados com você.",
       "icon": "fa-solid fa-box-archive",
       "ordem": 5,
       "selecionado": false,
       "ativo": true,
     },
   ]


9. ``GET /sala/tipo/<tipo>/``
-----------------------------


Retorna as salas do tipo informado.

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


Home
^^^^^

A home é uma aba especial que server para orientar o usuário, não tem salas vinculadas a ela.

* Pode mostrar as últimas N salas que o usuário acessou.
* Pode ter cards com links rápidos para as outras abas (usuários não costumam olhar para as abas), servindo de CTA.
* Não possui filtros.
* Não possui ordenação.
* Não possui quantidade de salas.

.. code-block:: json

   {
     "slug": "inicio",
     "rotulo_curto": "Início",
     "rotulo_longo": "Início",
     "dica": "Continue de onde você parou",
     "icon": "fa-regular fa-house",
     "ordem": 0,
     "selecionado": false,
     "ativo": true,
     "quantidade_salas": null,
     "suprimir": null,
     "filtros": null,
     "ordenacao": null
   }


Meus diários
^^^^^^^^^^^^^^^

Em meus diários são listados os cursos que geram diário nos quais o usuário está vinculado. Eles vêm do Suap via
Integrador AVA.

* Possui filtros.
* Possui ordenação.
* Possui quantidade de salas.
* A quantidade para alunos costuma ficar abaixo de 10, mas para professores fica acima de 100, chegando a 800.
* Os maiores nomes dos cursos e disciplinas tem quase 250 caracteres.
* O nome das turmas segue um padrão como "20261.1.0028.ZL.1E", sempre tendo 5 segmentos separados por ponto.
* Minicursos com ou sem auto-inscrição não têm diários, apenas turma, o código pode ser como
  20261.1.0028.ZL.1E.20261.1.0028.ZL.1E#1689
* O código de salas do tipo "diários" são como 20301.1.03905.1E.POS.0364#123456, onde 20301.1.03905.1E é a turma,
  POS.0364 é o código da disciplina, 20301.1.03905.1E.POS.0364 é o código do diário, #123456 é o ID do diário,
  isso se dá pois diários podem ser divididos então o código do diário pode gerar ambiguidade.

.. code-block:: json

   {
     "slug": "diario",
     "rotulo_curto": "Diários",
     "rotulo_longo": "Meus diários",
     "dica": "Diários de classe",
     "icon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" class=\"lucide lucide-book-open h-4 w-4\" aria-hidden=\"true\" data-tsd-source=\"/src/components/govbr/BrNavbar.tsx:42:17\"><path d=\"M12 7v14\"></path><path d=\"M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z\"></path></svg>",
     "ordem": 1,
     "selecionado": true,
     "ativo": true,
     "quantidade_salas": 503,
     "suprimir": null,
     "filtros": [
       {
         "slug": "situacao",
         "tipo": "select",
         "autocomplete": false,
         "icone": "fa-solid fa-book",
         "rotulo": "Situação",
         "selecionado": "inprogress",
         "opcoes": [
           {"label": "Em andamento",  "value": "inprogress" },
           {"label": "Favoritos",     "value": "favourites" },
           {"label": "Não iniciados", "value": "future"     },
           {"label": "Arquivados",    "value": "hidden"     },
           {"label": "Todos (lento)", "value": "all"        },
         ]
       },
       {
         "slug": "semestres",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-calendar-days",
         "rotulo": "Semestres",
         "selecionados": [],
         "opcoes": [{"label": "2026.2",  "value": "2026.2" }, {"label": "2023.1",  "value": "2023.1" }]
       },
       {
         "slug": "periodos",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-calendar-week",
         "rotulo": "Períodos",
         "selecionados": [],
         "opcoes": [{"label": "1º",  "value": "1º" }, {"label": "8º",  "value": "8º" }]
       },
       {
         "slug": "disciplinas",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-book-open",
         "rotulo": "Disciplinas",
         "selecionados": [],
         "opcoes": [{"label": "Disciplina 1", "value": "1"}, {"label": "Disciplina 8", "value": "8"}]
       },
       {
         "slug": "cursos",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-graduation-cap",
         "rotulo": "Cursos",
         "selecionados": [],
         "opcoes": [{"label": "Curso 1", "value": "1"}, {"label": "Curso 8", "value": "8"}]},
       {
         "slug": "papeis",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-user-tag",
         "rotulo": "Papéis",
         "selecionados": [],
         "opcoes": [{"label": "Aluno", "value": "student"}, {"label": "Professor", "value": "editingteacher"}]
       },
       {
         "slug": "ambientes",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-person-military-to-person",
         "rotulo": "Ambientes",
         "selecionados": [],
         "opcoes": [
           {"label": "Acadêmico",  "value": "academico",  "cor": "#0d6efd", "icone": "fa-solid fa-door-open"},
           {"label": "Presencial", "value": "presencial", "cor": "#0dcaf0", "icone": "fa-solid fa-chalkboard-user"},
           {"label": "Projetos",   "value": "projetos",   "cor": "#198754", "icone": "fa-solid fa-flask"},
         ]
       },
     ],
     "ordenacao": {
       "selecionada": "data_acesso",
       "opcoes": [
         { "value": "data_acesso", "direcao": "DESC", "rotulo": "Acesso mais recente"   },
         { "value": "data_inicio", "direcao": "DESC", "rotulo": "Início mais recente"   },
         { "value": "data_fim",    "direcao": "DESC", "rotulo": "Final mais recente"    },
         { "value": "titulo",      "direcao": "ASC",  "rotulo": "Título"                },
         { "value": "codigo",      "direcao": "ASC",  "rotulo": "Código"                },
         { "value": "semestre",    "direcao": "DESC", "rotulo": "Semestre mais recente" },
       ]
     }
   }


Salas de coordenações
^^^^^^^^^^^^^^^^^^^^^^^^^

Todo curso tem uma sala de coordenação, elas são usadas para reuniões, discussões e outras atividades administrativas.

* Possui filtros.
* Possui ordenação.
* Possui quantidade de salas.
* No AVA as salas são prefixadas com "Sala da Coordenação do Curso de ", mas aqui não faz sentido, por isso
  suprimimos esse prefixo.
* O código das salas são como ZL.15806 , ou seja, sigla do campus e código do curso. Eles são usados como filtro.
* Os nomes dos cursos podem chegar a 250 caracteres.

.. code-block:: json

   {
     "slug": "coordenacao",
     "rotulo_curto": "Coordenações",
     "rotulo_longo": "Salas de coordenações",
     "dica": "Salas de coordenações dos cursos",
     "icon": "fa-solid fa-arrows-to-circle",
     "ordem": 2,
     "selecionado": false,
     "ativo": true,
     "quantidade_salas": 2,
     "suprimir": "Sala da Coordenação do Curso de ",
     "filtros": [
       {
         "slug": "cursos",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-graduation-cap",
         "rotulo": "Cursos",
         "selecionados": [],
         "opcoes": [{"label": "Curso 1", "value": "1"}, {"label": "Curso 8", "value": "8"}]
       },
       {
         "slug": "papeis",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-user-tag",
         "rotulo": "Papéis",
         "selecionados": [],
         "opcoes": [{"label": "Aluno", "value": "student"}, {"label": "Professor", "value": "editingteacher"}]
       },
       {
         "slug": "ambientes",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-person-military-to-person",
         "rotulo": "Ambientes",
         "selecionados": [],
         "opcoes": [
           {"label": "Acadêmico",  "value": "academico",  "cor": "#0d6efd", "icone": "fa-solid fa-door-open"},
           {"label": "Presencial", "value": "presencial", "cor": "#0dcaf0", "icone": "fa-solid fa-chalkboard-user"},
           {"label": "Projetos",   "value": "projetos",   "cor": "#198754", "icone": "fa-solid fa-flask"},
         ]
       },
     ],
     "ordenacao": null
   }


Laboratórios de EaD
^^^^^^^^^^^^^^^^^^^^

Para todo aluno do curso de Formação em EaD é criado um laboratório de EaD, ou seja, um curso dentro do AVA em que
o aluno é professor editor e pode exercer a prática docente.

* Possui filtros.
* Possui ordenação.
* Possui quantidade de salas.
* O nome da sala é o nome do aluno.
* O código da sala é a matrícula do aluno.

.. code-block:: json

   {
     "slug": "laboratorio",
     "rotulo_curto": "Laboratórios",
     "rotulo_longo": "Laboratórios de EaD",
     "dica": "Laboratórios para práticas de EaD disponibilizados no Ambiente Virtual de Aprendizagem",
     "icon": "fa-solid fa-flask",
     "ordem": 3,
     "selecionado": false,
     "ativo": true,
     "quantidade_salas": 2,
     "suprimir": "Laboratório do aluno ",
     "filtros": [
       {
         "slug": "aluno",
         "tipo": "autocomplete",
         "icone": "fa-solid fa-user-graduate",
         "rotulo": "Aluno"
       },
       {
         "slug": "situacao",
         "tipo": "select",
         "autocomplete": false,
         "icone": "fa-solid fa-book",
         "rotulo": "Situação",
         "selecionado": "inprogress",
         "opcoes": [
           {"label": "Em andamento",  "value": "inprogress" },
           {"label": "Favoritos",     "value": "favourites" },
           {"label": "Não iniciados", "value": "future"     },
           {"label": "Arquivados",    "value": "hidden"     },
           {"label": "Todos (lento)", "value": "all"        },
         ]
       },
       {
         "slug": "semestres",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-calendar-days",
         "rotulo": "Semestres",
         "selecionados": [],
         "opcoes": [
           {"label": "2026.2",  "value": "2026.2" },
           {"label": "2026.1",  "value": "2026.1" },
           {"label": "2025.2",  "value": "2025.2" },
           {"label": "2025.1",  "value": "2025.1" },
           {"label": "2024.2",  "value": "2024.2" },
           {"label": "2024.1",  "value": "2024.1" },
           {"label": "2023.2",  "value": "2023.2" },
           {"label": "2023.1",  "value": "2023.1" },
         ]
       },
       {
         "slug": "periodos",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-calendar-week",
         "rotulo": "Períodos",
         "selecionados": [],
         "opcoes": [
           {"label": "1º",  "value": "1º" },
           {"label": "2º",  "value": "2º" },
           {"label": "3º",  "value": "3º" },
           {"label": "4º",  "value": "4º" },
           {"label": "5º",  "value": "5º" },
           {"label": "6º",  "value": "6º" },
           {"label": "7º",  "value": "7º" },
           {"label": "8º",  "value": "8º" },
         ]
       },
       {
         "slug": "papeis",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-user-tag",
         "rotulo": "Papéis",
         "selecionados": [],
         "opcoes": [
           {"label": "Gestor", "value": "1"},
           {"label": "Professor", "value": "2"},
           {"label": "Aluno", "value": "3"},
           {"label": "Orientador", "value": "4"},
         ]
       },
       {
         "slug": "ambientes",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-person-military-to-person",
         "rotulo": "Ambientes",
         "selecionados": [],
         "opcoes": [
           {"label": "Acadêmico",  "value": "academico",  "cor": "#0d6efd", "icone": "fa-solid fa-door-open"},
           {"label": "Presencial", "value": "presencial", "cor": "#0dcaf0", "icone": "fa-solid fa-chalkboard-user"},
           {"label": "Projetos",   "value": "projetos",   "cor": "#198754", "icone": "fa-solid fa-flask"},
         ]
       },
     ],
     "ordenacao": {
       "selecionada": "data_acesso",
       "opcoes": [
         { "value": "data_acesso", "direcao": "DESC", "rotulo": "Acesso mais recente"   },
         { "value": "data_inicio", "direcao": "DESC", "rotulo": "Início mais recente"   },
         { "value": "data_fim",    "direcao": "DESC", "rotulo": "Final mais recente"    },
         { "value": "titulo",      "direcao": "ASC",  "rotulo": "Título"                },
         { "value": "codigo",      "direcao": "ASC",  "rotulo": "Código"                },
         { "value": "semestre",    "direcao": "DESC", "rotulo": "Semestre mais recente" },
       ]
     }
   }


Auto-inscrições
^^^^^^^^^^^^^^^

São cursos em que qualquer aluno pode se inscrever sem aprovação prévia.

* Não possui filtros.
* Não possui ordenação.
* Possui quantidade de salas.
* O nome da sala é o nome do curso.
* O código da sala é o código da turma.

.. code-block:: json

   {
     "slug": "autoinscricoes",
     "rotulo_curto": "Auto-inscrições",
     "rotulo_longo": "Auto-inscrições",
     "dica": "Cursos para auto-inscrição",
     "subtitulo": "Cursos abertos em que você pode se inscrever sem aprovação prévia.",
     "icon": "fa-brands fa-stripe-s",
     "ordem": 4,
     "selecionado": false,
     "ativo": true,
     "quantidade_salas": 2,
     "suprimir": null,
     "filtros": null,
     "ordenacao": null
   }


Backup dos cursos
^^^^^^^^^^^^^^^^^^^^

Dos cursos podem ser feitos backup, automáticos ou pelos professores, professores podem compartilhar os backups
com outros professores.

* Possui filtros.
* Possui ordenação.
* Possui quantidade de salas.
* Os nomes e códigos seguem as regras dos diários, afinal, são apenas backups.

.. code-block:: json

   {
     "slug": "backup",
     "rotulo_curto": "Backups",
     "rotulo_longo": "Meus backups",
     "dica": "Backups",
     "subtitulo": "Backups dos seus diários ou compartilhados com você.",
     "icon": "fa-solid fa-box-archive",
     "ordem": 5,
     "selecionado": false,
     "ativo": true,
     "quantidade_salas": 200,
     "suprimir": null,
     "filtros": [
       {
         "slug": "posse",
         "tipo": "select",
         "autocomplete": false,
         "icone": "fa-solid fa-box-archive",
         "rotulo": "Posse",
         "selecionado": "meu",
         "opcoes": [{"label": "Meus backups", "value": "meu"}, {"label": "Compartilhados comigo", "value": "compartilhados"}]
       },
       {
         "slug": "semestres",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-calendar-days",
         "rotulo": "Semestres",
         "selecionados": [],
         "opcoes": [{"label": "2026.2",  "value": "2026.2" }, {"label": "2023.1",  "value": "2023.1" }]
       },
       {
         "slug": "periodos",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-calendar-week",
         "rotulo": "Períodos",
         "selecionados": [],
         "opcoes": [{"label": "1º",  "value": "1º" }, {"label": "8º",  "value": "8º" }]
       },
       {
         "slug": "disciplinas",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-book-open",
         "rotulo": "Disciplinas",
         "selecionados": [],
         "opcoes": [{"label": "Disciplina 1", "value": "1"}, {"label": "Disciplina 8", "value": "8"}]
       },
       {
         "slug": "cursos",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-graduation-cap",
         "rotulo": "Cursos",
         "selecionados": [],
         "opcoes": [{"label": "Curso 1", "value": "1"}, {"label": "Curso 800", "value": "800"}]
       },
       {
         "slug": "papeis",
         "tipo": "multiselect",
         "autocomplete": true,
         "icone": "fa-solid fa-user-tag",
         "rotulo": "Papéis",
         "selecionados": [],
         "opcoes": [{"label": "Aluno", "value": "student"}, {"label": "Professor", "value": "editingteacher"}]
       }
     ],
     "ordenacao": {
       "selecionada": "data_acesso",
       "opcoes": [
         { "value": "data_inicio", "direcao": "DESC", "rotulo": "Início mais recente"   },
         { "value": "data_fim",    "direcao": "DESC", "rotulo": "Final mais recente"    },
         { "value": "data_backup", "direcao": "DESC", "rotulo": "Backup mais recente"   },
         { "value": "titulo",      "direcao": "ASC",  "rotulo": "Título"                },
         { "value": "codigo",      "direcao": "ASC",  "rotulo": "Código"                },
       ]
     }
   }


10. ``GET /sala/tipo/quantidades/``
-----------------------------------


Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "inicio": 0,
     "diario": 0,
     "coordenacao": 0,
     "laboratorio": 0,
     "autoinscricoes": 0,
     "backup": 0
   }


11. ``GET /sala/tipo/<tipo>/<ava>/``
------------------------------------


Retorna as salas do tipo informado no AVA informado.

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
     {
         "sala_tipo": "",
         "id": "",
         "fullname": "",
         "shortname": "",
         "progress": null,
         "hasprogress": false,
         "isfavourite": false,
         "visible": "1",
         "can_set_visibility": 1,
         "can_check_grades": true,
         "viewurl": "",
         "checkgradesurl": "",
         "mensagemurl": "",
         "suapsurl": "",
         "gradesurl": "",
         "disciplina": {"id": "", "descricao": "", "sigla": ""},
         "curso": {"codigo": "", "nome": ""},
         "turma": {"codigo": "", "ano_periodo": ""},
         "diario": {"id": "", "id_clean": 0},
         "autoinscricao": {"restricoes": "", "details_url": "", "is_enrolled": false},
         "ambiente": {"label": "Acadêmico",  "value": "academico",  "cor": "#0d6efd", "icone": "fa-solid fa-door-open"}
     }
   ]


12. ``GET /sala/progresso/<ava>/<id>{,<id>/}{,<id>}/``
------------------------------------------------------


Retorna o progresso das salas solicitadas no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
     {
       "id": "",
       "progress": null,
       "hasprogress": false,
     }
   ]


13. ``PATCH /sala/favorito/<ava>/<id>/``
----------------------------------------


Adiciona ou remove a sala da lista de favoritos

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "favorite": true
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "favorite": true
   }


14. ``PATCH /sala/visivel/<ava>/<id>/``
---------------------------------------


Oculta ou mostra a sala

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
     "visible": true
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
     "visible": true
   }


Notificação
===========


15. ``GET /notificacao/``
-------------------------


Retorna o sumário das notificações do usuário.

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
       {
           "ava": "<string>",
           "unreadcount": 0
       }
   ]


16. ``GET /notificacao/<ava>/``
-------------------------------


Retorna as notificações do usuário no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
       "result": [
           {
               "id": 0,
               "useridfrom": -10,
               "useridto": 0,
               "subject": "",
               "shortenedsubject": "",
               "text": "",
               "fullmessage": "",
               "fullmessageformat": 4,
               "fullmessagehtml": "",
               "smallmessage": "",
               "contexturl": "",
               "contexturlname": "",
               "timecreated": "iso 8601",
               "timecreatedpretty": "<relative_time>",
               "timeread": "iso 8601 or null",
               "read": false,
               "deleted": false,
               "iconurl": "url",
               "component": "string",
               "eventtype": "string",
               "customdata": "string or null"
           }
       ],
       "unreadcount": 1
   }


17. ``GET /notificacao/<ava>/<id>{,<id>/}{,<id>}/``
---------------------------------------------------


Retorna o conteúdo das notificações solicitadas no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   {
       "id": 0,
       "useridfrom": -10,
       "useridto": 0,
       "subject": "",
       "shortenedsubject": "",
       "text": "",
       "fullmessage": "",
       "fullmessageformat": 4,
       "fullmessagehtml": "",
       "smallmessage": "",
       "contexturl": "",
       "contexturlname": "",
       "timecreated": "iso 8601",
       "timecreatedpretty": "<relative_time>",
       "timeread": "iso 8601 or null",
       "read": false,
       "deleted": false,
       "iconurl": "url",
       "component": "string",
       "eventtype": "string",
       "customdata": "string or null"
   }


18. ``PATCH /notificacao/<ava>/<id>{,<id>/}{,<id>}/``
-----------------------------------------------------


Marca as notificações como lida ou não lida no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
       "is_read": false
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
       {
           "error":false,
           "data":{
               "notificationid":0,
               "warnings":[]
           }
       }
   ]


Conversa
========


19. ``GET /conversa/``
----------------------


Retorna o sumário das mensagens do usuário.

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
       {
           "ava": "<string>",
           "unreadcount": 0,
           "favourites": 0
       }
   ]


20. ``GET /conversa/<ava>/``
----------------------------


Retorna as mensagens do usuário no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
     {
       "id": 1,
       "name": "",
       "subname": null,
       "imageurl": null,
       "type": 3,
       "membercount": 1,
       "ismuted": false,
       "isfavourite": true,
       "isread": true,
       "unreadcount": null,
       "members": [
         {
           "id": 3,
           "fullname": "",
           "profileurl": "",
           "profileimageurl": "",
           "profileimageurlsmall": "",
           "isonline": true,
           "showonlinestatus": true,
           "isblocked": false,
           "iscontact": false,
           "isdeleted": false,
           "canmessageevenifblocked": null,
           "canmessage": null,
           "requirescontact": null,
           "cancreatecontact": true,
           "contactrequests": []
         }
       ],
       "messages": [
         {
           "id": 13259,
           "useridfrom": 3,
           "text": "",
           "timecreated": 1677887869
         }
       ],
       "candeletemessagesforallusers": true
     }
   ]



21. ``GET /conversa/<ava>/<id>{,<id>}{,<id>}/``
-----------------------------------------------


Retorna o conteúdo das mensagens solicitadas no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``

Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [
     {
       "id": 5309,
       "members": [
         {
           "id": 8,
           "fullname": "",
           "profileurl": "",
           "profileimageurl": "",
           "profileimageurlsmall": "",
           "isonline": false,
           "showonlinestatus": true,
           "isblocked": false,
           "iscontact": false,
           "isdeleted": false,
           "canmessageevenifblocked": null,
           "canmessage": null,
           "requirescontact": null,
           "cancreatecontact": true,
           "contactrequests": []
         }
       ],
       "messages": [
         {
           "id": 14330,
           "useridfrom": 8,
           "text": "<p>Novo testes p\u00f3s DIGTI<\/p>",
           "timecreated": 1678147989
         }
       ]
     }
   ]


22. ``PATCH /conversa/<ava>/<id>/``
-----------------------------------


Marca as mensagens como lida ou não lida no AVA informado

Requisição de exemplo
~~~~~~~~~~~~~~~~~~~~~


Headers:

* ``Authorization: Bearer <seu_token_jwt>``
* ``accept: application/json``
* ``Content-Type: application/json``

.. code-block:: json

   {
       "is_read": true
   }


Respostas de exemplo
~~~~~~~~~~~~~~~~~~~~


.. code-block:: json

   [{"error":false,"data":null}]
