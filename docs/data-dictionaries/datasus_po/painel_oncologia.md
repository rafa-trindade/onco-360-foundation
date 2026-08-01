# Dicionário: painel_oncologia.parquet

Painel de Oncologia do DATASUS: registros de casos oncológicos do SUS desde
2013, com diagnóstico, estadiamento e primeiro tratamento. Uma linha por
registro de caso. Atualizado mensalmente na origem, inclusive anos anteriores.

Fonte: FTP DATASUS (PAINEL_ONCOLOGIA). Códigos decodificados conforme o
dicionário oficial do painel; topografia com descrição via a tabela CID-10.

| Coluna | Tipo | Descrição |
|---|---|---|
| TOPOGRAFIA_CID10 | texto | CID-10 detalhado do diagnóstico (C00-C97, D00-D09, D37-D48). |
| TOPOGRAFIA_CID10_DESCRICAO | texto | Descrição da topografia (tabela CID-10). |
| COD_CATEGORIA_DIAGNOSTICO | texto | Código da categoria de diagnóstico. |
| CATEGORIA_DIAGNOSTICO | texto | Categoria: neoplasia maligna (Lei 12.732/12), in situ, comportamento incerto, ou C44 e C73. |
| COD_ESTADIAMENTO | texto | Código do estadiamento. |
| ESTADIAMENTO | texto | Estadiamento: 0, I, II, III, IV, Não se aplica, Ignorado. |
| COD_TRATAMENTO | texto | Código do primeiro tratamento. |
| TRATAMENTO | texto | Primeiro tratamento: Cirurgia, Quimioterapia, Radioterapia, Quimio + Radio, ou Sem informação. |
| ANO_DIAGNOSTICO | texto | Ano do diagnóstico (AAAA). |
| ANO_MES_DIAGNOSTICO | texto | Ano e mês do diagnóstico (AAAAMM). |
| DATA_DIAGNOSTICO | texto | Data detalhada do diagnóstico (DD/MM/AAAA). |
| ANO_TRATAMENTO | texto | Ano do primeiro tratamento (AAAA). |
| ANO_MES_TRATAMENTO | texto | Ano e mês do primeiro tratamento (AAAAMM). |
| DATA_TRATAMENTO | texto | Data detalhada do primeiro tratamento (DD/MM/AAAA). |
| DIAS_ATE_TRATAMENTO | texto | Intervalo entre diagnóstico e tratamento. Sinal + (tratamento após laudo) ou - (antes), seguido do número de dias. 99999 = sem informação de tratamento. |
| IDADE_DIAGNOSTICO | inteiro | Idade no diagnóstico. Valor 999 (ignorada) na origem vira nulo. |
| SEXO | texto | Sexo (Feminino, Masculino). |
| DATA_NASCIMENTO | texto | Data de nascimento (DD/MM/AAAA). |
| COD_MUNICIPIO_RESIDENCIA | texto | Código IBGE do município de residência (6 dígitos). |
| COD_UF_RESIDENCIA | texto | Código IBGE da UF de residência. |
| COD_MUNICIPIO_DIAGNOSTICO | texto | Código IBGE do município onde foi registrado o diagnóstico. |
| COD_UF_DIAGNOSTICO | texto | Código IBGE da UF do diagnóstico. |
| COD_CNES_DIAGNOSTICO | texto | Código CNES do estabelecimento do diagnóstico (7 dígitos). |
| COD_MUNICIPIO_TRATAMENTO | texto | Código IBGE do município onde foi registrado o tratamento. |
| COD_UF_TRATAMENTO | texto | Código IBGE da UF do tratamento. |
| COD_CNES_TRATAMENTO | texto | Código CNES do estabelecimento do tratamento (7 dígitos). |
| ARQUIVO_ORIGEM | texto | Arquivo DBC de origem (linhagem). |

## Notas
- Base inteiramente oncológica: não há filtro de causa (diferente do SIM).
- COD_CNES_DIAGNOSTICO e COD_CNES_TRATAMENTO cruzam com a base
  cnes_instituicoes_oncologia (COD_CNES) para identificar o estabelecimento.
- Descartado o Cartão Nacional de Saúde (CNS_PAC): identificador pessoal do
  paciente, sensível e sem uso analítico.
- Datas mantidas no formato original DD/MM/AAAA; para série temporal, use
  ANO_DIAGNOSTICO ou ANO_MES_DIAGNOSTICO.
