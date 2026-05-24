"""Tela de ranking ao vivo."""

import streamlit as st

from lib import config, database, scoring, segredos, ui, utils
from lib.football_api import buscar_jogos, jogo_finalizado


def render():
    usuario = st.session_state["usuario_logado"]
    st.markdown("## Ranking ao vivo")

    participantes = database.listar_participantes()
    dados = buscar_jogos(segredos.chave_api_futebol())
    jogos = dados["jogos"]
    todos = database.listar_todos_palpites()
    ranking = scoring.calcular_ranking(participantes, todos, jogos)
    finalizados = sum(1 for j in jogos if jogo_finalizado(j))

    st.caption(
        f"{finalizados} de {len(jogos)} jogos da fase de grupos contabilizados. "
        "Desempate: mais placares cravados, depois mais acertos de resultado."
    )

    if not participantes:
        st.info(
            "Nenhum participante cadastrado ainda. "
            "Peca ao organizador para cadastrar o grupo."
        )
        return

    premio = len(participantes) * config.VALOR_ENTRADA
    st.markdown(
        ui.cartao_metrica(
            "Premio total em disputa", utils.moeda(premio),
            sub=f"{len(participantes)} participantes", destaque=True,
        ),
        unsafe_allow_html=True,
    )
    st.write("")

    pesos = [0.8, 4, 1.3, 1.5, 1.7, 1.4]
    cab = st.columns(pesos)
    for col, txt in zip(cab, ["#", "Participante", "Pontos", "Cravadas",
                              "Resultados", "Jogos"]):
        col.markdown(f"**{txt}**")
    st.divider()

    meu_id = str(usuario.get("id"))
    for r in ranking:
        linha = st.columns(pesos)
        cor = ui.cor_posicao(r["posicao"])
        linha[0].markdown(
            f"<span class='bc-pos' style='background:{cor};'>"
            f"{r['posicao']}</span>",
            unsafe_allow_html=True,
        )
        sou_eu = str(r["id"]) == meu_id
        sufixo = "  (voce)" if sou_eu else ""
        if r["posicao"] == 1 or sou_eu:
            linha[1].markdown(f"**{r['nome']}{sufixo}**")
        else:
            linha[1].write(f"{r['nome']}{sufixo}")
        linha[2].markdown(f"**{r['pontos']}**")
        linha[3].write(str(r["placares"]))
        linha[4].write(str(r["resultados"]))
        linha[5].write(str(r["jogos_pontuados"]))
