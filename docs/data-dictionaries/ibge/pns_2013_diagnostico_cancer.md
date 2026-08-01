# Dicionário: pns_2013_diagnostico_cancer.parquet

Respondentes da PNS 2013 (IBGE) com diagnóstico médico de câncer autorreferido.
Uma linha por pessoa. Recorte: apenas quem respondeu Sim ao diagnóstico.

Fonte: microdados de largura fixa da Pesquisa Nacional de Saúde 2013, IBGE.
Posições confirmadas contra o dicionário oficial.

| Coluna | Tipo | Descrição |
|---|---|---|
| DIAGNOSTICO_CANCER | texto | Diagnóstico médico de câncer (sempre "Sim" neste recorte). |
| TIPO_CANCER | texto | Tipo de câncer (categórico, um por pessoa): Pulmão, Intestino, Estômago, Mama, Colo de útero, Próstata, Pele, Outro. |
| IDADE_DIAGNOSTICO | inteiro | Idade no diagnóstico. |
| LIMITACAO_ATIVIDADES | texto | Grau de limitação nas atividades (Não limita a Muito intensamente). |
| SEXO | texto | Sexo (Masculino, Feminino). |
| IDADE | inteiro | Idade do respondente na entrevista. |
| COR_RACA | texto | Cor/raça (Branca, Preta, Amarela, Parda, Indígena, Ignorado). |
| COD_UF | texto | Código IBGE da UF. |
| ESTRATO_AMOSTRAL | texto | Estrato do desenho amostral da PNS. |
| UNIDADE_PRIMARIA_AMOSTRAGEM | texto | Unidade primária de amostragem (UPA). |
| NUM_ORDEM_DOMICILIO | texto | Número de ordem do domicílio na PNS. |
| NUM_ORDEM_MORADOR | texto | Número de ordem do morador no domicílio. |

## Notas
- Autorreferido: baseado no relato do respondente, não em registro clínico.
- Em 2013 o tipo de câncer é categórico (um por pessoa). Na PNS 2019 virou
  flags binárias (permite mais de um tipo).
- Colunas de amostragem (estrato, UPA, ordem) permitem cálculo de estimativas
  populacionais ponderadas.
