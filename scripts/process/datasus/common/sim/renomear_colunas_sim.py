"""Renomeação das colunas do SIM para nomes legíveis.

Padrão do projeto (vale para todas as bases): MAIÚSCULO com underscore, em
português, descritivo mas conciso. Sai o código críptico do DATASUS
(CAUSABAS, LOCOCOR, DTOBITO) e entra o nome claro (CAUSA_BASICA,
LOCAL_OCORRENCIA, DATA_OBITO).

O mapa cobre as duas eras (CID-9 e CID-10). Colunas ausentes são ignoradas;
colunas não mapeadas mantêm o nome original (a renomeação é aditiva e
segura). As colunas derivadas já nascem com nome legível.
"""

# nome_original (MAIÚSCULO) -> nome_legivel
RENOMEAR: dict[str, str] = {
    "CONTADOR": "ID_REGISTRO",
    "_ARQUIVO_ORIGEM": "ARQUIVO_ORIGEM",
    "ARQUIVO_ORIGEM": "ARQUIVO_ORIGEM",

    "CAUSABAS": "CAUSA_BASICA",

    "DTOBITO": "DATA_OBITO",
    "DATAOBITO": "DATA_OBITO",
    "DTNASC": "DATA_NASCIMENTO",
    "DATANASC": "DATA_NASCIMENTO",
    "HORAOBITO": "HORA_OBITO",

    "IDADE_ANOS": "IDADE_ANOS",
    "SEXO": "SEXO",
    "RACACOR": "RACA_COR",
    "ETNIA": "ETNIA_INDIGENA",
    "ESTCIV": "ESTADO_CIVIL",
    "ESTCIVIL": "ESTADO_CIVIL",
    "ESCFALAGR1": "ESCOLARIDADE",
    "INSTRUCAO": "ESCOLARIDADE",
    "OCUP": "OCUPACAO",
    "OCUPACAO": "OCUPACAO",
    "NATURAL": "NATURALIDADE",
    "CODMUNNATU": "COD_MUNICIPIO_NATURALIDADE",

    "CO_IBGE_RESIDENCIA": "COD_MUNICIPIO_RESIDENCIA",
    "COD_MUNICIPIO_ATUAL": "COD_MUNICIPIO_RESIDENCIA_ATUAL",
    "CODMUNOCOR": "COD_MUNICIPIO_OCORRENCIA",
    "MUNIOCOR": "COD_MUNICIPIO_OCORRENCIA",
    "LOCOCOR": "LOCAL_OCORRENCIA",

    "TIPOBITO": "TIPO_OBITO",
    "ASSISTMED": "ASSISTENCIA_MEDICA",
    "EXAME": "TEVE_EXAME",
    "CIRURGIA": "TEVE_CIRURGIA",
    "NECROPSIA": "TEVE_NECROPSIA",
    "ATESTANTE": "MEDICO_ATESTANTE",

    # Óbito em gestante/puérpera (relevante: câncer em gestante)
    "OBITOGRAV": "OBITO_NA_GRAVIDEZ",
    "OBITOPUERP": "OBITO_NO_PUERPERIO",
}


def nome_final(coluna: str) -> str:
    return RENOMEAR.get(coluna.upper(), coluna)


def aplicar_renomeacao(colunas: list[str]) -> dict[str, str]:
    """Retorna {nome_atual: nome_final} para as colunas presentes. Colunas
    sem entrada no mapa mantêm o nome original."""
    return {c: nome_final(c) for c in colunas}
