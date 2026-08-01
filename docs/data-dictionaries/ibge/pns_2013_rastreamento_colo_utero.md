# Dicionário: pns_2013_rastreamento_colo_utero.parquet

Comportamento de rastreamento de câncer de colo do útero (exame preventivo /
Papanicolau) das mulheres entrevistadas na PNS 2013 (IBGE). Uma linha por
mulher. Não filtra por diagnóstico: é sobre prevenção na população feminina.

Fonte: microdados de largura fixa da Pesquisa Nacional de Saúde 2013, IBGE.
Posições confirmadas contra o dicionário oficial.

| Coluna | Tipo | Descrição |
|---|---|---|
| ULTIMO_EXAME_PREVENTIVO | texto | Quando fez o último exame preventivo (de "Menos de 1 ano" a "Nunca fez"). |
| FEITO_PELO_SUS | texto | O último exame foi feito pelo SUS (Sim/Não/Não sabe). |
| PAGOU_EXAME | texto | Pagou algo pelo exame (Sim/Não). |
| COBERTO_PLANO_SAUDE | texto | Coberto por plano de saúde (Sim/Não). |
| TEMPO_ATE_RESULTADO | texto | Tempo até receber o resultado do exame preventivo. |
| FEZ_HISTERECTOMIA | texto | Já foi submetida a cirurgia de retirada do útero (Sim/Não). |
| MOTIVO_HISTERECTOMIA | texto | Motivo da retirada do útero (mioma, prolapso, endometriose, câncer ginecológico, complicações de gravidez/parto, sangramento anormal, outro). |
| IDADE_HISTERECTOMIA | inteiro | Idade quando fez a cirurgia de retirada do útero. |
| SEXO | texto | Sexo (Feminino neste recorte). |
| IDADE | inteiro | Idade da respondente na entrevista. |
| COR_RACA | texto | Cor/raça (Branca, Preta, Amarela, Parda, Indígena, Ignorado). |
| COD_UF | texto | Código IBGE da UF. |
| ESTRATO_AMOSTRAL | texto | Estrato do desenho amostral da PNS. |
| UNIDADE_PRIMARIA_AMOSTRAGEM | texto | Unidade primária de amostragem (UPA). |
| NUM_ORDEM_DOMICILIO | texto | Número de ordem do domicílio na PNS. |
| NUM_ORDEM_MORADOR | texto | Número de ordem do morador no domicílio. |

## Notas
- Recorte: mulheres com resposta no bloco de rastreamento.
- A histerectomia (retirada do útero) é relevante para interpretar o
  rastreamento: quem retirou o útero geralmente não precisa mais do exame
  preventivo de colo, o que muda a leitura de "nunca fez".
- Colunas de amostragem permitem estimativas populacionais ponderadas.
