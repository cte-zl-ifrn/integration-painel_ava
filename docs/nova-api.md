# Especificação da Nova API v2

A raiz da nova API será `/api/v2/`

## Autenticação

### 1. `POST /token/pair/`

Gera um novo par de tokens

#### Requisição de exemplo

Headers:

* `accept: application/json`
* `Content-Type: application/json`

```json
{
  "password": "string",
  "username": "string"
}
```

#### Respostas de exemplo

```json
{
  "username": "string",
  "refresh": "jwt",
  "access": "jwt"
}
```

```json
{
  "detail": "No active account found with the given credentials",
  "code": "authentication_failed"
}
```

```json
{
  "detail": "Invalid input.",
  "code": "invalid",
  "username": "username is required",
  "password": "password is required"
}
```

### 2. `POST /token/refresh/`

Gera um novo par de tokens no Painel AVA e nos AVA em que ocorreu a autenticação usando este token

#### Requisição de exemplo

Headers:

* `accept: application/json`
* `Content-Type: application/json`

```json
{
  "refresh": "string"
}
```

#### Respostas de exemplo

```json
{
  "refresh": "string",
  "access": "string"
}
```

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

```json
{
  "detail": "Invalid input.",
  "code": "invalid",
  "refresh": "token is required"
}
```

### 3. `POST /token/verify/`

Verifica se o token é válido

#### Requisição de exemplo

Headers:

* `accept: application/json`
* `Content-Type: application/json`

```json
{
  "token": "string"
}
```

#### Respostas de exemplo

```json
{
  "refresh": "jwt",
  "access": "jwt"
}
```

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

```json
{
  "detail": "Invalid input.",
  "code": "invalid",
  "token": "token is required"
}
```

### 4. `POST /token/revoke/`

Revoga o token no Painel AVA e nos AVA em que ocorreu a autenticação usando este token

#### Requisição de exemplo

Headers:

* `accept: application/json`
* `Content-Type: application/json`

```json
{
  "token": "jwt"
}
```

#### Respostas de exemplo

```json
{
    "detail": "Token revoked",
    "revoke_list": [
        {"service_name": "<string>", "url": "<string>", "revoked": true, "duration": "<duration in ISO 8601 format>"}
    ]
}
```

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

```json
{
  "detail": "Invalid input.",
  "code": "invalid",
  "token": "token is required"
}
```

## Usuário

### 5. `GET /usuario/info/`

Retorna informações do usuário

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`
* `Content-Type: application/json`

#### Respostas de exemplo

```json

```

### 6. `GET /usuario/preferencia/`

Retorna preferências do usuário

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 7. `PATCH /usuario/preferencia/`

Atualiza preferências do usuário

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

## Sala de aula virtual

### 8. `GET /sala/tipo/`

Lista os tipos de sala

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 9. `GET /sala/tipo/*/`

O mesmo que o anterior

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 10. `GET /sala/tipo/<ava>/`

Retorna os tipos de sala do AVA informado

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 11. `QUERY /sala/tipo/<ava>/<tipo>/`

Retorna as salas do tipo informado no AVA informado (filtros e paginação vão no body)

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 12. `GET /sala/continuar/`

Retorna um subconjunto de salas que o aluno tem progresso incompleto

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 13. `GET /sala/progresso/<ava>/<id>/{<id>/}{<id>/}`

Retorna o progresso das salas solicitadas no AVA informado

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 14. `PATCH /sala/favorito/<ava>/<id>/`

Adiciona ou remove a sala da lista de favoritos

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

### 15. `PATCH /sala/visivel/<ava>/<id>/`

Oculta ou mostra a sala

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```

## Notificação

### 16. `GET /notificacao/`

Retorna o sumário das notificações do usuário (filtros e paginação vão no body)

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`

#### Respostas de exemplo

```json
[
    {
        "ava": "<string>",
        "unreadcount": 0
    }
]
```

### 17. `GET /notificacao/<ava>/`

Retorna as notificações do usuário no AVA informado

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`

#### Respostas de exemplo

```json
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
```

### 18. `GET /notificacao/<ava>/<id>/{<id>/}{<id>/}`

Retorna o conteúdo das notificações solicitadas no AVA informado

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`

#### Respostas de exemplo

```json
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
```

### 19. `PATCH /notificacao/<ava>/<id>/{<id>/}{<id>/}`

Marca as notificações como lida ou não lida no AVA informado

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`
* `Content-Type: application/json`

```json
{
    "readed": false
}
```

#### Respostas de exemplo

```json
[
    {
        "error":false,
        "data":{
            "notificationid":0,
            "warnings":[]
        }
    }
]
```

## Mensagem

### 20. `GET /mensagem/`

Retorna o sumário das mensagens do usuário (filtros e paginação vão no body)

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`

#### Respostas de exemplo

```json
[
    {
        "ava": "<string>",
        "unreadcount": 0
    }
]
```

### 21. `GET /mensagem/<ava>/`

Retorna as mensagens do usuário no AVA informado

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`

#### Respostas de exemplo

```json
{
    "conversations": [
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
}
```

### 22. `GET /mensagem/<ava>/<id>/{<id>/}{<id>/}`

Retorna o conteúdo das mensagens solicitadas no AVA informado

#### Requisição de exemplo

Headers:

* `Authorization: Bearer <seu_token_jwt>`
* `accept: application/json`

#### Respostas de exemplo

```json

```

### 23. `PATCH /mensagem/<ava>/<id>/`

Marca as mensagens como lida ou não lida no AVA informado

#### Requisição de exemplo

```json

```

#### Respostas de exemplo

```json

```
