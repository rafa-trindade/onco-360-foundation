# Dicionário: pns_2019_rastreamento_mama.parquet

Comportamento de rastreamento de câncer de mama (exame clínico das mamas e
mamografia) das mulheres entrevistadas na PNS 2019 (IBGE). Uma linha por
mulher com resposta no bloco de mama.

Fonte: microdados de largura fixa da Pesquisa Nacional de Saúde 2019, IBGE.
Posições confirmadas contra o dicionário oficial.

| Coluna | Tipo | Descrição |
|---|---|---|
| ULTIMO_EXAME_CLINICO_MAMAS | texto | Quando um médico/enfermeiro fez o último exame clínico das mamas. |
| MAMOGRAFIA_SOLICITADA | texto | Algum médico já solicitou mamografia (Sim/Não/Ignorado). |
| FEZ_MAMOGRAFIA | texto | Fez o exame de mamografia (Sim/Não/Ignorado). |
| ULTIMA_MAMOGRAFIA | texto | Quando foi a última mamografia. |
| MAMOGRAFIA_PELO_SUS | texto | A última mamografia foi feita pelo SUS (Sim/Não/Não sabe). |
| PAGOU_MAMOGRAFIA | texto | Pagou algo pela última mamografia (Sim/Não/Ignorado). |
| TEMPO_ATE_RESULTADO | texto | Tempo até receber o resultado da mamografia. |
| ENCAMINHAMENTO_APOS_RESULTADO | texto | Houve encaminhamento após o resultado (Sim/Não/já era com especialista/Ignorado). |
| FOI_A_CONSULTA_ESPECIALISTA | texto | Foi à consulta com o especialista após encaminhamento (Sim/Não). |
| SEXO | texto | Sexo (Feminino neste recorte). |
| IDADE | inteiro | Idade da respondente na entrevista. |
| COR_RACA | texto | Cor/raça (Branca, Preta, Amarela, Parda, Indígena, Ignorado). |
| COD_UF | texto | Código IBGE da UF. |
| ESTRATO_AMOSTRAL | texto | Estrato do desenho amostral da PNS. |
| UNIDADE_PRIMARIA_AMOSTRAGEM | texto | Unidade primária de amostragem (UPA). |
| NUM_ORDEM_DOMICILIO | texto | Número de ordem do domicílio na PNS. |
| NUM_ORDEM_MORADOR | texto | Número de ordem do morador no domicílio. |

## Notas
- Recorte: mulheres com resposta no bloco de rastreamento de mama.
- Diferente de 2013, 2019 acrescenta se a mulher foi à consulta com o
  especialista após encaminhamento, mas não tem o campo de cobertura por plano.
- Colunas de amostragem permitem estimativas populacionais ponderadas.
