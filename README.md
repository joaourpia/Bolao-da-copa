# Bolão da Copa 2026

Aplicativo web para o bolão da Copa do Mundo FIFA 2026 entre amigos. Cada
participante entra com seu login, registra os palpites de placar de **todos
os 72 jogos da fase de grupos** e o sistema calcula o ranking sozinho à
medida que os resultados saem.

## Regras do bolão

Acertar o **placar exato** vale **3 pontos**. Acertar apenas o **resultado**
(vitória de um lado, do outro ou empate) vale **1 ponto**. Errar não pontua.
Só conta a fase de grupos; quem tiver mais pontos depois do último jogo leva
o bolão. Em caso de empate, desempata quem cravou mais placares e, depois,
quem acertou mais resultados. Cada participante cadastrado entra valendo
R$ 20, e o total arrecadado é calculado automaticamente (nº de
participantes × R$ 20).

## O que o aplicativo faz

O **Painel** mostra número de participantes, valor arrecadado, líder do
momento, próximos jogos e o Top 5. Em **Meus palpites** cada participante
preenche os placares, com bandeira e nome de cada país, até o prazo final.
**Jogos e resultados** traz os 72 confrontos com os placares reais e os
pontos que você fez. O **Ranking** é recalculado ao vivo. A **Auditoria**
deixa qualquer participante conferir os palpites dos demais depois do
fechamento — transparência total, já que envolve dinheiro. O **Admin** é o
painel do organizador.

Os resultados reais são buscados automaticamente na API oficial
football-data.org. Não é preciso digitar placar nenhum.

---

## Como funciona o "banco de dados"

O app usa uma **planilha do Google** como banco de dados. Ele cria sozinho
três abas na planilha: `participantes`, `palpites` e `config`. Você não
precisa formatar nada — basta criar a planilha vazia e dar acesso a ela.

Se a planilha não estiver configurada, o app entra em **modo local de
teste**, gravando tudo no arquivo `data/local_db.json`. Esse modo serve só
para experimentar na sua máquina; ao publicar na nuvem é obrigatório usar o
Google Sheets, senão os dados se perdem.

---

## Passo 1 — Rodar na sua máquina (teste rápido)

1. Instale o Python 3.11 ou superior.
2. Em um terminal, dentro da pasta do projeto, rode:

   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. O app abre no navegador. Sem segredos configurados, ele roda em modo
   local de teste e em modo de referência (sem resultados ao vivo) — o
   suficiente para ver as telas funcionando.

Para o login do organizador nesse teste, crie o arquivo
`.streamlit/secrets.toml` (copie de `.streamlit/secrets.toml.example`) e
preencha pelo menos a seção `[admin]`.

---

## Passo 2 — Criar a planilha do Google

1. Acesse https://sheets.google.com e crie uma planilha em branco.
2. Dê um nome a ela (ex.: "Bolão da Copa 2026").
3. Copie o **ID da planilha**: na URL
   `https://docs.google.com/spreadsheets/d/`**`ESTE_PEDACO`**`/edit`, o ID é
   o trecho entre `/d/` e `/edit`.

---

## Passo 3 — Criar a conta de serviço do Google

A conta de serviço é o "robô" que dá ao app permissão de ler e escrever na
planilha.

1. Acesse https://console.cloud.google.com e crie um projeto (ou use um
   existente).
2. No menu, vá em **APIs e serviços → Biblioteca** e ative a **Google
   Sheets API** e a **Google Drive API**.
3. Vá em **APIs e serviços → Credenciais → Criar credenciais → Conta de
   serviço**. Dê um nome e finalize.
4. Abra a conta de serviço criada, aba **Chaves → Adicionar chave → Criar
   nova chave → JSON**. Um arquivo `.json` será baixado.
5. Abra o JSON: copie o valor do campo `client_email` (algo como
   `nome@projeto.iam.gserviceaccount.com`).
6. Volte na planilha do Google, clique em **Compartilhar** e compartilhe a
   planilha com esse e-mail, com permissão de **Editor**.

---

## Passo 4 — Obter a chave da API de futebol

1. Registre-se gratuitamente em
   https://www.football-data.org/client/register
2. Você receberá por e-mail um **API Token** (uma sequência de caracteres).
3. Guarde esse token — ele vai no `secrets.toml`.

O plano gratuito da football-data.org cobre a Copa do Mundo. Importante:
veja a seção "Observações sobre a API" no fim deste documento.

---

## Passo 5 — Preencher o arquivo de segredos

Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e
preencha:

- `[admin]` — usuário, senha e nome do organizador (o login master).
- `[gsheets]` — o `spreadsheet_id` copiado no Passo 2.
- `[api]` — o `football_data_key` obtido no Passo 4.
- `[gcp_service_account]` — copie cada campo do arquivo JSON baixado no
  Passo 3 para o campo correspondente.

O `secrets.toml` **nunca** deve ir para o GitHub. Ele já está no
`.gitignore`.

---

## Passo 6 — Publicar no Streamlit Community Cloud (grátis)

1. Crie uma conta no GitHub e suba esta pasta para um repositório novo
   (pode ser privado). O `secrets.toml` não será enviado por causa do
   `.gitignore` — isso é o esperado.
2. Acesse https://share.streamlit.io e entre com a conta do GitHub.
3. Clique em **Create app / New app**, escolha o repositório e informe
   `app.py` como arquivo principal.
4. Em **Advanced settings → Secrets**, cole todo o conteúdo do seu
   `secrets.toml` (o mesmo do Passo 5).
5. Clique em **Deploy**. Em um ou dois minutos o app estará no ar com um
   link público que você pode mandar para o grupo.

Na primeira vez que o app abrir, ele cria sozinho as abas na planilha.

---

## Passo 7 — Usar o sistema (organizador)

1. Abra o app e entre com o usuário/senha definidos em `[admin]`.
2. Vá em **Admin → Participantes** e cadastre cada amigo (nome, login e
   senha). Informe a cada um o login e a senha dele.
3. Em **Admin → Prazo dos palpites**, defina a data e a hora limite para o
   envio dos palpites (sugestão: o horário do primeiro jogo da Copa).
4. Cada participante entra com o próprio login, vai em **Meus palpites** e
   preenche os 72 jogos antes do prazo.
5. Depois do prazo, ninguém mais consegue alterar nada e os palpites de
   todos ficam visíveis na aba **Auditoria**.
6. Durante a Copa, o ranking se atualiza sozinho. Se quiser forçar uma
   atualização imediata, use **Admin → Sistema → Sincronizar agora**.

---

## Perguntas comuns

**Preciso atualizar os resultados na mão?** Não. O app busca os placares na
API oficial automaticamente. O botão "Sincronizar agora" existe só para
quem quiser forçar a atualização na hora.

**Os participantes podem ver os palpites uns dos outros?** Só depois do
prazo. Antes disso, cada um vê apenas os próprios palpites — assim ninguém
copia. Depois do fechamento, tudo fica aberto para auditoria.

**Um jogo trava quando começa?** Sim. Mesmo dentro do prazo geral, cada
partida deixa de aceitar palpites no horário de início dela.

**O organizador também joga?** O login `[admin]` é só do organizador. Se
você quiser participar do bolão, cadastre a si mesmo também como
participante (com outro login) e jogue por essa conta.

---

## Observações sobre a API

O app foi feito para usar os resultados da football-data.org de forma
**100% automática**. Antes da Copa começar, vale testar: entre como
organizador em **Admin → Sistema** e confira se aparece "dados recebidos da
API oficial".

Caso a API gratuita não traga os jogos da Copa 2026, o app continua
funcionando normalmente — os participantes preenchem os palpites pela
tabela do sorteio oficial — mas os resultados não serão atualizados
sozinhos. Se isso acontecer, a alternativa é trocar de fonte de dados; o
código foi organizado no arquivo `lib/football_api.py` justamente para
facilitar essa troca.

## Estrutura do projeto

```
bolao-copa-2026/
├── app.py                  ponto de entrada (login + navegação)
├── requirements.txt        dependências
├── .streamlit/
│   ├── config.toml         tema visual
│   └── secrets.toml.example modelo de segredos
├── lib/                    lógica do sistema
│   ├── config.py           constantes e regras
│   ├── flags.py            seleções, grupos e bandeiras
│   ├── football_api.py     integração com a API + jogos
│   ├── database.py         banco de dados (Google Sheets)
│   ├── auth.py             login e senhas
│   ├── scoring.py          pontuação e ranking
│   ├── segredos.py         leitura segura do secrets.toml
│   ├── utils.py            datas e prazos
│   └── ui.py               estilo visual e componentes
└── views/                  as telas do app
    ├── dashboard.py        painel inicial
    ├── palpites.py         envio de palpites
    ├── jogos.py            jogos e resultados
    ├── ranking.py          ranking ao vivo
    ├── auditoria.py        auditoria dos palpites
    └── admin.py            painel do organizador
```
