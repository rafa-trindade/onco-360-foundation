# Dicionário: geo_macroregiao.parquet

Referência geográfica por município: as duas divisões territoriais do país
(saúde e IBGE), identificação, população, situação e geolocalização. Uma linha
por município.

Fontes combinadas: base de macrorregiões de saúde do Ministério da Saúde (CSV),
planilha de geolocalização (coordenadas e área) e CADMUN do DATASUS (situação,
capital, meso e microrregião). O MS + planilha são a base; o CADMUN apenas
complementa o que elas não têm, sem duplicar colunas.

## Dois sistemas de divisão territorial (não confundir)

O Brasil tem duas divisões paralelas e independentes:

- **Divisão de saúde (SUS)**: UF > Macrorregião de Saúde > Região de Saúde >
  Município. Usada para planejar a assistência do SUS.
- **Divisão estatística (IBGE)**: UF > Mesorregião > Microrregião > Município.
  Agrupamentos geográficos do IBGE.

Portanto COD_MACRORREGIAO_DE_SAUDE (saúde) e COD_MESORREGIAO/COD_MICRORREGIAO
(IBGE) são de sistemas diferentes, não são equivalentes.

## Colunas (na ordem do arquivo)

| Coluna | Tipo | Descrição |
|---|---|---|
| CO_REGIAO_PAIS | texto | Código da região do país (1=Norte ... 5=Centro-Oeste). |
| REGIAO_PAIS | texto | Nome da região do país. |
| CO_UF | texto | Código IBGE da UF (2 dígitos). |
| SG_UF | texto | Sigla da UF (ex: AC). |
| UF | texto | Nome da UF. |
| COD_MACRORREGIAO_DE_SAUDE | texto | Código da macrorregião de saúde (SUS). |
| MACRORREGIAO_DE_SAUDE | texto | Nome da macrorregião de saúde. |
| COD_REGIAO_DE_SAUDE | texto | Código da região de saúde (SUS). |
| REGIAO_DE_SAUDE | texto | Nome da região de saúde. |
| COD_MESORREGIAO | texto | Código da mesorregião (IBGE). |
| COD_MICRORREGIAO | texto | Código da microrregião (IBGE). |
| COD_MUNICIPIO | texto | Código IBGE do município (6 dígitos). |
| MUNCODDV | texto | Código IBGE do município com dígito verificador (7 dígitos). |
| NOME_MUNICIPIO | texto | Nome do município. |
| EH_CAPITAL | texto | Indica se o município é capital. |
| SITUACAO_MUNICIPIO | texto | Situação do município no CADMUN (ex: ATIVO). |
| POPULACAO_IBGE_2022 | texto | População do município (Censo IBGE 2022). |
| LATITUDE | decimal | Latitude do município. |
| LONGITUDE | decimal | Longitude do município. |
| ALTITUDE | decimal | Altitude do município. |
| AREA_KM2 | decimal | Área do município em km². |

## Notas
- Sem colunas duplicadas: quando MS/planilha e CADMUN traziam a mesma
  informação (coordenadas, área), prevalece a da base MS/planilha; o CADMUN só
  entra com situação, capital, meso e micro.
- Ordem harmônica: da maior agregação (região do país) à menor (município),
  com as duas divisões territoriais agrupadas, depois atributos e geolocalização.
- Deve ser processada ANTES do SIM: gera o de-para de sinônimos de município
  (geo_sinonimos_municipio) que o SIM consome para COD_MUNICIPIO_RESIDENCIA_ATUAL.