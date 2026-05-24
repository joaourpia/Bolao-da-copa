"""
Acesso seguro aos segredos do Streamlit (secrets.toml).

Quando o arquivo de segredos nao existe (rodando local, sem configurar),
o Streamlit lanca erro ao acessar st.secrets. Estas funcoes evitam isso e
permitem que o app funcione em modo de teste mesmo sem nenhum segredo.
"""

import streamlit as st


def tem_secao(nome):
    """True se a secao existe no secrets.toml."""
    try:
        return nome in st.secrets
    except Exception:  # noqa: BLE001
        return False


def secao(nome):
    """Devolve a secao como dicionario (vazio se nao existir)."""
    try:
        if nome in st.secrets:
            return dict(st.secrets[nome])
    except Exception:  # noqa: BLE001
        pass
    return {}


def valor(nome_secao, chave, padrao=None):
    """Le um valor especifico de uma secao."""
    return secao(nome_secao).get(chave, padrao)


def chave_api_futebol():
    """Chave da API football-data.org (ou None)."""
    chave = valor("api", "football_data_key", None)
    if chave and str(chave).strip() and "COLE_AQUI" not in str(chave):
        return str(chave).strip()
    return None


def admin_configurado():
    """Dados do organizador definidos nas secrets."""
    return secao("admin")
