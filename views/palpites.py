"""Tela de envio dos palpites (apenas para participantes)."""

import streamlit as st

from lib import database, segredos, ui, utils
from lib.football_api import buscar_jogos, codigos_ordenados


def _valores_salvos(jogo, palpites_salvos):
    """Devolve (gols_casa, gols_fora) ja salvos para o jogo, ou (None, None)."""
    mk = jogo["match_key"]
    salvo = palpites_salvos.get(mk)
    if not salvo:
        return None, None
    c1, _ = codigos_ordenados(mk)
    if jogo["casa"] == c1:
        return salvo[0], salvo[1]
    return salvo[1], salvo[0]


def _linha_jogo(jogo, palpites_salvos, aberto):
    """Renderiza uma partida com os campos de palpite."""
    mk = jogo["match_key"]
    gc, gf = _valores_salvos(jogo, palpites_salvos)
    bloqueado = (not aberto) or utils.jogo_bloqueado(jogo)

    cols = st.columns([3, 1, 0.5, 1, 3])
    cols[0].markdown(ui.time_bloco(jogo["casa"]), unsafe_allow_html=True)
    cols[4].markdown(ui.time_bloco(jogo["fora"]), unsafe_allow_html=True)
    cols[2].markdown("<div class='bc-vs'>x</div>", unsafe_allow_html=True)

    if bloqueado:
        tc = "-" if gc is None else gc
        tf = "-" if gf is None else gf
        cols[1].markdown(f"<div class='bc-placar'>{tc}</div>",
                         unsafe_allow_html=True)
        cols[3].markdown(f"<div class='bc-placar'>{tf}</div>",
                         unsafe_allow_html=True)
    else:
        cols[1].number_input(
            "Gols casa", min_value=0, max_value=99,
            value=int(gc) if gc is not None else 0,
            key=f"casa_{mk}", label_visibility="collapsed",
        )
        cols[3].number_input(
            "Gols fora", min_value=0, max_value=99,
            value=int(gf) if gf is not None else 0,
            key=f"fora_{mk}", label_visibility="collapsed",
        )

    rotulo = f"Rodada {jogo['rodada']} - {utils.fmt_data_curta(jogo['data_utc'])}"
    if bloqueado and aberto:
        rotulo += "  (jogo ja iniciado - bloqueado)"
    st.caption(rotulo)


def render():
    usuario = st.session_state["usuario_logado"]
    st.markdown("## Meus palpites")

    if usuario["papel"] == "admin":
        st.info(
            "Voce esta logado como organizador. A tela de palpites e dos "
            "participantes - use a aba **Admin** para gerenciar o bolao."
        )
        return

    if st.session_state.pop("_palpites_ok", False):
        st.success("Palpites salvos com sucesso!")

    dados = buscar_jogos(segredos.chave_api_futebol())
    jogos = dados["jogos"]
    palpites_salvos = database.obter_palpites(usuario["id"])
    aberto = utils.palpites_abertos()
    prazo = utils.prazo_palpites()

    if aberto:
        st.success(
            f"Prazo para enviar/editar os palpites: "
            f"{utils.fmt_data_longa(prazo)} (faltam {utils.tempo_restante(prazo)})"
        )
    else:
        st.warning(
            f"Os palpites foram encerrados em {utils.fmt_data_longa(prazo)}. "
            "Agora voce pode apenas visualizar o que enviou."
        )

    st.caption(
        "Pontuacao: **3 pontos** pelo placar exato e **1 ponto** por acertar "
        "o resultado (vitoria, empate ou derrota). Vale a fase de grupos."
    )
    st.caption(
        f"Voce ja registrou palpite em **{len(palpites_salvos)} de "
        f"{len(jogos)}** jogos."
    )

    # agrupa os jogos por grupo
    por_grupo = {}
    for j in jogos:
        por_grupo.setdefault(j["grupo"], []).append(j)
    letras = sorted(por_grupo)

    with st.form("form_palpites"):
        abas = st.tabs([f"Grupo {l}" for l in letras])
        for aba, letra in zip(abas, letras):
            with aba:
                partidas = sorted(
                    por_grupo[letra],
                    key=lambda j: (j["rodada"], j["data_utc"]),
                )
                for j in partidas:
                    _linha_jogo(j, palpites_salvos, aberto)
                    st.divider()
        enviado = st.form_submit_button(
            "Salvar meus palpites", type="primary", disabled=not aberto,
            use_container_width=True,
        )

    if enviado and aberto:
        novos = dict(palpites_salvos)
        for j in jogos:
            mk = j["match_key"]
            kc, kf = f"casa_{mk}", f"fora_{mk}"
            if kc in st.session_state and kf in st.session_state:
                gc = int(st.session_state[kc])
                gf = int(st.session_state[kf])
                c1, _ = codigos_ordenados(mk)
                novos[mk] = [gc, gf] if j["casa"] == c1 else [gf, gc]
        database.salvar_palpites(usuario["id"], novos)
        st.session_state["_palpites_ok"] = True
        st.rerun()
