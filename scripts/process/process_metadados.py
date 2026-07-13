"""
Gera data/raw/raw_onco360_metadados.csv -- manifesto de todos os
arquivos publicados no dataset, cruzando o registro central
(scripts/config/fontes.py) com o que REALMENTE existe em data/raw/.

Não confia cegamente no registro: se um arquivo esperado não existir,
aparece como tal no manifesto (não é omitido). Arquivos que existem em
data/raw/ mas não estão em nenhuma Fonte do registro (ex: o resumo
anual do SIM, que é subproduto de 3 fontes diferentes) também entram,
com descrição genérica -- pra nunca ficar um arquivo "invisível" no
manifesto.
"""
import datetime
import pandas as pd
import pyarrow.parquet as pq

from scripts.common.paths import RAW_DIR
from scripts.config.fontes import FONTES

ARQUIVO_SAIDA = RAW_DIR / "raw_onco360_metadados.csv"


def _contar_registros(caminho) -> int | None:
    try:
        if caminho.suffix == ".parquet":
            return pq.ParquetFile(caminho).metadata.num_rows
        if caminho.suffix == ".csv":
            with open(caminho, "r", encoding="utf-8-sig", errors="replace") as f:
                return sum(1 for _ in f) - 1  # desconta o cabeçalho
    except Exception as e:
        print(f"[AVISO] Não foi possível contar registros de {caminho.name}: {e}")
    return None


def _info_arquivo(caminho, fonte_id, fonte_nome, descricao, tipo, url_origem, nota) -> dict:
    existe = caminho.exists()
    return {
        "arquivo": caminho.name,
        "fonte_id": fonte_id,
        "fonte_nome": fonte_nome,
        "descricao": descricao,
        "tipo": tipo,
        "url_origem": url_origem,
        "existe": existe,
        "num_registros": _contar_registros(caminho) if existe else None,
        "tamanho_bytes": caminho.stat().st_size if existe else None,
        "data_modificacao": (
            datetime.datetime.fromtimestamp(caminho.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if existe else None
        ),
        "nota": nota,
    }


def main():
    linhas = []
    arquivos_cobertos_pelo_registro = set()

    for fonte in FONTES:
        for nome_arquivo in fonte.arquivos_saida:
            caminho = RAW_DIR / nome_arquivo
            arquivos_cobertos_pelo_registro.add(caminho.name)
            linhas.append(_info_arquivo(
                caminho, fonte.id, fonte.nome, fonte.descricao, fonte.tipo, fonte.url_origem, fonte.nota
            ))

    # Arquivos que existem em data/raw/ mas não estão em nenhuma Fonte
    # do registro (ex: resumos/subprodutos derivados de mais de uma fonte)
    if RAW_DIR.exists():
        for caminho in sorted(RAW_DIR.glob("*")):
            if not caminho.is_file():
                continue
            if caminho.name in arquivos_cobertos_pelo_registro or caminho.name == ARQUIVO_SAIDA.name:
                continue
            linhas.append(_info_arquivo(
                caminho, fonte_id="(derivado)", fonte_nome="Arquivo derivado/subproduto",
                descricao="Não mapeado 1:1 a uma única Fonte do registro (ex: resumo agregando múltiplas fontes).",
                tipo="derivado", url_origem="", nota="",
            ))

    df = pd.DataFrame(linhas)

    faltando = df[~df["existe"]]
    if not faltando.empty:
        print(f"[AVISO] {len(faltando)} arquivo(s) esperado(s) pelo registro mas NÃO encontrado(s) em data/raw/:")
        for _, r in faltando.iterrows():
            print(f"  - {r['arquivo']} (fonte: {r['fonte_id']})")

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print(f"✔ Metadados salvos em {ARQUIVO_SAIDA} ({len(df)} linha(s), {len(faltando)} faltando).")

if __name__ == "__main__":
    main()