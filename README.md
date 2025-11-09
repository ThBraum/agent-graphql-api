Agent GraphQL API
==================

API GraphQL (FastAPI + Strawberry) para gerenciar memórias de agentes, com suporte a Prompt do assistente exposto via GraphQL.

Como rodar localmente
---------------------

1) Copie o exemplo de ambiente e ajuste:

	 cp .env.example .env

	 Edite `DATABASE_URL` se for usar o Postgres. Para testar apenas o GraphQL/health e o prompt, não é necessário banco (a conexão só é usada ao consultar/alterar memórias).

2) Instale dependências (via Poetry ou pip):

	 - Poetry (recomendado)

		 poetry install

	 - Pip

		 pip install -e .

3) Rode o servidor (Uvicorn):

	 uvicorn app.main:app --reload

Endpoints
---------

- Health: GET http://localhost:8000/healthz → {"status":"ok"}
- GraphQL: POST http://localhost:8000/graphql

Se você definir `GRAPHQL_API_KEY` no `.env`, envie o header `x-api-key: <sua-chave>` nas chamadas ao GraphQL.

Para uso em frontends/clients, você também pode configurar `GRAPHQL_URL` no `.env` (por padrão: `http://localhost:8000/graphql`).

No GraphQL, você pode consultar o prompt do assistente:

query {\n  assistantPrompt\n}

Para sobrescrever o prompt em produção, defina `ASSISTANT_PROMPT` no `.env` (use `\n` para quebras de linha) ou ajuste o default em `app/config.py`.

Integração n8n (passo a passo rápido)
-------------------------------------

- No n8n, no node do seu provedor LLM (ex.: OpenAI Chat), cole o conteúdo do prompt em:
	- System Instructions / System Prompt (ou campo equivalente). Se houver um campo de "imagem" no seu fluxo atual, substitua-o pelo texto do prompt.
- Se quiser buscar sempre a versão mais recente do prompt a partir da API, adicione um HTTP Request node em n8n apontando para `POST http://localhost:8000/graphql` com o body JSON:

	{"query":"query { assistantPrompt }"}

	Em seguida, use a resposta `data.assistantPrompt` como variável no node do LLM.

Notas
-----

- O banco Postgres só é necessário para operações em `memories`/`agents`. A consulta `assistantPrompt` não acessa o banco.
- CORS: configure `ALLOWED_ORIGINS` no `.env` para permitir seu frontend.
 - Para frontends, use a variável `GRAPHQL_URL` apontando para o endpoint da API.
