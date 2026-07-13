"""
Códigos de Habilitação em Alta Complexidade em Oncologia do CNES.

Fonte: Portaria SAES/MS nº 688, de 28 de agosto de 2023 (Anexo IV -- 
Classificação e Formulário de Verificação dos Critérios Mínimos para
Habilitação na Alta Complexidade em Oncologia no SUS), que consolida e
atualiza os códigos originalmente definidos nas Portarias SAS/MS
146/2008, 62/2009 e 102/2012.

*** ATENÇÃO -- VALIDAÇÃO PENDENTE ***
O formato exato de armazenamento do código no campo CO_HABILITACAO do
.dbc (com ou sem ponto, com ou sem zeros à esquerda, ex: "1706" vs
"17.06" vs "0001706") ainda não foi confirmado contra um arquivo real
-- confirmar assim que o primeiro HB*.dbc for baixado e processado.
"""

# Cada código de habilitação em oncologia -> se é pediátrico ou não.
# Qualquer código nesta lista significa "tem habilitação oncológica".
HABILITACOES_ONCOLOGIA = {
    "1704": {"descricao": "Serviço Isolado de Radioterapia", "pediatrico": False},
    "1705": {"descricao": "Serviço Isolado de Quimioterapia/Oncologia Clínica", "pediatrico": False},
    "1706": {"descricao": "UNACON - Unidade de Assistência de Alta Complexidade em Oncologia", "pediatrico": False},
    "1707": {"descricao": "UNACON com Serviço de Radioterapia", "pediatrico": False},
    "1708": {"descricao": "UNACON com Serviço de Hematologia", "pediatrico": False},
    "1709": {"descricao": "UNACON com Serviço de Oncologia Pediátrica", "pediatrico": True},
    "1710": {"descricao": "UNACON Exclusiva de Hematologia", "pediatrico": False},
    "1711": {"descricao": "UNACON Exclusiva de Oncologia Pediátrica", "pediatrico": True},
    "1712": {"descricao": "CACON - Centro de Assistência de Alta Complexidade em Oncologia", "pediatrico": False},
    "1713": {"descricao": "CACON com Serviço de Oncologia Pediátrica", "pediatrico": True},
    "1714": {"descricao": "Hospital Geral com Cirurgia Oncológica", "pediatrico": False},
    "1715": {"descricao": "Serviço de Radioterapia de Complexo Hospitalar", "pediatrico": False},
    "1716": {"descricao": "Serviço de Oncologia Clínica de Complexo Hospitalar", "pediatrico": False},
}


def eh_habilitacao_oncologia(codigo: str) -> bool:
    """Aceita o código em qualquer formato razoável (com/sem ponto, com/sem
    zeros à esquerda) e verifica se é uma habilitação de oncologia."""
    normalizado = str(codigo).strip().replace(".", "").lstrip("0")
    normalizado = normalizado.zfill(4)  # garante 4 dígitos (ex: "706" -> "0706"... ajustado abaixo)
    # Códigos reais são 17XX -- normaliza removendo zeros à esquerda e
    # comparando só os 4 dígitos finais relevantes
    candidatos = {str(codigo).strip(), str(codigo).strip().replace(".", "")}
    return bool(candidatos & set(HABILITACOES_ONCOLOGIA.keys())) or normalizado in HABILITACOES_ONCOLOGIA


def eh_pediatrico(codigo: str) -> bool:
    info = HABILITACOES_ONCOLOGIA.get(str(codigo).strip().replace(".", ""))
    return info["pediatrico"] if info else False