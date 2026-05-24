"""Constantes e parametros globais do Bolao da Copa 2026."""

from zoneinfo import ZoneInfo

# ----------------------------------------------------------------------
# Identidade do app
# ----------------------------------------------------------------------
APP_TITULO = "Bolao da Copa 2026"
APP_SUBTITULO = "Copa do Mundo FIFA 2026 - Canada / Mexico / EUA"
APP_ICONE = "trofeu"  # usado apenas como referencia textual

# ----------------------------------------------------------------------
# Regras do bolao
# ----------------------------------------------------------------------
# Valor de entrada por participante (R$). O total arrecadado e
# calculado automaticamente: nº de participantes x VALOR_ENTRADA.
VALOR_ENTRADA = 20.0

# Pontuacao (apenas a fase de grupos conta para o bolao)
PONTOS_PLACAR_EXATO = 3   # acertou o placar exato
PONTOS_RESULTADO = 1      # acertou apenas o resultado (vitoria/empate/derrota)

# ----------------------------------------------------------------------
# Fusos horarios
# ----------------------------------------------------------------------
TZ_BR = ZoneInfo("America/Sao_Paulo")
TZ_UTC = ZoneInfo("UTC")

# ----------------------------------------------------------------------
# API de futebol - football-data.org
# ----------------------------------------------------------------------
FD_BASE_URL = "https://api.football-data.org/v4"
FD_COMPETICAO = "WC"          # codigo da Copa do Mundo
FD_TEMPORADA = "2026"         # edicao
CACHE_TTL_JOGOS = 90          # segundos que os jogos/resultados ficam em cache

# ----------------------------------------------------------------------
# Prazo padrao para envio dos palpites
# (usado quando o organizador ainda nao configurou um prazo no painel).
# Horario de Brasilia. Abertura da Copa de 2026: 11/06/2026.
# ----------------------------------------------------------------------
PRAZO_PADRAO = "2026-06-11 14:00"

# Chave usada na aba "config" da planilha
CHAVE_PRAZO = "prazo_palpites"

# ----------------------------------------------------------------------
# Banco de dados local (modo de teste, sem Google Sheets)
# ----------------------------------------------------------------------
ARQUIVO_DB_LOCAL = "data/local_db.json"
