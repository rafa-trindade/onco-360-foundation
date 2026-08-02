# Dicionário: siscan_rastreamento_colo_mama.parquet

Exames de rastreamento de câncer de colo do útero (citopatológico) e de mama
(mamografia), do SISCAN, tabulados via TABNET. Diferente das demais bases do
acervo, é **dado agregado** (contagens), não registro individual: cada linha é
uma combinação de visão, medida e cruzamento de dimensões.

Fonte: TABNET/DATASUS (SISCAN), visões nacionais. Série desde 2013. Atualização
conforme o DATASUS publica.

## Visões disponíveis (10)
Cada visão é publicada num parquet próprio (`{visao_id}.parquet`):
- **Colo do útero - citopatológico:** `cito_colo_residencia`, `cito_colo_atendimento`
- **Colo do útero - histopatológico (biópsia):** `histo_colo_residencia`, `histo_colo_atendimento`
- **Mama - mamografia:** `mamografia_residencia`, `mamografia_atendimento`
- **Mama - citopatológico (PAAF/punção):** `cito_mama_residencia`, `cito_mama_atendimento`
- **Mama - histopatológico (biópsia):** `histo_mama_residencia`, `histo_mama_atendimento`

As visões "por residência" cruzam por UF de residência da paciente; as "por
atendimento" cruzam por UF do prestador de serviço.

## Medidas por tipo de exame
- **Citopatológico de colo:** total e cascata (ASC-US, ASC-H, lesões de baixo/alto grau, carcinomas, adenocarcinomas).
- **Histopatológico de colo:** total e neoplasias (NIC I/II/III, carcinomas, adenocarcinomas).
- **Mamografia:** total, achados, BI-RADS 3, lesão com câncer, nódulo, microcalcificação, assimetrias.
- **Citopatológico de mama:** total de exames (os resultados de PAAF são dimensões no SISCAN).
- **Histopatológico de mama:** total e cascata de lesões benignas (hiperplasias, fibroadenoma, papilomas, mastite, etc.).

## Estrutura (formato longo)
| Coluna | Descrição |
|---|---|
| VISAO | Identificador da visão (colo_residencia, colo_atendimento, mama_residencia, mama_atendimento). |
| EXAME | Tipo de exame: "Colo do útero (citopatológico)" ou "Mama (mamografia)". |
| PERFIL | "Por local de residência" ou "Por local de atendimento". |
| DIMENSAO_LINHA | Dimensão na linha da tabulação (ex: UF de residencia). |
| CATEGORIA_LINHA | Valor da dimensão de linha (ex: "35 São Paulo"). |
| DIMENSAO_COLUNA | Dimensão na coluna (ex: Ano competencia). |
| CATEGORIA_COLUNA | Valor da dimensão de coluna (ex: "2025"). |
| MEDIDA | O que é contado (ver medidas abaixo). |
| QTD | Quantidade de exames (contagem inteira). |

## Medidas de colo do útero (resultado citopatológico)
Total de exames e a cascata diagnóstica: ASC-US, ASC-H, atipias glandulares de
significado indeterminado (não neoplásica e de alto grau), lesão intraepitelial
de baixo grau, de alto grau, de alto grau com microinvasão, carcinoma
epidermoide invasor, adenocarcinoma in situ, adenocarcinoma invasor, outras
neoplasias, e o consolidado "Exames Alterados".

## Medidas de mama (mamografia)
Total de exames, achados diagnósticos, categoria BI-RADS 3, lesão com
diagnóstico de câncer, nódulo, microcalcificação e achado benigno.

## Notas
- **Dado agregado:** não há paciente individual. Para incidência/rastreamento
  populacional em nível de pessoa, ver as bases da PNS (rastreamento de colo e
  mama) e o INCA (RCBP).
- A dimensão de resultado do exame está embutida nas MEDIDAS (cada tipo de
  resultado é uma medida contada separadamente), não como categoria de linha.
- Cruzamentos disponíveis são entre as dimensões geográfico-temporais (UF,
  município, ano). Faixa etária, raça/cor e escolaridade existem no SISCAN como
  filtros, mas não como eixo de cruzamento nesta extração.
- As duas perspectivas (residência e atendimento) permitem comparar onde a
  mulher mora versus onde foi atendida, útil para fluxo assistencial.
- Contagens podem ser revisadas pelo DATASUS a cada atualização.
