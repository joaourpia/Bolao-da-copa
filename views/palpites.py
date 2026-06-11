"""Tela de envio dos palpites e download da copia para conferencia."""

import hashlib
import html as _html
import json
from datetime import datetime

import streamlit as st

from lib import config, database, flags, segredos, ui, utils
from lib.football_api import buscar_jogos, codigos_ordenados


# ---------------------------------------------------------------------
# Helpers de exibicao da tela
# ---------------------------------------------------------------------
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
        cols[1].markdown(
            f"<div class='bc-placar'>{tc}</div>", unsafe_allow_html=True
        )
        cols[3].markdown(
            f"<div class='bc-placar'>{tf}</div>", unsafe_allow_html=True
        )
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


# ---------------------------------------------------------------------
# Geracao do HTML para download (mesmo visual do app)
# ---------------------------------------------------------------------
def _hash_palpites(palpites):
    """Identificador curto e estavel do conjunto de palpites (assinatura)."""
    texto = json.dumps(palpites, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


_CSS_DOC = """
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
  background: radial-gradient(circle at 18% -10%, #21347d 0%, #0B1437 58%);
  color: #EEF2FF;
  margin: 0; padding: 28px 18px;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.container { max-width: 880px; margin: 0 auto; }
.header {
  background: linear-gradient(115deg,#FF2D78 0%,#A028D6 48%,#00B4D8 100%);
  border-radius: 18px; padding: 22px 28px; margin-bottom: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,.4);
}
.header h1 { margin: 0; font-size: 1.55rem; letter-spacing: .3px; color: #fff; }
.header p { margin: 6px 0 0; opacity: .92; font-size: .92rem; color: #fff; }
.info-card {
  background: #152253; border: 1px solid rgba(255,255,255,.08);
  border-radius: 14px; padding: 14px 18px; margin-bottom: 14px;
}
.info-card .label {
  color: #9fb0d9; font-size: .72rem;
  text-transform: uppercase; letter-spacing: .6px;
}
.info-card .value {
  font-weight: 800; font-size: 1.15rem; margin-top: 4px; color: #EEF2FF;
}
.grupo-title {
  color: #FF2D78; font-weight: 800; font-size: 1.05rem;
  margin: 18px 0 8px; letter-spacing: .4px;
}
.match {
  background: #152253; border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;
  display: grid;
  grid-template-columns: 3fr 1fr .4fr 1fr 3fr;
  align-items: center; column-gap: 12px; row-gap: 6px;
}
.team { display: flex; flex-direction: column; align-items: center; gap: 5px; }
.team img {
  width: 42px; height: auto; border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0,0,0,.35);
}
.team .name {
  font-size: .82rem; font-weight: 600; text-align: center; line-height: 1.15;
}
.score {
  font-size: 1.55rem; font-weight: 800; text-align: center; color: #EEF2FF;
}
.vs { text-align: center; color: #7e90bf; font-weight: 700; }
.match-info {
  text-align: center; color: #7e90bf; font-size: .72rem;
  grid-column: 1 / -1; padding-top: 2px;
}
.footer {
  margin-top: 24px; padding: 14px 18px;
  background: #152253; border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px; color: #9fb0d9; font-size: .82rem; line-height: 1.55;
}
.footer code {
  background: rgba(255,255,255,.08); padding: 2px 6px;
  border-radius: 4px; color: #EEF2FF;
  font-family: ui-monospace, Menlo, monospace;
}
@media print {
  body { padding: 10px; background: #0B1437; }
  .match { page-break-inside: avoid; }
  .grupo-title { page-break-after: avoid; }
  .header { page-break-after: avoid; }
}
"""


def _gerar_html_palpites(usuario, palpites_salvos, jogos):
    """Gera o documento HTML com os palpites do participante."""
    agora_txt = datetime.now(config.TZ_BR).strftime("%d/%m/%Y as %H:%M")
    hash_curto = _hash_palpites(palpites_salvos)

    por_grupo = {}
    for j in jogos:
        por_grupo.setdefault(j["grupo"], []).append(j)

    blocos = []
    for letra in sorted(por_grupo):
        partidas = sorted(
            por_grupo[letra], key=lambda j: (j["rodada"], j["data_utc"])
        )
        blocos.append(f'<div class="grupo-title">Grupo {letra}</div>')
        for j in partidas:
            mk = j["match_key"]
            salvo = palpites_salvos.get(mk)
            c1, _ = codigos_ordenados(mk)
            if salvo:
                if j["casa"] == c1:
                    gc_txt, gf_txt = str(salvo[0]), str(salvo[1])
                else:
                    gc_txt, gf_txt = str(salvo[1]), str(salvo[0])
            else:
                gc_txt, gf_txt = "-", "-"
            url_casa = flags.bandeira_url(j["casa"], 80)
            url_fora = flags.bandeira_url(j["fora"], 80)
            nome_casa = _html.escape(flags.nome_pt(j["casa"]))
            nome_fora = _html.escape(flags.nome_pt(j["fora"]))
            data_txt = _html.escape(utils.fmt_data_curta(j["data_utc"]))
            blocos.append(
                '<div class="match">'
                f'<div class="team"><img src="{url_casa}" alt=""/>'
                f'<div class="name">{nome_casa}</div></div>'
                f'<div class="score">{gc_txt}</div>'
                '<div class="vs">x</div>'
                f'<div class="score">{gf_txt}</div>'
                f'<div class="team"><img src="{url_fora}" alt=""/>'
                f'<div class="name">{nome_fora}</div></div>'
                f'<div class="match-info">Rodada {j["rodada"]} - '
                f'{data_txt}</div>'
                '</div>'
            )
    grupos_html = "\n".join(blocos)

    preenchidos = sum(1 for j in jogos if palpites_salvos.get(j["match_key"]))
    nome = _html.escape(usuario.get("nome", ""))
    login = _html.escape(usuario.get("usuario", ""))

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Bolao da Copa 2026 - Palpites de {nome}</title>
<style>{_CSS_DOC}</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>BOLAO DA COPA 2026 - Meus palpites</h1>
    <p>Participante: <strong>{nome}</strong> (login: {login})</p>
    <p>Gerado em: {agora_txt}</p>
  </div>
  <div class="info-card">
    <div class="label">Total de palpites preenchidos</div>
    <div class="value">{preenchidos} de {len(jogos)} jogos da fase de grupos</div>
  </div>
  {grupos_html}
  <div class="footer">
    Este e o documento dos palpites enviados por <strong>{nome}</strong>
    em <strong>{agora_txt}</strong>. Guarde para conferencia.<br>
    Identificador deste conjunto de palpites:
    <code>{hash_curto}</code>. Se voce baixar este documento de novo
    sem ter alterado nenhum palpite, esse codigo sera identico - serve
    para confirmar que os seus palpites no sistema continuam sendo
    exatamente esses.
  </div>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------
# Tela
# ---------------------------------------------------------------------
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

    # ---- download dos palpites (para conferencia) -------------------
    html_doc = _gerar_html_palpites(usuario, palpites_salvos, jogos)
    carimbo = datetime.now(config.TZ_BR).strftime("%Y%m%d-%H%M")
    nome_arquivo = (
        f"palpites-{usuario.get('usuario', 'meu')}-{carimbo}.html"
    )
    st.download_button(
        "Baixar meus palpites (para conferencia)",
        data=html_doc.encode("utf-8"),
        file_name=nome_arquivo,
        mime="text/html",
        use_container_width=True,
    )
    st.caption(
        "Abra o arquivo em qualquer navegador para conferir. "
        "Para uma versao em PDF, use 'Imprimir > Salvar como PDF' do navegador."
    )

    # ---- formulario de palpites -------------------------------------
    por_grupo = {}
    for j in jogos:
        por_grupo.setdefault(j["grupo"], []).append(j)
    letras = sorted(por_grupo)

    # PROTECAO contra "palpite que mudou sozinho":
    # se outro aparelho/aba salvou novos valores depois que esta sessao
    # carregou o formulario, ressincroniza os campos a partir do banco
    # para o proximo Salvar nao sobrescrever os novos valores com
    # os antigos da sessao. A "assinatura" do banco e comparada com
    # a ultima que esta sessao viu.
    hash_db = _hash_palpites(palpites_salvos)
    if st.session_state.get("_hash_palpites_db") != hash_db:
        for j in jogos:
            mk = j["match_key"]
            gc_db, gf_db = _valores_salvos(j, palpites_salvos)
            st.session_state[f"casa_{mk}"] = int(gc_db) if gc_db is not None else 0
            st.session_state[f"fora_{mk}"] = int(gf_db) if gf_db is not None else 0
        st.session_state["_hash_palpites_db"] = hash_db

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
