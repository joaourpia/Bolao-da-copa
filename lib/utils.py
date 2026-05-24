"""Funcoes utilitarias: datas, formatacao e prazo dos palpites."""

from datetime import datetime

from lib import config, database


def agora():
    """Datetime atual no fuso de Brasilia."""
    return datetime.now(config.TZ_BR)


def parse_prazo(texto):
    """Converte um texto de data/hora para datetime (fuso de Brasilia)."""
    if not texto:
        return None
    texto = str(texto).strip()
    formatos = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
    )
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt).replace(tzinfo=config.TZ_BR)
        except ValueError:
            continue
    return None


def prazo_palpites():
    """Datetime do prazo final para envio dos palpites."""
    bruto = database.obter_config(config.CHAVE_PRAZO, config.PRAZO_PADRAO)
    return parse_prazo(bruto) or parse_prazo(config.PRAZO_PADRAO)


def palpites_abertos():
    """True enquanto o prazo geral nao terminou."""
    prazo = prazo_palpites()
    if prazo is None:
        return True
    return agora() < prazo


def jogo_bloqueado(jogo):
    """
    Um jogo fica bloqueado para palpites se o prazo geral passou
    OU se a partida ja comecou.
    """
    if not palpites_abertos():
        return True
    data = jogo.get("data_utc")
    if data is not None:
        try:
            return agora() >= data
        except TypeError:
            return False
    return False


def fmt_data_curta(dt):
    """Formata um datetime para 'dd/mm HH:MM' (horario de Brasilia)."""
    if dt is None:
        return "a definir"
    try:
        return dt.astimezone(config.TZ_BR).strftime("%d/%m %H:%M")
    except (ValueError, AttributeError):
        return "a definir"


def fmt_data_longa(dt):
    """Formata um datetime para 'dd/mm/aaaa as HH:MM' (horario de Brasilia)."""
    if dt is None:
        return "-"
    try:
        return dt.astimezone(config.TZ_BR).strftime("%d/%m/%Y as %H:%M")
    except (ValueError, AttributeError):
        return "-"


def moeda(valor):
    """Formata um numero como 'R$ 1.200'."""
    try:
        return "R$ " + f"{float(valor):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "R$ 0"


def tempo_restante(dt_alvo):
    """Texto amigavel do tempo que falta ate dt_alvo."""
    if dt_alvo is None:
        return ""
    segundos = int((dt_alvo - agora()).total_seconds())
    if segundos <= 0:
        return "encerrado"
    dias = segundos // 86400
    horas = (segundos % 86400) // 3600
    minutos = (segundos % 3600) // 60
    if dias > 0:
        return f"{dias}d {horas}h"
    if horas > 0:
        return f"{horas}h {minutos}min"
    return f"{minutos}min"
