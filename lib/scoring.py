"""
Pontuacao e ranking do Bolao da Copa 2026.

Regras (apenas a fase de grupos conta):
  - Acertou o PLACAR exato ............ 3 pontos
  - Acertou apenas o RESULTADO ........ 1 ponto
  - Errou ............................ 0 ponto

Palpites e resultados sao sempre representados como a tupla
(gols_c1, gols_c2), onde c1 e c2 sao os dois codigos da partida em
ordem alfabetica (a mesma ordem usada no match_key). Isso garante que
a comparacao seja sempre consistente.
"""

from lib import config
from lib.football_api import resultado_real


def _sinal(a, b):
    """1 se a>b, -1 se a<b, 0 se empate."""
    return (a > b) - (a < b)


def pontos_palpite(palpite, real):
    """
    Retorna (pontos, tipo).
    tipo: 'placar', 'resultado', 'erro' ou None (sem palpite/sem resultado).
    """
    if palpite is None or real is None:
        return 0, None
    try:
        pc1, pc2 = int(palpite[0]), int(palpite[1])
        rc1, rc2 = int(real[0]), int(real[1])
    except (TypeError, ValueError, IndexError):
        return 0, None
    if pc1 == rc1 and pc2 == rc2:
        return config.PONTOS_PLACAR_EXATO, "placar"
    if _sinal(pc1, pc2) == _sinal(rc1, rc2):
        return config.PONTOS_RESULTADO, "resultado"
    return 0, "erro"


def pontuar_participante(palpites, jogos):
    """
    Soma a pontuacao de um participante.
    palpites: {match_key: [gols_c1, gols_c2]}
    jogos: lista de jogos (cada um com resultado real, se finalizado)
    """
    total = placares = resultados = pontuados = 0
    detalhe = {}
    for jogo in jogos:
        real = resultado_real(jogo)
        if real is None:
            continue
        mk = jogo["match_key"]
        pts, tipo = pontos_palpite(palpites.get(mk), real)
        detalhe[mk] = (pts, tipo)
        if tipo is None:
            continue
        pontuados += 1
        total += pts
        if tipo == "placar":
            placares += 1
        elif tipo == "resultado":
            resultados += 1
    return {
        "pontos": total,
        "placares": placares,
        "resultados": resultados,
        "jogos_pontuados": pontuados,
        "detalhe": detalhe,
    }


def calcular_ranking(participantes, todos_palpites, jogos):
    """
    Monta o ranking (lider primeiro).
    Desempate: mais placares cravados, depois mais resultados, depois nome.
    """
    linhas = []
    for p in participantes:
        resumo = pontuar_participante(todos_palpites.get(str(p["id"]), {}), jogos)
        linhas.append({
            "id": p["id"],
            "nome": p["nome"],
            "pontos": resumo["pontos"],
            "placares": resumo["placares"],
            "resultados": resumo["resultados"],
            "jogos_pontuados": resumo["jogos_pontuados"],
        })

    linhas.sort(key=lambda x: (
        -x["pontos"], -x["placares"], -x["resultados"], x["nome"].lower()
    ))

    # numero da posicao, tratando empates
    posicao = 0
    chave_anterior = None
    for i, linha in enumerate(linhas):
        chave = (linha["pontos"], linha["placares"], linha["resultados"])
        if chave != chave_anterior:
            posicao = i + 1
            chave_anterior = chave
        linha["posicao"] = posicao
    return linhas


def lider(ranking):
    """Nome do lider atual (ou None)."""
    if ranking and ranking[0]["jogos_pontuados"] >= 0:
        if ranking[0]["pontos"] > 0:
            return ranking[0]["nome"]
    return None
