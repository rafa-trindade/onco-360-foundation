# Dicionário: pns_2019_rastreamento_colo_utero.parquet

Comportamento de rastreamento de câncer de colo do útero (exame preventivo /
Papanicolau) das mulheres entrevistadas na PNS 2019 (IBGE). Uma linha por
mulher. Edição 2019 tem campos adicionais sobre motivo, resultado e
encaminhamento.

Fonte: microdados de largura fixa da Pesquisa Nacional de Saúde 2019, IBGE.
Posições confirmadas contra o dicionário oficial.

| Coluna | Tipo | Descrição |
|---|---|---|
| ULTIMO_EXAME_PREVENTIVO | texto | Quando fez o último exame preventivo (de "Há menos de 1 ano" a "Nunca fez"). |
| MOTIVO_NAO_FEZ | texto | Motivo de não ter feito o exame (13 categorias: nunca teve relações, não acha necessário, dificuldades financeiras, histerectomia, etc.). |
| FEITO_PELO_SUS | texto | O último exame foi feito pelo SUS (Sim/Não/Não sabe). |
| PAGOU_EXAME | texto | Pagou algo pelo exame (Sim/Não/Ignorado). |
| TEMPO_ATE_RESULTADO | texto | Tempo até receber o resultado (de "Menos de 1 mês" a "Nunca recebi"). |
| ENCAMINHAMENTO_APOS_RESULTADO | texto | Houve encaminhamento após o resultado (Sim/Não/já era com especialista/Ignorado). |
| FEZ_HISTERECTOMIA | texto | Já foi submetida a cirurgia de retirada do útero (Sim/Não/Ignorado). |
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
- MOTIVO_NAO_FEZ só é preenchido para quem não fez o exame no prazo recomendado.
- A histerectomia (retirada do útero) é relevante para interpretar o
  rastreamento: quem retirou o útero geralmente não precisa mais do exame
  preventivo de colo.
- Colunas de amostragem permitem estimativas populacionais ponderadas.
