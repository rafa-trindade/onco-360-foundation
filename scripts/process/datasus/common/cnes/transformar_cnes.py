"""Renomeação e descrição de códigos do CNES (estabelecimentos de oncologia).
"""
import pandas as pd

RENOMEAR_CNES = {
    "CNES": "COD_CNES",
    "NU_CNPJ": "CNPJ",
    "NU_CNPJ_MANTENEDORA": "CNPJ_MANTENEDORA",
    "NO_RAZAO_SOCIAL": "RAZAO_SOCIAL",
    "NO_FANTASIA": "NOME_FANTASIA",
    "CO_UF": "COD_UF",
    "CO_IBGE": "COD_MUNICIPIO",
    "CO_CEP": "CEP",
    "NO_LOGRADOURO": "LOGRADOURO",
    "NU_ENDERECO": "NUMERO_ENDERECO",
    "NO_BAIRRO": "BAIRRO",
    "NU_LATITUDE": "LATITUDE",
    "NU_LONGITUDE": "LONGITUDE",
    "NU_TELEFONE": "TELEFONE",
    "NO_EMAIL": "EMAIL",
    "CO_NATUREZA_JUR": "COD_NATUREZA_JURIDICA",
    "CO_ESFERA_ADMINISTRATIVA": "COD_ESFERA_ADMINISTRATIVA",
    "DS_ESFERA_ADMINISTRATIVA": "ESFERA_ADMINISTRATIVA",
    "TP_UNIDADE": "COD_TIPO_UNIDADE",
    "ST_CENTRO_CIRURGICO": "TEM_CENTRO_CIRURGICO",
    "ST_CENTRO_OBSTETRICO": "TEM_CENTRO_OBSTETRICO",
    "ST_CENTRO_NEONATAL": "TEM_CENTRO_NEONATAL",
    "ST_ATEND_HOSPITALAR": "TEM_ATENDIMENTO_HOSPITALAR",
    "ST_SERVICO_APOIO": "TEM_SERVICO_APOIO",
    "ST_ATEND_AMBULATORIAL": "TEM_ATENDIMENTO_AMBULATORIAL",
}


TIPO_UNIDADE_CNES = {
    "01": "Posto de Saúde",
    "02": "Centro de Saúde / Unidade Básica",
    "04": "Policlínica",
    "05": "Hospital Geral",
    "07": "Hospital Especializado",
    "15": "Unidade Mista",
    "20": "Pronto Socorro Geral",
    "21": "Pronto Socorro Especializado",
    "36": "Clínica / Centro de Especialidade",
    "39": "Unidade de Serviço de Apoio de Diagnose e Terapia (SADT)",
    "40": "Unidade de Apoio Diagnose e Terapia (SADT Isolado)",
    "42": "Unidade Móvel de Nível Pré-Hospitalar (Urgência/Emergência)",
    "43": "Farmácia",
    "45": "Unidade de Saúde da Família",
    "50": "Unidade de Vigilância em Saúde",
    "60": "Cooperativa ou Empresa de Cessão de Trabalhadores na Saúde",
    "61": "Centro de Parto Normal Isolado",
    "62": "Hospital / Dia",
    "67": "Laboratório Central de Saúde Pública (LACEN)",
    "69": "Centro de Atenção Hemoterápica e/ou Hematológica",
    "70": "Centro de Atenção Psicossocial",
    "71": "Centro de Apoio à Saúde da Família",
    "72": "Unidade de Atenção à Saúde Indígena",
    "73": "Pronto Atendimento",
    "74": "Polo Academia da Saúde",
    "76": "Central de Regulação Médica das Urgências",
    "80": "Laboratório de Saúde Pública",
    "81": "Central de Regulação do Acesso",
}

_COLUNAS_FLAG = [
    "TEM_CENTRO_CIRURGICO", "TEM_CENTRO_OBSTETRICO", "TEM_CENTRO_NEONATAL",
    "TEM_ATENDIMENTO_HOSPITALAR", "TEM_SERVICO_APOIO", "TEM_ATENDIMENTO_AMBULATORIAL",
]

_ORDEM = [
    "COD_CNES", "RAZAO_SOCIAL", "NOME_FANTASIA", "CNPJ", "CNPJ_MANTENEDORA",
    "HABILITACOES_ONCOLOGIA", "QTD_HABILITACOES_ONCOLOGIA", "TEM_ONCOLOGIA_PEDIATRICA",
    "PORTARIAS", "DATA_PORTARIA_MAIS_ANTIGA",
    "COD_TIPO_UNIDADE", "TIPO_UNIDADE",
    "ESFERA_ADMINISTRATIVA", "COD_ESFERA_ADMINISTRATIVA",
    "COD_NATUREZA_JURIDICA",
    "TOTAL_LEITOS_CNES",
    "TEM_CENTRO_CIRURGICO", "TEM_CENTRO_OBSTETRICO", "TEM_CENTRO_NEONATAL",
    "TEM_ATENDIMENTO_HOSPITALAR", "TEM_ATENDIMENTO_AMBULATORIAL", "TEM_SERVICO_APOIO",
    "COD_MUNICIPIO", "COD_UF", "CEP", "LOGRADOURO", "NUMERO_ENDERECO", "BAIRRO",
    "LATITUDE", "LONGITUDE", "TELEFONE", "EMAIL",
    "ENCONTRADO_NO_CNES",
]


def _flag_sim_nao(valor) -> str | None:
    if valor is None:
        return None
    v = str(valor).strip().upper()
    if v in ("1", "1.0", "S", "SIM", "TRUE", "T"):
        return "Sim"
    if v in ("0", "0.0", "N", "NAO", "NÃO", "FALSE", "F"):
        return "Não"
    return None


def aplicar_transformacoes(df):
    """Renomeia colunas, decodifica tipo de unidade e flags S/N, e ordena por
    importância. Recebe o DataFrame com os nomes técnicos do CNES + as colunas
    agregadas já criadas (HABILITACOES_ONCOLOGIA etc.)."""
    df = df.rename(columns={c: RENOMEAR_CNES.get(c, c.upper()) for c in df.columns})

    if "COD_TIPO_UNIDADE" in df.columns:
        cod = df["COD_TIPO_UNIDADE"].astype(str).str.strip().str.zfill(2)
        df["TIPO_UNIDADE"] = cod.map(TIPO_UNIDADE_CNES).fillna(cod)

    if "TOTAL_LEITOS_CNES" in df.columns:
        df["TOTAL_LEITOS_CNES"] = (
            pd.to_numeric(df["TOTAL_LEITOS_CNES"], errors="coerce").round().astype("Int64")
        )

    for coluna in _COLUNAS_FLAG:
        if coluna in df.columns:
            df[coluna] = df[coluna].map(_flag_sim_nao)

    presentes = [c for c in _ORDEM if c in df.columns]
    resto = [c for c in df.columns if c not in _ORDEM]
    return df[presentes + resto]
