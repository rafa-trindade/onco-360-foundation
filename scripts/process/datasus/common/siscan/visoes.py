"""Configuração das visões do SISCAN no TABNET (colo, mama e mamografia, nacional).
"""

# -----------------------------------------------------------------------------
# DEFINIÇÃO DE MEDIDAS POR TIPO DE EXAME
# -----------------------------------------------------------------------------

MEDIDAS_CITO_COLO = [
    "Exames",
    "Exames Alterados",
    "ASC-US",
    "ASC-H",
    "Les IE Baixo Grau",
    "Les IEp Alto Grau",
    "Les IE AG Mic. Inv",
    "Carc. Epiderm. Inv",
    "Adenocarc in situ",
    "Adenocarc invasor",
    "Outras Neoplasias"
]

MEDIDAS_HISTO_COLO = [
    "Exames",
    "Res_Exames_Neo_Preneo",
    "Neo. NIC I",
    "Neo. NIC II",
    "Neo. NIC III",
    "Neo. Carc. epid. Micr",
    "Neo. Carc. epid. Inva",
    "Neo. Carc. epid. imp.",
    "Neo. Adeno in situ",
    "Neo. Adeno invas",
    "Out  NEOPL.MALIG"
]

MEDIDAS_MAMO = [
    "Exames",
    "Mmg Diag Achados",
    "Mmg Diag Categoria 3",
    "Mmg Diag Lesao cancer",
    "Mmg Diag Aval QT",
    "Mmg Diag Revisao",
    "Mmg Diag pos biopsia",
    "Assimetria Focal",
    "Assimetria Difusa",
    "Distorção Focal",
    "Area Densa",
    "Achado Benigno",
    "Nódulo_Resul",
    "Microcalcificação"
]

MEDIDAS_CITO_MAMA = [
    "Exames",
]

MEDIDAS_HISTO_MAMA = [
    "Exames",
    "Lesão benigna",
    "Les B_Hip duc.s/at",
    "Les B_Hip duc.c/at",
    "Les B_Hip lob.c/at",
    "Ben_Adnose SOE",
    "Ben_Lesão esc. rad",
    "Ben_Cond fibrocíst",
    "Ben_Fibroadenoma",
    "Ben_Pap. solitário",
    "Ben_Pap. múltiplo",
    "Ben_Pap. flor. mam",
    "Ben_Mastite",
    "Ben_Outros"
]


# -----------------------------------------------------------------------------
# MAPEAMENTO DAS VISÕES E SEUS CRUZAMENTOS GEOGRÁFICOS
# -----------------------------------------------------------------------------

VISOES = {
    # ------------------ CITOPATOLÓGICO DE COLO ------------------
    "cito_colo_residencia": {
        "def_rel": "SISCAN/cito_colo_residbr.def",
        "exame": "Colo do útero (citopatológico)",
        "perfil": "Por local de residência",
        "medidas": MEDIDAS_CITO_COLO,
        "cruzamentos": [
            ("UF de residencia", "Ano competencia"),
        ],
    },
    "cito_colo_atendimento": {
        "def_rel": "SISCAN/cito_colo_atendbr.def",
        "exame": "Colo do útero (citopatológico)",
        "perfil": "Por local de atendimento",
        "medidas": MEDIDAS_CITO_COLO,
        "cruzamentos": [
            ("UF do prest.serviço", "Ano competencia"),
        ],
    },  

    # ------------------ HISTOPATOLÓGICO DE COLO (BIÓPSIA) ------------------
    "histo_colo_residencia": {
        "def_rel": "siscan/histo_residbr.def",
        "exame": "Colo do útero (histopatológico)",
        "perfil": "Por local de residência",
        "medidas": MEDIDAS_HISTO_COLO,
        "cruzamentos": [
            ("UF de residencia", "Ano competencia"),
        ],
    },   
    "histo_colo_atendimento": {
        "def_rel": "siscan/histo_atendbr.def",
        "exame": "Colo do útero (histopatológico)",
        "perfil": "Por local de atendimento",
        "medidas": MEDIDAS_HISTO_COLO,
        "cruzamentos": [
            ("UF do prest.serviço", "Ano competencia"),
        ],
    },    

    # ------------------ MAMOGRAFIA ------------------
    "mamografia_residencia": {
        "def_rel": "siscan/mamografia_residbr.def",
        "exame": "Mamografia",
        "perfil": "Por local de residência",
        "medidas": MEDIDAS_MAMO,
        "cruzamentos": [
            ("UF de residencia", "Ano competencia"),
        ],
    },   
    "mamografia_atendimento": {
        "def_rel": "siscan/mamografia_atendbr.def",
        "exame": "Mamografia",
        "perfil": "Por local de atendimento",
        "medidas": MEDIDAS_MAMO,
        "cruzamentos": [
            ("UF do prest.serviço", "Ano competencia"),
        ],
    }, 

    # ------------------ CITOPATOLÓGICO DE MAMA (PAAF/PUNÇÃO) ------------------
    "cito_mama_residencia": {
        "def_rel": "SISCAN/CITOMAMA_RESIDbr.def",
        "exame": "Mama (citopatológico)",
        "perfil": "Por local de residência",
        "medidas": MEDIDAS_CITO_MAMA,
        "cruzamentos": [
            ("UF de residencia", "Ano competencia"),
        ],
        "submissao": {
            "dimensoes": {
                "UF de residencia": "UF de residencia|CO_UF_RESIDENCIA|1|territorio\\br_uf.cnv",
                "Ano competencia": "Ano competencia|NU_ANO_COMPETENCIA|1|SISCAN\\ano.cnv",
            },
            "medidas": {"Exames": "Exames|QT_EXAME"},
        },
    },
    "cito_mama_atendimento": {
        "def_rel": "SISCAN/CITOMAMA_ATENDbr.def",
        "exame": "Mama (citopatológico)",
        "perfil": "Por local de atendimento",
        "medidas": MEDIDAS_CITO_MAMA,
        "cruzamentos": [
            ("UF do prest.serviço", "Ano competencia"),
        ],
        "submissao": {
            "dimensoes": {
                "UF do prest.serviço": "UF do prest.serviço|CO_UF_PREST_SERVICO|1|territorio\\br_uf.cnv",
                "Ano competencia": "Ano competencia|NU_ANO_COMPETENCIA|1|SISCAN\\ano.cnv",
            },
            "medidas": {"Exames": "Exames|QT_EXAME"},
        },
    },

    # ------------------ HISTOPATOLÓGICO DE MAMA (BIÓPSIA) ------------------
    "histo_mama_residencia": {
        "def_rel": "SISCAN/HISTMAMA_RESID_br.def",
        "exame": "Mama (histopatológico)",
        "perfil": "Por local de residência",
        "medidas": MEDIDAS_HISTO_MAMA,
        "cruzamentos": [
            ("UF de residencia", "Ano competencia"),
        ],
    },
    "histo_mama_atendimento": {
        "def_rel": "SISCAN/HISTMAMA_ATEND_br.def",
        "exame": "Mama (histopatológico)",
        "perfil": "Por local de atendimento",
        "medidas": MEDIDAS_HISTO_MAMA,
        "cruzamentos": [
            ("UF do prest.serviço", "Ano competencia"),
        ],
    },
}

ANOS = [str(a) for a in range(2013, 2027)]