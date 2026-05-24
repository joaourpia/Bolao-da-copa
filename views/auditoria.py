"""Tela de auditoria: ver os palpites de qualquer participante."""

import streamlit as st

from lib import database, scoring, segredos, ui, utils
from lib.football_api import (buscar_jogos, codigos_ordenados,
                              resultado_real)


def _linha(jogo, palpites):
    mk = jogo["match_key"]
    salvo = palpites.get(mk)
    cols = st.columns([3, 1.6, 3, 1.6])
    cols[0].markdown(ui.time_inline(jogo["casa"]), unsafe_allow_html=True)
    cols[2].markdown(ui.time_inline(jogo["fora"]), unsafe_allow_html=True)

    if salvo:
        c1, _ = codigos_ordenados(mk)
        if jogo["casa"] == c1:
            pc, pf = salvo[0], salvo[1]
        else:
            pc, pf = salvo[1], salvo[0]
        cols[1].markdown(
            f"<div class='bc-placar' style='font-size:1.15rem;'>{pc} x {pf}"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        cols[1].markdown(
            "<div class='bc-vs'>sem palpite</div>", unsafe_allow_html=True
        )

    real = resultado_real(jogo)
    if real is not None:
        pts, _ = scoring.pontos_palpite(salvo, real)
        if pts > 0:
            cols[3].markdown(
                ui.badge(f"+{pts} pts", ui.COR_VERDE, "#0B1437"),
                unsafe_allow_html=True,
            )
        else:
            cols[3].markdown(
                ui.badge("0 pts", "#2c3c74", "#cdd8ff"),
                unsafe_allow_html=True,
            )


def render():
    usuario = st.session_state["usuario_logado"]
    st.markdown("## Auditoria dos palpites")
    st.caption(
        "Transparencia total: confira os palpites enviados por qualquer "
        "participante. Como o bolao envolve dinheiro, todos podem auditar."
    )

    participantes = database.listar_participantes()
    if not participantes:
        st.info("Nenhum participante cadastrado ainda.")
        return

    aberto = utils.palpites_abertos()
    if aberto and usuario["papel"] != "admin":
        st.warning(
            "Para evitar copia, os palpites dos outros participantes ficam "
            "visiveis somente apos o encerramento do prazo. Os seus voce "
            "confere na aba **Meus palpites**."
        )
        return

    nomes = [p["nome"] for p in participantes]
    escolhido = st.selectbox("Escolha um participante", nomes)
    participante = next(p for p in participantes if p["nome"] == escolhido)
    palpites = database.obter_palpites(participante["id"])

    dados = buscar_jogos(segredos.chave_api_futebol())
    jogos = dados["jogos"]
    resumo = scoring.pontuar_participante(palpites, jogos)

    ui.linha_cartoes([
        ui.cartao_metrica("Pontos", resumo["pontos"], destaque=True),
        ui.cartao_metrica("Placares cravados", resumo["placares"]),
        ui.cartao_metrica("Resultados certos", resumo["resultados"]),
        ui.cartao_metrica("Palpites enviados",
                          f"{len(palpites)}/{len(jogos)}"),
    ])
    st.write("")

    por_grupo = {}
    for j in jogos:
        por_grupo.setdefault(j["grupo"], []).append(j)
    letras = sorted(por_grupo)

    abas = st.tabs([f"Grupo {l}" for l in letras])
    for aba, letra in zip(abas, letras):
        with aba:
            partidas = sorted(
                por_grupo[letra], key=lambda j: (j["rodada"], j["data_utc"])
            )
            for j in partidas:
                _linha(j, palpites)
                st.divider()
