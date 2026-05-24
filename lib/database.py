"""
Camada de dados do Bolao da Copa 2026.

O "banco" e uma planilha do Google (3 abas: participantes, palpites, config).
Se as credenciais do Google nao estiverem configuradas, o app cai para um
MODO LOCAL de teste, gravando tudo em data/local_db.json - util para rodar
na sua maquina antes de publicar.

Todas as leituras ficam em cache curto (15s) para deixar o app rapido sem
estourar os limites do Google. Cada escrita limpa o cache correspondente.
"""

import json
import os
from datetime import datetime

import streamlit as st

from lib import config, segredos

# Cabecalhos das abas / colunas
_H_PARTICIPANTES = ["id", "nome", "usuario", "senha_hash", "salt", "papel", "criado_em"]
_H_PALPITES = ["participante_id", "palpites_json", "atualizado_em"]
_H_CONFIG = ["chave", "valor"]


# ----------------------------------------------------------------------
# Conexao
# ----------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _conexao():
    """
    Conecta ao backend de dados.
    Retorna ('sheets', {nome_aba: worksheet}) ou ('local', caminho_arquivo).
    """
    creds = segredos.secao("gcp_service_account")
    gsheets = segredos.secao("gsheets")
    tem_sheets = bool(creds) and bool(gsheets.get("spreadsheet_id"))
    if tem_sheets and "COLE_AQUI" not in str(gsheets.get("spreadsheet_id", "")):
        try:
            import gspread

            gc = gspread.service_account_from_dict(creds)
            planilha = gc.open_by_key(gsheets["spreadsheet_id"])
            abas = {
                "participantes": _garantir_aba(planilha, "participantes", _H_PARTICIPANTES),
                "palpites": _garantir_aba(planilha, "palpites", _H_PALPITES),
                "config": _garantir_aba(planilha, "config", _H_CONFIG),
            }
            return ("sheets", abas)
        except Exception as erro:  # noqa: BLE001
            st.session_state["_erro_db"] = (
                f"Nao foi possivel conectar ao Google Sheets ({erro}). "
                "O app esta usando o modo local de teste."
            )
    return ("local", config.ARQUIVO_DB_LOCAL)


def _garantir_aba(planilha, nome, cabecalho):
    """Garante que a aba existe e tem o cabecalho correto."""
    import gspread

    try:
        aba = planilha.worksheet(nome)
        if aba.row_values(1) != cabecalho:
            aba.update(range_name="A1", values=[cabecalho])
        return aba
    except gspread.WorksheetNotFound:
        aba = planilha.add_worksheet(title=nome, rows=500, cols=max(6, len(cabecalho)))
        aba.append_row(cabecalho)
        return aba


def modo_banco():
    """'sheets' (producao) ou 'local' (teste)."""
    return _conexao()[0]


# ----------------------------------------------------------------------
# Backend local (arquivo JSON)
# ----------------------------------------------------------------------
def _ler_local(caminho):
    if not os.path.exists(caminho):
        return {"participantes": [], "palpites": [], "config": []}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"participantes": [], "palpites": [], "config": []}
    dados.setdefault("participantes", [])
    dados.setdefault("palpites", [])
    dados.setdefault("config", [])
    return dados


def _gravar_local(caminho, dados):
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------
# Leituras (com cache curto)
# ----------------------------------------------------------------------
@st.cache_data(ttl=15, show_spinner=False)
def listar_participantes():
    """Lista de participantes (apenas jogadores - o admin nao entra aqui)."""
    modo, ref = _conexao()
    if modo == "sheets":
        registros = ref["participantes"].get_all_records()
    else:
        registros = _ler_local(ref)["participantes"]
    return [
        {
            "id": str(r.get("id", "")),
            "nome": str(r.get("nome", "")),
            "usuario": str(r.get("usuario", "")),
            "senha_hash": str(r.get("senha_hash", "")),
            "salt": str(r.get("salt", "")),
            "papel": str(r.get("papel", "participante")),
            "criado_em": str(r.get("criado_em", "")),
        }
        for r in registros
        if str(r.get("id", "")).strip()
    ]


@st.cache_data(ttl=15, show_spinner=False)
def _palpites_registros():
    modo, ref = _conexao()
    if modo == "sheets":
        return ref["palpites"].get_all_records()
    return _ler_local(ref)["palpites"]


@st.cache_data(ttl=15, show_spinner=False)
def _config_registros():
    modo, ref = _conexao()
    if modo == "sheets":
        return ref["config"].get_all_records()
    return _ler_local(ref)["config"]


def listar_todos_palpites():
    """Dicionario {participante_id: {match_key: [gols_c1, gols_c2]}}."""
    resultado = {}
    for r in _palpites_registros():
        pid = str(r.get("participante_id", "")).strip()
        if not pid:
            continue
        try:
            resultado[pid] = json.loads(r.get("palpites_json") or "{}")
        except (json.JSONDecodeError, TypeError):
            resultado[pid] = {}
    return resultado


def obter_palpites(participante_id):
    """Palpites de um participante: {match_key: [gols_c1, gols_c2]}."""
    return listar_todos_palpites().get(str(participante_id), {})


def obter_config(chave, padrao=None):
    for r in _config_registros():
        if str(r.get("chave", "")) == chave:
            valor = r.get("valor", "")
            return valor if str(valor).strip() != "" else padrao
    return padrao


def obter_participante_por_usuario(usuario):
    alvo = (usuario or "").strip().lower()
    for p in listar_participantes():
        if p["usuario"].strip().lower() == alvo:
            return p
    return None


# ----------------------------------------------------------------------
# Escritas
# ----------------------------------------------------------------------
def _agora():
    return datetime.now(config.TZ_BR).strftime("%Y-%m-%d %H:%M:%S")


def _proximo_id(participantes):
    maior = 0
    for p in participantes:
        try:
            maior = max(maior, int(p["id"]))
        except (ValueError, KeyError, TypeError):
            pass
    return str(maior + 1)


def adicionar_participante(nome, usuario, senha_hash, salt):
    """Cria um novo participante. Retorna o id gerado."""
    atuais = listar_participantes()
    novo_id = _proximo_id(atuais)
    criado = _agora()
    linha = [novo_id, nome, usuario, senha_hash, salt, "participante", criado]

    modo, ref = _conexao()
    if modo == "sheets":
        ref["participantes"].append_row(linha, value_input_option="USER_ENTERED")
    else:
        dados = _ler_local(ref)
        dados["participantes"].append(dict(zip(_H_PARTICIPANTES, linha)))
        _gravar_local(ref, dados)

    listar_participantes.clear()
    return novo_id


def atualizar_senha(participante_id, senha_hash, salt):
    """Redefine a senha de um participante."""
    modo, ref = _conexao()
    if modo == "sheets":
        linha = _linha_por_valor(ref["participantes"], participante_id, coluna=1)
        if linha:
            ref["participantes"].update(
                range_name=f"D{linha}:E{linha}",
                values=[[senha_hash, salt]],
            )
    else:
        dados = _ler_local(ref)
        for p in dados["participantes"]:
            if str(p.get("id")) == str(participante_id):
                p["senha_hash"] = senha_hash
                p["salt"] = salt
        _gravar_local(ref, dados)
    listar_participantes.clear()


def remover_participante(participante_id):
    """Remove o participante e os palpites dele."""
    modo, ref = _conexao()
    if modo == "sheets":
        linha = _linha_por_valor(ref["participantes"], participante_id, coluna=1)
        if linha:
            ref["participantes"].delete_rows(linha)
        linha_p = _linha_por_valor(ref["palpites"], participante_id, coluna=1)
        if linha_p:
            ref["palpites"].delete_rows(linha_p)
    else:
        dados = _ler_local(ref)
        dados["participantes"] = [
            p for p in dados["participantes"]
            if str(p.get("id")) != str(participante_id)
        ]
        dados["palpites"] = [
            p for p in dados["palpites"]
            if str(p.get("participante_id")) != str(participante_id)
        ]
        _gravar_local(ref, dados)
    listar_participantes.clear()
    _palpites_registros.clear()


def salvar_palpites(participante_id, palpites):
    """Grava (substitui) todos os palpites de um participante."""
    palpites_json = json.dumps(palpites, ensure_ascii=False)
    quando = _agora()
    modo, ref = _conexao()
    if modo == "sheets":
        linha = _linha_por_valor(ref["palpites"], participante_id, coluna=1)
        if linha:
            ref["palpites"].update(
                range_name=f"B{linha}:C{linha}",
                values=[[palpites_json, quando]],
            )
        else:
            ref["palpites"].append_row(
                [str(participante_id), palpites_json, quando],
                value_input_option="USER_ENTERED",
            )
    else:
        dados = _ler_local(ref)
        achou = False
        for p in dados["palpites"]:
            if str(p.get("participante_id")) == str(participante_id):
                p["palpites_json"] = palpites_json
                p["atualizado_em"] = quando
                achou = True
        if not achou:
            dados["palpites"].append({
                "participante_id": str(participante_id),
                "palpites_json": palpites_json,
                "atualizado_em": quando,
            })
        _gravar_local(ref, dados)
    _palpites_registros.clear()


def definir_config(chave, valor):
    """Grava um parametro de configuracao (ex.: prazo dos palpites)."""
    modo, ref = _conexao()
    if modo == "sheets":
        linha = _linha_por_valor(ref["config"], chave, coluna=1)
        if linha:
            ref["config"].update(range_name=f"B{linha}", values=[[valor]])
        else:
            ref["config"].append_row([chave, valor], value_input_option="USER_ENTERED")
    else:
        dados = _ler_local(ref)
        achou = False
        for r in dados["config"]:
            if str(r.get("chave")) == chave:
                r["valor"] = valor
                achou = True
        if not achou:
            dados["config"].append({"chave": chave, "valor": valor})
        _gravar_local(ref, dados)
    _config_registros.clear()


def _linha_por_valor(aba, valor, coluna=1):
    """Numero da linha (na planilha) cujo valor da coluna bate com 'valor'."""
    valores = aba.col_values(coluna)
    for i, v in enumerate(valores, start=1):
        if str(v) == str(valor):
            return i
    return None


def limpar_caches():
    """Forca a releitura de todos os dados na proxima vez."""
    listar_participantes.clear()
    _palpites_registros.clear()
    _config_registros.clear()
