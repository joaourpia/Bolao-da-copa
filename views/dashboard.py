"""Tela inicial: painel interativo do bolao."""

import streamlit as st

from lib import config, database, scoring, segredos, ui, utils
from lib.football_api import buscar_jogos, jogo_finalizado


def render():
    st.markdown("## Painel do bolao")

    participantes = database.listar_participantes()
    dados = buscar_jogos(segredos.chave_api_futebol())
    jogos = dados["jogos"]
    todos_palpites = database.listar_todos_palpites()
    ranking = scoring.calcular_ranking(participantes, todos_palpites, jogos)

    n_part = len(participantes)
    arrecadado = n_part * config.VALOR_ENTRADA
    finalizados = sum(1 for j in jogos if jogo_finalizado(j))

    tem_lider = bool(ranking) and ranking[0]["pontos"] > 0
    nome_lider = ranking[0]["nome"] if tem_lider else "a definir"
    sub_lider = f"{ranking[0]['pontos']} pontos" if tem_lider else "sem pontos ainda"

    ui.linha_cartoes([
        ui.cartao_metrica("Participantes", n_part, sub="jogadores no bolao"),
        ui.cartao_metrica("Valor arrecadado", utils.moeda(arrecadado),
                          sub=f"{utils.moeda(config.VALOR_ENTRADA)} por pessoa"),
        ui.cartao_metrica("Lider do momento", nome_lider, sub=sub_lider,
                          destaque=True),
        ui.cartao_metrica("Jogos encerrados", f"{finalizados}/{len(jogos)}",
                          sub="fase de grupos"),
    ])

    # ---- prazo dos palpites ------------------------------------------
    prazo = utils.prazo_palpites()
    if utils.palpites_abertos():
        st.success(
            f"Palpites ABERTOS - prazo final: {utils.fmt_data_longa(prazo)} "
            f"(faltam {utils.tempo_restante(prazo)})"
        )
    else:
        st.warning(
            f"Palpites ENCERRADOS desde {utils.fmt_data_longa(prazo)}."
        )

    col_esq, col_dir = st.columns(2)

    # ---- proximos jogos ---------------------------------------------
    with col_esq:
        st.markdown("### Proximos jogos")
        proximos = [
            j for j in jogos
            if not jogo_finalizado(j)
            and j["status"] not in ("CANCELLED", "POSTPONED")
        ][:6]
        if not proximos:
            st.caption("Todos os jogos da fase de grupos ja foram disputados.")
        for j in proximos:
            c = st.columns([0.9, 3, 0.7, 3, 1.8])
            c[0].markdown(ui.badge(f"Gr {j['grupo']}", "#2c3c74"),
                          unsafe_allow_html=True)
            c[1].markdown(ui.time_inline(j["casa"]), unsafe_allow_html=True)
            c[2].markdown("<div class='bc-vs'>x</div>", unsafe_allow_html=True)
            c[3].markdown(ui.time_inline(j["fora"]), unsafe_allow_html=True)
            c[4].caption(utils.fmt_data_curta(j["data_utc"]))

    # ---- top 5 do ranking -------------------------------------------
    with col_dir:
        st.markdown("### Top 5 do ranking")
        if not tem_lider:
            st.caption(
                "O ranking aparece aqui assim que os primeiros jogos "
                "forem encerrados."
            )
        else:
            for r in ranking[:5]:
                c = st.columns([0.7, 4, 1.6])
                cor = ui.cor_posicao(r["posicao"])
                c[0].markdown(
                    f"<span class='bc-pos' style='background:{cor};'>"
                    f"{r['posicao']}</span>",
                    unsafe_allow_html=True,
                )
                c[1].write(r["nome"])
                c[2].write(f"**{r['pontos']}** pts")

    # ---- rodape ------------------------------------------------------
    if dados["fonte"] == "api":
        st.caption("Resultados sincronizados automaticamente com a API oficial.")
    else:
        st.caption(
            "Modo de referencia: os resultados ao vivo aparecerao quando a "
            "API de futebol estiver configurada."
        )
