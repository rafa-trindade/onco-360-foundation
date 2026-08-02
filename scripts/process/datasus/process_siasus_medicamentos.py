"""SIASUS - APAC de Medicamentos oncológicos (process).

A base de medicamentos de alto custo (AM) é genérica; este recorte mantém
apenas os registros relacionados à oncologia (Visão ONCO360):
- C00-C97 (Neoplasias Malignas)
- D00-D09 (In situ) e D37-D48 (Comportamento incerto)
- B21 (Doença pelo HIV resultando em neoplasia)
- Códigos Z de histórico, seguimento e tratamento (Z51, Z08, Z85)
* Exclui estritamente tumores benignos (D10-D36).
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.siasus.transformar_siasus import montar_query_medicamentos

PASTA_BUCKET = "datasus_siasus"
NOME_ARQUIVO_FINAL = "siasus_medicamentos_oncologicos.parquet"
DBC_DIR = LANDING_DIR / "dbc_siasus_medicamentos"

COLUNA_CID_CANDIDATAS = ["AP_CIDPRI", "AP_CIDSEC", "AP_CIDCAS"]


def _eh_neoplasia(cid: str) -> bool:
    """
    Filtro ONCO360: Captura Cânceres (Malignos, In situ, Incertos) e 
    histórico/tratamento oncológico. Exclui tumores benignos (D10-D36).
    """
    if not cid:
        return False
    c = str(cid).strip().upper()
    if not c:
        return False
    
    letra = c[0]
    
    # Neoplasias Malignas (Capítulo II: C00 até C97)
    if letra == "C":
        return True
        
    # Neoplasias In Situ (D00-D09) e Comportamento Incerto (D37-D48)
    if letra == "D" and len(c) >= 3 and c[1:3].isdigit():
        num = int(c[1:3])
        if (0 <= num <= 9) or (37 <= num <= 48):
            return True

    # HIV resultando em neoplasia maligna
    if c.startswith("B21"):
        return True

    # Códigos Z de Oncologia (Quimio, Rádio, Seguimento, Histórico)
    if c.startswith("Z51") or c.startswith("Z08") or c.startswith("Z85"):
        return True

    return False


def _filtro_oncologico(df):
    coluna = next((c for c in COLUNA_CID_CANDIDATAS if c in df.columns), None)
    if coluna is None:
        return df.iloc[0:0]
    return df[df[coluna].apply(_eh_neoplasia)]


def main() -> int:
    return processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        filtro_chunk=_filtro_oncologico,
        query_transformacao=montar_query_medicamentos,
    )


if __name__ == "__main__":
    sys.exit(main())