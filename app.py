"""
Bolao da Copa 2026
==================
Aplicativo Streamlit para o bolao da Copa do Mundo entre amigos.

Regras: 3 pontos por acertar o placar exato, 1 ponto por acertar o
resultado (vitoria/empate/derrota). Vale a fase de grupos.

Este arquivo cuida do login e da navegacao entre as telas.
As telas ficam na pasta  views/  e a logica na pasta  lib/.
"""

import streamlit as st

from lib import auth, config, ui
from views import admin, auditoria, dashboard, jogos, palpites, ranking

st.set_page_config(
    page_title=config.APP_TITULO,
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.aplicar_estilo()


# ---------------------------------------------------------------------
# Tela de login
# ---------------------------------------------------------------------
def tela_login():
    ui.cabecalho(config.APP_TITULO, config.APP_SUBTITULO)
    _, meio, _ = st.columns([1, 1.5, 1])
    with meio:
        st.markdown("### Entrar")
        with st.form("login"):
            usuario = st.text_input("Usuario")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button(
                "Entrar", type="primary", use_container_width=True
            )
        if entrar:
            dados = auth.autenticar(usuario, senha)
            if dados:
                auth.fazer_login(dados)
                st.rerun()
            else:
                st.error("Usuario ou senha incorretos.")
        st.caption(
            "Nao tem acesso? Peca o seu login ao organizador do bolao."
        )


# ---------------------------------------------------------------------
# Aplicativo (apos o login)
# ---------------------------------------------------------------------
def aplicativo(usuario):
    ui.cabecalho(config.APP_TITULO, f"Ola, {usuario['nome']}!")

    with st.sidebar:
        st.markdown(f"### {usuario['nome']}")
        papel = "Organizador" if usuario["papel"] == "admin" else "Participante"
        st.caption(papel)
        if st.button("Sair", use_container_width=True):
            auth.logout()
            st.rerun()
        st.divider()

    paginas = [
        st.Page(dashboard.render, title="Painel", icon=":material/dashboard:",
                url_path="painel", default=True),
    ]
    if usuario["papel"] == "participante":
        paginas.append(
            st.Page(palpites.render, title="Meus palpites",
                    icon=":material/edit_note:", url_path="meus-palpites")
        )
    paginas += [
        st.Page(jogos.render, title="Jogos e resultados",
                icon=":material/sports_soccer:", url_path="jogos"),
        st.Page(ranking.render, title="Ranking",
                icon=":material/leaderboard:", url_path="ranking"),
        st.Page(auditoria.render, title="Auditoria",
                icon=":material/visibility:", url_path="auditoria"),
    ]
    if usuario["papel"] == "admin":
        paginas.append(
            st.Page(admin.render, title="Admin", icon=":material/settings:",
                    url_path="admin")
        )

    st.navigation(paginas).run()


# ---------------------------------------------------------------------
# Roteamento: mostra o login ou o aplicativo
# ---------------------------------------------------------------------
def main():
    usuario_logado = auth.usuario_atual()
    if usuario_logado:
        aplicativo(usuario_logado)
    else:
        tela_login()


main()
