"""
Bolao da Copa 2026
==================
Aplicativo Streamlit para o bolao da Copa do Mundo entre amigos.

Regras: 3 pontos por acertar o placar exato, 1 ponto por acertar o
resultado (vitoria/empate/derrota). Vale a fase de grupos.

Cada pessoa cria a propria conta (usuario e senha) pela tela inicial.
O organizador entra com o login definido no secrets.toml.
"""

import streamlit as st

from lib import auth, config, database, segredos, ui
from views import admin, auditoria, dashboard, jogos, palpites, ranking

st.set_page_config(
    page_title=config.APP_TITULO,
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.aplicar_estilo()


# ---------------------------------------------------------------------
# Formulario de login
# ---------------------------------------------------------------------
def _form_login():
    st.caption("Ja tem conta? Entre com o seu usuario e senha.")
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


# ---------------------------------------------------------------------
# Formulario de cadastro (cada pessoa cria a propria conta)
# ---------------------------------------------------------------------
def _validar_cadastro(nome, usuario, senha, senha2):
    nome = (nome or "").strip()
    usuario = (usuario or "").strip()
    if not nome:
        return "Informe o seu nome."
    if not usuario:
        return "Escolha um usuario (login)."
    if " " in usuario:
        return "O usuario nao pode conter espacos."
    if len(senha or "") < 4:
        return "A senha deve ter ao menos 4 caracteres."
    if senha != senha2:
        return "As duas senhas digitadas nao sao iguais."
    admin_cfg = segredos.admin_configurado()
    if usuario.lower() == str(admin_cfg.get("usuario", "")).strip().lower():
        return "Esse usuario nao esta disponivel. Escolha outro."
    if database.obter_participante_por_usuario(usuario):
        return "Ja existe um participante com esse usuario. Escolha outro."
    return None


def _form_cadastro():
    st.caption(
        "Primeira vez? Crie o seu acesso. Guarde bem o usuario e a senha - "
        "e com eles que voce volta depois para editar os palpites."
    )
    with st.form("cadastro"):
        nome = st.text_input("Seu nome (como aparece no ranking)")
        usuario = st.text_input("Escolha um usuario (login, sem espacos)")
        senha = st.text_input("Crie uma senha", type="password")
        senha2 = st.text_input("Repita a senha", type="password")
        criar = st.form_submit_button(
            "Criar conta e entrar", type="primary", use_container_width=True
        )
    if criar:
        erro = _validar_cadastro(nome, usuario, senha, senha2)
        if erro:
            st.error(erro)
        else:
            senha_hash, salt = auth.gerar_hash(senha)
            novo_id = database.adicionar_participante(
                nome.strip(), usuario.strip(), senha_hash, salt
            )
            auth.fazer_login({
                "id": novo_id,
                "nome": nome.strip(),
                "usuario": usuario.strip(),
                "papel": "participante",
            })
            st.rerun()


# ---------------------------------------------------------------------
# Tela inicial (login + cadastro)
# ---------------------------------------------------------------------
def tela_entrada():
    ui.cabecalho(config.APP_TITULO, config.APP_SUBTITULO)
    _, meio, _ = st.columns([1, 1.6, 1])
    with meio:
        aba_entrar, aba_criar = st.tabs(["Entrar", "Criar minha conta"])
        with aba_entrar:
            _form_login()
        with aba_criar:
            _form_cadastro()


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
# Roteamento: mostra a tela de entrada ou o aplicativo
# ---------------------------------------------------------------------
def main():
    usuario_logado = auth.usuario_atual()
    if usuario_logado:
        aplicativo(usuario_logado)
    else:
        tela_entrada()


main()
