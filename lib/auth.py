"""
Autenticacao do Bolao da Copa 2026.

- O ADMIN (organizador) e definido no secrets.toml.
- Os PARTICIPANTES sao cadastrados pelo admin e ficam na planilha,
  com a senha guardada apenas como hash (PBKDF2-SHA256 + salt).
"""

import hashlib
import hmac
import os

import streamlit as st

from lib import database, segredos

_ITERACOES = 200_000


def _hash(senha, salt_hex):
    return hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), bytes.fromhex(salt_hex), _ITERACOES
    ).hex()


def gerar_hash(senha):
    """Gera (hash, salt) para guardar uma nova senha."""
    salt = os.urandom(16).hex()
    return _hash(senha, salt), salt


def verificar(senha, salt_hex, hash_esperado):
    """Confere se a senha bate com o hash guardado."""
    if not senha or not salt_hex or not hash_esperado:
        return False
    try:
        return hmac.compare_digest(_hash(senha, salt_hex), hash_esperado)
    except ValueError:
        return False


def autenticar(usuario, senha):
    """
    Tenta logar. Retorna o dicionario do usuario ou None.
    Papel: 'admin' (organizador) ou 'participante' (jogador).
    """
    usuario = (usuario or "").strip()
    senha = senha or ""
    if not usuario or not senha:
        return None

    # 1) Organizador / admin (secrets.toml)
    admin = segredos.admin_configurado()
    adm_user = str(admin.get("usuario", "")).strip()
    if adm_user and usuario.lower() == adm_user.lower():
        if hmac.compare_digest(senha, str(admin.get("senha", ""))):
            return {
                "id": "admin",
                "nome": admin.get("nome", "Organizador"),
                "usuario": adm_user,
                "papel": "admin",
            }
        return None

    # 2) Participante (planilha)
    p = database.obter_participante_por_usuario(usuario)
    if p and verificar(senha, p["salt"], p["senha_hash"]):
        return {
            "id": p["id"],
            "nome": p["nome"],
            "usuario": p["usuario"],
            "papel": "participante",
        }
    return None


def usuario_atual():
    """Usuario logado na sessao (ou None)."""
    return st.session_state.get("usuario_logado")


def fazer_login(usuario_dict):
    st.session_state["usuario_logado"] = usuario_dict


def logout():
    st.session_state.pop("usuario_logado", None)
