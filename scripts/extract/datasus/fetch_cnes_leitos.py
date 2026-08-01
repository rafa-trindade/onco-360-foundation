"""Extração FTP CNES: Leitos (Retrato atual).

Regra de negócio: Obtém a contagem real de leitos (o campo NULEITOS da base de Habilitações não é confiável/frequentemente zerado).
Otimização de rede: O diretório FTP particiona por UF/Mês com histórico longo. A extração identifica dinamicamente a competência mais recente e restringe o download a este corte transversal (27 UFs), descartando a série histórica.
"""
import re
import socket
from scripts.extract.datasus.common.base_ftp import FTPPasvFix, FTP_HOST, baixar_arquivo, ensure_output_dir
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/CNES/200508_/Dados/LT"
OUTPUT_DIR = str(LANDING_DIR / "dbc_cnes_leitos")

PADRAO_ARQUIVO = re.compile(r"^LT([A-Z]{2})(\d{4})\.dbc$", re.IGNORECASE)


def listar_arquivos() -> list[str]:
    ip_v4 = socket.gethostbyname(FTP_HOST)
    with FTPPasvFix() as ftp:
        ftp.connect(ip_v4, 21, timeout=30)
        ftp.login()
        ftp.set_pasv(True)
        ftp.cwd(FTP_DIR)
        arquivos = ftp.nlst()
    return arquivos


def main():
    print(f"Listando arquivos em {FTP_DIR} (pode demorar, são milhares de arquivos)...")
    arquivos = listar_arquivos()
    print(f"Total listado: {len(arquivos)} arquivo(s).")

    candidatos = []
    for nome in arquivos:
        m = PADRAO_ARQUIVO.match(nome)
        if m:
            uf, competencia = m.group(1).upper(), m.group(2)
            candidatos.append((uf, competencia, nome))

    if not candidatos:
        print("[ERRO] Nenhum arquivo no padrão LT{UF}{AAMM}.dbc encontrado -- confira se o padrão de nome mudou.")
        exit(exit_codes.ERRO)

    competencia_mais_recente = max(c[1] for c in candidatos)
    print(f"Competência mais recente encontrada: {competencia_mais_recente}")

    alvo = sorted(nome for uf, comp, nome in candidatos if comp == competencia_mais_recente)
    print(f"{len(alvo)} arquivo(s) da competência mais recente (esperado por volta de 27, uma por UF).")

    ensure_output_dir(OUTPUT_DIR)
    sucesso_geral = True
    houve_novidade = False
    for nome in alvo:
        sucesso, novidade = baixar_arquivo(FTP_DIR, nome, OUTPUT_DIR)
        sucesso_geral = sucesso_geral and sucesso
        houve_novidade = houve_novidade or novidade

    if not sucesso_geral:
        exit(exit_codes.ERRO)
    elif not houve_novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)


if __name__ == "__main__":
    main()