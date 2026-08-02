"""
Filtros de "óbito por câncer" (neoplasia maligna), compartilhados entre
process_sim_obitos_cancer_cid9.py, _cid10.py e _prelim.py.

Faixas de CAUSABAS confirmadas linha a linha contra as tabelas oficiais
do DATASUS (CIDCAP.DBF / CIDCAP10.DBF e CID9.DBF / CID10.DBF, capítulo
II - Neoplasias):

  CID-9  (1979-1995): CAUSABAS entre 140 e 208 (neoplasmas malignos)
  CID-10 (1996-atual, inclui PRELIM): CAUSABAS entre C00 e C97 (neoplasias malignas)

Faixas adjacentes foram deliberadamente EXCLUÍDAS por não serem "câncer"
no sentido clínico/epidemiológico padrão (mesma definição usada por
INCA e OMS/IARC para estatística de mortalidade por câncer):

  CID-10  D00-D09  Carcinoma in situ            -- excluído
  CID-10  D10-D36  Neoplasias benignas          -- excluído
  CID-10  D37-D48  Comportamento incerto/desc.  -- excluído
  CID-9   210-229  Neoplasmas benignos          -- excluído
  CID-9   230-234  Carcinoma in situ            -- excluído
  CID-9   235-239  Incerto/não especificado     -- excluído
"""

import re

COLUNA_CAUSABAS_CID9_CANDIDATAS = ["CAUSABAS", "CAUSAMORT", "CAUSAM", "CAUSABAS_O"]

_PADRAO_CID10 = re.compile(r"^C(\d{2})")


def filtro_cancer_cid10(registro: dict) -> bool:
    """CAUSABAS entre C00 e C97 (neoplasia maligna). Exige C seguido de
    exatamente dois dígitos, evitando códigos malformados (C9, CX, CA)."""
    valor = str(registro.get("CAUSABAS", "")).strip().upper()
    m = _PADRAO_CID10.match(valor)
    if not m:
        return False
    return int(m.group(1)) <= 97


def criar_filtro_cancer_cid9():
    """
    Cria a função de filtro pro CID-9. Detecta a coluna de causa básica
    só no primeiro registro (evita refazer a busca a cada linha) e
    avisa uma única vez no log qual coluna encontrou.

    *** ATENÇÃO -- VALIDAÇÃO PENDENTE ***
    O nome exato da coluna de causa básica na era CID-9 do SIM ainda não
    foi confirmado contra um arquivo real. Confira a linha de log
    "[INFO] Usando '...' como coluna de causa básica no CID-9" antes de
    considerar o resultado confiável.
    """
    estado = {"coluna": None, "detectada": False}

    def filtro(registro: dict) -> bool:
        if not estado["detectada"]:
            estado["coluna"] = next((c for c in COLUNA_CAUSABAS_CID9_CANDIDATAS if c in registro), None)
            estado["detectada"] = True
            if estado["coluna"] is None:
                print(f"[AVISO] Nenhuma coluna candidata a CAUSABAS encontrada no CID-9. "
                      f"Colunas disponíveis: {list(registro.keys())}")
                print("        Ajuste COLUNA_CAUSABAS_CID9_CANDIDATAS neste arquivo com o nome correto.")
            else:
                print(f"[INFO] Usando '{estado['coluna']}' como coluna de causa básica no CID-9.")

        if estado["coluna"] is None:
            return False

        valor = str(registro.get(estado["coluna"], "")).strip()
        try:
            numero = int(valor[:3])
        except ValueError:
            return False
        return 140 <= numero <= 208

    return filtro

# --- Filtros no formato chunk (DataFrame -> DataFrame) ---
# Usados pelo modelo de processamento streaming (base_process_dbc_stream),
# que filtra por bloco de linhas em memória antes de persistir, em vez de
# registro a registro.

def filtro_chunk_cancer_cid10(df):
    """Mantém só linhas com CAUSABAS de neoplasia maligna (C00-C97).
    Exige C seguido de exatamente dois dígitos (^C\\d{2}), evitando
    códigos malformados como C9, CX ou CA."""
    if "CAUSABAS" not in df.columns:
        return df.iloc[0:0]
    causa = df["CAUSABAS"].astype(str).str.strip().str.upper()
    
    # Captura a letra (C ou D ou B) e os 2 números
    # Para incluir C00-C97, D00-D48 e B21
    m = causa.str.extract(r"^([CDB])(\d{2})", expand=True)
    valido = m[0].notna()
    
    letra = m[0].where(valido, "X")
    numero = m[1].where(valido, "99").astype(int)
    
    mask_c = (letra == 'C') & (numero <= 97)
    mask_d = (letra == 'D') & (numero <= 48)
    mask_b = (letra == 'B') & (numero == 21)
    
    return df[mask_c | mask_d | mask_b]


def criar_filtro_chunk_cancer_cid9():
    """Cria o filtro de chunk pro CID-9 (CAUSABAS 140-208), detectando a
    coluna de causa básica no primeiro chunk que a contiver e avisando
    uma única vez qual foi usada."""
    estado = {"coluna": None, "detectada": False}

    def filtro(df):
        if not estado["detectada"]:
            estado["coluna"] = next((c for c in COLUNA_CAUSABAS_CID9_CANDIDATAS if c in df.columns), None)
            estado["detectada"] = True
            if estado["coluna"] is None:
                print(f"[AVISO] Nenhuma coluna candidata a CAUSABAS encontrada no CID-9. "
                      f"Colunas disponíveis: {list(df.columns)}")
            else:
                print(f"[INFO] Usando '{estado['coluna']}' como coluna de causa básica no CID-9.")

        if estado["coluna"] is None or estado["coluna"] not in df.columns:
            return df.iloc[0:0]

        prefixo = df[estado["coluna"]].astype(str).str.strip().str.extract(r"^(\d{3})", expand=False)
        valido = prefixo.notna()
        numero = prefixo.where(valido, "0").astype(int)
        return df[valido & (numero >= 140) & (numero <= 208)]

    return filtro
