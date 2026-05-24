"""
Selecoes da Copa do Mundo 2026, grupos, bandeiras e nomes em portugues.

Sorteio realizado em 05/12/2025 (Washington, D.C.).
Cada selecao tem um codigo de 3 letras (padrao FIFA) usado internamente.
As bandeiras vem do servico publico flagcdn.com (codigo ISO 3166-1).
"""

# ----------------------------------------------------------------------
# Os 12 grupos (A a L) - ordem do sorteio
# ----------------------------------------------------------------------
GRUPOS = {
    "A": ["MEX", "RSA", "KOR", "CZE"],
    "B": ["CAN", "BIH", "QAT", "SUI"],
    "C": ["BRA", "MAR", "HAI", "SCO"],
    "D": ["USA", "PAR", "AUS", "TUR"],
    "E": ["GER", "CUW", "CIV", "ECU"],
    "F": ["NED", "JPN", "SWE", "TUN"],
    "G": ["BEL", "EGY", "IRN", "NZL"],
    "H": ["ESP", "CPV", "KSA", "URU"],
    "I": ["FRA", "SEN", "IRQ", "NOR"],
    "J": ["ARG", "ALG", "AUT", "JOR"],
    "K": ["POR", "COD", "UZB", "COL"],
    "L": ["ENG", "CRO", "GHA", "PAN"],
}

# ----------------------------------------------------------------------
# Dados de cada selecao
#   nome    -> nome em portugues (exibicao)
#   nome_en -> nome em ingles (vem da API)
#   iso     -> codigo da bandeira no flagcdn.com
#   apelidos-> variacoes de nome usadas para casar com a API
# ----------------------------------------------------------------------
TIMES = {
    "MEX": {"nome": "Mexico", "nome_en": "Mexico", "iso": "mx",
            "apelidos": ["mexico"]},
    "RSA": {"nome": "Africa do Sul", "nome_en": "South Africa", "iso": "za",
            "apelidos": ["south africa"]},
    "KOR": {"nome": "Coreia do Sul", "nome_en": "South Korea", "iso": "kr",
            "apelidos": ["south korea", "korea republic", "republic of korea",
                         "korea, republic of"]},
    "CZE": {"nome": "Tchequia", "nome_en": "Czechia", "iso": "cz",
            "apelidos": ["czechia", "czech republic"]},

    "CAN": {"nome": "Canada", "nome_en": "Canada", "iso": "ca",
            "apelidos": ["canada"]},
    "BIH": {"nome": "Bosnia e Herzegovina", "nome_en": "Bosnia and Herzegovina",
            "iso": "ba", "apelidos": ["bosnia and herzegovina",
                                      "bosnia-herzegovina", "bosnia & herzegovina",
                                      "bosnia herzegovina"]},
    "QAT": {"nome": "Catar", "nome_en": "Qatar", "iso": "qa",
            "apelidos": ["qatar"]},
    "SUI": {"nome": "Suica", "nome_en": "Switzerland", "iso": "ch",
            "apelidos": ["switzerland"]},

    "BRA": {"nome": "Brasil", "nome_en": "Brazil", "iso": "br",
            "apelidos": ["brazil"]},
    "MAR": {"nome": "Marrocos", "nome_en": "Morocco", "iso": "ma",
            "apelidos": ["morocco"]},
    "HAI": {"nome": "Haiti", "nome_en": "Haiti", "iso": "ht",
            "apelidos": ["haiti"]},
    "SCO": {"nome": "Escocia", "nome_en": "Scotland", "iso": "gb-sct",
            "apelidos": ["scotland"]},

    "USA": {"nome": "Estados Unidos", "nome_en": "United States", "iso": "us",
            "apelidos": ["united states", "usa", "united states of america"]},
    "PAR": {"nome": "Paraguai", "nome_en": "Paraguay", "iso": "py",
            "apelidos": ["paraguay"]},
    "AUS": {"nome": "Australia", "nome_en": "Australia", "iso": "au",
            "apelidos": ["australia"]},
    "TUR": {"nome": "Turquia", "nome_en": "Turkiye", "iso": "tr",
            "apelidos": ["turkey", "turkiye", "turkiye"]},

    "GER": {"nome": "Alemanha", "nome_en": "Germany", "iso": "de",
            "apelidos": ["germany"]},
    "CUW": {"nome": "Curacao", "nome_en": "Curacao", "iso": "cw",
            "apelidos": ["curacao", "curacao"]},
    "CIV": {"nome": "Costa do Marfim", "nome_en": "Cote d'Ivoire", "iso": "ci",
            "apelidos": ["ivory coast", "cote d'ivoire", "cote d ivoire",
                         "cote divoire"]},
    "ECU": {"nome": "Equador", "nome_en": "Ecuador", "iso": "ec",
            "apelidos": ["ecuador"]},

    "NED": {"nome": "Holanda", "nome_en": "Netherlands", "iso": "nl",
            "apelidos": ["netherlands", "holland"]},
    "JPN": {"nome": "Japao", "nome_en": "Japan", "iso": "jp",
            "apelidos": ["japan"]},
    "SWE": {"nome": "Suecia", "nome_en": "Sweden", "iso": "se",
            "apelidos": ["sweden"]},
    "TUN": {"nome": "Tunisia", "nome_en": "Tunisia", "iso": "tn",
            "apelidos": ["tunisia"]},

    "BEL": {"nome": "Belgica", "nome_en": "Belgium", "iso": "be",
            "apelidos": ["belgium"]},
    "EGY": {"nome": "Egito", "nome_en": "Egypt", "iso": "eg",
            "apelidos": ["egypt"]},
    "IRN": {"nome": "Ira", "nome_en": "Iran", "iso": "ir",
            "apelidos": ["iran", "ir iran", "iran, islamic republic of"]},
    "NZL": {"nome": "Nova Zelandia", "nome_en": "New Zealand", "iso": "nz",
            "apelidos": ["new zealand"]},

    "ESP": {"nome": "Espanha", "nome_en": "Spain", "iso": "es",
            "apelidos": ["spain"]},
    "CPV": {"nome": "Cabo Verde", "nome_en": "Cape Verde", "iso": "cv",
            "apelidos": ["cape verde", "cabo verde"]},
    "KSA": {"nome": "Arabia Saudita", "nome_en": "Saudi Arabia", "iso": "sa",
            "apelidos": ["saudi arabia"]},
    "URU": {"nome": "Uruguai", "nome_en": "Uruguay", "iso": "uy",
            "apelidos": ["uruguay"]},

    "FRA": {"nome": "Franca", "nome_en": "France", "iso": "fr",
            "apelidos": ["france"]},
    "SEN": {"nome": "Senegal", "nome_en": "Senegal", "iso": "sn",
            "apelidos": ["senegal"]},
    "IRQ": {"nome": "Iraque", "nome_en": "Iraq", "iso": "iq",
            "apelidos": ["iraq"]},
    "NOR": {"nome": "Noruega", "nome_en": "Norway", "iso": "no",
            "apelidos": ["norway"]},

    "ARG": {"nome": "Argentina", "nome_en": "Argentina", "iso": "ar",
            "apelidos": ["argentina"]},
    "ALG": {"nome": "Argelia", "nome_en": "Algeria", "iso": "dz",
            "apelidos": ["algeria"]},
    "AUT": {"nome": "Austria", "nome_en": "Austria", "iso": "at",
            "apelidos": ["austria"]},
    "JOR": {"nome": "Jordania", "nome_en": "Jordan", "iso": "jo",
            "apelidos": ["jordan"]},

    "POR": {"nome": "Portugal", "nome_en": "Portugal", "iso": "pt",
            "apelidos": ["portugal"]},
    "COD": {"nome": "RD Congo", "nome_en": "DR Congo", "iso": "cd",
            "apelidos": ["dr congo", "congo dr", "congo democratic republic",
                         "democratic republic of the congo", "congo, dr"]},
    "UZB": {"nome": "Uzbequistao", "nome_en": "Uzbekistan", "iso": "uz",
            "apelidos": ["uzbekistan"]},
    "COL": {"nome": "Colombia", "nome_en": "Colombia", "iso": "co",
            "apelidos": ["colombia"]},

    "ENG": {"nome": "Inglaterra", "nome_en": "England", "iso": "gb-eng",
            "apelidos": ["england"]},
    "CRO": {"nome": "Croacia", "nome_en": "Croatia", "iso": "hr",
            "apelidos": ["croatia"]},
    "GHA": {"nome": "Gana", "nome_en": "Ghana", "iso": "gh",
            "apelidos": ["ghana"]},
    "PAN": {"nome": "Panama", "nome_en": "Panama", "iso": "pa",
            "apelidos": ["panama"]},
}

# Indice reverso: cada apelido/nome -> codigo
_INDICE_NOME = {}
for _code, _info in TIMES.items():
    _INDICE_NOME[_code.lower()] = _code
    _INDICE_NOME[_info["nome"].lower()] = _code
    _INDICE_NOME[_info["nome_en"].lower()] = _code
    for _a in _info["apelidos"]:
        _INDICE_NOME[_a.lower()] = _code


def grupo_do_time(code):
    """Retorna a letra do grupo de uma selecao."""
    for letra, times in GRUPOS.items():
        if code in times:
            return letra
    return "?"


def nome_pt(code):
    """Nome em portugues da selecao."""
    return TIMES.get(code, {}).get("nome", code)


def bandeira_url(code, largura=80):
    """URL da bandeira (PNG) no flagcdn.com."""
    iso = TIMES.get(code, {}).get("iso", "")
    if not iso:
        return ""
    return f"https://flagcdn.com/w{largura}/{iso}.png"


def code_por_nome(nome, tla=None):
    """
    Converte um nome vindo da API (em ingles) para o codigo interno.
    Tenta pelo nome; se falhar, tenta pela sigla de 3 letras (tla).
    """
    if nome:
        chave = nome.strip().lower()
        if chave in _INDICE_NOME:
            return _INDICE_NOME[chave]
    if tla:
        tla_up = tla.strip().upper()
        if tla_up in TIMES:
            return tla_up
    return None


# Lista de todas as selecoes em ordem de grupo
TODAS_SELECOES = [c for g in GRUPOS.values() for c in g]
