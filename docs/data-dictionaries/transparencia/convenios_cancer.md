# Dicionário: convenios_cancer.parquet

Convênios federais cujo objeto menciona câncer/oncologia, extraídos do Portal
da Transparência, e cruzados por CNPJ com as instituições habilitadas em
oncologia no CNES. Uma linha por convênio.

Fonte: Portal da Transparência (dump semanal, histórico integral desde 1996),
filtrado por palavras-chave no objeto e enriquecido com o CNES publicado.

## Colunas do Portal da Transparência
Mantidas do arquivo original (nomes conforme exportação do Portal), incluindo
número do convênio, órgão, convenente, objeto, valores e vigência. As
principais para análise são o objeto (que motivou o filtro), o código
convenente (CNPJ, usado no cruzamento) e os valores.

## Colunas do cruzamento com o CNES
| Coluna | Tipo | Descrição |
|---|---|---|
| HABILITADO_CNES_ONCOLOGIA | booleano | O convenente é uma instituição habilitada em oncologia no CNES. |
| CNES_TEM_ONCOLOGIA_PEDIATRICA | booleano | Alguma unidade vinculada ao CNPJ tem habilitação pediátrica. |
| CNES_NOME_FANTASIA | texto | Nome fantasia da instituição no CNES. |
| CNES_RAZAO_SOCIAL | texto | Razão social da instituição no CNES. |
| CNES_HABILITACOES | texto | Habilitações de oncologia da(s) unidade(s), separadas por "; ". |
| CNES_QTD_UNIDADES_VINCULADAS | inteiro | Quantas unidades CNES compartilham o mesmo CNPJ efetivo. |
| CNES_TOTAL_LEITOS | inteiro | Total de leitos somado das unidades vinculadas. |
| CNES_COD_UF | texto | Código IBGE da UF da instituição. |
| CNES_COD_MUNICIPIO | texto | Código IBGE do município da instituição. |
| CNES_LOGRADOURO | texto | Logradouro da instituição. |
| CNES_LATITUDE | texto | Latitude da instituição. |
| CNES_LONGITUDE | texto | Longitude da instituição. |
| CNES_VIA_CNPJ_MANTENEDORA | booleano | O cruzamento foi feito pelo CNPJ da mantenedora (unidade sem CNPJ próprio). |

## Notas
- O filtro usa palavras-chave no objeto do convênio (câncer, oncologia,
  quimioterapia, radioterapia, neoplasia, etc.); é um recorte por texto, então
  pode haver convênios de fronteira.
- O cruzamento por CNPJ usa fallback para a mantenedora, cobrindo redes e
  hospitais universitários sem CNPJ próprio.
- Convênios cujo convenente não é instituição habilitada ficam com
  HABILITADO_CNES_ONCOLOGIA = false e as colunas CNES_* vazias.
