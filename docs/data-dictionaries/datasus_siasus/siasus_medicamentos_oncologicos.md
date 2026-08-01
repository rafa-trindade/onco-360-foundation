# Dicionário: siasus_medicamentos_oncologicos.parquet

APAC de Medicamentos de alto custo do SIASUS, recorte oncológico: apenas
registros cujo CID principal é uma neoplasia (capítulo II da CID-10, C00-D48).
Uma linha por procedimento autorizado. Desde 2008.

Fonte: FTP DATASUS (SIASUS, arquivos AM), filtrado por CID de neoplasia.

| Coluna | Tipo | Descrição |
|---|---|---|
| CID_PRINCIPAL | texto | CID principal (sempre uma neoplasia neste recorte). |
| CID_PRINCIPAL_DESCRICAO | texto | Descrição do CID principal (tabela CID-10). |
| CID_SECUNDARIO / CID_CAUSAS_ASSOCIADAS | texto | CIDs secundário e causas associadas. |
| PESO_KG | texto | Peso do paciente em kg. |
| ALTURA_CM | texto | Altura do paciente em cm. |
| GESTANTE | texto | Indicador de gestante (Sim/Não). |
| NUM_APAC | texto | Número da APAC. |
| COD_PROCEDIMENTO_PRINCIPAL | texto | Código do procedimento/medicamento (SIGTAP). |
| VALOR_TOTAL_APAC | texto | Valor total aprovado da APAC. |
| ANO_MES_ATENDIMENTO | texto | Ano e mês do atendimento (AAAAMM). |
| SEXO | texto | Sexo do paciente. |
| IDADE | texto | Idade do paciente. |
| COD_RACA_COR / RACA_COR | texto | Raça/cor do paciente. |
| COD_CNES | texto | CNES do estabelecimento executante. |
| CNPJ_ESTABELECIMENTO / CNPJ_MANTENEDORA | texto | CNPJ do executante e da mantenedora. |
| COD_UF_MUNICIPIO_ESTABELECIMENTO | texto | UF + município do estabelecimento. |
| COD_MUNICIPIO_RESIDENCIA | texto | Município de residência do paciente. |
| COD_TIPO_APAC / TIPO_APAC | texto | Tipo de APAC (Inicial, Continuidade, Única). |
| ARQUIVO_ORIGEM | texto | Arquivo DBC de origem (linhagem). |

## Notas
- O recorte oncológico é feito por CID principal C00-C97 ou D00-D48 (capítulo II
  da CID-10). A base bruta de medicamentos é muito maior e cobre outras doenças.
- Peso e altura permitem estimar superfície corporal, base do cálculo de dose
  de quimioterápicos.
- Descartados campos de controle interno, à semelhança das demais APAC.
