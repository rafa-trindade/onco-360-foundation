# Dicionário: pns_2019_diagnostico_cancer.parquet

Respondentes da PNS 2019 (IBGE) com diagnóstico médico de câncer autorreferido.
Uma linha por pessoa. Recorte: apenas quem respondeu Sim ao diagnóstico.

Fonte: microdados de largura fixa da Pesquisa Nacional de Saúde 2019, IBGE.
Posições confirmadas contra o dicionário oficial.

Diferente de 2013, o tipo de câncer é registrado como 15 flags binárias
independentes (a pessoa pode ter mais de um tipo). Não há idade no diagnóstico
nesta edição.

| Coluna | Tipo | Descrição |
|---|---|---|
| DIAGNOSTICO_CANCER | texto | Diagnóstico médico de câncer (sempre "Sim" neste recorte). |
| TIPO_PELE | texto | Câncer de pele não melanoma (Sim/Não/Ignorado). |
| TIPO_PELE_MELANOMA | texto | Melanoma de pele (Sim/Não/Ignorado). |
| TIPO_PULMAO | texto | Câncer de pulmão (Sim/Não/Ignorado). |
| TIPO_COLON_RETO | texto | Câncer de cólon/reto (Sim/Não/Ignorado). |
| TIPO_ESTOMAGO | texto | Câncer de estômago (Sim/Não/Ignorado). |
| TIPO_MAMA | texto | Câncer de mama (Sim/Não/Ignorado). |
| TIPO_COLO_UTERO | texto | Câncer de colo do útero (Sim/Não/Ignorado). |
| TIPO_PROSTATA | texto | Câncer de próstata (Sim/Não/Ignorado). |
| TIPO_BOCA_OROFARINGE_LARINGE | texto | Câncer de boca, orofaringe ou laringe (Sim/Não/Ignorado). |
| TIPO_BEXIGA | texto | Câncer de bexiga (Sim/Não/Ignorado). |
| TIPO_LINFOMA_LEUCEMIA | texto | Linfoma ou leucemia (Sim/Não/Ignorado). |
| TIPO_CEREBRO | texto | Câncer de cérebro (Sim/Não/Ignorado). |
| TIPO_OVARIO | texto | Câncer de ovário (Sim/Não/Ignorado). |
| TIPO_TIREOIDE | texto | Câncer de tireoide (Sim/Não/Ignorado). |
| TIPO_OUTRO | texto | Outro tipo de câncer (Sim/Não/Ignorado). |
| LIMITACAO_ATIVIDADES | texto | Grau de limitação nas atividades. |
| SEXO | texto | Sexo (Masculino, Feminino). |
| IDADE | inteiro | Idade do respondente na entrevista. |
| COR_RACA | texto | Cor/raça (Branca, Preta, Amarela, Parda, Indígena, Ignorado). |
| COD_UF | texto | Código IBGE da UF. |
| ESTRATO_AMOSTRAL | texto | Estrato do desenho amostral da PNS. |
| UNIDADE_PRIMARIA_AMOSTRAGEM | texto | Unidade primária de amostragem (UPA). |
| NUM_ORDEM_DOMICILIO | texto | Número de ordem do domicílio na PNS. |
| NUM_ORDEM_MORADOR | texto | Número de ordem do morador no domicílio. |

## Notas
- Autorreferido: baseado no relato do respondente.
- Tipo de câncer em flags binárias: some as flags "Sim" para contar tipos por
  pessoa; a mesma pessoa pode ter mais de um.
- Colunas de amostragem permitem estimativas populacionais ponderadas.
