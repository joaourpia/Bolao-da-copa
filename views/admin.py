"""Painel do organizador (somente admin)."""

import streamlit as st

from lib import auth, config, database, scoring, segredos, ui, utils
from lib.football_api import buscar_jogos, jogo_finalizado


# ----------------------------------------------------------------------
# Aba: Participantes
# ----------------------------------------------------------------------
def _validar_cadastro(nome, usuario, senha):
    nome = (nome or "").strip()
    usuario = (usuario or "").strip()
    if not nome:
        return "Informe o nome do participante."
    if not usuario:
        return "Informe o usuario (login)."
    if " " in usuario:
        return "O usuario nao pode conter espacos."
    if len(senha or "") < 4:
        return "A senha deve ter ao menos 4 caracteres."
    admin = segredos.admin_configurado()
    if usuario.lower() == str(admin.get("usuario", "")).strip().lower():
        return "Esse usuario e o do organizador. Escolha outro."
    if database.obter_participante_por_usuario(usuario):
        return "Ja existe um participante com esse usuario."
    return None


def _aba_participantes():
    st.markdown("### Cadastrar participante")
    st.caption(
        "Em geral cada pessoa cria a propria conta na tela inicial. Use o "
        "formulario abaixo so se quiser cadastrar alguem manualmente."
    )
    with st.form("novo_participante", clear_on_submit=True):
        cols = st.columns(3)
        nome = cols[0].text_input("Nome completo")
        usuario = cols[1].text_input("Usuario (login)")
        senha = cols[2].text_input("Senha", type="password")
        criar = st.form_submit_button("Cadastrar participante", type="primary")

    if criar:
        erro = _validar_cadastro(nome, usuario, senha)
        if erro:
            st.error(erro)
        else:
            senha_hash, salt = auth.gerar_hash(senha)
            database.adicionar_participante(
                nome.strip(), usuario.strip(), senha_hash, salt
            )
            st.success(
                f"Participante '{nome.strip()}' cadastrado. "
                f"Login: {usuario.strip()}  |  Senha: {senha}"
            )

    st.divider()
    participantes = database.listar_participantes()
    total = len(participantes)
    st.markdown(f"### Participantes cadastrados ({total})")
    if total:
        st.caption(
            f"Total arrecadado: {utils.moeda(total * config.VALOR_ENTRADA)}"
        )
    if not participantes:
        st.info("Nenhum participante cadastrado ainda.")
        return

    for p in participantes:
        cols = st.columns([3, 2, 1.5, 1.2])
        cols[0].markdown(f"**{p['nome']}**")
        rotulo = f"login: {p['usuario']}"
        if p.get("precisa_trocar"):
            rotulo += "  -  senha zerada (aguarda troca)"
        cols[1].caption(rotulo)
        if cols[2].button("Zerar senha", key=f"zs_{p['id']}"):
            temp = auth.gerar_senha_temporaria()
            senha_hash, salt = auth.gerar_hash(temp)
            database.atualizar_senha(
                p["id"], senha_hash, salt, precisa_trocar=True
            )
            st.session_state[f"_temp_senha_{p['id']}"] = temp
        if cols[3].button("Remover", key=f"rm_{p['id']}"):
            database.remover_participante(p["id"])
            st.rerun()
        if st.session_state.get(f"_temp_senha_{p['id']}"):
            temp = st.session_state[f"_temp_senha_{p['id']}"]
            ca, cb = st.columns([5, 1])
            ca.success(
                f"Senha temporaria de **{p['nome']}**: **{temp}**  -  "
                "envie para a pessoa; ela sera obrigada a trocar no proximo login."
            )
            if cb.button("Esconder", key=f"hide_{p['id']}"):
                st.session_state.pop(f"_temp_senha_{p['id']}", None)
                st.rerun()


# ----------------------------------------------------------------------
# Aba: Prazo dos palpites
# ----------------------------------------------------------------------
def _aba_prazo():
    st.markdown("### Prazo final para envio dos palpites")
    prazo = utils.prazo_palpites()
    if utils.palpites_abertos():
        st.info(
            f"Prazo atual: {utils.fmt_data_longa(prazo)} "
            f"(faltam {utils.tempo_restante(prazo)})"
        )
    else:
        st.warning(
            f"Os palpites estao ENCERRADOS desde {utils.fmt_data_longa(prazo)}."
        )

    cols = st.columns(2)
    nova_data = cols[0].date_input("Nova data", value=prazo.date())
    nova_hora = cols[1].time_input("Novo horario", value=prazo.time())

    if st.button("Salvar novo prazo", type="primary"):
        texto = f"{nova_data.strftime('%Y-%m-%d')} {nova_hora.strftime('%H:%M')}"
        database.definir_config(config.CHAVE_PRAZO, texto)
        st.success(
            f"Prazo atualizado para {nova_data.strftime('%d/%m/%Y')} as "
            f"{nova_hora.strftime('%H:%M')}."
        )
        st.rerun()

    st.caption(
        "Apos o prazo, os participantes nao conseguem mais inserir ou alterar "
        "palpites. Cada jogo tambem trava automaticamente no momento em que "
        "comeca. Encerrado o prazo, os palpites de todos ficam visiveis na "
        "aba Auditoria."
    )


# ----------------------------------------------------------------------
# Aba: Acompanhamento
# ----------------------------------------------------------------------
def _aba_acompanhamento():
    st.markdown("### Acompanhamento")
    participantes = database.listar_participantes()
    if not participantes:
        st.info("Nenhum participante cadastrado ainda.")
        return

    dados = buscar_jogos(segredos.chave_api_futebol())
    jogos = dados["jogos"]
    total_jogos = len(jogos)
    todos = database.listar_todos_palpites()
    ranking = scoring.calcular_ranking(participantes, todos, jogos)
    rank_por_id = {str(r["id"]): r for r in ranking}
    finalizados = sum(1 for j in jogos if jogo_finalizado(j))

    ui.linha_cartoes([
        ui.cartao_metrica("Participantes", len(participantes)),
        ui.cartao_metrica("Arrecadado",
                          utils.moeda(len(participantes) * config.VALOR_ENTRADA)),
        ui.cartao_metrica("Jogos encerrados", f"{finalizados}/{total_jogos}"),
    ])
    st.write("")

    pesos = [3, 2, 1.4, 1.4]
    cab = st.columns(pesos)
    for col, txt in zip(cab, ["Participante", "Palpites preenchidos",
                              "Pontos", "Posicao"]):
        col.markdown(f"**{txt}**")
    st.divider()

    for p in participantes:
        preenchidos = len(todos.get(str(p["id"]), {}))
        r = rank_por_id.get(str(p["id"]))
        cols = st.columns(pesos)
        cols[0].write(p["nome"])
        if preenchidos >= total_jogos:
            cor = ui.COR_VERDE
        elif preenchidos > 0:
            cor = ui.COR_OURO
        else:
            cor = ui.COR_PRIMARIA
        cols[1].markdown(
            ui.badge(f"{preenchidos}/{total_jogos}", cor, "#0B1437"),
            unsafe_allow_html=True,
        )
        cols[2].write(str(r["pontos"]) if r else "0")
        cols[3].write(f"{r['posicao']}o" if r else "-")


# ----------------------------------------------------------------------
# Aba: Sistema - diagnostico da conexao com o Google Sheets
# ----------------------------------------------------------------------
def _diagnostico_sheets():
    """Testa a conexao com o Google Sheets na hora e devolve o resultado."""
    res = {
        "gcp": False, "gsheets": False, "spreadsheet_id": "",
        "client_email": "", "conectou": False, "abas": [],
        "erro": "", "dica": "",
    }
    creds = segredos.secao("gcp_service_account")
    gsheets = segredos.secao("gsheets")
    res["gcp"] = bool(creds)
    res["gsheets"] = bool(gsheets)
    res["spreadsheet_id"] = str(gsheets.get("spreadsheet_id", "")).strip()
    res["client_email"] = str(creds.get("client_email", "")).strip()

    if not creds:
        res["erro"] = "A secao [gcp_service_account] nao foi encontrada nos Secrets."
        res["dica"] = (
            "Adicione a secao [gcp_service_account] no painel Secrets do "
            "Streamlit, com TODOS os campos do arquivo JSON da conta de servico."
        )
        return res
    if not res["spreadsheet_id"] or "COLE_AQUI" in res["spreadsheet_id"]:
        res["erro"] = "A secao [gsheets] esta sem um spreadsheet_id valido."
        res["dica"] = (
            'Adicione a secao [gsheets] nos Secrets com '
            'spreadsheet_id = "..." (o trecho da URL da planilha entre '
            "/d/ e /edit)."
        )
        return res
    try:
        import gspread

        gc = gspread.service_account_from_dict(creds)
        planilha = gc.open_by_key(res["spreadsheet_id"])
        res["abas"] = [ws.title for ws in planilha.worksheets()]
        res["conectou"] = True
    except Exception as erro:  # noqa: BLE001
        res["erro"] = f"{type(erro).__name__}: {erro}"
        texto = f"{type(erro).__name__} {erro}".lower()
        if "notfound" in texto or "not found" in texto or "404" in texto:
            res["dica"] = (
                "A planilha nao foi encontrada. Confira se o spreadsheet_id "
                "esta correto E, principalmente, se a planilha foi "
                "COMPARTILHADA (como Editor) com o e-mail da conta de servico "
                f"mostrado acima: {res['client_email']}"
            )
        elif ("permission" in texto or "403" in texto
              or "disabled" in texto or "has not been used" in texto):
            res["dica"] = (
                "Acesso negado. Faca as duas coisas: (1) compartilhe a "
                f"planilha como Editor com {res['client_email']}; (2) ative a "
                "Google Sheets API e a Google Drive API no projeto do Google "
                "Cloud (APIs e servicos > Biblioteca)."
            )
        else:
            res["dica"] = (
                "Verifique os campos da secao [gcp_service_account] nos "
                "Secrets, principalmente o private_key (ele deve estar em "
                "uma unica linha, com os \\n no lugar das quebras)."
            )
    return res


def _aba_sistema():
    st.markdown("### Status do sistema")
    diag = _diagnostico_sheets()

    if diag["conectou"]:
        st.success("Google Sheets CONECTADO com sucesso!")
        st.caption("Abas encontradas na planilha: " + ", ".join(diag["abas"]))
    else:
        st.error(
            "O app NAO esta conectado ao Google Sheets - ele esta em modo "
            "local e os dados sao temporarios (se perdem quando o app "
            "reinicia)."
        )

    st.markdown("#### Diagnostico da conexao")
    st.write(
        "- Secao **[gcp_service_account]** nos Secrets: "
        + ("encontrada" if diag["gcp"] else "**NAO encontrada**")
    )
    st.write(
        "- Secao **[gsheets]** nos Secrets: "
        + ("encontrada" if diag["gsheets"] else "**NAO encontrada**")
    )
    st.write(f"- spreadsheet_id lido: `{diag['spreadsheet_id'] or '(vazio)'}`")
    st.write(
        f"- e-mail da conta de servico: `{diag['client_email'] or '(vazio)'}`"
    )

    if diag["client_email"] and not diag["conectou"]:
        st.info(
            "A planilha do Google PRECISA estar compartilhada, como **Editor**, "
            f"com este e-mail:\n\n**{diag['client_email']}**"
        )
    if diag["erro"]:
        st.error("Erro tecnico retornado: " + diag["erro"])
    if diag["dica"]:
        st.warning("Como resolver: " + diag["dica"])

    st.divider()
    if segredos.chave_api_futebol():
        st.success("API de resultados: chave configurada.")
    else:
        st.warning("API de resultados: nenhuma chave configurada.")

    st.divider()
    st.markdown("### Recarregar / reconectar")
    st.caption(
        "Depois de ajustar os Secrets ou o compartilhamento da planilha, "
        "clique abaixo para o app tentar reconectar."
    )
    if st.button("Recarregar e reconectar", type="primary"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()


# ----------------------------------------------------------------------
def render():
    usuario = st.session_state["usuario_logado"]
    if usuario["papel"] != "admin":
        st.error("Acesso restrito ao organizador do bolao.")
        return

    st.markdown("## Painel do organizador")
    aba1, aba2, aba3, aba4 = st.tabs([
        "Participantes", "Prazo dos palpites", "Acompanhamento", "Sistema",
    ])
    with aba1:
        _aba_participantes()
    with aba2:
        _aba_prazo()
    with aba3:
        _aba_acompanhamento()
    with aba4:
        _aba_sistema()
