# Dicionário: obitos_cancer_cid10.parquet

bitos relacionados à oncologia (CAUSABAS C00-C97, D00-D48 e B21) do SIM/DATASUS,
era CID-10 consolidada (1996 até o último ano homologado). Uma linha por óbito.

Fonte: SIM (Sistema de Informações sobre Mortalidade), arquivos DORES/DOBR do
FTP DATASUS. Campos categóricos decodificados para texto.

| Coluna | Tipo | Descrição |
|---|---|---|
| ID_REGISTRO | texto | Identificador sequencial do registro na origem (CONTADOR). |
| CAUSA_BASICA | texto | Código CID-10 da causa básica do óbito (C00-C97: Malignas; D00-D48: In situ e Incertas; B21: HIV). |
| CAUSA_BASICA_DESCRICAO | texto | Descrição da causa básica (tabela CID-10 oficial). |
| ANO_OBITO | inteiro | Ano do óbito, extraído da data. Coluna confiável para série temporal. |
| DATA_OBITO | texto | Data do óbito no formato original DDMMAAAA. |
| DATA_NASCIMENTO | texto | Data de nascimento no formato original DDMMAAAA. |
| IDADE_ANOS | inteiro | Idade em anos no óbito (0-120; valores implausíveis viram nulo). |
| SEXO | texto | Sexo (Masculino, Feminino, Ignorado). |
| RACA_COR | texto | Raça/cor (Branca, Preta, Amarela, Parda, Indígena, Ignorado). |
| ESTADO_CIVIL | texto | Estado civil do falecido. |
| ESCOLARIDADE | texto | Escolaridade agregada (ESCFALAGR1), comparável entre épocas. |
| OCUPACAO | texto | Ocupação no formato "código - texto" (CBO antigo ou CBO-2002). Código sem correspondência fica só com o número. |
| NATURALIDADE | texto | Naturalidade resolvida: UF de nascimento (se brasileiro) ou país. |
| COD_MUNICIPIO_RESIDENCIA | texto | Código IBGE (6 díg) do município de residência, como veio no óbito. |
| COD_MUNICIPIO_RESIDENCIA_ATUAL | texto | Código vigente do município (resolvido via sinônimos do CADMUN). |
| COD_MUNICIPIO_OCORRENCIA | texto | Código IBGE (6 díg) do município de ocorrência do óbito. |
| LOCAL_OCORRENCIA | texto | Local de ocorrência (Hospital, Domicílio, Via pública, etc.). |
| TIPO_OBITO | texto | Tipo de óbito (Fetal, Não fetal). |
| ASSISTENCIA_MEDICA | texto | Teve assistência médica durante a doença (Sim, Não, Ignorado). |
| TEVE_EXAME | texto | Diagnóstico confirmado por exame complementar. |
| TEVE_CIRURGIA | texto | Diagnóstico confirmado por cirurgia. |
| TEVE_NECROPSIA | texto | Houve necropsia. |
| MEDICO_ATESTANTE | texto | Quem atestou o óbito (médico assistente, IML, SVO, outro). |
| OBITO_NA_GRAVIDEZ | texto | Óbito ocorrido durante a gravidez (relevante para câncer em gestante). |
| OBITO_NO_PUERPERIO | texto | Óbito ocorrido no puerpério. |
| ARQUIVO_ORIGEM | texto | Arquivo DBC de origem (linhagem/proveniência do registro). |

## Notas
- Formato de data: DDMMAAAA (dia primeiro). Use ANO_OBITO para série temporal.
- Colunas removidas de propósito: cadeia causal crua (LINHAA-D/II, já
  consolidada em CAUSA_BASICA), controle interno (cartório, flags de sistema),
  campos maternos/fetais e de investigação de baixa completude, escolaridade
  por época (mantida só a agregada), HORA_OBITO (100% nulo) e código de
  município de naturalidade (redundante com NATURALIDADE).
