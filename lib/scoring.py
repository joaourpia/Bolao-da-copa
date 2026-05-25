"""
Pontuacao, ranking e premiacao do Bolao da Copa 2026.

Regras de pontuacao (apenas a fase de grupos conta):
  - Acertou o PLACAR exato ............ 3 pontos
  - Acertou apenas o RESULTADO ........ 1 ponto
  - Errou ............................ 0 ponto

Ordem de desempate (quando ha empate em pontos totais):
  1) mais placares cravados em jogos do Brasil
  2) mais pontos em jogos do Brasil
  3) mais placares cravados no geral
  4) maior pontuacao na ultima rodada (rodada 3)
Se ainda assim houver empate, os empatados dividem igualmente o premio
das posicoes que ocupam (regra 5).

Premiacao: 1o lugar 70%, 2o lugar 20%, 3o lugar 10% do total arrecadado.
"""

from lib import config
from lib.football_api import resultado_real

# Codigo da selecao do Brasil (usado nos criterios de desempate)
_CODIGO_BRASIL = "BRA"
# Numero da ultima rodada da fase de grupos
_RODADA_FINAL = 3

# Fracao do premio por colocacao (1o, 2o, 3o lugares)
PREMIO_POR_COLOCACAO = {1: 0.70, 2: 0.20, 3: 0.10}


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
    Soma a pontuacao de um participante e calcula os criterios de desempate.
    palpites: {match_key: [gols_c1, gols_c2]}
    jogos: lista de jogos (cada um com resultado real, se finalizado)
    """
    total = placares = resultados = pontuados = 0
    placares_brasil = pontos_brasil = pontos_ultima_rodada = 0
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
        # criterios de desempate
        if _CODIGO_BRASIL in (jogo.get("casa"), jogo.get("fora")):
            pontos_brasil += pts
            if tipo == "placar":
                placares_brasil += 1
        if jogo.get("rodada") == _RODADA_FINAL:
            pontos_ultima_rodada += pts
    return {
        "pontos": total,
        "placares": placares,
        "resultados": resultados,
        "jogos_pontuados": pontuados,
        "placares_brasil": placares_brasil,
        "pontos_brasil": pontos_brasil,
        "pontos_ultima_rodada": pontos_ultima_rodada,
        "detalhe": detalhe,
    }


def _distribuir_premios(linhas, pote):
    """
    Define o campo 'premio' (R$) de cada linha do ranking.
    Quando varias pessoas ocupam a mesma posicao, elas somam o premio das
    colocacoes que ocupam e dividem igualmente (regra 5).
    """
    grupos = {}
    for linha in linhas:
        grupos.setdefault(linha["posicao"], []).append(linha)
    for posicao, membros in grupos.items():
        tamanho = len(membros)
        fracao = sum(
            PREMIO_POR_COLOCACAO.get(posicao + k, 0.0) for k in range(tamanho)
        )
        premio_cada = round((fracao * pote) / tamanho, 2) if tamanho else 0.0
        for m in membros:
            m["premio"] = premio_cada
            m["premiado"] = premio_cada > 0.0


def calcular_ranking(participantes, todos_palpites, jogos):
    """
    Monta o ranking completo (lider primeiro), ja com posicao, marcacao de
    empate e premio projetado de cada participante.
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
            "placares_brasil": resumo["placares_brasil"],
            "pontos_brasil": resumo["pontos_brasil"],
            "pontos_ultima_rodada": resumo["pontos_ultima_rodada"],
        })

    # ordena por pontos e, em empate, pelas 4 regras de desempate
    linhas.sort(key=lambda x: (
        -x["pontos"],
        -x["placares_brasil"],
        -x["pontos_brasil"],
        -x["placares"],
        -x["pontos_ultima_rodada"],
        x["nome"].lower(),
    ))

    # posicao: quem empata em TODOS os criterios fica na mesma posicao
    posicao = 0
    chave_anterior = None
    for i, linha in enumerate(linhas):
        chave = (
            linha["pontos"], linha["placares_brasil"], linha["pontos_brasil"],
            linha["placares"], linha["pontos_ultima_rodada"],
        )
        if chave != chave_anterior:
            posicao = i + 1
            chave_anterior = chave
        linha["posicao"] = posicao

    # marca quem esta empatado (mesma posicao que outra pessoa)
    contagem = {}
    for linha in linhas:
        contagem[linha["posicao"]] = contagem.get(linha["posicao"], 0) + 1
    for linha in linhas:
        linha["empatado"] = contagem[linha["posicao"]] > 1

    # premio projetado
    pote = len(participantes) * config.VALOR_ENTRADA
    _distribuir_premios(linhas, pote)
    return linhas


def lider(ranking):
    """Nome do lider atual (ou None, se ninguem pontuou)."""
    if ranking and ranking[0]["pontos"] > 0:
        return ranking[0]["nome"]
    return None
