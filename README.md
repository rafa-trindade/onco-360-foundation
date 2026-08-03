![header](docs/images/onco-banner.png)

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-c8922a?labelColor=0d2137)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Dataset-Kaggle-7ab3d4?labelColor=0d2137&logo=kaggle&logoColor=7ab3d4)](https://www.kaggle.com/datasets/rafatrindade/onco-360)
[![GitHub Stars](https://img.shields.io/github/stars/rafa-trindade/onco-360-foundation?style=flat&labelColor=0d2137&color=4a7fa5)](https://github.com/rafa-trindade/onco-360-foundation)

**Onco-360** nasceu da necessidade de reunir, num único lugar e num formato pronto para análise, os dados públicos brasileiros sobre câncer que hoje estão espalhados entre sistemas diferentes do Ministério da Saúde, do IBGE, do INCA e da Controladoria-Geral da União - cada um com seu próprio formato, sua própria periodicidade e sua própria forma de acesso.

O projeto reúne mortalidade por câncer, rede assistencial habilitada em oncologia (com sinalizador adulto/pediátrico, endereço, geolocalização e leitos reais), procedimentos e tratamentos realizados no SUS (quimioterapia, radioterapia, medicamentos de alto custo), rastreamento de colo e mama, diagnóstico e rastreamento autorreferidos pela população, câncer relacionado ao trabalho, repasses públicos federais por instituição, e o perfil de incidência e atendimento hospitalar consolidado pelo INCA - cuidadosamente curados, padronizados e documentados, prontos para que pesquisadores, cientistas de dados e profissionais de saúde possam conduzir seus próprios estudos de forma organizada e reproduzível.

O dataset final está disponível no [Kaggle](https://www.kaggle.com/datasets/rafatrindade/onco-360), com um [notebook de exemplo](https://www.kaggle.com/code/rafatrindade/integra-o-e-vincula-o-de-dados-python) demonstrando como cruzar as bases (rede assistencial, repasses e mortalidade, por UF). Cobre diferentes dimensões do cuidado oncológico no Brasil: desde onde a rede está habilitada a atender e quanto de recurso público ela recebeu, até quem morre, quem é diagnosticado, quem é tratado, quem se previne, e como diferentes fontes descrevem o mesmo problema sob ângulos distintos.

📄 Cada base publicada tem um dicionário de dados próprio em [`docs/data-dictionaries/`](https://github.com/rafa-trindade/onco-360-foundation/tree/main/docs/data-dictionaries) no repositório, descrevendo colunas, decodificações e decisões de processamento.

![header](docs/images/onco-banner-2.png)

## 🏗️ Arquitetura do Pipeline

> Não existe uma pasta local persistida com o histórico completo de dados brutos. O diretório de landing é puramente um scratch space temporário - cada arquivo é baixado, processado e enviado direto ao bucket (MinIO), com o local sendo apagado logo em seguida. A detecção de "isso já existe, não precisa reprocessar" é feita comparando contra um **manifesto** (`_manifest.json`) mantido no próprio bucket, não contra disco local. Cada fonte publica na sua pasta de bucket, e fontes que compartilham a mesma pasta (ex: as três APAC do SIASUS) consolidam seus metadados no mesmo manifesto.

O fluxo é orquestrado por `scripts/run_all.py` em três etapas sequenciais: **extract** (baixa da origem), **process** (filtra o recorte oncológico, decodifica para colunas legíveis e converte para Parquet) e **load** (gera o manifesto de metadados e publica no Kaggle). O `process` só roda se o `extract` reportar dado novo, e o `load` só publica quando pelo menos uma fonte automática traz novidade real - evitando versões vazias no Kaggle e preservando tags/metadados configurados manualmente entre publicações.

---

## 📊 Fontes de Dados e Escopo

### **1. Rede Assistencial Habilitada em Oncologia (Fonte: CNES - DATASUS)**

O **Cadastro Nacional de Estabelecimentos de Saúde (CNES)** é o registro oficial de todos os estabelecimentos de saúde do Brasil. Aqui, é filtrado para as instituições habilitadas em alta complexidade em oncologia (UNACON, CACON e afins).

**Escopo e Processamento:** As habilitações e os leitos vêm via FTP público do DATASUS, organizados por UF e competência; o cadastro geral de estabelecimentos vem via HTTP/ZIP dos Dados Abertos do Ministério da Saúde e atua como insumo de enriquecimento (endereço, CNPJ próprio e da mantenedora, geolocalização, telefone, classificação administrativa). O resultado é uma linha por instituição habilitada, com sinalizador adulto/pediátrico. A contagem de leitos usa a base de Leitos (o campo de leitos da Habilitação não é confiável). Como o CNES é um **retrato** (não uma série histórica que acumula), cada nova competência substitui por completo a anterior.

**Base disponibilizada:**

- `cnes_instituicoes_oncologia.parquet` - Estabelecimentos com habilitação em oncologia: identificação, CNPJ (próprio e da mantenedora), endereço, lat/long, telefone, sinalizador adulto/pediátrico, habilitações, leitos reais, classificação administrativa e capacidades assistenciais.

> BRASIL. Ministério da Saúde. DATASUS. *Cadastro Nacional de Estabelecimentos de Saúde (CNES)*. Brasília, DF: Ministério da Saúde. Disponível em: <https://cnes.datasus.gov.br/>.

---

### **2. Mortalidade por Câncer (Fonte: SIM - DATASUS)**

O **Sistema de Informações sobre Mortalidade (SIM)** consolida as Declarações de Óbito de todo o país desde 1979 e é a base oficial para estatísticas de mortalidade no Brasil.

**Escopo e Processamento:** São baixados via FTP público do DATASUS os arquivos de Declaração de Óbito (`.dbc`) das três eras disponíveis - **CID-9 (1979-1995)**, **CID-10 consolidado (1996-atual)** e **CID-10 preliminar** (dados do ano corrente ainda não fechados) - convertidos para Parquet e filtrados **direto no processamento**, sem materializar a base geral de mortalidade (todas as causas), já que só o recorte de câncer interessa a este projeto. São mantidos os óbitos com causa básica (`CAUSABAS`) de **neoplasia maligna**, confirmada linha a linha contra as tabelas oficiais do DATASUS (capítulo II - Neoplasias): `140`-`208` no CID-9, `C00`-`C97` no CID-10. Faixas adjacentes (carcinoma in situ, neoplasias benignas, comportamento incerto) são deliberadamente excluídas por não serem "câncer" no sentido clínico/epidemiológico padrão - mesma definição usada por INCA e OMS/IARC. As colunas são decodificadas para nomes legíveis em português e o código de município é normalizado, pronto para cruzar com as demais bases sem tratamento adicional.

**Bases disponibilizadas:**

- `obitos_cancer_cid9.parquet` - Óbitos por câncer, 1979-1995.
- `obitos_cancer_cid10.parquet` - Óbitos por câncer, 1996-atual.
- `obitos_cancer_prelim.parquet` - Óbitos por câncer do ano corrente, ainda não consolidados.
- `obitos_cancer_resumo_anual.parquet` - Resumo ano a ano (total de óbitos, total de câncer, proporção), unificado entre as três eras.

*Observação: o arquivo preliminar pode legitimamente conter 0 registros entre ciclos de publicação do DATASUS - não é um erro de processamento.*

> BRASIL. Ministério da Saúde. DATASUS. *Sistema de Informações sobre Mortalidade (SIM)*. Brasília, DF: Ministério da Saúde. Disponível em: <https://datasus.saude.gov.br/mortalidade-desde-1996-pela-cid-10>.

---

### **3. Procedimentos Oncológicos no SUS (Fonte: Painel de Oncologia - DATASUS)**

O **Painel de Oncologia**, disponibilizado pelo DATASUS desde 2013, registra os procedimentos de diagnóstico e tratamento oncológico realizados no âmbito do SUS, reunindo diagnóstico, estadiamento e primeiro tratamento numa mesma base.

**Escopo e Processamento:** Sincronização via FTP público do DATASUS, com conversão dos arquivos `.dbc` para Parquet e decodificação de topografia CID-10, estadiamento, tipo de tratamento e sexo, normalização de idade e exclusão de campos sensíveis do paciente. O processamento é incremental via manifesto - execuções futuras só reprocessam o que for novo.

**Base disponibilizada:**

- `painel_oncologia.parquet` - Procedimentos oncológicos realizados no SUS, desde 2013, com diagnóstico, estadiamento e primeiro tratamento.

> BRASIL. Ministério da Saúde. DATASUS. *Painel de Oncologia*. Brasília, DF: Ministério da Saúde. Disponível em: <https://www.gov.br/inca/pt-br/assuntos/gestor-e-profissional-de-saude/painel-oncologia>.

---

### **4. Tratamento Ambulatorial de Alta Complexidade (Fonte: SIASUS - DATASUS)**

O **Sistema de Informações Ambulatoriais (SIASUS)** registra os procedimentos ambulatoriais de alta complexidade autorizados por APAC, incluindo toda a linha de tratamento oncológico realizada fora da internação.

**Escopo e Processamento:** Baixados via FTP público do DATASUS (série desde 2008), os arquivos `.dbc` são filtrados para as APAC oncológicas e convertidos para Parquet com decodificação de topografia, estadiamento e esquema terapêutico. São publicados os três eixos do tratamento oncológico ambulatorial, cada um na base própria. Processamento incremental via manifesto - só reprocessa competências novas.

**Bases disponibilizadas:**

- `siasus_quimioterapia.parquet` - APAC de quimioterapia, com topografia, estadiamento, linfonodos, grau histopatológico e esquema terapêutico.
- `siasus_radioterapia.parquet` - APAC de radioterapia, com topografia, estadiamento e finalidade (radical/adjuvante/paliativa).
- `siasus_medicamentos_oncologicos.parquet` - APAC de medicamentos de alto custo com CID principal de neoplasia (C00-D48).

> BRASIL. Ministério da Saúde. DATASUS. *Sistema de Informações Ambulatoriais do SUS (SIA/SUS)*. Brasília, DF: Ministério da Saúde. Disponível em: <https://datasus.saude.gov.br/acesso-a-informacao/producao-ambulatorial-sia-sus/>.

---

### **5. Rastreamento de Colo do Útero e Mama (Fonte: SISCAN - DATASUS)**

O **Sistema de Informação do Câncer (SISCAN)** consolida os exames de rastreamento e diagnóstico de câncer de colo do útero e de mama realizados no SUS.

**Escopo e Processamento:** Diferente das demais fontes do DATASUS, o SISCAN **não disponibiliza microdados individuais por FTP** - apenas tabulações agregadas via TABNET. O pipeline consulta o TABNET diretamente (montando as requisições a partir dos arquivos de definição `.def` de cada visão), extrai os resultados em CSV e empilha num formato longo padronizado, com quantidade de exames por UF, ano e resultado do exame. São **dez visões independentes**, combinando o tipo de exame (citopatológico e histopatológico do colo; mamografia, citopatológico e histopatológico da mama) com a perspectiva geográfica (local de residência da paciente ou local de atendimento). A verificação de novidade é **individual por visão**, comparando a data de atualização publicada pelo DATASUS; quando há atualização, apenas os anos mais recentes são reprocessados e mesclados ao histórico, sem refazer a série inteira.

**Bases disponibilizadas (dado agregado, série desde 2013):**

- `cito_colo_residencia.parquet` / `cito_colo_atendimento.parquet` - Citopatológico do colo do útero.
- `histo_colo_residencia.parquet` / `histo_colo_atendimento.parquet` - Histopatológico do colo do útero.
- `mamografia_residencia.parquet` / `mamografia_atendimento.parquet` - Mamografia.
- `cito_mama_residencia.parquet` / `cito_mama_atendimento.parquet` - Citopatológico da mama.
- `histo_mama_residencia.parquet` / `histo_mama_atendimento.parquet` - Histopatológico da mama.

> BRASIL. Ministério da Saúde. DATASUS. *Sistema de Informação do Câncer (SISCAN)*. Brasília, DF: Ministério da Saúde. Disponível em: <https://datasus.saude.gov.br/acesso-a-informacao/sistema-de-informacao-do-cancer-siscan-colo-do-utero-e-mama/>.

---

### **6. Diagnóstico e Rastreamento Declarados (Fonte: PNS - IBGE)**

A **Pesquisa Nacional de Saúde (PNS)** é um inquérito domiciliar do **IBGE**, realizado em parceria com o Ministério da Saúde, que inclui módulos dedicados a diagnóstico de câncer e rastreamento de câncer de colo do útero e de mama - captando o comportamento da população independente de passagem pelo SUS.

**Escopo e Processamento:** Foram utilizados os microdados de posição fixa das duas edições disponíveis (**2013 e 2019**). As posições de cada variável foram conferidas campo a campo contra os dicionários oficiais de cada edição antes de escrever os scripts de extração - as duas edições têm layouts diferentes o suficiente para não serem diretamente comparáveis (2013 registra o tipo de câncer como uma única variável categórica; 2019 usa flags binárias independentes, permitindo mais de um tipo por pessoa, mas removeu a variável de idade no diagnóstico que existia em 2013). São produzidos três recortes por edição: quem relatou diagnóstico de câncer, o rastreamento de colo do útero, e o rastreamento de mama - estes dois últimos cobrindo todas as mulheres entrevistadas, independente de diagnóstico prévio.

**Bases disponibilizadas:**

- `pns_2013_diagnostico_cancer.parquet` / `pns_2019_diagnostico_cancer.parquet` - Diagnóstico, tipo de câncer, e (só em 2013) idade no diagnóstico e limitação nas atividades.
- `pns_2013_rastreamento_colo_utero.parquet` / `pns_2019_rastreamento_colo_utero.parquet` - Rastreamento preventivo (Papanicolau): última vez que fez, motivo de não ter feito e encaminhamento após resultado (só 2019), se foi pelo SUS, histerectomia.
- `pns_2013_rastreamento_mama.parquet` / `pns_2019_rastreamento_mama.parquet` - Rastreamento de mama (exame clínico das mamas e mamografia): resultado e encaminhamento.

*Observação: por serem arquivos volumosos e sujeitos aos termos de uso de download do IBGE, os microdados brutos são obtidos manualmente, não via automação.*

> INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA (IBGE). *Pesquisa Nacional de Saúde (PNS)*. Rio de Janeiro: IBGE. Disponível em: <https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html>.

---

### **7. Incidência e Perfil Hospitalar (Fonte: INCA)**

O **Instituto Nacional de Câncer (INCA)** mantém dois sistemas de referência nacional: o **Registro de Câncer de Base Populacional (RCBP)**, com estimativas de incidência por população, e o **Registro Hospitalar de Câncer (RHC)**, com o perfil de atendimento hospitalar por unidade.

**Escopo e Processamento:** Bases **estáticas**, trazidas manualmente a partir de um snapshot já publicado. O INCA descontinuou o download integral do RCBP (o arquivo consolidado ficou grande demais; hoje a base só é disponibilizada por solicitação, um registro e uma janela de 4 anos por vez) e o download do RHC é gerado dinamicamente via formulário com sessão (sem URL fixa automatizável) - nenhum dos dois se presta a um pipeline de sincronização automática nos moldes das demais fontes deste projeto. A publicação (sem transformação) é automatizada.

**Bases disponibilizadas:**

- `cancer_populacional.parquet` - Estimativas de incidência de câncer por população (RCBP).
- `registro_hospitalar.parquet` - Perfil de atendimento hospitalar de pacientes com câncer (RHC).

> BRASIL. Ministério da Saúde. Instituto Nacional de Câncer (INCA). *Registro de Câncer de Base Populacional* e *Registro Hospitalar de Câncer*. Rio de Janeiro: INCA. Disponível em: <https://www.inca.gov.br/>.

---

### **8. Câncer Relacionado ao Trabalho (Fonte: SINAN - DATASUS)**

O **Sistema de Informação de Agravos de Notificação (SINAN)** registra as notificações de câncer relacionado ao trabalho - a única fonte deste acervo que capta a exposição ocupacional a agentes cancerígenos ao longo da vida profissional.

**Escopo e Processamento:** Baixado via FTP público do DATASUS (arquivos `CANCBR` das pastas FINAIS e PRELIM, nível Brasil), convertido para Parquet com decodificação de ocupação (CBO), situação no mercado de trabalho, evolução do caso e das exposições ocupacionais - asbesto, sílica, benzeno, radiações ionizantes e não ionizantes, antineoplásicos, cromo, níquel, aminas aromáticas, entre outras, cada uma como um campo próprio (Sim/Não/Ignorado). A idade codificada do SINAN é normalizada para anos.

**Base disponibilizada:**

- `cancer_relacionado_ao_trabalho.parquet` - Notificações de câncer relacionado ao trabalho (agravo C80), com ocupação, situação no mercado de trabalho, exposição ocupacional a agentes cancerígenos e evolução do caso.

> BRASIL. Ministério da Saúde. DATASUS. *Sistema de Informação de Agravos de Notificação (SINAN)*. Brasília, DF: Ministério da Saúde. Disponível em: <https://datasus.saude.gov.br/sinan/>.

---

### **9. Repasses Públicos por Instituição Oncológica (Fonte: Portal da Transparência)**

O **Portal da Transparência do Governo Federal** disponibiliza, via mecanismo público de **Dados Abertos** (sem chave de API, sem login), o histórico completo de convênios federais - incluindo o CNPJ do beneficiário, o que permite cruzar diretamente com o CNES.

**Escopo e Processamento:** São baixados os convênios acumulados **desde 1996** (o arquivo é sempre o histórico completo até a data de referência, não um recorte por período - a fonte é atualizada semanalmente, e o pipeline detecta e baixa sempre a atualização mais recente). São mantidos apenas os convênios cujo objeto menciona câncer/oncologia (filtro por palavra-chave), cruzados por CNPJ com `cnes_instituicoes_oncologia.parquet` - com **fallback para o CNPJ da entidade mantenedora** quando a unidade não tem CNPJ próprio (comum em hospitais universitários e redes, ex: EBSERH), sinalizado explicitamente em `CNES_VIA_CNPJ_MANTENEDORA`.

**Base disponibilizada:**

- `convenios_cancer.parquet` - Convênios federais com objeto relacionado a câncer/oncologia, já cruzados com a instituição beneficiária (nome, endereço, geolocalização, sinalizador adulto/pediátrico).

> BRASIL. Controladoria-Geral da União (CGU). *Portal da Transparência*. Brasília, DF: CGU. Disponível em: <https://portaldatransparencia.gov.br/>.

---

### **10. Base Auxiliar (Macrorregião de Saúde)**

Para permitir cruzamentos geográficos entre as demais bases, o projeto conta com uma base auxiliar de referência, construída a partir de **dados abertos do Ministério da Saúde**.

**Escopo e Processamento:** o arquivo de municípios (Dados Abertos da Saúde) é combinado, via join no código do município (com correção de zero à esquerda), com um arquivo complementar de geolocalização.

**Base disponibilizada:**

- `geo_macroregiao.parquet` - Municípios brasileiros associados às suas macrorregiões de saúde, regiões de saúde, UF e coordenadas geográficas.

---

## 🗓️ Cobertura Histórica

O repositório combina diferentes janelas temporais, de acordo com a fonte:

- **SIM/DATASUS (mortalidade):** série histórica desde 1979 (CID-9) até o ano corrente (CID-10 preliminar), com atualização contínua.
- **Painel de Oncologia:** desde 2013, com atualização contínua.
- **SIASUS (quimio/radio/medicamentos):** desde 2008, com atualização contínua.
- **SISCAN (rastreamento colo/mama):** dado agregado, desde 2013.
- **CNES (Estabelecimentos/Habilitações/Leitos):** retrato do mês mais recente disponível (não histórico).
- **SINAN (câncer do trabalho):** notificações a partir dos anos 2000.
- **Portal da Transparência (Convênios):** acumulado desde 1996, atualizado semanalmente - é a fonte com a cadência de atualização mais frequente do projeto.
- **PNS/IBGE:** edições pontuais de 2013 e 2019 (periodicidade do próprio inquérito).
- **INCA (RCBP/RHC):** snapshots estáticos, na cobertura temporal da última extração disponível antes da descontinuação do download integral.

---

## 🔄 Atualização e Confiabilidade

Nem todas as fontes têm a mesma dinâmica de atualização:

- **SIM, Painel de Oncologia, SIASUS, SINAN, CNES, Portal da Transparência:** sincronização totalmente automatizada (FTP ou Dados Abertos), com detecção de novidade real (por tamanho/hash de conteúdo) antes de reprocessar ou publicar - nenhuma dessas fontes reprocessa ou republica à toa quando nada mudou na origem.
- **SISCAN:** sincronização automatizada via TABNET, com verificação **individual por visão** (data de atualização do DATASUS) e reprocessamento apenas dos anos recentes, mesclados ao histórico.
- **PNS/IBGE:** bases estáticas por edição - cada edição é um retrato fechado no tempo, incorporada quando o IBGE publica os microdados oficiais. O processamento é automatizado; a obtenção do microdado bruto é manual.
- **INCA (RCBP/RHC):** bases estáticas, sem pipeline de atualização (ver Fontes de Dados acima para o motivo).

O pipeline só publica uma nova versão (bucket + Kaggle) quando pelo menos uma fonte automatizada reporta dado novo de verdade - evita gerar versões vazias no Kaggle e preserva tags/metadados configurados manualmente entre publicações.

---

## 📁 Estrutura de Pastas do Dataset

```
cnes/
  cnes_instituicoes_oncologia.parquet

datasus_sim/
  obitos_cancer_cid9.parquet
  obitos_cancer_cid10.parquet
  obitos_cancer_prelim.parquet
  obitos_cancer_resumo_anual.parquet

datasus_po/
  painel_oncologia.parquet

datasus_siasus/
  siasus_quimioterapia.parquet
  siasus_radioterapia.parquet
  siasus_medicamentos_oncologicos.parquet

datasus_siscan/
  cito_colo_residencia.parquet, cito_colo_atendimento.parquet
  histo_colo_residencia.parquet, histo_colo_atendimento.parquet
  mamografia_residencia.parquet, mamografia_atendimento.parquet
  cito_mama_residencia.parquet, cito_mama_atendimento.parquet
  histo_mama_residencia.parquet, histo_mama_atendimento.parquet

datasus_sinan/
  cancer_relacionado_ao_trabalho.parquet

ibge/
  pns_2013_diagnostico_cancer.parquet, pns_2019_diagnostico_cancer.parquet
  pns_2013_rastreamento_colo_utero.parquet, pns_2019_rastreamento_colo_utero.parquet
  pns_2013_rastreamento_mama.parquet, pns_2019_rastreamento_mama.parquet

inca/
  cancer_populacional.parquet
  registro_hospitalar.parquet

transparencia/
  convenios_cancer.parquet

macroregiao/
  geo_macroregiao.parquet

onco360-metadados.csv   -- manifesto de todos os arquivos: fonte(s), descrição,
                           contagem de registros, tamanho e data de modificação
```

---

## 📄 Licença e Créditos

Este dataset consolidado é disponibilizado sob licença **CC0 1.0** (domínio público). Isso se refere ao trabalho de curadoria, padronização e harmonização realizado neste repositório - os dados originais permanecem de titularidade e responsabilidade das instituições abaixo, que devem ser citadas ao utilizar cada fonte individualmente:

- **DATASUS (CNES, SIM, Painel de Oncologia, SIASUS, SISCAN, SINAN):**
  > BRASIL. Ministério da Saúde. DATASUS. Brasília, DF: Ministério da Saúde. Disponível em: <https://datasus.saude.gov.br/>.

- **IBGE (Pesquisa Nacional de Saúde):**
  > INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA (IBGE). *Pesquisa Nacional de Saúde (PNS)*. Rio de Janeiro: IBGE. Disponível em: <https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html>.

- **INCA (RCBP e RHC):**
  > BRASIL. Ministério da Saúde. Instituto Nacional de Câncer (INCA). Rio de Janeiro: INCA. Disponível em: <https://www.inca.gov.br/>.

- **Portal da Transparência (Convênios):**
  > BRASIL. Controladoria-Geral da União (CGU). *Portal da Transparência*. Brasília, DF: CGU. Disponível em: <https://portaldatransparencia.gov.br/>.

Se você utilizar este dataset em pesquisas, reportagens ou análises, considere citar tanto a fonte original relevante (acima) quanto este repositório de curadoria.

---

#### **Idealização e manutenção:**
- [Rafael Trindade](https://www.linkedin.com/in/rafatrindade/)
