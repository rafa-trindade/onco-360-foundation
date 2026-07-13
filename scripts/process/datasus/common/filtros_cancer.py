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

COLUNA_CAUSABAS_CID9_CANDIDATAS = ["CAUSABAS", "CAUSAMORT", "CAUSAM", "CAUSABAS_O"]


def filtro_cancer_cid10(registro: dict) -> bool:
    """CAUSABAS entre C00 e C97 (neoplasia maligna). Coluna já confirmada
    (mesmo layout usado no consolidado e no preliminar do SIM CID-10)."""
    valor = str(registro.get("CAUSABAS", "")).strip().upper()
    if len(valor) < 3 or valor[0] != "C":
        return False
    try:
        numero = int(valor[1:3])
    except ValueError:
        return False
    return numero <= 97


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