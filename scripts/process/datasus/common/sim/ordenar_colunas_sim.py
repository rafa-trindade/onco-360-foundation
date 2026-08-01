"""Seleção e ordenação das colunas do SIM.

Aplica as decisões de projeto às três variantes (CID-9, CID-10, prelim):

1. Descarta colunas brutas que já têm versão tratada (IDADE -> IDADE_ANOS;
   CODMUNRES/MUNIRES -> CO_IBGE_RESIDENCIA + COD_MUNICIPIO_ATUAL; LINHAA-D/II
   -> a causa consolidada já está em CAUSABAS).
2. Descarta controle interno / sistema (cartório, registro, flags, regionais
   estaduais, datas de trâmite, escolaridade por época já coberta pela
   agregada). Inclui HORAOBITO (100% nulo) e CODMUNNATU (redundante com
   NATURALIDADE em texto).
3. Descarta campos de baixa completude sem valor para óbito por câncer
   (maternos/fetais, causas externas, investigação materno/infantil),
   confirmados por medição na base real. Exceção: OBITO_NA_GRAVIDEZ /
   OBITO_NO_PUERPERIO (câncer em gestante/puérpera, ~8%, relevante).
4. Ordena por importância analítica: identificador e causa à frente, depois
   datas, demografia, geografia e dados clínicos. ARQUIVO_ORIGEM vai para o
   fim (linhagem, não analítico).

Comparação case-insensitive (o CID-9 traz alguns nomes em minúsculo, ex:
'contador'), preservando o nome original para o SQL. Colunas ausentes são
ignoradas sem erro.
"""

# Brutas com versão tratada equivalente + cadeia causal crua (LINHAs).
_DESCARTE_BRUTAS = {
    "IDADE", "CODMUNRES", "MUNIRES",
    "LINHAA", "LINHAB", "LINHAC", "LINHAD", "LINHAII", "LINHA_II", "CAUSAMAT",
}

# Controle interno / sistema / código local sem uso analítico.
_DESCARTE_CONTROLE = {
    # CID-10 / era moderna
    "ORIGEM", "CRM", "COMUNSVOIM", "DTATESTADO", "NUMEROLOTE", "TPPOS",
    "DTINVESTIG", "DTCADASTRO", "STCODIFICA", "CODIFICADO", "VERSAOSIST",
    "VERSAOSCB", "DTRECEBIM", "DTRECORIGA", "DTRECORIG", "DIFDATA", "NUDIASOBCO",
    "NUDIASOBIN", "DTCADINV", "DTCONINV", "FONTES", "NUDIASINF", "DTCADINF",
    "DTCONCASO", "FONTESINF", "CODBAIRES", "CODBAIOCOR", "TPASSINA",
    "CODMUNCART", "CODCART", "NUMREGCART", "DTREGCART", "EXPDIFDATA", "NUMERODN",
    "CB_PRE", "CAUSABAS_O", "ATESTADO", "STDOEPIDEM", "STDONOVA", "ESTABDESCR",
    "CODESTAB", "SERIESCFAL",
    # Escolaridade: mantém só a agregada (ESCFALAGR1/ESCMAEAGR1), comparável
    # entre épocas; descarta as versões por época.
    "ESC", "ESC2010", "ESCMAE", "ESCMAE2010", "SERIESCMAE",
    # CID-9 / era antiga
    "CARTORIO", "REGISTRO", "DATAREG", "CRITICA", "NUMEXPORT", "CRSOCOR",
    "CRSRES", "BAIRES", "AREARES", "CODIGO", "UFINFORM",
    # 100% nulo na base real
    "HORAOBITO",
    # código de município de nascimento: redundante com NATURALIDADE (texto),
    # completude média, sem valor analítico direto.
    "CODMUNNATU",
}

# Baixa completude + irrelevância para óbito por câncer (medição real).
# Mantêm-se OBITOGRAV/OBITOPUERP (~8%, câncer em gestante/puérpera).
_DESCARTE_BAIXA_COMPLETUDE = {
    # Causas externas (câncer não é morte violenta)
    "CIRCOBITO", "ACIDTRAB", "FONTE", "TIPOVIOL", "TIPOACID", "LOCACID",
    "FONTINFO", "FONTEINV",
    # Maternos/fetais (óbito por câncer é adulto)
    "IDADEMAE", "ESCMAEAGR1", "OCUPMAE", "INSTRMAE", "OCUPPAI", "INSTRPAI",
    "QTDFILVIVO", "QTDFILMORT", "FILHVIVOS", "FILHMORT", "GRAVIDEZ", "TIPOGRAV",
    "SEMAGESTAC", "SEMANGEST", "GESTACAO", "PARTO", "TIPOPARTO", "OBITOPARTO",
    "MORTEPARTO", "PESO", "PESONASC", "OBITOFE1", "OBITOFE2",
    # Investigação de óbito materno/infantil (só para esses casos)
    "TPMORTEOCO", "TPOBITOCOR", "TPNIVELINV", "TPRESGINFO", "ALTCAUSA",
}

DESCARTAR = _DESCARTE_BRUTAS | _DESCARTE_CONTROLE | _DESCARTE_BAIXA_COMPLETUDE

# Descarte exclusivo do CID-9: nunca coletados antes de 1996 (0% na base).
# No CID-10 essas colunas são úteis, então o descarte é aplicado só na era
# CID-9 (ver _filtrar_cid9 em decodificar_sim_cid9).
DESCARTE_APENAS_CID9 = {"RACACOR", "ETNIA", "DATANASC"}

_GRUPOS = [
    ["CONTADOR"],
    ["CAUSABAS", "CAUSA_BASICA", "CAUSA_BASICA_DESCRICAO"],
    ["ANO_OBITO", "DTOBITO", "DATAOBITO", "DTNASC", "DATANASC"],
    ["IDADE_ANOS", "SEXO", "RACACOR", "ETNIA", "ESTCIV", "ESTCIVIL",
     "ESCFALAGR1", "INSTRUCAO", "OCUP", "OCUPACAO", "NATURAL"],
    ["CO_IBGE_RESIDENCIA", "COD_MUNICIPIO_ATUAL", "CODMUNOCOR", "MUNIOCOR", "LOCOCOR"],
    ["TIPOBITO", "ASSISTMED", "EXAME", "CIRURGIA", "NECROPSIA", "ATESTANTE"],
]

# Vão para o fim (esparsos, mas mantidos por relevância clínica).
_FIM = ["OBITOGRAV", "OBITOPUERP"]

# Linhagem: sempre a última coluna.
_LINHAGEM = ["_ARQUIVO_ORIGEM", "ARQUIVO_ORIGEM"]


def ordenar_colunas(colunas_presentes: list[str]) -> list[str]:
    """Filtra descartes e ordena por importância. ARQUIVO_ORIGEM ao fim."""
    descarte_upper = {c.upper() for c in DESCARTAR}
    presentes = [c for c in colunas_presentes if c.upper() not in descarte_upper]

    por_upper = {}
    for c in presentes:
        por_upper.setdefault(c.upper(), c)

    restantes = dict(por_upper)
    ordenadas = []

    def _adicionar(nomes):
        for nome in nomes:
            chave = nome.upper()
            if chave in restantes:
                ordenadas.append(restantes.pop(chave))

    for grupo in _GRUPOS:
        _adicionar(grupo)

    reservado = {c.upper() for c in _FIM + _LINHAGEM}
    nao_classificadas = [c for c in presentes
                         if c.upper() in restantes and c.upper() not in reservado]
    _adicionar(nao_classificadas)

    _adicionar(_FIM)
    _adicionar(_LINHAGEM)
    _adicionar([c for c in presentes if c.upper() in restantes])
    return ordenadas
