# Dicionário: obitos_cancer_prelim.parquet

Óbitos por câncer (CID-10) dos dados **preliminares** do SIM, do ano corrente
ainda não homologado pelo DATASUS. Espelha a estrutura do CID-10 consolidado.

Fonte: SIM, arquivos preliminares (DOBR do ano corrente). Mesmo tratamento do
consolidado. Pode vir vazio entre ciclos do DATASUS (nesse caso é publicado um
parquet vazio com o schema padrão, para o consumidor distinguir "sem dado novo"
de "nunca publicado").

As colunas são idênticas às de `obitos_cancer_cid10.parquet`. Veja o dicionário
`obitos_cancer_cid10.md` para a descrição de cada coluna:

ID_REGISTRO, CAUSA_BASICA, CAUSA_BASICA_DESCRICAO, ANO_OBITO, DATA_OBITO,
DATA_NASCIMENTO, IDADE_ANOS, SEXO, RACA_COR, ESTADO_CIVIL, ESCOLARIDADE,
OCUPACAO, NATURALIDADE, COD_MUNICIPIO_RESIDENCIA, COD_MUNICIPIO_RESIDENCIA_ATUAL,
COD_MUNICIPIO_OCORRENCIA, LOCAL_OCORRENCIA, TIPO_OBITO, ASSISTENCIA_MEDICA,
TEVE_EXAME, TEVE_CIRURGIA, TEVE_NECROPSIA, MEDICO_ATESTANTE, OBITO_NA_GRAVIDEZ,
OBITO_NO_PUERPERIO, ARQUIVO_ORIGEM.

## Notas
- Dado preliminar: sujeito a revisão e reclassificação pelo DATASUS. Para
  análise definitiva, prefira o consolidado quando o ano for homologado.
