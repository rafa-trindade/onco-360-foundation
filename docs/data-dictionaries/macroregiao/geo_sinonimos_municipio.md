# Dicionário: geo_sinonimos_municipio.parquet

De-para de código municipal antigo para o código vigente, para resolver
códigos IBGE extintos em bases históricas. Uma linha por código antigo.

Fonte: campo MUNSINON do CADMUN (DATASUS). Só substituições reais de código
histórico por município ativo entram; faixas administrativas gigantes (ex:
todo o DF, faixa de "ignorado") e destinos não-ativos são descartados.

| Coluna | Tipo | Descrição |
|---|---|---|
| COD_MUNICIPIO_ANTIGO | texto | Código IBGE (6 díg) antigo/extinto que aparece em bases históricas. |
| COD_MUNICIPIO_ATUAL | texto | Código IBGE (6 díg) vigente correspondente. |

## Notas
- Usado pelo SIM para preencher COD_MUNICIPIO_RESIDENCIA_ATUAL: o código
  original do óbito (COD_MUNICIPIO_RESIDENCIA) é mantido, e o atual é resolvido
  por este de-para (quando não há sinônimo, o atual repete o original).
- Exemplos legítimos: subdistritos antigos de São Paulo (358001-358058 ->
  355030), do Rio (334501-334530 -> 330455), e substituições pontuais de
  municípios que mudaram de código.
