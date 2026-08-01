"""Decodificação dos campos categóricos do SIM para texto legível.

Substitui o código pelo rótulo direto na coluna (decisão de projeto: a base
final não deve exigir dicionário para leitura). Os domínios cobrem a união
das versões do SIM (campos como ESTCIV e ESC mudaram de dicionário ao longo
do tempo); códigos fora do domínio conhecido caem em 'Ignorado'.

Domínios conferidos contra as estruturas oficiais do DATASUS: Estrutura do
SIM para CD-ROM (até 2005 e 2006), edição 12/2019 e edição 07/2025. Onde as
versões divergem no nome da coluna (ESTCIV vs ESTCIVIL), ambas as chaves são
mapeadas -- só a presente no arquivo é decodificada, sem conflito.

IDADE tem tratamento à parte (idade_anos): o campo cru do SIM não é a idade
em anos, e sim unidade+valor (ver montar_expr_idade_anos). Apesar de o texto
da edição 2025 resumir a tabela de unidades de forma imprecisa, os exemplos
oficiais (410=10 anos, 505=105 anos) confirmam unidade 4=anos e 5=anos+100
em todas as edições.

Campos de sistema (ORIGEM, STCODIFICA, CODIFICADO) não são decodificados de
propósito: são metadados técnicos sem valor analítico.

A decodificação é aplicada como transformação SQL no DuckDB durante a
publicação (memory-safe, sem reler o arquivo).
"""

# Cada entrada: coluna_original -> {codigo: rótulo}. O rótulo substitui o
# código na mesma coluna. Valores ausentes do dicionário viram 'Ignorado'.
DOMINIOS: dict[str, dict[str, str]] = {
    "TIPOBITO": {"1": "Fetal", "2": "Não fetal"},
    "SEXO": {"0": "Ignorado", "1": "Masculino", "2": "Feminino", "M": "Masculino", "F": "Feminino", "I": "Ignorado"},
    "RACACOR": {"1": "Branca", "2": "Preta", "3": "Amarela", "4": "Parda", "5": "Indígena"},
    "ESTCIV": {"1": "Solteiro", "2": "Casado", "3": "Viúvo",
               "4": "Separado judicialmente/divorciado", "5": "União estável"},
    "ESTCIVIL": {"1": "Solteiro", "2": "Casado", "3": "Viúvo",
                 "4": "Separado judicialmente/divorciado", "5": "União estável"},
    "ESC": {"1": "Nenhuma", "2": "1 a 3 anos", "3": "4 a 7 anos",
            "4": "8 a 11 anos", "5": "12 e mais", "8": "9 a 11 anos"},
    "ESCMAE": {"1": "Nenhuma", "2": "1 a 3 anos", "3": "4 a 7 anos",
               "4": "8 a 11 anos", "5": "12 e mais"},
    "ESC2010": {"0": "Sem escolaridade", "1": "Fundamental I (1ª a 4ª série)",
                "2": "Fundamental II (5ª a 8ª série)", "3": "Médio (antigo 2º grau)",
                "4": "Superior incompleto", "5": "Superior completo"},
    "ESCMAE2010": {"0": "Sem escolaridade", "1": "Fundamental I (1ª a 4ª série)",
                   "2": "Fundamental II (5ª a 8ª série)", "3": "Médio (antigo 2º grau)",
                   "4": "Superior incompleto", "5": "Superior completo"},
    "ESCFALAGR1": {"00": "Sem escolaridade", "01": "Fundamental I incompleto",
                   "02": "Fundamental I completo", "03": "Fundamental II incompleto",
                   "04": "Fundamental II completo", "05": "Ensino Médio incompleto",
                   "06": "Ensino Médio completo", "07": "Superior incompleto",
                   "08": "Superior completo", "10": "Fundamental I incompleto ou inespecífico",
                   "11": "Fundamental II incompleto ou inespecífico",
                   "12": "Ensino Médio incompleto ou inespecífico"},
    "ESCMAEAGR1": {"00": "Sem escolaridade", "01": "Fundamental I incompleto",
                   "02": "Fundamental I completo", "03": "Fundamental II incompleto",
                   "04": "Fundamental II completo", "05": "Ensino Médio incompleto",
                   "06": "Ensino Médio completo", "07": "Superior incompleto",
                   "08": "Superior completo", "10": "Fundamental I incompleto ou inespecífico",
                   "11": "Fundamental II incompleto ou inespecífico",
                   "12": "Ensino Médio incompleto ou inespecífico"},
    "LOCOCOR": {"1": "Hospital", "2": "Outro estabelecimento de saúde",
                "3": "Domicílio", "4": "Via pública", "5": "Outros",
                "6": "Aldeia indígena"},
    "ASSISTMED": {"1": "Com assistência", "2": "Sem assistência"},
    "ATESTANTE": {"1": "Sim, atendeu ao falecido", "2": "Substituto",
                  "3": "Instituto Médico Legal", "4": "Serviço de Verificação de Óbitos",
                  "5": "Outros"},
    "EXAME": {"1": "Sim", "2": "Não"},
    "CIRURGIA": {"1": "Sim", "2": "Não"},
    "NECROPSIA": {"1": "Sim", "2": "Não"},
    "ACIDTRAB": {"1": "Sim", "2": "Não"},
    "OBITOGRAV": {"1": "Sim", "2": "Não"},
    "OBITOPUERP": {"1": "Sim, até 42 dias após o parto",
                   "2": "Sim, de 43 dias a 1 ano", "3": "Não"},
    "GRAVIDEZ": {"1": "Única", "2": "Dupla", "3": "Tripla e mais"},
    "GESTACAO": {"1": "Menos de 22 semanas", "2": "22 a 27 semanas",
                 "3": "28 a 31 semanas", "4": "32 a 36 semanas",
                 "5": "37 a 41 semanas", "6": "42 semanas e mais"},
    "PARTO": {"1": "Vaginal", "2": "Cesáreo"},
    "OBITOPARTO": {"1": "Antes", "2": "Durante", "3": "Depois"},
    "TPMORTEOCO": {"1": "Na gravidez", "2": "No parto", "3": "No aborto",
                   "4": "Até 42 dias após o parto",
                   "5": "De 43 dias a 1 ano após o parto",
                   "8": "Não ocorreu nestes períodos"},
    "CIRCOBITO": {"1": "Acidente", "2": "Suicídio", "3": "Homicídio", "4": "Outros"},
    "FONTE": {"1": "Ocorrência policial", "2": "Hospital", "3": "Família", "4": "Outra"},
    "FONTEINV": {"1": "Comitê de Morte Materna e/ou Infantil",
                 "2": "Visita domiciliar/Entrevista família",
                 "3": "Estabelecimento de Saúde/Prontuário",
                 "4": "Relacionamento com outros bancos de dados",
                 "5": "Serviço de Verificação de Óbitos", "6": "Instituto Médico Legal",
                 "7": "Outra fonte", "8": "Múltiplas fontes"},
    "TPPOS": {"1": "Sim", "2": "Não"},
    "ALTCAUSA": {"1": "Sim", "2": "Não"},
    "STDOEPIDEM": {"1": "Sim", "0": "Não"},
    "STDONOVA": {"1": "Sim", "0": "Não"},
    "TPNIVELINV": {"E": "Estadual", "R": "Regional", "M": "Municipal"},
    "MORTEPARTO": {"1": "Antes", "2": "Durante", "3": "Após"},
    "TPRESGINFO": {"01": "Não acrescentou nem corrigiu informação",
                   "02": "Permitiu resgate de novas informações",
                   "03": "Permitiu correção de causa informada"},
    "TPOBITOCOR": {"1": "Durante a gestação", "2": "Durante o abortamento",
                   "3": "Após o abortamento", "4": "No parto ou até 1h após",
                   "5": "No puerpério (até 42 dias)", "6": "Entre 43 dias e 1 ano",
                   "7": "Investigação não identificou o momento",
                   "8": "Mais de um ano após o parto",
                   "9": "Não ocorreu nas circunstâncias anteriores"},
}

ROTULO_IGNORADO = "Ignorado"


def _sql_literal(texto: str) -> str:
    return "'" + texto.replace("'", "''") + "'"


def montar_expr_decodificacao(coluna: str, dominio: dict[str, str]) -> str:
    """CASE WHEN que troca o código pelo rótulo na própria coluna; qualquer
    valor fora do domínio (inclui nulo/vazio) vira 'Ignorado'."""
    ramos = " ".join(
        f"WHEN TRIM(CAST({coluna} AS VARCHAR)) = {_sql_literal(codigo)} THEN {_sql_literal(rotulo)}"
        for codigo, rotulo in dominio.items()
    )
    return f"CASE {ramos} ELSE {_sql_literal(ROTULO_IGNORADO)} END AS {coluna}"


def montar_expr_idade_anos() -> str:
    """Converte o campo IDADE do SIM (unidade+valor) em idade_anos numérica.

    Codificação DATASUS: o 1º dígito é a unidade
    (0 minutos, 1 horas, 2 dias, 3 meses, 4 anos, 5 anos>=100), os demais o
    valor. Só a partir de 4 (anos) a idade em anos é > 0; abaixo disso é
    fração de ano, arredondada para 0. Idades resultantes fora de [0, 120]
    são tratadas como dado inválido da fonte e viram NULL (ex: unidade 5 com
    subcampo alto gerando '190').
    """
    corpo = "TRY_CAST(SUBSTR(TRIM(CAST(IDADE AS VARCHAR)), 2) AS INTEGER)"
    unidade = "SUBSTR(TRIM(CAST(IDADE AS VARCHAR)), 1, 1)"
    bruto = (
        "CASE "
        f"WHEN {unidade} = '4' THEN {corpo} "
        f"WHEN {unidade} = '5' THEN {corpo} + 100 "
        f"WHEN {unidade} IN ('0','1','2','3') THEN 0 "
        "ELSE NULL END"
    )
    return f"CASE WHEN ({bruto}) BETWEEN 0 AND 120 THEN ({bruto}) ELSE NULL END AS IDADE_ANOS"


def colunas_decodificaveis_presentes(nomes_colunas: list[str]) -> list[str]:
    return [c for c in DOMINIOS if c in nomes_colunas]


def montar_query_transformacao_sim(colunas_presentes: list[str],
                                    coluna_municipio: str | None,
                                    tem_idade: bool,
                                    renomear: bool = True) -> str:
    """Monta o SELECT único (token __ORIGEM__) que:
      - decodifica cada campo categórico presente (código -> texto);
      - adiciona IDADE_ANOS a partir de IDADE, se presente;
      - adiciona CO_IBGE_RESIDENCIA normalizado, se a coluna de município existir;
      - descarta colunas sem valor e ordena por importância analítica;
      - renomeia as colunas para nomes legíveis (renomear=True). Quando a
        query é embrulhada por outra camada (sinônimos), passa renomear=False
        e a renomeação é feita na camada externa.
    """
    from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
    from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final

    # Expressão por coluna: decodificada, derivada ou passthrough simples.
    expr_por_coluna = {c: montar_expr_decodificacao(c, DOMINIOS[c])
                       for c in DOMINIOS if c in colunas_presentes}

    colunas_finais = list(colunas_presentes)

    if tem_idade:
        expr_por_coluna["IDADE_ANOS"] = montar_expr_idade_anos()
        colunas_finais.append("IDADE_ANOS")

    if "DTOBITO" in colunas_presentes:
        expr_por_coluna["ANO_OBITO"] = montar_expr_ano_obito_cid10("DTOBITO")
        colunas_finais.append("ANO_OBITO")

    if coluna_municipio:
        expr_por_coluna["CO_IBGE_RESIDENCIA"] = (
            f"CASE WHEN length(trim(CAST({coluna_municipio} AS VARCHAR))) >= 7 "
            f"THEN substr(trim(CAST({coluna_municipio} AS VARCHAR)), 1, 6) "
            f"ELSE nullif(trim(CAST({coluna_municipio} AS VARCHAR)), '') END AS CO_IBGE_RESIDENCIA"
        )
        colunas_finais.append("CO_IBGE_RESIDENCIA")

    ordem = ordenar_colunas(colunas_finais)

    def _seletor(c):
        alvo = nome_final(c) if renomear else c.upper()
        expr = expr_por_coluna.get(c)
        if expr is not None:
            # expr já termina em `AS <NOME_TECNICO>`; troca o alias final.
            base_expr = expr.rsplit(" AS ", 1)[0]
            return f'{base_expr} AS "{alvo}"'
        return f'"{c}" AS "{alvo}"'

    seletores = [_seletor(c) for c in ordem]
    return f"SELECT {', '.join(seletores)} FROM __ORIGEM__"


def montar_query_com_sinonimos(colunas_presentes: list[str], coluna_municipio: str | None,
                               tem_idade: bool, sinonimos_uri: str) -> str:
    """Como montar_query_transformacao_sim, mas resolve também o código
    municipal atual: adiciona cod_municipio_atual = código vigente do
    município, usando o de-para de sinônimos do CADMUN (geo_sinonimos). O
    CO_IBGE_RESIDENCIA original (o que veio no óbito) é preservado.

    sinonimos_uri: caminho/URI legível pelo DuckDB (read_parquet) com as
    colunas COD_MUNICIPIO_ANTIGO e COD_MUNICIPIO_ATUAL.
    """
    from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
    from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final

    # Base sem renomear: o wrapper referencia nomes técnicos e renomeia por fora.
    base = montar_query_transformacao_sim(colunas_presentes, coluna_municipio,
                                          tem_idade, renomear=False)
    if not coluna_municipio:
        return montar_query_transformacao_sim(colunas_presentes, coluna_municipio, tem_idade)

    colunas_finais = list(colunas_presentes)
    if tem_idade:
        colunas_finais.append("IDADE_ANOS")
    if "DTOBITO" in colunas_presentes:
        colunas_finais.append("ANO_OBITO")
    colunas_finais += ["CO_IBGE_RESIDENCIA", "COD_MUNICIPIO_ATUAL"]
    ordem = ordenar_colunas(colunas_finais)

    seletores = []
    for c in ordem:
        if c == "COD_MUNICIPIO_ATUAL":
            seletores.append(
                f'COALESCE(sin.COD_MUNICIPIO_ATUAL, base."CO_IBGE_RESIDENCIA") AS "{nome_final(c)}"')
        else:
            seletores.append(f'base."{c.upper()}" AS "{nome_final(c)}"')

    return (
        f"SELECT {', '.join(seletores)} "
        f"FROM ({base}) base "
        f"LEFT JOIN read_parquet('{sinonimos_uri}') sin "
        "ON base.\"CO_IBGE_RESIDENCIA\" = sin.COD_MUNICIPIO_ANTIGO"
    )


def baixar_sinonimos_municipio() -> str | None:
    """Baixa geo_sinonimos_municipio.parquet (produzido pela fonte macroregiao)
    para um arquivo local legível pelo DuckDB. Retorna o caminho, ou None se
    a geo ainda não foi processada -- nesse caso o SIM publica sem
    cod_municipio_atual, sem travar."""
    from botocore.exceptions import ClientError

    from scripts.common import env
    from scripts.common.paths import PROCESSED_DIR
    from scripts.common.bucket_sync import get_s3_client

    destino = PROCESSED_DIR / "_geo_sinonimos_tmp.parquet"
    destino.parent.mkdir(parents=True, exist_ok=True)
    s3 = get_s3_client()
    try:
        s3.download_file(env.MINIO_BUCKET, "macroregiao/geo_sinonimos_municipio.parquet", str(destino))
    except ClientError:
        return None
    return str(destino)


def ordem_colunas_finais_sim(colunas_presentes: list[str], coluna_municipio: str | None,
                             tem_idade: bool, com_sinonimos: bool) -> list[str]:
    """Ordem final das colunas (nomes legíveis) que a query de transformação
    produz. Usada para posicionar as colunas de descrição corretamente."""
    from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
    from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final

    colunas_finais = list(colunas_presentes)
    if tem_idade:
        colunas_finais.append("IDADE_ANOS")
    if "DTOBITO" in colunas_presentes:
        colunas_finais.append("ANO_OBITO")
    if coluna_municipio:
        colunas_finais.append("CO_IBGE_RESIDENCIA")
        if com_sinonimos:
            colunas_finais.append("COD_MUNICIPIO_ATUAL")
    ordem = ordenar_colunas(colunas_finais)
    return [nome_final(c) for c in ordem]


def montar_query_sim_cid10(colunas_presentes: list[str], coluna_municipio: str,
                           tem_idade: bool, sinonimos_uri: str | None) -> str:
    """Orquestra a query completa do CID-10: transformação (decodifica,
    idade, município), sinônimos (COD_MUNICIPIO_ATUAL) e descrições de código
    (causa CID-10, ocupação, naturalidade). Retorna a query final."""
    from scripts.process.datasus.common.sim.descricao_codigos_sim import montar_descricoes, REF_CID10

    if sinonimos_uri:
        base = montar_query_com_sinonimos(colunas_presentes, coluna_municipio, tem_idade, sinonimos_uri)
    else:
        base = montar_query_transformacao_sim(colunas_presentes, coluna_municipio, tem_idade)

    ordem = ordem_colunas_finais_sim(colunas_presentes, coluna_municipio, tem_idade,
                                     com_sinonimos=bool(sinonimos_uri))
    return montar_descricoes(base, ordem, REF_CID10, tem_ocupacao=True, tem_naturalidade=True)


def montar_expr_ano_obito_cid10(coluna_data: str = "DTOBITO") -> str:
    """ANO_OBITO numérico a partir de DTOBITO no formato DDMMAAAA (CID-10):
    ano são os últimos 4 dígitos. Tolera valores curtos/parciais (NULL)."""
    d = f"trim(CAST({coluna_data} AS VARCHAR))"
    return (
        f"CASE WHEN length({d}) = 8 THEN TRY_CAST(substr({d}, 5, 4) AS INTEGER) "
        f"ELSE NULL END AS ANO_OBITO"
    )
