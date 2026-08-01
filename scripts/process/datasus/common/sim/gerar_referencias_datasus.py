"""Gera os parquets de referência do DATASUS (código -> descrição) a partir
das tabelas DBF oficiais, para uso na descrição de códigos do SIM.

Insumos (DBFs oficiais, extraídos dos pacotes Docs_Tabs do DATASUS):
  CID10.DBF, CID9.DBF (causa), TABOCUP.DBF (ocupação/CBO),
  TABPAIS.DBF (país), TABUF.DBF (UF).

Saída: parquets em MANUAL_DATASUS_REF_DIR, cada um com colunas CODIGO e
DESCRICAO (UF também com SIGLA_UF).

Uso:
    python -m scripts.process.datasus.common.gerar_referencias_datasus <dir_dbfs>
"""
import sys
from pathlib import Path

import pandas as pd
from dbfread import DBF

from scripts.common.paths import MANUAL_DATASUS_REF_DIR


def _ler_dbf(caminho: Path) -> pd.DataFrame:
    return pd.DataFrame(iter(DBF(str(caminho), encoding="latin1")))


def _gerar_ocupacao(dir_dbfs: Path) -> None:
    """Gera ref_ocupacao combinando o CBO antigo (TABOCUP.DBF, 3 dígitos) com
    o CBO-2002 (cbo2002.csv, 5-6 dígitos), tudo num formato de código único
    para JOIN direto. O SIM usa CBO antigo nos anos mais antigos (código de 3
    dígitos gravado como NNN00) e CBO-2002 nos recentes. O CBO-2002 tem
    prioridade quando há sobreposição. O CSV cbo2002.csv (MTE/SEADE) é
    opcional: se ausente, gera só com o CBO antigo."""
    import csv

    linhas = []

    csv_cbo2002 = dir_dbfs / "cbo2002.csv"
    if csv_cbo2002.exists():
        with open(csv_cbo2002, encoding="latin1") as f:
            leitor = csv.reader(f, delimiter=";")
            next(leitor)
            for linha in leitor:
                codigo, descricao = linha[5].strip(), linha[7].strip()
                if codigo and descricao:
                    linhas.append({"CODIGO": codigo, "DESCRICAO": descricao, "_FONTE": "1_CBO2002"})

    ocup_antigo = _ler_dbf(dir_dbfs / "TABOCUP.DBF")[["CODIGO", "DESCRICAO"]]
    for _, linha in ocup_antigo.iterrows():
        cod3 = str(linha["CODIGO"]).zfill(3)
        descricao = str(linha["DESCRICAO"]).strip()
        # CBO antigo aparece em dois formatos no SIM: 3 dígitos no CID-9
        # (OCUPACAO C(03)) e 5 dígitos NNN00 no CID-10 antigo.
        linhas.append({"CODIGO": cod3, "DESCRICAO": descricao, "_FONTE": "2_ANTIGO"})
        linhas.append({"CODIGO": cod3 + "00", "DESCRICAO": descricao, "_FONTE": "2_ANTIGO"})

    df = (pd.DataFrame(linhas)
          .sort_values("_FONTE")
          .drop_duplicates("CODIGO", keep="first")[["CODIGO", "DESCRICAO"]])
    df.to_parquet(MANUAL_DATASUS_REF_DIR / "ref_ocupacao.parquet", index=False)


def gerar(dir_dbfs: Path) -> None:
    MANUAL_DATASUS_REF_DIR.mkdir(parents=True, exist_ok=True)

    cid10 = _ler_dbf(dir_dbfs / "CID10.DBF")
    cid10["DESCRICAO"] = cid10["DESCR"].str.replace(r"^\S+\s+", "", regex=True).str.strip()
    (cid10[["CID10", "DESCRICAO"]].rename(columns={"CID10": "CODIGO"})
     .drop_duplicates("CODIGO")
     .to_parquet(MANUAL_DATASUS_REF_DIR / "ref_causa_cid10.parquet", index=False))

    cid9 = _ler_dbf(dir_dbfs / "CID9.DBF")
    cid9["DESCRICAO"] = cid9["DESCRICAO"].str.replace(r"^\d+\s+", "", regex=True).str.strip()
    (cid9[["CAUSAS", "DESCRICAO"]].rename(columns={"CAUSAS": "CODIGO"})
     .drop_duplicates("CODIGO")
     .to_parquet(MANUAL_DATASUS_REF_DIR / "ref_causa_cid9.parquet", index=False))

    _gerar_ocupacao(dir_dbfs)

    pais = _ler_dbf(dir_dbfs / "TABPAIS.DBF")[["CODIGO", "DESCRICAO"]].drop_duplicates("CODIGO")
    pais["CODIGO"] = pais["CODIGO"].str.zfill(3)
    pais["DESCRICAO"] = pais["DESCRICAO"].str.strip()
    pais.to_parquet(MANUAL_DATASUS_REF_DIR / "ref_pais.parquet", index=False)

    uf = _ler_dbf(dir_dbfs / "TABUF.DBF")[["CODIGO", "DESCRICAO", "SIGLA_UF"]].drop_duplicates("CODIGO")
    uf["DESCRICAO"] = uf["DESCRICAO"].str.strip()
    uf.to_parquet(MANUAL_DATASUS_REF_DIR / "ref_uf.parquet", index=False)

    print(f"Referências geradas em {MANUAL_DATASUS_REF_DIR}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m scripts.process.datasus.common.gerar_referencias_datasus <dir_dbfs>")
        sys.exit(1)
    gerar(Path(sys.argv[1]))
