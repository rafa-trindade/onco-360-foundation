"""Bloco comum das APAC do SIASUS (Autorização de Procedimento Ambulatorial) e 
decodificações compartilhadas.

AQ (Quimioterapia), AR (Radioterapia) e AM (Medicamentos) compartilham o mesmo
cabeçalho AP_* e adicionam seu próprio bloco.

Referência de CID-10 (topografia) reutiliza a mesma tabela do SIM/painel.
"""
from scripts.common.paths import MANUAL_DATASUS_REF_DIR

REF_CID10 = MANUAL_DATASUS_REF_DIR / "ref_causa_cid10.parquet"

RENOMEAR_COMUM = {
    "AP_CODUNI": "COD_CNES",
    "AP_AUTORIZ": "NUM_APAC",
    "AP_CMP": "ANO_MES_ATENDIMENTO",
    "AP_PRIPAL": "COD_PROCEDIMENTO_PRINCIPAL",
    "AP_VL_AP": "VALOR_TOTAL_APAC",
    "AP_UFMUN": "COD_UF_MUNICIPIO_ESTABELECIMENTO",
    "AP_CNPJCPF": "CNPJ_ESTABELECIMENTO",
    "AP_CNPJMNT": "CNPJ_MANTENEDORA",
    "AP_COIDADE": "COD_TIPO_IDADE",
    "AP_NUIDADE": "IDADE",
    "AP_SEXO": "SEXO",
    "AP_RACACOR": "COD_RACA_COR",
    "AP_MUNPCN": "COD_MUNICIPIO_RESIDENCIA",
    "AP_UFNACIO": "COD_NACIONALIDADE",
    "AP_CEPPCN": "CEP_PACIENTE",
    "AP_DTINIC": "DATA_INICIO_VALIDADE",
    "AP_DTFIM": "DATA_FIM_VALIDADE",
    "AP_TPATEN": "COD_TIPO_ATENDIMENTO",
    "AP_TPAPAC": "COD_TIPO_APAC",
    "AP_CATEND": "COD_CARATER_ATENDIMENTO",
    "AP_CIDPRI": "CID_PRINCIPAL",
    "AP_CIDSEC": "CID_SECUNDARIO",
    "AP_CIDCAS": "CID_CAUSAS_ASSOCIADAS",
    "AP_DTSOLIC": "DATA_SOLICITACAO",
    "AP_DTAUT": "DATA_AUTORIZACAO",
    "AP_NATJUR": "COD_NATUREZA_JURIDICA",
}

DESCARTAR_COMUM = {
    "AP_MVM", "AP_CONDIC", "AP_GESTAO", "AP_TPUPS", "AP_TIPPRE", "AP_MN_IND",
    "AP_CNSPCN", "AP_MOTSAI", "AP_OBITO", "AP_ENCERR", "AP_PERMAN", "AP_ALTA",
    "AP_TRANSF", "AP_DTOCOR", "AP_CODEMI", "AP_APACANT", "AP_UNISOL", "AP_ETNIA",
    "AP_UFDIF", "AP_MNDIF",
}

MAPA_SEXO = {"1": "Masculino", "M": "Masculino", "2": "Feminino", "F": "Feminino"}
MAPA_RACA_COR = {
    "01": "Branca", "02": "Preta", "03": "Parda", "04": "Amarela",
    "05": "Indígena", "99": "Sem informação",
}
MAPA_SIM_NAO = {"S": "Sim", "N": "Não"}
MAPA_LINFONODOS = {"S": "Sim", "N": "Não", "3": "Não avaliáveis"}
MAPA_ESTADIAMENTO = {"0": "0", "1": "I", "2": "II", "3": "III", "4": "IV"}
MAPA_TIPO_APAC = {"1": "Inicial", "2": "Continuidade", "3": "Única"}
MAPA_FINALIDADE_RADIO = {
    "1": "Radical", "2": "Adjuvante", "3": "Antiálgica",
    "4": "Paliativa", "5": "Prévia", "6": "Antihemorrágica",
}
