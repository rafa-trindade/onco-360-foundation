# Dicionário: pns_2013_rastreamento_mama.parquet

Comportamento de rastreamento de câncer de mama (exame clínico das mamas e
mamografia) das mulheres entrevistadas na PNS 2013 (IBGE). Uma linha por
mulher com resposta no bloco de mama. Não filtra por diagnóstico: é sobre
prevenção na população feminina.

Fonte: microdados de largura fixa da Pesquisa Nacional de Saúde 2013, IBGE.
Posições confirmadas contra o dicionário oficial.

| Coluna | Tipo | Descrição |
|---|---|---|
| ULTIMO_EXAME_CLINICO_MAMAS | texto | Quando um médico/enfermeiro fez o último exame clínico das mamas (de "Menos de 1 ano" a "Nunca fez"). |
| MAMOGRAFIA_SOLICITADA | texto | Algum médico já solicitou mamografia (Sim/Não). |
| FEZ_MAMOGRAFIA | texto | Fez o exame de mamografia (Sim/Não). |
| ULTIMA_MAMOGRAFIA | texto | Quando foi a última mamografia (de "Menos de 1 ano" a "3 anos ou mais"). |
| MAMOGRAFIA_PELO_SUS | texto | A última mamografia foi feita pelo SUS (Sim/Não/Não sabe). |
| PAGOU_MAMOGRAFIA | texto | Pagou algo pela última mamografia (Sim/Não). |
| MAMOGRAFIA_COBERTA_PLANO | texto | A última mamografia foi coberta por plano de saúde (Sim/Não). |
| TEMPO_ATE_RESULTADO | texto | Tempo até receber o resultado da mamografia. |
| ENCAMINHAMENTO_APOS_RESULTADO | texto | Houve encaminhamento após o resultado (Sim/Não/já era com especialista). |
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
- Distingue exame clínico das mamas (feito por profissional) da mamografia
  (exame de imagem), que são etapas diferentes do rastreamento.
- Colunas de amostragem permitem estimativas populacionais ponderadas.
