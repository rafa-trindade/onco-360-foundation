# Dicionário: registro_hospitalar.parquet

Registro Hospitalar de Câncer (RHC), do Integrador de Registros Hospitalares de
Câncer (IRHC/INCA). Consolida os casos de câncer atendidos nas unidades
hospitalares com Registro Hospitalar, com dados de diagnóstico, estadiamento,
tratamento e desfecho. Uma linha por caso.

Fonte: snapshot do IRHC/INCA (arquivo estático, publicado como veio da origem).
Este dicionário documenta os campos conforme o dicionário oficial do IRHC; os
nomes das colunas seguem o padrão do INCA.

## Identificação e datas
| Coluna | Descrição |
|---|---|
| TPCASO | Tipo de caso: 1 Analítico; 2 Não analítico. |
| ANTRI | Ano da triagem. |
| DTTRIAGE | Data da triagem. |
| DATAPRICON | Data da 1ª consulta. |
| DTPRICON | Ano da 1ª consulta. |
| ANOPRIDI | Data do diagnóstico. |
| DTDIAGNO | Data do primeiro diagnóstico. |
| DATAINITRT | Data de início do primeiro tratamento no hospital. |
| DTINITRT | Ano de início do primeiro tratamento no hospital. |
| DATAOBITO | Data do óbito. |

## Perfil do paciente
| Coluna | Descrição |
|---|---|
| SEXO | 1 Masculino; 2 Feminino. |
| IDADE | Idade em anos (0 para menores de 1 ano). |
| RACACOR | Raça/cor: 1 Branca; 2 Preta; 3 Amarela; 4 Parda; 5 Indígena; 9 Sem informação. |
| INSTRUC | Escolaridade: 1 Nenhuma; 2 Fundamental incompleto; 3 Fundamental completo; 4 Nível médio; 5 Superior incompleto; 6 Superior completo; 9 Sem informação. |
| ESTCONJ | Estado conjugal: 1 Solteiro; 2 Casado; 3 Viúvo; 4 Separado judicialmente; 5 União consensual; 9 Sem informação. |
| OCUPACAO | Ocupação principal (Classificação Brasileira de Ocupações - CBO). |
| LOCALNAS | Sigla da UF de nascimento. |
| PROCEDEN | Código do município de residência (IBGE). |
| ESTADRES | Sigla da UF de procedência. |

## Hábitos e histórico
| Coluna | Descrição |
|---|---|
| ALCOOLIS | Consumo de álcool: 1 Nunca; 2 Ex-consumidor; 3 Sim; 4 Não avaliado; 8 Não se aplica; 9 Sem informação. |
| TABAGISM | Consumo de tabaco: mesma escala de ALCOOLIS. |
| HISTFAMC | Histórico familiar de câncer: 1 Sim; 2 Não; 9 Sem informação. |
| DIAGANT | Diagnóstico e tratamento anteriores: 1 Sem diag./Sem trat.; 2 Com diag./Sem trat.; 3 Com diag./Com trat.; 4 Outros; 9 Sem informação. |
| ORIENC | Origem do encaminhamento: 1 SUS; 2 Não SUS; 3 Por conta própria; 8 Não se aplica; 9 Sem informação. |

## Tumor e diagnóstico
| Coluna | Descrição |
|---|---|
| LOCTUDET | Localização primária (CID-O, 3 dígitos). |
| LOCTUPRI | Localização primária detalhada (CID-O, 4 dígitos). |
| LOCTUPRO | Localização provável do tumor primário (CID-O, 4 dígitos). |
| TIPOHIST | Tipo histológico do tumor primário (morfologia CID-O). |
| LATERALI | Lateralidade: 1 Direita; 2 Esquerda; 3 Bilateral; 8 Não se aplica; 9 Sem informação. |
| MAISUMTU | Ocorrência de mais um tumor primário: 1 Não; 2 Sim; 3 Duvidoso. |
| BASMAIMP | Base mais importante para o diagnóstico: 1 Clínica; 2 Pesquisa clínica; 3 Exame por imagem; 4 Marcadores tumorais; 5 Citologia; 6 Histologia da metástase; 7 Histologia do tumor primário; 9 Sem informação. |
| BASDIAGSP | Base do diagnóstico: 1 Exame clínico; 2 Recursos auxiliares não microscópicos; 3 Confirmação microscópica; 4 Sem informação. |
| EXDIAG | Exames relevantes para diagnóstico: 1 Exame clínico e patologia clínica; 2 Imagem; 3 Endoscopia e cirurgia exploradora; 4 Anatomia patológica; 5 Marcadores tumorais; 8 Não se aplica; 9 Sem informação. |

## Estadiamento
| Coluna | Descrição |
|---|---|
| TNM | Codificação do estádio clínico segundo classificação TNM. |
| ESTADIAM | Estadiamento clínico (grupamento do estádio TNM). |
| ESTADIAG | Grupo estádio clínico segundo TNM. |
| OUTROESTA | Outros estadiamentos clínicos (classificações que não a TNM). |

## Tratamento e desfecho
| Coluna | Descrição |
|---|---|
| CLIATEN | Clínica do primeiro atendimento (Tabela de Clínicas do SisRHC). |
| CLITRAT | Clínica de início do tratamento (Tabela de Clínicas do SisRHC). |
| PRITRATH | Primeiro tratamento no hospital: 1 Nenhum; 2 Cirurgia; 3 Radioterapia; 4 Quimioterapia; 5 Hormonioterapia; 6 Transplante de medula óssea; 7 Imunoterapia; 8 Outras; 9 Sem informação. |
| ESTDFIMT | Estado da doença ao fim do 1º tratamento: 1 Sem evidência (remissão completa); 2 Remissão parcial; 3 Doença estável; 4 Doença em progressão; 5 Suporte terapêutico oncológico; 6 Óbito; 8 Não se aplica; 9 Sem informação. |
| RZNTR | Razão para não realizar tratamento: 1 Recusa; 2 Tratamento fora; 3 Doença avançada/falta de condições; 4 Abandono; 5 Complicações; 6 Óbito; 7 Outras; 8 Não se aplica; 9 Sem informação. |

## Unidade hospitalar
| Coluna | Descrição |
|---|---|
| CNES | CNES do hospital (cruza com cnes_instituicoes_oncologia). |
| MUUH | Município da unidade hospitalar (IBGE). |
| UFUH | Sigla da UF da unidade hospitalar. |
| VALOR_TOT | Valor total (campo do DataSource de origem). |

## Tabela de Clínicas do SisRHC (CLIATEN / CLITRAT)
Códigos relevantes para oncologia: 23 Oncologia Cirúrgica; 24 Oncologia Clínica;
25 Pediatria Oncológica; 31 Radioterapia; 33 Mastologia; 34 Oncologia Cutânea;
38 CEMO; 43 Hemoterapia; 44 Medicina Nuclear; 48 Suporte Terapêutico Oncológico;
17 Hematologia Clínica; 15 Ginecologia; 32 Urologia. Códigos administrativos:
46 Triagem; 88 Não se aplica; 99 Sem informação. A tabela completa tem ~50
clínicas cobrindo todas as especialidades.

## Notas
- O RHC é hospitalar (casos atendidos em unidades com registro), distinto do
  RCBP (base populacional) e do Painel de Oncologia (procedimentos SUS).
- Localização do tumor e morfologia usam a CID-O (Classificação Internacional
  de Doenças para Oncologia), não a CID-10.
- Caso "analítico" (TPCASO=1): diagnóstico e/ou primeiro tratamento na unidade;
  é o recorte mais usado em análises de sobrevida.
