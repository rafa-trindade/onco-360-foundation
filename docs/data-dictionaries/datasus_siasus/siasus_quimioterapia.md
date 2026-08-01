# Dicionário: siasus_quimioterapia.parquet

APAC de Quimioterapia do SIASUS: procedimentos de quimioterapia autorizados no
SUS desde 2008. Uma linha por procedimento autorizado. Base inteiramente
oncológica.

Fonte: FTP DATASUS (SIASUS, arquivos AQ). Códigos decodificados conforme o
informe técnico; topografia descrita pela tabela CID-10.

| Coluna | Tipo | Descrição |
|---|---|---|
| TOPOGRAFIA_CID10 | texto | CID-10 de topografia do tumor (AQ_CID10). |
| TOPOGRAFIA_CID10_DESCRICAO | texto | Descrição da topografia (tabela CID-10). |
| CID_PRINCIPAL | texto | CID principal da APAC. |
| COD_ESTADIAMENTO / ESTADIAMENTO | texto | Estádio clínico (0, I, II, III, IV). |
| COD_LINFONODOS_INVADIDOS / LINFONODOS_INVADIDOS | texto | Linfonodos regionais invadidos (Sim/Não/Não avaliáveis). |
| GRAU_HISTOPATOLOGICO | texto | Grau histopatológico do tumor. |
| COD_TRATAMENTO_ANTERIOR / TEVE_TRATAMENTO_ANTERIOR | texto | Houve tratamento anterior (Sim/Não). |
| DATA_IDENTIFICACAO_PATOLOGICA | texto | Data da identificação patológica do caso. |
| CONTINUIDADE_TRATAMENTO | texto | Continuidade do tratamento (Sim/Não). |
| DATA_INICIO_TRATAMENTO | texto | Data de início do tratamento solicitado. |
| ESQUEMA_TERAPEUTICO_INICIO / _FIM | texto | Sigla do esquema terapêutico (partes inicial e final). |
| TOTAL_MESES_PLANEJADOS | texto | Total de meses planejados de tratamento. |
| TOTAL_MESES_AUTORIZADOS | texto | Total de meses autorizados. |
| NUM_APAC | texto | Número da APAC. |
| COD_PROCEDIMENTO_PRINCIPAL | texto | Código do procedimento principal (SIGTAP). |
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
- Uma APAC gera um registro por procedimento; o valor é o total da APAC.
- Descartados campos de controle interno (indicadores de óbito/alta/permanência,
  motivo de saída, órgão emissor, datas de validade administrativa, CNS do
  paciente por privacidade).
- COD_CNES cruza com cnes_instituicoes_oncologia; a topografia cruza com as
  demais bases oncológicas por CID-10.
