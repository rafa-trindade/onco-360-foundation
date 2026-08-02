"""Catálogo central de fontes e orquestração do pipeline.

Regra arquitetural: `pasta_bucket` define o destino do Parquet e do `_manifest.json`. 
Múltiplas fontes apontando para a mesma pasta consolidam seus metadados e subprodutos no mesmo manifesto.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Fonte:
    id: str
    nome: str
    descricao: str
    pasta_bucket: str
    automatica: bool
    url_origem: str = ""
    extract_modules: list[str] = field(default_factory=list)
    process_modules: list[str] = field(default_factory=list)
    nota: str = ""


FONTES: list[Fonte] = [
    Fonte(
        id="macroregiao",
        nome="Macrorregião de Saúde (geolocalização)",
        descricao="Referência geográfica de municípios (macrorregião/região de saúde e coordenadas), usada pra cruzar com as demais fontes.",
        pasta_bucket="macroregiao",
        automatica=True,
        url_origem="https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbgeral/macroregiao_de_saude_csv.zip",
        extract_modules=["scripts.extract.dados_abertos.fetch_macroregiao_de_saude"],
        process_modules=["scripts.process.dados_abertos.process_macroregiao_de_saude"],
        nota="Dependência manual: requer 'macro_geolocalizacao.xls' em MANUAL_DIR/macroregiao/.",
    ),
    Fonte(
        id="painel_oncologia",
        nome="Painel de Oncologia (DATASUS)",
        descricao="Procedimentos oncológicos realizados no SUS, desde 2013 (diagnóstico, estadiamento, tratamento).",
        pasta_bucket="datasus_po",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/PAINEL_ONCOLOGIA/DADOS",
        extract_modules=["scripts.extract.datasus.fetch_painel_oncologia"],
        process_modules=["scripts.process.datasus.process_painel_oncologia"],
    ),
        Fonte(
        id="siasus_quimioterapia",
        nome="SIASUS - APAC de Quimioterapia",
        descricao="Procedimentos de quimioterapia autorizados no SUS (APAC), com topografia, estadiamento e esquema terapêutico. Desde 2008.",
        pasta_bucket="datasus_siasus",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIASUS/200801_/Dados",
        extract_modules=["scripts.extract.datasus.fetch_siasus_apac_quimioterapia"],
        process_modules=["scripts.process.datasus.process_siasus_quimioterapia"],
    ),
    Fonte(
        id="siasus_radioterapia",
        nome="SIASUS - APAC de Radioterapia",
        descricao="Procedimentos de radioterapia autorizados no SUS (APAC), com topografia, estadiamento e finalidade. Desde 2008.",
        pasta_bucket="datasus_siasus",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIASUS/200801_/Dados",
        extract_modules=["scripts.extract.datasus.fetch_siasus_apac_radioterapia"],
        process_modules=["scripts.process.datasus.process_siasus_radioterapia"],
    ),
    Fonte(
        id="siasus_medicamentos_oncologicos",
        nome="SIASUS - APAC de Medicamentos Oncológicos",
        descricao="Medicamentos de alto custo autorizados no SUS (APAC) com CID principal de neoplasia (C00-D48). Desde 2008.",
        pasta_bucket="datasus_siasus",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIASUS/200801_/Dados",
        extract_modules=["scripts.extract.datasus.fetch_siasus_apac_medicamentos"],
        process_modules=["scripts.process.datasus.process_siasus_medicamentos"],
    ),
        Fonte(
        id="sinan_cancer_trabalho",
        nome="SINAN - Câncer Relacionado ao Trabalho",
        descricao="Notificações de câncer relacionado ao trabalho (agravo C80), com ocupação, exposição ocupacional a agentes cancerígenos e evolução do caso.",
        pasta_bucket="datasus_sinan",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS",
        extract_modules=["scripts.extract.datasus.fetch_sinan_cancer_trabalho"],
        process_modules=["scripts.process.datasus.process_sinan_cancer_trabalho"],
    ),
        Fonte(
        id="siscan_colo_mama",
        nome="SISCAN - Rastreamento de Câncer de Colo e Mama",
        descricao="Conjunto de tabulações agregadas do SISCAN/TABNET que gera arquivos independentes de citopatológico, histopatológico e mamografia para câncer de colo do útero e de mama, nas visões por local de residência e por local de atendimento, com série histórica desde 2013.",
        pasta_bucket="datasus_siscan",
        automatica=True,
        url_origem="http://tabnet.datasus.gov.br/cgi/dhdat.exe?SISCAN/",
        extract_modules=[],
        process_modules=["scripts.process.datasus.process_siscan_cancer"],
    ),
    Fonte(
        id="sim_obitos_cancer_cid9",
        nome="SIM - Óbitos por Câncer, CID-9 (1979-1995)",
        descricao="Óbitos com causa básica de neoplasia maligna (CAUSABAS 140-208), filtrado direto do SIM/DATASUS.",
        pasta_bucket="datasus_sim",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID9/DORES",
        extract_modules=["scripts.extract.datasus.fetch_sim_declaracao_obito_cid9"],
        process_modules=["scripts.process.datasus.process_sim_obitos_cancer_cid9"],
    ),
    Fonte(
        id="sim_obitos_cancer_cid10",
        nome="SIM - Óbitos por Câncer, CID-10 (1996-atual)",
        descricao="Óbitos com causa básica de neoplasia maligna (CAUSABAS C00-C97), filtrado direto do SIM/DATASUS.",
        pasta_bucket="datasus_sim",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES",
        extract_modules=["scripts.extract.datasus.fetch_sim_declaracao_obito_cid10"],
        process_modules=["scripts.process.datasus.process_sim_obitos_cancer_cid10"],
    ),
    Fonte(
        id="sim_obitos_cancer_prelim",
        nome="SIM - Óbitos por Câncer, Preliminar",
        descricao="Mesmo filtro do CID-10 consolidado, aplicado aos dados ainda não fechados/homologados do ano corrente.",
        pasta_bucket="datasus_sim",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/PRELIM/DORES",
        extract_modules=["scripts.extract.datasus.fetch_sim_declaracao_obito_prelim"],
        process_modules=["scripts.process.datasus.process_sim_obitos_cancer_prelim"],
        nota="Zero registros é um estado válido entre ciclos do DATASUS. Subproduto de resumo anual consolidado nesta mesma pasta.",
    ),
    Fonte(
        id="cnes_oncologia_instituicoes",
        nome="CNES - Instituições com Habilitação em Oncologia",
        descricao="Estabelecimentos habilitados em Alta Complexidade em Oncologia (UNACON/CACON/etc.), uma linha por instituição, com sinalizador adulto/pediátrico, endereço/geolocalização, contato e classificação administrativa, cruzado com o cadastro geral do CNES.",
        pasta_bucket="cnes",
        automatica=True,
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/CNES/200508_/Dados/HB",
        extract_modules=[
            "scripts.extract.dados_abertos.fetch_cnes_estabelecimentos",
            "scripts.extract.datasus.fetch_cnes_habilitacao",
            "scripts.extract.datasus.fetch_cnes_leitos",
        ],
        process_modules=["scripts.process.datasus.process_cnes_instituicoes_oncologia"],
        nota="CSV de Estabelecimentos atua apenas como insumo de enriquecimento. Contagem real utiliza a base de Leitos (NULEITOS da Habilitação não é confiável).",
    ),
    Fonte(
        id="inca_cancer_populacional",
        nome="INCA - Registro de Câncer de Base Populacional (RCBP)",
        descricao="Estimativas de incidência de câncer por população.",
        pasta_bucket="inca",
        automatica=False,
        url_origem="https://www.inca.gov.br/BasePopIncidencias/InicioSolicitacaoBaseExterna.action",
        process_modules=["scripts.process.inca.process_cancer_populacional"],
        nota="Download integral descontinuado na origem. Depende de snapshot estático persistente em MANUAL_DIR/inca/cancer_populacional.parquet.",
    ),
    Fonte(
        id="inca_registro_hospitalar",
        nome="INCA - Registro Hospitalar de Câncer (RHC)",
        descricao="Perfil de atendimento hospitalar de pacientes com câncer, por unidade hospitalar.",
        pasta_bucket="inca",
        automatica=False,
        url_origem="https://irhc.inca.gov.br/RHCNet/",
        process_modules=["scripts.process.inca.process_registro_hospitalar"],
        nota="Download restrito por formulário JS/sessão na origem. Depende de snapshot estático persistente em MANUAL_DIR/inca/registro_hospitalar.parquet.",
    ),
    Fonte(
        id="pns_2013_diagnostico_cancer",
        nome="PNS 2013 - Diagnóstico e Tipo de Câncer",
        descricao="Respondentes com diagnóstico médico de câncer autorreferido, tipo (1 categoria por pessoa), idade no diagnóstico e limitação nas atividades.",
        pasta_bucket="ibge",
        automatica=False,
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2013_diagnostico_cancer"],
        nota="Requer MANUAL_DIR/ibge/pns/PNS_2013.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2019_diagnostico_cancer",
        nome="PNS 2019 - Diagnóstico e Tipo de Câncer",
        descricao="Mesmo recorte de 2013, mas o tipo de câncer é registrado como 16 flags binárias independentes (permite mais de 1 tipo por pessoa); sem variável de idade no diagnóstico (removida nesta edição).",
        pasta_bucket="ibge",
        automatica=False,
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2019_diagnostico_cancer"],
        nota="Requer MANUAL_DIR/ibge/pns/PNS_2019.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2013_rastreamento_colo_utero",
        nome="PNS 2013 - Rastreamento de Câncer de Colo do Útero",
        descricao="Comportamento de rastreamento (exame preventivo) de todas as mulheres entrevistadas -- não depende de diagnóstico prévio de câncer.",
        pasta_bucket="ibge",
        automatica=False,
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2013_rastreamento_colo_utero"],
        nota="Requer MANUAL_DIR/ibge/pns/PNS_2013.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2019_rastreamento_colo_utero",
        nome="PNS 2019 - Rastreamento de Câncer de Colo do Útero",
        descricao="Mesmo recorte de 2013, com bloco mais rico: motivo de não ter rastreado, tempo até resultado, encaminhamento após resultado.",
        pasta_bucket="ibge",
        automatica=False,
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2019_rastreamento_colo_utero"],
        nota="Requer MANUAL_DIR/ibge/pns/PNS_2019.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2013_rastreamento_mama",
        nome="PNS 2013 - Rastreamento de Câncer de Mama",
        descricao="Comportamento de rastreamento de mama (exame clínico das mamas e mamografia) das mulheres entrevistadas -- não depende de diagnóstico prévio de câncer.",
        pasta_bucket="ibge",
        automatica=False,
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2013_rastreamento_mama"],
        nota="Requer MANUAL_DIR/ibge/pns/PNS_2013.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2019_rastreamento_mama",
        nome="PNS 2019 - Rastreamento de Câncer de Mama",
        descricao="Mesmo recorte de 2013, com o acréscimo de ida à consulta com especialista após encaminhamento.",
        pasta_bucket="ibge",
        automatica=False,
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2019_rastreamento_mama"],
        nota="Requer MANUAL_DIR/ibge/pns/PNS_2019.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="transparencia_convenios",
        nome="Portal da Transparência - Convênios (repasses por instituição focada em câncer)",
        descricao="Convênios federais cujo objeto menciona câncer/oncologia, cruzados por CNPJ com o CNES para confirmar instituições habilitadas em oncologia (com sinalizador adulto/pediátrico).",
        pasta_bucket="transparencia",
        automatica=True,
        url_origem="https://portaldatransparencia.gov.br/download-de-dados/convenios",
        extract_modules=["scripts.extract.dados_abertos.fetch_convenios_download_dados"],
        process_modules=["scripts.process.dados_abertos.process_convenios_cancer"],
        nota="Atualização semanal via Dados Abertos. Dependência estrita: requer processamento prévio do CNES Habilitação (cruzamento por CNPJ).",
    ),
    Fonte(
        id="transparencia_convenios",
        nome="Portal da Transparência - Convênios (repasses por instituição focada em câncer)",
        descricao="Convênios federais cujo objeto menciona câncer/oncologia, cruzados por CNPJ com o CNES para confirmar instituições habilitadas em oncologia (com sinalizador adulto/pediátrico).",
        pasta_bucket="transparencia",
        automatica=True,
        url_origem="https://portaldatransparencia.gov.br/download-de-dados/convenios",
        extract_modules=["scripts.extract.dados_abertos.fetch_convenios_download_dados"],
        process_modules=["scripts.process.dados_abertos.process_convenios_cancer"],
        nota="Atualização semanal via Dados Abertos. Dependência estrita: requer processamento prévio do CNES Habilitação (cruzamento por CNPJ).",
    ),
]


def get_fonte(id: str) -> Fonte:
    for f in FONTES:
        if f.id == id:
            return f
    raise KeyError(f"Fonte '{id}' não registrada em scripts/config/fontes.py")


def pastas_bucket() -> list[str]:
    vistas = []
    for f in FONTES:
        if f.pasta_bucket not in vistas:
            vistas.append(f.pasta_bucket)
    return vistas
