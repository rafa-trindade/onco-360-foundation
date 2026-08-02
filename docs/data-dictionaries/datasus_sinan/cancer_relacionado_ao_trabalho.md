# Dicionário: cancer_relacionado_ao_trabalho.parquet

Notificações de câncer relacionado ao trabalho (SINAN, agravo C80). Uma linha
por notificação. O diferencial desta base é registrar a exposição ocupacional
a agentes cancerígenos ao longo da vida profissional. Base inteiramente
oncológica (não requer filtro).

Fonte: FTP DATASUS (SINAN, arquivos CANC, pastas FINAIS e PRELIM). Códigos
decodificados conforme a ficha de investigação oficial.

## Notificação e diagnóstico
| Coluna | Descrição |
|---|---|
| DATA_NOTIFICACAO | Data da notificação. |
| ANO_NOTIFICACAO | Ano da notificação. |
| COD_AGRAVO | Código do agravo (C80). |
| COD_UF_NOTIFICACAO | UF da notificação. |
| COD_MUNICIPIO_NOTIFICACAO | Município da notificação (IBGE). |
| COD_UNIDADE_NOTIFICACAO | Unidade de saúde notificadora (CNES). |
| DATA_DIAGNOSTICO | Data do diagnóstico. |
| CID_DIAGNOSTICO_ESPECIFICO | Código CID-10 do diagnóstico específico do câncer. |
| CID_DIAGNOSTICO_ESPECIFICO_DESCRICAO | Descrição textual da causa básica (tabela oficial CID-10). |

## Perfil do paciente
| Coluna | Descrição |
|---|---|
| ANO_NASCIMENTO | Ano de nascimento. |
| COD_IDADE / IDADE_ANOS | Idade: código cru do SINAN e idade em anos (nula para bebês em dias/meses). |
| SEXO | Masculino, Feminino, Ignorado. |
| COD_GESTACAO / GESTACAO | Situação gestacional (trimestre, não, não se aplica, ignorado). |
| COD_RACA_COR / RACA_COR | Raça/cor (Branca, Preta, Amarela, Parda, Indígena, Ignorado). |
| COD_ESCOLARIDADE / ESCOLARIDADE | Escolaridade (do analfabeto ao superior completo). |
| COD_UF_RESIDENCIA | UF de residência. |
| COD_MUNICIPIO_RESIDENCIA | Município de residência (IBGE). |

## Trabalho
| Coluna | Descrição |
|---|---|
| COD_OCUPACAO | Código da ocupação (Classificação Brasileira de Ocupações - CBO). |
| OCUPACAO_DESCRICAO | Descrição textual da ocupação (tabela oficial CBO). |
| COD_SITUACAO_MERCADO_TRABALHO / SITUACAO_MERCADO_TRABALHO | Vínculo (empregado registrado, autônomo, servidor, aposentado, desempregado, etc.). |
| TEMPO_TRABALHO_QTD / COD_TEMPO_TRABALHO_UNIDADE / TEMPO_TRABALHO_UNIDADE | Tempo de trabalho na ocupação (quantidade e unidade: Hora/Dia/Mês/Ano). |
| COD_CNAE | Atividade econômica da empresa (CNAE). |
| COD_EMPREGADOR_TERCEIRIZADO / EMPREGADOR_TERCEIRIZADO | Empregador é empresa terceirizada (Sim/Não/Não se aplica/Ignorado). |
| TEMPO_EXPOSICAO_QTD / COD_TEMPO_EXPOSICAO_UNIDADE / TEMPO_EXPOSICAO_UNIDADE | Tempo de exposição ao agente de risco. |

## Exposições ocupacionais a agentes cancerígenos
Cada campo indica se houve exposição àquele agente ao longo da vida
profissional (Sim/Não/Ignorado):

EXPOSICAO_ASBESTO, EXPOSICAO_SILICA_ARSENICO, EXPOSICAO_AMINAS_AROMATICAS,
EXPOSICAO_BENZENO, EXPOSICAO_ALCATRAO, EXPOSICAO_HIDROCARBONETOS,
EXPOSICAO_OLEOS_MINERAIS, EXPOSICAO_BERILIO, EXPOSICAO_CADMIO, EXPOSICAO_CROMO,
EXPOSICAO_NIQUEL, EXPOSICAO_RADIACOES_IONIZANTES,
EXPOSICAO_RADIACOES_NAO_IONIZANTES, EXPOSICAO_HORMONIOS,
EXPOSICAO_ANTINEOPLASICOS, EXPOSICAO_OUTROS.

| Coluna | Descrição |
|---|---|
| EXPOSICAO_OUTROS_DESCRICAO | Descrição livre de outros agentes (texto). |

## Hábitos
| Coluna | Descrição |
|---|---|
| COD_HABITO_FUMAR / HABITO_FUMAR | Hábito de fumar (Sim/Não/Ex-fumante/Ignorado). |
| TEMPO_FUMO_QTD / COD_TEMPO_FUMO_UNIDADE / TEMPO_FUMO_UNIDADE | Tempo de exposição ao tabaco. |

## Conclusão e evolução
| Coluna | Descrição |
|---|---|
| COD_REGIME_TRATAMENTO / REGIME_TRATAMENTO | Regime do tratamento realizado (Hospitalar, Ambulatorial). |
| COD_OUTROS_TRABALHADORES_DOENCA / OUTROS_TRABALHADORES_DOENCA | Há/houve outros trabalhadores com a mesma doença no local (Sim/Não/Ignorado). |
| COD_EVOLUCAO / EVOLUCAO_CASO | Evolução: remissão completa/parcial, doença estável/em progressão, fora de possibilidade terapêutica, óbito por câncer do trabalho, óbito por outras causas, não se aplica, ignorado. |
| DATA_OBITO | Data do óbito, se houver. |
| COD_COMUNICACAO_ACIDENTE_TRABALHO / COMUNICACAO_ACIDENTE_TRABALHO | Foi emitida a CAT (Sim/Não/Não se aplica/Ignorado). |
| ARQUIVO_ORIGEM | Arquivo DBC de origem (linhagem). |

## Notas
- Base única no acervo: nenhuma outra fonte registra exposição ocupacional a
  agentes cancerígenos, o que permite estudos de nexo causal entre trabalho e
  câncer.
- Descartados campos de identificação pessoal (nomes, endereço, telefone) e de
  fluxo interno do SINAN (datas de digitação/transferência, lotes).
- A idade em anos (IDADE_ANOS) é derivada do código do SINAN, contemplando centenários; para menores de
  1 ano (registrados em dias/meses) fica nula, com o código cru em COD_IDADE.
- Inclui casos das bases FINAIS (consolidadas) e PRELIM (preliminares).