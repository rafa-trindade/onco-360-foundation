# Dicionário: cancer_populacional.parquet

Registro de Câncer de Base Populacional (RCBP), do INCA. Consolida os casos de
câncer diagnosticados na população de áreas geográficas cobertas por Registros
de Câncer de Base Populacional (ex: RCBP Porto Alegre). Diferente do registro
hospitalar (por unidade), o RCBP mede incidência na população. Uma linha por
caso. Snapshot com ~2,37 milhões de casos.

Fonte: snapshot do INCA (arquivo estático, publicado como veio da origem, já
com nomes descritivos e valores decodificados). Os nomes das colunas preservam
o formato original do INCA (com espaços e acentos).

## Identificação e registro
| Coluna | Descrição |
|---|---|
| Código do Paciente | Identificador do caso no RCBP. |
| Nome do RCBP | Registro de origem (ex: RCBP Porto Alegre). |
| Indicador de Caso Raro | Marca casos classificados como raros (true/false). |

## Perfil do paciente
| Coluna | Descrição |
|---|---|
| Sexo | Sexo do paciente (Masculino/Feminino). |
| Data de Nascimento | Data de nascimento (DD/MM/AAAA). |
| Idade | Idade em anos. |
| Raca/Cor | Raça/cor (Branco, Preto, Amarelo, Pardo, Indígena, Sem informação). |
| Nacionalidade | País de nacionalidade. |
| Naturalidade Estado | UF de naturalidade. |
| Naturalidade | Município/local de naturalidade. |
| Grau de Instrução | Escolaridade (ex: Fundamental I, Sem informação). |
| Estado Civil | Estado civil (Solteiro, Casado, Viúvo, etc.). |
| Código Profissão / Nome Profissão | Ocupação (código e descrição). |
| Estado Endereço / Cidade Endereço | UF e município de residência. |

## Tumor: topografia, morfologia e classificações
| Coluna | Descrição |
|---|---|
| Descrição da Topografia / Código da Topografia | Localização primária do tumor (CID-O topografia). |
| Descrição da Morfologia / Código da Morfologia | Tipo histológico (CID-O morfologia). |
| Descrição da Doenca / Código da Doenca | Doença correspondente na CID-10 (ex: C539). |
| Descrição da Doenca Infantil / Código da Doenca Infantil | Classificação Internacional do Câncer na Infância (ICCC), ex: III-F. |
| Descrição da Doenca Adulto Jovem / Código da Doenca Adulto Jovem | Classificação de câncer em adolescentes e adultos jovens. |
| Metástase à distância | CID(s) de sítio(s) de metástase à distância. |

## Diagnóstico e estadiamento
| Coluna | Descrição |
|---|---|
| Meio de Diagnostico | Base do diagnóstico (ex: Histologia do tumor primário). |
| Extensão | Extensão da doença (Localizado, Regional, à Distância, etc.). |
| Lateralidade | Lateralidade do tumor. |
| Estadiamento | Estadiamento clínico (ex: "99 - Sem informação"). |
| TNM | Codificação TNM. |
| Data de Diagnostico | Data do diagnóstico (DD/MM/AAAA). |

## Desfecho
| Coluna | Descrição |
|---|---|
| Status Vital | Situação vital (Vivo/Morto). |
| Tipo do Obito | Se o óbito foi por câncer ou não câncer. |
| Data do Óbito | Data do óbito (DD/MM/AAAA). |
| Data de Último Contato | Data do último contato/acompanhamento (DD/MM/AAAA). |

## Notas
- O RCBP mede incidência populacional; é a base de referência para taxas de
  incidência de câncer por região, diferente do RHC (hospitalar) e do Painel
  de Oncologia (procedimentos SUS).
- Traz três sistemas de classificação da doença em paralelo: CID-10 (Doenca),
  ICCC infantil (Doenca Infantil) e a de adolescentes/adultos jovens, o que
  permite recortes por faixa etária com nomenclatura oncológica adequada.
- Topografia e morfologia seguem a CID-O (padrão oncológico), como no RHC.
- O snapshot já vem decodificado (valores em texto) e com nomes descritivos;
  é publicado sem reprocessamento.
- Campos de data com valores como "Data de Último Contato" anterior ao
  diagnóstico podem ocorrer na origem; não são corrigidos no snapshot.
