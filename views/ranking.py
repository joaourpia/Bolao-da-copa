"""Tela de ranking ao vivo, com premiacao e criterios de desempate."""

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

    if not participantes:
        st.info(
            "Nenhum participante cadastrado ainda. "
            "Os jogadores criam a conta na tela inicial do app."
        )
        return

    pote = len(participantes) * config.VALOR_ENTRADA

    # ---- premiacao ---------------------------------------------------
    st.markdown("### Premiacao")
    ui.linha_cartoes([
        ui.cartao_metrica(
            "Total arrecadado", utils.moeda(pote),
            sub=f"{len(participantes)} x {utils.moeda(config.VALOR_ENTRADA)}",
        ),
        ui.cartao_metrica("1o lugar - 70%", utils.moeda(pote * 0.70),
                          destaque=True),
        ui.cartao_metrica("2o lugar - 20%", utils.moeda(pote * 0.20)),
        ui.cartao_metrica("3o lugar - 10%", utils.moeda(pote * 0.10)),
    ])
    st.caption(
        f"{finalizados} de {len(jogos)} jogos da fase de grupos contabilizados."
    )

    # ---- antes de qualquer jogo terminar -----------------------------
    if finalizados == 0:
        st.info(
            "A classificacao e os premios projetados aparecem aqui assim que "
            "os primeiros jogos da Copa forem encerrados."
        )
        st.markdown("### Participantes inscritos")
        for p in sorted(participantes, key=lambda x: x["nome"].lower()):
            st.write("- " + p["nome"])
        return

    # ---- classificacao ----------------------------------------------
    st.markdown("### Classificacao")
    pesos = [0.8, 3.4, 1.9, 1.1, 1.2]
    cab = st.columns(pesos)
    for col, txt in zip(cab, ["#", "Participante", "Premio projetado",
                              "Pontos", "Cravadas"]):
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
        nome = r["nome"] + ("  (voce)" if sou_eu else "")
        if r["empatado"]:
            nome += "  - empate"
        if r["posicao"] == 1 or sou_eu:
            linha[1].markdown(f"**{nome}**")
        else:
            linha[1].write(nome)
        if r["premio"] > 0:
            linha[2].markdown(f"**{utils.moeda(r['premio'])}**")
        else:
            linha[2].write("-")
        linha[3].markdown(f"**{r['pontos']}**")
        linha[4].write(str(r["placares"]))

    if any(r["empatado"] and r["premiado"] for r in ranking):
        st.caption(
            "Ha empate em posicao premiada: o premio das colocacoes "
            "envolvidas foi somado e dividido igualmente entre os empatados."
        )

    # ---- criterios de desempate -------------------------------------
    with st.expander("Criterios de desempate e detalhamento"):
        st.markdown(
            "Havendo empate em pontos, decide nesta ordem: "
            "**1)** mais placares cravados em jogos do Brasil; "
            "**2)** mais pontos em jogos do Brasil; "
            "**3)** mais placares cravados no geral; "
            "**4)** maior pontuacao na ultima rodada (3a rodada). "
            "Se ainda assim continuar empatado, vale a regra 5: o premio "
            "das posicoes empatadas e somado e dividido igualmente."
        )
        pesos2 = [0.7, 3, 1.5, 1.3, 1.3, 1.5]
        cab2 = st.columns(pesos2)
        for col, txt in zip(cab2, ["#", "Participante", "Cravadas BRA",
                                   "Pts BRA", "Cravadas", "Pts 3a rod."]):
            col.markdown(f"**{txt}**")
        for r in ranking:
            l = st.columns(pesos2)
            l[0].write(str(r["posicao"]))
            l[1].write(r["nome"])
            l[2].write(str(r["placares_brasil"]))
            l[3].write(str(r["pontos_brasil"]))
            l[4].write(str(r["placares"]))
            l[5].write(str(r["pontos_ultima_rodada"]))
