#!/usr/bin/env python3
"""
Orquestrador do pipeline onco-360-foundation.

Uso:
    python run_all.py                  # roda tudo: fontes -> metadados -> bucket -> Kaggle (se houver novidade)
    python run_all.py --only cnes_estabelecimentos   # roda só uma fonte (ver scripts/config/fontes.py)
    python run_all.py --process-only    # pula o extract de todas as fontes automatizadas
    python run_all.py --force-load      # publica mesmo sem novidade detectada (ex: após atualizar fonte manual/estática)
    python run_all.py --no-load         # nunca publica (bucket/Kaggle), só roda extract+process+metadados

Cada Fonte em scripts/config/fontes.py tem um `tipo`:
    "pipeline"        -- extract + process automatizados
    "pipeline_manual" -- só process automatizado (extract é manual, ex: PNS)
    "estatico"        -- sem script nenhum (arquivo trazido manualmente pro data/raw/, ex: INCA)
Fontes sem extract_modules/process_modules (estático, ou pendente como o
Portal da Transparência) são identificadas e puladas com uma mensagem
clara, não tratadas como erro.

Ao final, sempre roda scripts/process/process_metadados.py (reflete o
estado atual de data/raw/, independente de ter havido novidade ou não).

Publicação (bucket + Kaggle): o bucket SEMPRE roda (é idempotente --
scripts/load/load_to_bucket.py já compara cada arquivo contra o que já
está PUBLICADO no bucket, não contra o que foi baixado nesta execução
-- importante porque um arquivo pode existir localmente sem nunca ter
sido publicado, ex: rodou o extract manualmente antes do run_all.py).
O Kaggle só roda se o bucket realmente subiu algo novo (ou com
--force-load) -- evita criar uma versão nova no Kaggle à toa.
"""
import argparse
import runpy
import sys
import traceback

from scripts.config.fontes import FONTES, Fonte
from scripts.common import exit_codes

SUCESSO, SEM_NOVIDADE, ERRO = "sucesso", "sem_novidade", "erro"


def _run_module(module_path: str) -> str:
    """
    Executa um módulo exatamente como `python -m module_path` executaria
    -- via runpy, com run_name="__main__". Funciona com ou sem o script
    expor uma função main().

    Retorna SUCESSO, SEM_NOVIDADE ou ERRO -- lido do exit code do
    script, se ele usar scripts.common.exit_codes; senão assume SUCESSO.
    """
    print(f"  -> {module_path}")
    try:
        runpy.run_module(module_path, run_name="__main__")
        return SUCESSO
    except SystemExit as e:
        codigo = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        if codigo == exit_codes.SUCESSO:
            return SUCESSO
        elif codigo == exit_codes.SEM_NOVIDADE:
            return SEM_NOVIDADE
        else:
            print(f"  [ERRO] {module_path} terminou com exit code {codigo}")
            return ERRO
    except Exception:
        print(f"  [ERRO] Falha em {module_path}:")
        traceback.print_exc()
        return ERRO


def rodar_fonte(fonte: Fonte, pular_extract: bool) -> tuple[bool, bool]:
    """Retorna (ok, teve_novidade_confiavel)."""
    print(f"\n{'=' * 70}\n{fonte.nome} ({fonte.id}) [{fonte.tipo}]\n{'=' * 70}")

    if fonte.nota:
        print(f"  Nota: {fonte.nota}")

    if not fonte.extract_modules and not fonte.process_modules:
        print(f"  [SEM SCRIPT] Fonte {fonte.tipo} -- nada a rodar aqui "
              f"(arquivo já deve estar em data/raw/ manualmente, ou fonte ainda não construída).")
        print(f"OK: {fonte.id}")
        return True, False

    houve_erro = False
    houve_novidade = True  # default: roda o process (extract pulado, ou fonte manual/estática)
    novidade_confiavel = False

    if fonte.extract_modules and not pular_extract:
        resultados = [_run_module(m) for m in fonte.extract_modules]
        houve_erro = ERRO in resultados
        houve_novidade = any(r == SUCESSO for r in resultados)
        novidade_confiavel = houve_novidade
    elif not fonte.extract_modules and fonte.process_modules:
        print(f"  [MANUAL] Sem extract automatizado -- assumindo que o dado bruto já foi atualizado manualmente.")

    if houve_erro:
        print(f"  [PULADO] process não roda -- extract falhou.")
    elif not houve_novidade and fonte.extract_modules and not pular_extract:
        print(f"  [PULADO] process não roda -- nenhum dado novo desde a última execução.")
    else:
        for m in fonte.process_modules:
            if _run_module(m) == ERRO:
                houve_erro = True

    ok = not houve_erro
    print(f"{'OK' if ok else 'COM FALHAS'}: {fonte.id}")
    return ok, novidade_confiavel


def main():
    parser = argparse.ArgumentParser(description="Orquestrador do pipeline onco-360-foundation")
    parser.add_argument("--only", help="Roda só a fonte com este id (ver scripts/config/fontes.py)")
    parser.add_argument("--process-only", action="store_true", help="Pula o extract de todas as fontes automatizadas")
    parser.add_argument("--force-load", action="store_true",
                         help="Publica (bucket/Kaggle) mesmo sem novidade detectada")
    parser.add_argument("--no-load", action="store_true", help="Nunca publica (bucket/Kaggle)")
    args = parser.parse_args()

    alvo = [f for f in FONTES if f.id == args.only] if args.only else FONTES
    if args.only and not alvo:
        print(f"Fonte '{args.only}' não encontrada. Fontes disponíveis: {[f.id for f in FONTES]}")
        sys.exit(1)

    resultados = {f.id: rodar_fonte(f, pular_extract=args.process_only) for f in alvo}

    print(f"\n{'=' * 70}\nResumo das fontes\n{'=' * 70}")
    for id_fonte, (ok, _) in resultados.items():
        print(f"  {'✔' if ok else '✘'} {id_fonte}")

    sucesso_geral = all(ok for ok, _ in resultados.values())

    # Metadados: sempre roda no final, reflete o estado atual de data/raw/
    print(f"\n{'=' * 70}\nMetadados\n{'=' * 70}")
    if _run_module("scripts.process.process_metadados") == ERRO:
        sucesso_geral = False

    if args.no_load:
        print("\n[LOAD] Pulado (--no-load).")
    elif not sucesso_geral:
        print("\n[LOAD] Pulado -- pelo menos uma fonte falhou, não publica dado possivelmente incompleto.")
    else:
        # Bucket: SEMPRE roda (não depende de "houve novidade nesta
        # execução do extract") -- load_to_bucket.py já compara contra o
        # que está PUBLICADO no bucket, não contra o que foi baixado
        # agora. Isso importa porque um arquivo pode já existir
        # localmente (de uma execução manual anterior, ou de --process-only)
        # sem nunca ter sido publicado -- gatear pela novidade do
        # extract perderia esse arquivo pra sempre.
        print(f"\n{'=' * 70}\nBucket\n{'=' * 70}")
        resultado_bucket = _run_module("scripts.load.load_to_bucket")
        if resultado_bucket == ERRO:
            sucesso_geral = False

        houve_upload_bucket = resultado_bucket == SUCESSO

        if houve_upload_bucket or args.force_load:
            print(f"\n{'=' * 70}\nKaggle\n{'=' * 70}")
            if _run_module("scripts.load.load_to_kaggle") == ERRO:
                sucesso_geral = False
        else:
            print("\n[KAGGLE] Pulado -- nada novo foi enviado ao bucket nesta execução. "
                  "Use --force-load pra publicar uma versão nova mesmo assim.")

    if not sucesso_geral:
        sys.exit(1)


if __name__ == "__main__":
    main()