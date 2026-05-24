"""Tela de jogos e resultados da fase de grupos."""

import streamlit as st

from lib import database, scoring, segredos, ui, utils
from lib.football_api import (buscar_jogos, codigos_ordenados,
                              jogo_finalizado, resultado_real)

_ETIQUETA = {
    "placar": "placar exato",
    "resultado": "resultado certo",
    "erro": "sem pontos",
}


def _palpite_casa_fora(jogo, palpites):
    """Palpite do usuario para o jogo, na ordem casa/fora."""
    salvo = palpites.get(jogo["match_key"])
    if not salvo:
        return None
    c1, _ = codigos_ordenados(jogo["match_key"])
    if jogo["casa"] == c1:
        return salvo[0], salvo[1]
    return salvo[1], salvo[0]


def _card_jogo(jogo, palpites):
    cols = st.columns([3, 2, 3])
    cols[0].markdown(ui.time_bloco(jogo["casa"]), unsafe_allow_html=True)
    cols[2].markdown(ui.time_bloco(jogo["fora"]), unsafe_allow_html=True)

    tem_placar = jogo["gols_casa"] is not None and jogo["gols_fora"] is not None
    if tem_placar:
        placar = f"{jogo['gols_casa']} x {jogo['gols_fora']}"
    else:
        placar = "x"
    meio = (
        f"<div class='bc-placar'>{placar}</div>"
        f"<div style='text-align:center;margin-top:6px;'>"
        f"{ui.badge_status(jogo['status'])}</div>"
        f"<div style='text-align:center;color:#7e90bf;font-size:.74rem;"
        f"margin-top:5px;'>{utils.fmt_data_curta(jogo['data_utc'])}</div>"
    )
    cols[1].markdown(meio, unsafe_allow_html=True)

    if palpites is None:
        return
    palpite = _palpite_casa_fora(jogo, palpites)
    if palpite is None:
        st.caption("Voce nao registrou palpite neste jogo.")
        return
    texto = f"Seu palpite: {palpite[0]} x {palpite[1]}"
    real = resultado_real(jogo)
    if real is not None:
        pts, tipo = scoring.pontos_palpite(
            palpites.get(jogo["match_key"]), real
        )
        texto += f"  -  +{pts} pts ({_ETIQUETA.get(tipo, '')})"
    st.caption(texto)


def render():
    usuario = st.session_state["usuario_logado"]
    st.markdown("## Jogos e resultados")

    dados = buscar_jogos(segredos.chave_api_futebol())
    jogos = dados["jogos"]

    if dados["fonte"] == "api":
        st.caption(
            "Resultados atualizados automaticamente pela API oficial "
            "(football-data.org)."
        )
    else:
        st.warning(
            "Os resultados ao vivo ainda nao estao disponiveis (API nao "
            "configurada ou indisponivel). Os confrontos abaixo seguem o "
            "sorteio oficial da Copa 2026."
        )

    palpites = None
    if usuario["papel"] == "participante":
        palpites = database.obter_palpites(usuario["id"])

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
            rodada_atual = None
            for j in partidas:
                if j["rodada"] != rodada_atual:
                    rodada_atual = j["rodada"]
                    st.markdown(
                        f"<div class='bc-grupo'>Rodada {rodada_atual}</div>",
                        unsafe_allow_html=True,
                    )
                _card_jogo(j, palpites)
                st.divider()
