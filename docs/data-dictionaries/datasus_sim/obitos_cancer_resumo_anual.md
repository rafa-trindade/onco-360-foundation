# Dicionário: obitos_cancer_resumo_anual.parquet

Resumo anual da mortalidade por câncer no SIM. Uma linha por ano/fonte, com o
total de óbitos, o total de óbitos por câncer e a proporção. Subproduto
compartilhado das três variantes do SIM (CID-9, CID-10, preliminar).

| Coluna | Tipo | Descrição |
|---|---|---|
| ANO | inteiro | Ano de referência dos óbitos. |
| FONTE | texto | Origem do dado: CID9, CID10 ou PRELIM. |
| ARQUIVO | texto | Arquivo DBC de origem do ano (ex: DOBR2020.dbc). |
| TOTAL_OBITOS_GERAL | inteiro | Total de óbitos no ano (todas as causas). |
| TOTAL_OBITOS_CANCER | inteiro | Total de óbitos por neoplasia maligna no ano. |
| PROPORCAO_OBITOS_CANCER | decimal | Proporção de óbitos por câncer sobre o total (TOTAL_OBITOS_CANCER / TOTAL_OBITOS_GERAL). |
| ERRO | texto | Mensagem de erro se a contagem falhou; nulo quando OK. |

## Notas
- Upsert por ano: quando um ano é reprocessado, sua linha é substituída.
- A proporção sobe historicamente (~8% em 1979 a ~17% em anos recentes),
  refletindo envelhecimento populacional e melhora do diagnóstico.
- Para o consolidado x preliminar do mesmo ano, o consolidado prevalece.
