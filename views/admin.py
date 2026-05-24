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
    st.markdown("### Cadastrar novo participante")
    st.caption(
        "Cada participante cadastrado entra automaticamente no bolao valendo "
        f"{utils.moeda(config.VALOR_ENTRADA)}."
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
            "Total arrecadado: "
            f"{utils.moeda(total * config.VALOR_ENTRADA)}"
        )
    if not participantes:
        st.info("Nenhum participante cadastrado ainda.")
        return

    for p in participantes:
        cols = st.columns([3, 2.4, 2, 1.4])
        cols[0].markdown(f"**{p['nome']}**")
        cols[1].caption(f"login: {p['usuario']}")
        with cols[2].popover("Redefinir senha"):
            nova = st.text_input(
                "Nova senha", type="password", key=f"ns_{p['id']}"
            )
            if st.button("Salvar nova senha", key=f"bs_{p['id']}"):
                if len(nova or "") < 4:
                    st.error("Minimo de 4 caracteres.")
                else:
                    h, s = auth.gerar_hash(nova)
                    database.atualizar_senha(p["id"], h, s)
                    st.success("Senha atualizada.")
        if cols[3].button("Remover", key=f"rm_{p['id']}"):
            database.remover_participante(p["id"])
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
# Aba: Sistema
# ----------------------------------------------------------------------
def _aba_sistema():
    st.markdown("### Status do sistema")

    if database.modo_banco() == "sheets":
        st.success("Banco de dados: Google Sheets conectado.")
    else:
        st.warning(
            "Banco de dados: MODO LOCAL de teste (data/local_db.json). "
            "Os dados nao ficam salvos na nuvem. Configure o Google Sheets "
            "para o uso definitivo - veja o README."
        )

    dados = buscar_jogos(segredos.chave_api_futebol())
    if segredos.chave_api_futebol():
        st.success("API de resultados: chave configurada.")
    else:
        st.warning(
            "API de resultados: nenhuma chave configurada. Os resultados "
            "nao serao atualizados automaticamente."
        )
    if dados["fonte"] == "api":
        st.success("Ultima leitura: dados recebidos da API oficial.")
    else:
        st.info(
            "Ultima leitura: usando a tabela de referencia do sorteio "
            "(sem resultados ao vivo)."
        )

    if st.session_state.get("_erro_api"):
        st.caption(f"Aviso da API: {st.session_state['_erro_api']}")
    if st.session_state.get("_erro_db"):
        st.caption(st.session_state["_erro_db"])

    st.divider()
    st.markdown("### Sincronizar resultados")
    st.caption(
        "Os resultados sao atualizados automaticamente a cada poucos minutos. "
        "Use o botao abaixo para forcar uma atualizacao imediata."
    )
    if st.button("Sincronizar agora", type="primary"):
        st.cache_data.clear()
        st.success("Cache limpo - os dados serao recarregados da API.")
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
