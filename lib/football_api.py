"""
Integracao com a API de futebol (football-data.org) e geracao da
lista oficial de jogos da fase de grupos da Copa 2026.

Estrategia:
  1. Sempre montamos a lista "canonica" dos 72 jogos da fase de grupos
     a partir dos grupos sorteados (modulo flags.py).
  2. Se houver chave de API, buscamos os dados ao vivo (datas, status e
     placares) e sobrepomos nos jogos canonicos.
  3. Se a API falhar ou nao houver chave, o app continua funcionando:
     os palpites podem ser preenchidos normalmente, apenas os resultados
     reais nao serao atualizados automaticamente.

Cada jogo tem uma CHAVE ESTAVEL (match_key) baseada no grupo + os dois
codigos de selecao em ordem alfabetica. Assim os palpites continuam
validos mesmo que a fonte dos dados mude (API <-> reserva).
"""

from datetime import datetime, timedelta, timezone

import requests
import streamlit as st

from lib import config
from lib.flags import GRUPOS, code_por_nome

# Sequencia de confrontos de um grupo de 4 selecoes (indices 0-3).
# Cobre os 6 jogos do returno unico, 2 por rodada.
_CONFRONTOS = {
    1: [(0, 1), (2, 3)],
    2: [(0, 2), (1, 3)],
    3: [(0, 3), (1, 2)],
}

# Datas-base aproximadas de cada rodada (usadas apenas no modo reserva).
_DATAS_BASE = {
    1: datetime(2026, 6, 11, 18, 0, tzinfo=timezone.utc),
    2: datetime(2026, 6, 18, 18, 0, tzinfo=timezone.utc),
    3: datetime(2026, 6, 24, 18, 0, tzinfo=timezone.utc),
}

STATUS_FINALIZADO = {"FINISHED", "AWARDED"}


def chave_jogo(grupo, time_a, time_b):
    """Chave estavel de um jogo: grupo + 2 codigos em ordem alfabetica."""
    c1, c2 = sorted([time_a, time_b])
    return f"{grupo}-{c1}-{c2}"


def codigos_ordenados(match_key):
    """Devolve (c1, c2) - os dois codigos do jogo em ordem alfabetica."""
    partes = match_key.split("-")
    return partes[1], partes[2]


def _jogos_canonicos():
    """Monta os 72 jogos da fase de grupos a partir do sorteio."""
    jogos = {}
    for idx, (letra, times) in enumerate(GRUPOS.items()):
        for rodada, pares in _CONFRONTOS.items():
            base = _DATAS_BASE[rodada] + timedelta(days=idx // 2)
            for pos, (i, j) in enumerate(pares):
                casa, fora = times[i], times[j]
                mk = chave_jogo(letra, casa, fora)
                jogos[mk] = {
                    "match_key": mk,
                    "grupo": letra,
                    "rodada": rodada,
                    "casa": casa,
                    "fora": fora,
                    "data_utc": base + timedelta(hours=pos * 3),
                    "status": "SCHEDULED",
                    "gols_casa": None,
                    "gols_fora": None,
                    "fonte": "reserva",
                }
    return jogos


def _buscar_da_api(api_key):
    """Busca os jogos da fase de grupos na football-data.org."""
    url = f"{config.FD_BASE_URL}/competitions/{config.FD_COMPETICAO}/matches"
    resp = requests.get(
        url,
        headers={"X-Auth-Token": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    dados = resp.json()
    return dados.get("matches", [])


def _parse_data(texto):
    """Converte a data ISO da API para datetime com fuso UTC."""
    if not texto:
        return None
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None


@st.cache_data(ttl=config.CACHE_TTL_JOGOS, show_spinner=False)
def buscar_jogos(api_key):
    """
    Devolve a lista completa de jogos da fase de grupos, ordenada por data.
    Resultado fica em cache por alguns segundos para nao estourar o limite
    de requisicoes da API gratuita.
    """
    jogos = _jogos_canonicos()
    fonte_global = "reserva"

    if api_key:
        try:
            partidas = _buscar_da_api(api_key)
            aplicados = 0
            for m in partidas:
                if m.get("stage") != "GROUP_STAGE":
                    continue
                grupo_raw = (m.get("group") or "").replace("GROUP_", "").strip()
                home = m.get("homeTeam", {}) or {}
                away = m.get("awayTeam", {}) or {}
                casa = code_por_nome(home.get("name"), home.get("tla"))
                fora = code_por_nome(away.get("name"), away.get("tla"))
                if not casa or not fora or not grupo_raw:
                    continue
                mk = chave_jogo(grupo_raw, casa, fora)
                if mk not in jogos:
                    continue
                placar = (m.get("score", {}) or {}).get("fullTime", {}) or {}
                jogo = jogos[mk]
                jogo["casa"] = casa
                jogo["fora"] = fora
                jogo["data_utc"] = _parse_data(m.get("utcDate")) or jogo["data_utc"]
                jogo["status"] = m.get("status", jogo["status"])
                jogo["rodada"] = m.get("matchday") or jogo["rodada"]
                jogo["gols_casa"] = placar.get("home")
                jogo["gols_fora"] = placar.get("away")
                jogo["fonte"] = "api"
                aplicados += 1
            if aplicados > 0:
                fonte_global = "api"
        except Exception as erro:  # noqa: BLE001 - degrada para o modo reserva
            st.session_state["_erro_api"] = str(erro)

    lista = sorted(
        jogos.values(),
        key=lambda j: (j["data_utc"], j["grupo"], j["rodada"]),
    )
    return {"jogos": lista, "fonte": fonte_global}


def resultado_real(jogo):
    """
    Resultado real de um jogo finalizado, no formato (gols_c1, gols_c2),
    alinhado a ordem alfabetica dos codigos (mesma ordem do match_key).
    Devolve None se o jogo ainda nao terminou.
    """
    if jogo["status"] not in STATUS_FINALIZADO:
        return None
    if jogo["gols_casa"] is None or jogo["gols_fora"] is None:
        return None
    c1, _ = codigos_ordenados(jogo["match_key"])
    if jogo["casa"] == c1:
        return (jogo["gols_casa"], jogo["gols_fora"])
    return (jogo["gols_fora"], jogo["gols_casa"])


def jogo_finalizado(jogo):
    """True se o jogo ja terminou (placar disponivel)."""
    return resultado_real(jogo) is not None
