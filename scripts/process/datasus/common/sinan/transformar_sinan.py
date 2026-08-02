"""Transformação do SINAN CANC (câncer relacionado ao trabalho).

Renomeia as colunas técnicas do DBC para nomes legíveis, decodifica os campos
conforme a ficha de investigação e descarta campos de controle e identificação
pessoal. As exposições ocupacionais a agentes cancerígenos são o diferencial
desta base (flags Sim/Não/Ignorado).
"""

import re
from scripts.common.paths import MANUAL_DATASUS_REF_DIR


# Colunas técnicas -> nomes legíveis (campos de valor analítico).
RENOMEAR = {
    "DT_NOTIFIC": "DATA_NOTIFICACAO",
    "NU_ANO": "ANO_NOTIFICACAO",
    "ID_AGRAVO": "COD_AGRAVO",
    "SG_UF_NOT": "COD_UF_NOTIFICACAO",
    "ID_MUNICIP": "COD_MUNICIPIO_NOTIFICACAO",
    "ID_UNIDADE": "COD_UNIDADE_NOTIFICACAO",
    "DT_DIAG": "DATA_DIAGNOSTICO",
    "ANO_NASC": "ANO_NASCIMENTO",
    "SG_UF": "COD_UF_RESIDENCIA",
    "ID_MN_RESI": "COD_MUNICIPIO_RESIDENCIA",
    "ID_OCUPA_N": "COD_OCUPACAO",
    "NUTEMPO": "TEMPO_TRABALHO_QTD",
    "CNAE": "COD_CNAE",
    "NUTEMPORIS": "TEMPO_EXPOSICAO_QTD",
    "DIAG_ESP": "CID_DIAGNOSTICO_ESPECIFICO",
    "OUT_EXP_DE": "EXPOSICAO_OUTROS_DESCRICAO",
    "TEMPO_FUMA": "TEMPO_FUMO_QTD",
    "DT_OBITO": "DATA_OBITO",
}

# Campos de controle interno, fluxo do SINAN e identificação, descartados.
DESCARTAR = {
    "TP_NOT", "SEM_NOT", "ID_REGIONA", "SEM_DIAG", "ID_RG_RESI", "ID_PAIS",
    "UF_EMP", "MUN_EMP", "DT_DIGITA", "DT_TRANSUS", "DT_TRANSDM", "DT_TRANSSM",
    "DT_TRNASRM", "DT_TRANSRS", "DT_TRANSSE", "NU_LOTE_V", "NU_LOTE_H",
}

ORDENAR = [
    "DATA_NOTIFICACAO", "ANO_NOTIFICACAO", "COD_AGRAVO",
    "COD_UF_NOTIFICACAO", "COD_MUNICIPIO_NOTIFICACAO", "COD_UNIDADE_NOTIFICACAO",
    "COD_UF_RESIDENCIA", "COD_MUNICIPIO_RESIDENCIA",
    "ANO_NASCIMENTO", "COD_IDADE", "IDADE_ANOS", "SEXO", 
    "COD_RACA_COR", "RACA_COR", "COD_GESTACAO", "GESTACAO", 
    "COD_ESCOLARIDADE", "ESCOLARIDADE",
    "COD_SITUACAO_MERCADO_TRABALHO", "SITUACAO_MERCADO_TRABALHO",
    "COD_OCUPACAO", "OCUPACAO_DESCRICAO", "COD_CNAE", 
    "COD_EMPREGADOR_TERCEIRIZADO", "EMPREGADOR_TERCEIRIZADO",
    "COD_TEMPO_TRABALHO_UNIDADE", "TEMPO_TRABALHO_UNIDADE", "TEMPO_TRABALHO_QTD",
    "COD_TEMPO_EXPOSICAO_UNIDADE", "TEMPO_EXPOSICAO_UNIDADE", "TEMPO_EXPOSICAO_QTD",
    "EXPOSICAO_ASBESTO", "EXPOSICAO_SILICA_ARSENICO", "EXPOSICAO_AMINAS_AROMATICAS",
    "EXPOSICAO_BENZENO", "EXPOSICAO_ALCATRAO", "EXPOSICAO_HIDROCARBONETOS",
    "EXPOSICAO_OLEOS_MINERAIS", "EXPOSICAO_BERILIO", "EXPOSICAO_CADMIO",
    "EXPOSICAO_CROMO", "EXPOSICAO_NIQUEL", "EXPOSICAO_RADIACOES_IONIZANTES",
    "EXPOSICAO_RADIACOES_NAO_IONIZANTES", "EXPOSICAO_HORMONIOS",
    "EXPOSICAO_ANTINEOPLASICOS", "EXPOSICAO_OUTROS", "EXPOSICAO_OUTROS_DESCRICAO",
    "COD_HABITO_FUMAR", "HABITO_FUMAR", "COD_TEMPO_FUMO_UNIDADE", 
    "TEMPO_FUMO_UNIDADE", "TEMPO_FUMO_QTD",
    "COD_OUTROS_TRABALHADORES_DOENCA", "OUTROS_TRABALHADORES_DOENCA",
    "COD_COMUNICACAO_ACIDENTE_TRABALHO", "COMUNICACAO_ACIDENTE_TRABALHO",
    "DATA_DIAGNOSTICO", "CID_DIAGNOSTICO_ESPECIFICO", "CID_DIAGNOSTICO_ESPECIFICO_DESCRICAO",
    "COD_REGIME_TRATAMENTO", "REGIME_TRATAMENTO",
    "COD_EVOLUCAO", "EVOLUCAO_CASO", "DATA_OBITO", "ARQUIVO_ORIGEM"
]

MAPA_SEXO = {"M": "Masculino", "F": "Feminino", "I": "Ignorado"}
MAPA_RACA_COR = {
    "1": "Branca", "2": "Preta", "3": "Amarela", "4": "Parda",
    "5": "Indígena", "9": "Ignorado",
}
MAPA_GESTACAO = {
    "1": "1º trimestre", "2": "2º trimestre", "3": "3º trimestre",
    "4": "Idade gestacional ignorada", "5": "Não", "6": "Não se aplica",
    "9": "Ignorado",
}
MAPA_ESCOLARIDADE = {
    "00": "Analfabeto",
    "01": "1ª a 4ª série incompleta do EF",
    "02": "4ª série completa do EF",
    "03": "5ª à 8ª série incompleta do EF",
    "04": "Ensino fundamental completo",
    "05": "Ensino médio incompleto",
    "06": "Ensino médio completo",
    "07": "Educação superior incompleta",
    "08": "Educação superior completa",
    "09": "Ignorado",
    "10": "Não se aplica",
}
MAPA_SITUACAO_TRABALHO = {
    "01": "Empregado registrado com carteira assinada",
    "02": "Empregado não registrado",
    "03": "Autônomo/conta própria",
    "04": "Servidor público estatutário",
    "05": "Servidor público celetista",
    "06": "Aposentado",
    "07": "Desempregado",
    "08": "Trabalho temporário",
    "09": "Cooperativado",
    "10": "Trabalhador avulso",
    "11": "Empregador",
    "12": "Outros",
    "99": "Ignorado",
}
MAPA_UNIDADE_TEMPO = {"1": "Hora", "2": "Dia", "3": "Mês", "4": "Ano"}
MAPA_TERCEIRIZADO = {"1": "Sim", "2": "Não", "3": "Não se aplica", "9": "Ignorado"}
MAPA_REGIME = {"1": "Hospitalar", "2": "Ambulatorial"}
MAPA_EXPOSICAO = {"1": "Sim", "2": "Não", "9": "Ignorado"}
MAPA_FUMAR = {"1": "Sim", "2": "Não", "3": "Ex-fumante", "9": "Ignorado"}
MAPA_SIM_NAO_IGN = {"1": "Sim", "2": "Não", "9": "Ignorado"}
MAPA_EVOLUCAO = {
    "1": "Sem evidência da doença (remissão completa)",
    "2": "Remissão parcial",
    "3": "Doença estável",
    "4": "Doença em progressão",
    "5": "Fora de possibilidade terapêutica",
    "6": "Óbito por câncer relacionado ao trabalho",
    "7": "Óbito por outras causas",
    "8": "Não se aplica",
    "9": "Ignorado",
}

EXPOSICOES = {
    "ASBESTO": "EXPOSICAO_ASBESTO",
    "SILICA": "EXPOSICAO_SILICA_ARSENICO",
    "AMINA": "EXPOSICAO_AMINAS_AROMATICAS",
    "BENZENO": "EXPOSICAO_BENZENO",
    "ALCATRAO": "EXPOSICAO_ALCATRAO",
    "HIDROCARBO": "EXPOSICAO_HIDROCARBONETOS",
    "OLEOS": "EXPOSICAO_OLEOS_MINERAIS",
    "BERILIO": "EXPOSICAO_BERILIO",
    "CADMIO": "EXPOSICAO_CADMIO",
    "CROMO": "EXPOSICAO_CROMO",
    "NIQUEL": "EXPOSICAO_NIQUEL",
    "IONIZANTES": "EXPOSICAO_RADIACOES_IONIZANTES",
    "NAO_IONIZA": "EXPOSICAO_RADIACOES_NAO_IONIZANTES",
    "HORMONIO": "EXPOSICAO_HORMONIOS",
    "NEOPLASICO": "EXPOSICAO_ANTINEOPLASICOS",
    "OUTRO_EXP": "EXPOSICAO_OUTROS",
}

DECODIFICAR = [
    ("CS_SEXO", MAPA_SEXO, None, "SEXO"),
    ("CS_RACA", MAPA_RACA_COR, "COD_RACA_COR", "RACA_COR"),
    ("CS_GESTANT", MAPA_GESTACAO, "COD_GESTACAO", "GESTACAO"),
    ("CS_ESCOL_N", MAPA_ESCOLARIDADE, "COD_ESCOLARIDADE", "ESCOLARIDADE"),
    ("SIT_TRAB", MAPA_SITUACAO_TRABALHO, "COD_SITUACAO_MERCADO_TRABALHO", "SITUACAO_MERCADO_TRABALHO"),
    ("TPTEMPO", MAPA_UNIDADE_TEMPO, "COD_TEMPO_TRABALHO_UNIDADE", "TEMPO_TRABALHO_UNIDADE"),
    ("TPTEMPORIS", MAPA_UNIDADE_TEMPO, "COD_TEMPO_EXPOSICAO_UNIDADE", "TEMPO_EXPOSICAO_UNIDADE"),
    ("TERCEIRIZA", MAPA_TERCEIRIZADO, "COD_EMPREGADOR_TERCEIRIZADO", "EMPREGADOR_TERCEIRIZADO"),
    ("REGIME", MAPA_REGIME, "COD_REGIME_TRATAMENTO", "REGIME_TRATAMENTO"),
    ("FUMA", MAPA_FUMAR, "COD_HABITO_FUMAR", "HABITO_FUMAR"),
    ("TP_TEMP_FU", MAPA_UNIDADE_TEMPO, "COD_TEMPO_FUMO_UNIDADE", "TEMPO_FUMO_UNIDADE"),
    ("TRAB_DOE", MAPA_SIM_NAO_IGN, "COD_OUTROS_TRABALHADORES_DOENCA", "OUTROS_TRABALHADORES_DOENCA"),
    ("CAT", MAPA_TERCEIRIZADO, "COD_COMUNICACAO_ACIDENTE_TRABALHO", "COMUNICACAO_ACIDENTE_TRABALHO"),
    ("EVOLUCAO", MAPA_EVOLUCAO, "COD_EVOLUCAO", "EVOLUCAO_CASO"),
]


def _case(coluna_origem, mapa, coluna_saida, fallback=None):
    ramos = " ".join(
        f"WHEN trim(base.\"{coluna_origem}\") = '{cod}' THEN '{txt}'"
        for cod, txt in mapa.items()
    )
    senao = f"'{fallback}'" if fallback is not None else f'trim(base."{coluna_origem}")'
    return f'CASE {ramos} ELSE {senao} END AS "{coluna_saida}"'


def montar_query_sinan(cols):
    
    presentes = {c.upper() for c in cols}
    sel = []
    joins = []

    for origem, destino in RENOMEAR.items():
        if origem in presentes:
            sel.append(f'trim(base."{origem}") AS "{destino}"')

    if "NU_IDADE_N" in presentes:
        sel.append('trim(base."NU_IDADE_N") AS "COD_IDADE"')
        sel.append(
            'CASE '
            'WHEN substr(trim(base."NU_IDADE_N"), 1, 1) = \'4\' THEN try_cast(substr(trim(base."NU_IDADE_N"), 2) AS INTEGER) '
            'WHEN substr(trim(base."NU_IDADE_N"), 1, 1) = \'5\' THEN try_cast(substr(trim(base."NU_IDADE_N"), 2) AS INTEGER) + 100 '
            'ELSE NULL END AS "IDADE_ANOS"'
        )

    for origem, mapa, cod_saida, txt_saida in DECODIFICAR:
        if origem in presentes:
            if cod_saida:
                sel.append(f'trim(base."{origem}") AS "{cod_saida}"')
            sel.append(_case(origem, mapa, txt_saida))

    for origem, destino in EXPOSICOES.items():
        if origem in presentes:
            sel.append(_case(origem, MAPA_EXPOSICAO, destino))


    # Descrição do CID-10
    if "DIAG_ESP" in presentes:
        ref_cid = MANUAL_DATASUS_REF_DIR / "ref_causa_cid10.parquet"
        if ref_cid.exists():
            sel.append('rcid.DESCRICAO AS "CID_DIAGNOSTICO_ESPECIFICO_DESCRICAO"')
            joins.append(
                f"LEFT JOIN read_parquet('{ref_cid.as_posix()}') rcid "
                f"ON replace(trim(base.\"DIAG_ESP\"), '.', '') = rcid.CODIGO"
            )

    # Descrição da Ocupação (CBO)
    if "ID_OCUPA_N" in presentes:
        ref_cbo = MANUAL_DATASUS_REF_DIR / "ref_ocupacao.parquet"
        if ref_cbo.exists():
            sel.append('rocup.DESCRICAO AS "OCUPACAO_DESCRICAO"')
            joins.append(
                f"LEFT JOIN read_parquet('{ref_cbo.as_posix()}') rocup "
                f"ON trim(base.\"ID_OCUPA_N\") = rocup.CODIGO"
            )

    if "ARQUIVO_ORIGEM" in presentes:
        sel.append('base."ARQUIVO_ORIGEM" AS "ARQUIVO_ORIGEM"')

    query_interna = f"SELECT {', '.join(sel)} FROM __ORIGEM__ base " + " ".join(joins)
    
    colunas_produzidas = {re.search(r'AS "([^"]+)"', s).group(1) for s in sel}
    
    colunas_saida = [f'"{c}"' for c in ORDENAR if c in colunas_produzidas]
    
    sobras = [f'"{c}"' for c in colunas_produzidas if c not in ORDENAR]
    
    query_final = f"SELECT {', '.join(colunas_saida + sobras)} FROM ({query_interna}) tb_ordenada"
    
    return query_final