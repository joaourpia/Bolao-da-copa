"""
Componentes visuais e estilo (CSS) do Bolao da Copa 2026.

O visual e inspirado na identidade da Copa 2026: fundo azul profundo
com um banner em degrade vibrante (rosa / roxo / ciano).
"""

import streamlit as st

from lib import flags

# Paleta
COR_PRIMARIA = "#FF2D78"
COR_CIANO = "#00D4E0"
COR_OURO = "#FFC93C"
COR_VERDE = "#28E0A0"
COR_FUNDO_CARD = "#152253"

_CSS = """
<style>
/* ---- fundo geral ---- */
.stApp {
  background: radial-gradient(circle at 18% -10%, #21347d 0%, #0B1437 58%);
}
.block-container { padding-top: 1.6rem; max-width: 1150px; }

/* ---- banner de cabecalho ---- */
.bc-header {
  background: linear-gradient(115deg,#FF2D78 0%,#A028D6 48%,#00B4D8 100%);
  border-radius: 20px; padding: 24px 30px; margin-bottom: 14px;
  box-shadow: 0 12px 34px rgba(0,0,0,.40);
}
.bc-header h1 {
  color:#fff; font-size:1.95rem; margin:0; font-weight:800; letter-spacing:.4px;
}
.bc-header p { color:rgba(255,255,255,.88); margin:.3rem 0 0; font-size:.95rem; }

/* ---- cartoes de metrica ---- */
.bc-grid { display:flex; gap:14px; flex-wrap:wrap; margin:8px 0 6px; }
.bc-card {
  flex:1 1 180px; background:var(--cardbg,#152253);
  border:1px solid rgba(255,255,255,.09); border-radius:16px; padding:16px 18px;
}
.bc-card .rotulo {
  color:#9fb0d9; font-size:.74rem; text-transform:uppercase; letter-spacing:.7px;
}
.bc-card .valor { color:#fff; font-size:1.7rem; font-weight:800; margin-top:5px; }
.bc-card .sub { color:#8295c2; font-size:.78rem; margin-top:3px; }
.bc-card.destaque { border-color:#FFC93C; box-shadow:0 0 0 1px rgba(255,201,60,.35); }

/* ---- time / bandeira ---- */
.bc-time { display:flex; flex-direction:column; align-items:center; gap:6px; }
.bc-bandeira {
  width:52px; height:auto; border-radius:5px; box-shadow:0 2px 7px rgba(0,0,0,.45);
}
.bc-time-nome {
  color:#EEF2FF; font-size:.85rem; font-weight:600; text-align:center; line-height:1.15;
}
.bc-inline { display:flex; align-items:center; gap:8px; }
.bc-inline img { width:26px; border-radius:3px; }
.bc-inline span { color:#EEF2FF; font-size:.9rem; }

.bc-vs { color:#7e90bf; font-weight:800; text-align:center; font-size:.95rem; }
.bc-placar {
  text-align:center; font-size:1.6rem; font-weight:800; color:#fff; line-height:1.1;
}
.bc-placar .pend { font-size:.7rem; color:#28E0A0; font-weight:700; display:block; }

/* ---- badges ---- */
.bc-badge {
  display:inline-block; padding:3px 11px; border-radius:999px;
  font-size:.70rem; font-weight:700; letter-spacing:.4px;
}
.bc-grupo {
  color:#FF2D78; font-weight:800; font-size:1.05rem;
  margin:14px 0 2px; letter-spacing:.4px;
}

/* ---- linha de jogo (cartao) ---- */
.bc-jogo {
  background:#152253; border:1px solid rgba(255,255,255,.08);
  border-radius:14px; padding:12px 16px; margin-bottom:8px;
}

/* ---- posicao no ranking ---- */
.bc-pos {
  display:inline-flex; align-items:center; justify-content:center;
  width:30px; height:30px; border-radius:50%; font-weight:800;
  color:#0B1437; font-size:.9rem;
}

/* ---- ajustes finos do Streamlit ---- */
div[data-testid="stNumberInput"] input { text-align:center; font-weight:700; }
.stButton button { border-radius:10px; font-weight:700; }
h2, h3 { color:#EEF2FF; }
</style>
"""


def aplicar_estilo():
    """Injeta o CSS global. Chamar uma vez por pagina."""
    st.markdown(_CSS, unsafe_allow_html=True)


def cabecalho(titulo, subtitulo=""):
    """Renderiza o banner principal."""
    st.markdown(
        f"""<div class="bc-header">
              <h1>{titulo}</h1>
              {f'<p>{subtitulo}</p>' if subtitulo else ''}
            </div>""",
        unsafe_allow_html=True,
    )


def time_bloco(code, largura_bandeira=160):
    """HTML de uma selecao: bandeira em cima, nome embaixo."""
    url = flags.bandeira_url(code, largura_bandeira)
    nome = flags.nome_pt(code)
    img = f'<img src="{url}" class="bc-bandeira"/>' if url else ""
    return f'<div class="bc-time">{img}<div class="bc-time-nome">{nome}</div></div>'


def time_inline(code):
    """HTML compacto: bandeira pequena + nome na mesma linha."""
    url = flags.bandeira_url(code, 40)
    nome = flags.nome_pt(code)
    img = f'<img src="{url}"/>' if url else ""
    return f'<div class="bc-inline">{img}<span>{nome}</span></div>'


def cartao_metrica(rotulo, valor, sub="", destaque=False):
    """HTML de um cartao de metrica."""
    classe = "bc-card destaque" if destaque else "bc-card"
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return (
        f'<div class="{classe}"><div class="rotulo">{rotulo}</div>'
        f'<div class="valor">{valor}</div>{sub_html}</div>'
    )


def linha_cartoes(cartoes_html):
    """Agrupa varios cartoes em uma linha responsiva."""
    st.markdown(
        f'<div class="bc-grid">{"".join(cartoes_html)}</div>',
        unsafe_allow_html=True,
    )


def badge(texto, cor="#3a4a82", cor_texto="#fff"):
    """HTML de um badge/pill colorido."""
    return (
        f'<span class="bc-badge" style="background:{cor};color:{cor_texto};">'
        f'{texto}</span>'
    )


_STATUS = {
    "SCHEDULED": ("Agendado", "#3a4a82", "#cdd8ff"),
    "TIMED": ("Agendado", "#3a4a82", "#cdd8ff"),
    "IN_PLAY": ("AO VIVO", "#FF2D78", "#fff"),
    "PAUSED": ("Intervalo", "#FFC93C", "#0B1437"),
    "FINISHED": ("Encerrado", "#28E0A0", "#0B1437"),
    "AWARDED": ("Encerrado", "#28E0A0", "#0B1437"),
    "POSTPONED": ("Adiado", "#8295c2", "#0B1437"),
    "SUSPENDED": ("Suspenso", "#8295c2", "#0B1437"),
    "CANCELLED": ("Cancelado", "#8295c2", "#0B1437"),
}


def badge_status(status):
    """HTML do badge de status de um jogo."""
    texto, cor, cor_txt = _STATUS.get(status, ("Agendado", "#3a4a82", "#cdd8ff"))
    return badge(texto, cor, cor_txt)


def cor_posicao(posicao):
    """Cor de fundo da bolinha de posicao no ranking."""
    return {1: COR_OURO, 2: "#C7D0E8", 3: "#E0A063"}.get(posicao, "#2c3c74")
