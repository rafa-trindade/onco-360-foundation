# Dicionário: cnes_oncologia_instituicoes.parquet

Instituições de saúde com habilitação em alta complexidade em oncologia no SUS.
Uma linha por instituição (CNES), não por habilitação: uma instituição com mais
de uma habilitação (ex: UNACON adulto + pediátrica) aparece uma única vez, com
as habilitações consolidadas.

Fontes combinadas: habilitação (HB, .dbc do FTP DATASUS, filtrada para os
códigos de oncologia), cadastro de estabelecimentos (CSV de dados abertos) e
leitos (LT, .dbc, opcional). Código CNES normalizado em 7 dígitos nos dois
lados antes de cruzar.

| Coluna | Tipo | Descrição |
|---|---|---|
| COD_CNES | texto | Código CNES do estabelecimento (7 dígitos). |
| RAZAO_SOCIAL | texto | Razão social da instituição. |
| NOME_FANTASIA | texto | Nome fantasia. |
| CNPJ | texto | CNPJ do estabelecimento. |
| CNPJ_MANTENEDORA | texto | CNPJ da mantenedora, quando houver. |
| HABILITACOES_ONCOLOGIA | texto | Habilitações de oncologia da instituição, separadas por "; ". |
| QTD_HABILITACOES_ONCOLOGIA | inteiro | Quantidade de habilitações de oncologia. |
| TEM_ONCOLOGIA_PEDIATRICA | booleano | Indica se ao menos uma habilitação é pediátrica. |
| PORTARIAS | texto | Portarias das habilitações, separadas por "; ". |
| DATA_PORTARIA_MAIS_ANTIGA | texto | Data da portaria de habilitação mais antiga. |
| COD_TIPO_UNIDADE | texto | Código do tipo de unidade (CNES). |
| TIPO_UNIDADE | texto | Tipo de unidade decodificado (ex: Hospital Geral, Hospital Especializado). |
| ESFERA_ADMINISTRATIVA | texto | Esfera administrativa (Federal, Estadual, Municipal, Privada). |
| COD_ESFERA_ADMINISTRATIVA | texto | Código da esfera administrativa. |
| COD_NATUREZA_JURIDICA | texto | Código da natureza jurídica (tabela IBGE). |
| TOTAL_LEITOS_CNES | inteiro | Total de leitos do estabelecimento (fonte CNES-Leitos, não recorte de oncologia). Nulo quando o estabelecimento não tem leitos cadastrados. |
| TEM_CENTRO_CIRURGICO | texto | Possui centro cirúrgico (Sim/Não). |
| TEM_CENTRO_OBSTETRICO | texto | Possui centro obstétrico (Sim/Não). |
| TEM_CENTRO_NEONATAL | texto | Possui centro neonatal (Sim/Não). |
| TEM_ATENDIMENTO_HOSPITALAR | texto | Faz atendimento hospitalar (Sim/Não). |
| TEM_ATENDIMENTO_AMBULATORIAL | texto | Faz atendimento ambulatorial (Sim/Não). |
| TEM_SERVICO_APOIO | texto | Possui serviço de apoio (Sim/Não). |
| COD_MUNICIPIO | texto | Código IBGE do município (7 dígitos, com dígito verificador). |
| COD_UF | texto | Código IBGE da UF. |
| CEP | texto | CEP do estabelecimento. |
| LOGRADOURO | texto | Logradouro do endereço. |
| NUMERO_ENDERECO | texto | Número do endereço. |
| BAIRRO | texto | Bairro. |
| LATITUDE | decimal | Latitude do estabelecimento. |
| LONGITUDE | decimal | Longitude do estabelecimento. |
| TELEFONE | texto | Telefone de contato. |
| EMAIL | texto | E-mail de contato. |
| ENCONTRADO_NO_CNES | booleano | False quando a instituição tem habilitação mas não teve correspondência no cadastro de estabelecimentos (demais campos vazios). Nunca é descartada. |

## Notas
- Habilitações de oncologia: códigos 1704-1716 (Portaria SAES/MS 688/2023 e
  antecessoras). Inclui serviços isolados de radio/quimioterapia, UNACON,
  CACON e suas variantes com hematologia ou oncologia pediátrica.
- Contagem de leitos vem do dataset CNES-Leitos (campo de leitos existentes),
  não do campo interno da habilitação (comprovadamente não confiável). É o
  total do estabelecimento, não um recorte de oncologia.
- COD_NATUREZA_JURIDICA fica só com o código (baixo valor analítico para
  oncologia; a esfera administrativa já distingue público de privado).
- Tipo de unidade e esfera administrativa trazem código + descrição, para
  permitir filtro e leitura.
- Removidas as colunas de natureza da organização e nível de hierarquia: estão
  vazias para ~99,98% dos estabelecimentos na origem (campos descontinuados no
  CNES de dados abertos).
