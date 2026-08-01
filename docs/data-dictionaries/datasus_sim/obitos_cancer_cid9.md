# Dicionário: obitos_cancer_cid9.parquet

Óbitos por neoplasia maligna (CAUSABAS 140-208) do SIM/DATASUS, era CID-9
(1979-1995). Uma linha por óbito.

Fonte: SIM, arquivos DORES/DOBR do FTP DATASUS (era CID-9). Campos categóricos
decodificados para texto.

| Coluna | Tipo | Descrição |
|---|---|---|
| ID_REGISTRO | texto | Identificador sequencial do registro na origem (contador). |
| CAUSA_BASICA | texto | Código CID-9 da causa básica (categoria de 3 dígitos + subcategoria, ex: 1519, 185X). |
| CAUSA_BASICA_DESCRICAO | texto | Descrição da causa no nível de categoria (3 dígitos), tabela CID-9 oficial. |
| ANO_OBITO | inteiro | Ano do óbito, extraído da data. Coluna confiável para série temporal. |
| DATA_OBITO | texto | Data do óbito no formato original AAMMDD (pode vir parcial: só ano, ou dia 00). |
| IDADE_ANOS | inteiro | Idade em anos no óbito (0-120; valores implausíveis viram nulo). |
| SEXO | texto | Sexo (Masculino, Feminino, Ignorado). |
| ESTADO_CIVIL | texto | Estado civil (1=Solteiro, 2=Casado, 3=Viúvo, 4=Separado/divorciado). |
| ESCOLARIDADE | texto | Escolaridade (INSTRUCAO), em anos de estudo agregados. |
| OCUPACAO | texto | Ocupação no formato "código - texto" (CBO antigo, 3 dígitos). Código 000 (ignorado) fica só com o número. |
| NATURALIDADE | texto | Naturalidade resolvida: UF de nascimento (se brasileiro) ou país. |
| COD_MUNICIPIO_RESIDENCIA | texto | Código IBGE (6 díg) do município de residência, como veio no óbito. |
| COD_MUNICIPIO_RESIDENCIA_ATUAL | texto | Código vigente do município (resolvido via sinônimos do CADMUN). |
| COD_MUNICIPIO_OCORRENCIA | texto | Código IBGE (6 díg) do município de ocorrência. |
| LOCAL_OCORRENCIA | texto | Local de ocorrência (Hospital, Domicílio, etc.). |
| TIPO_OBITO | texto | Tipo de óbito (Fetal, Não fetal). |
| ASSISTENCIA_MEDICA | texto | Teve assistência médica durante a doença. |
| TEVE_EXAME | texto | Diagnóstico confirmado por exame complementar. |
| TEVE_CIRURGIA | texto | Diagnóstico confirmado por cirurgia. |
| TEVE_NECROPSIA | texto | Houve necropsia. |
| MEDICO_ATESTANTE | texto | Quem atestou o óbito. |
| ARQUIVO_ORIGEM | texto | Arquivo DBC de origem (linhagem/proveniência do registro). |

## Notas
- Formato de data: AAMMDD (ano primeiro), diferente do CID-10 (DDMMAAAA). Há
  registros parciais (só ano, ex: "95"; ou dia 00, ex: "950500"). Use
  ANO_OBITO para série temporal.
- CAUSA_BASICA guarda 4 caracteres (categoria + subcategoria, ex: 1519, 185X);
  a descrição é no nível de categoria (3 díg), granularidade da tabela oficial.
- Particularidade histórica: o dicionário do CID-9 (MORT98.HLP) omite "Viúvo"
  no texto corrido do estado civil; confirmado com os dados que o código 3 é
  Viúvo.
- Colunas removidas de propósito: RACA_COR e ETNIA (0% nesta era, só coletados
  a partir de 1996), DATA_NASCIMENTO (80% nula, coberta por IDADE_ANOS),
  maternos/fetais, controle interno, e as demais conforme a política do SIM.
