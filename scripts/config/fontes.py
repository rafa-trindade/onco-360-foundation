"""
Registro central de todas as fontes de dados do onco-360-foundation.

Usado por:
  - run_all.py           -- orquestra extract+process de cada fonte
  - process_metadados.py -- gera o manifesto raw_onco360_metadados.csv

Para adicionar uma fonte nova: escreva o extract/process normalmente,
seguindo o padrão das fontes existentes, e adicione uma entrada aqui.
Nada mais precisa ser editado -- run_all.py e o gerador de metadados já
pegam automaticamente.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Fonte:
    id: str
    nome: str
    descricao: str
    tipo: str  # "pipeline" (extract+process automatizados) ou "estatico" (manual/Kaggle)
    url_origem: str
    extract_modules: list[str] = field(default_factory=list)
    process_modules: list[str] = field(default_factory=list)
    arquivos_saida: list[str] = field(default_factory=list)  # relativo a data/raw/
    nota: str = ""


FONTES: list[Fonte] = [
    Fonte(
        id="macroregiao_de_saude",
        nome="Macrorregião de Saúde (geolocalização)",
        descricao="Referência geográfica de municípios -- macrorregião/região de saúde e coordenadas, usada pra cruzar com as demais fontes.",
        tipo="pipeline",
        url_origem="https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbgeral/macroregiao_de_saude_csv.zip",
        extract_modules=["scripts.extract.dados_abertos.fetch_macroregiao_de_saude"],
        process_modules=["scripts.process.dados_abertos.process_macroregiao_de_saude"],
        arquivos_saida=["raw_macroregiao_de_saude.parquet"],
        nota="Precisa da planilha 'macro_geolocalizacao.xls' colocada manualmente em data/landing/macroregiao/.",
    ),
    Fonte(
        id="painel_oncologia",
        nome="Painel de Oncologia (DATASUS)",
        descricao="Procedimentos oncológicos realizados no SUS, desde 2013 -- diagnóstico, estadiamento, tratamento.",
        tipo="pipeline",
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/PAINEL_ONCOLOGIA/DADOS",
        extract_modules=["scripts.extract.datasus.fetch_painel_oncologia"],
        process_modules=["scripts.process.datasus.process_painel_oncologia"],
        arquivos_saida=["raw_painel_de_oncologia.parquet"],
    ),
    Fonte(
        id="sim_obitos_cancer_cid9",
        nome="SIM - Óbitos por Câncer, CID-9 (1979-1995)",
        descricao="Óbitos com causa básica de neoplasia maligna (CAUSABAS 140-208), filtrado direto do SIM/DATASUS.",
        tipo="pipeline",
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID9/DORES",
        extract_modules=["scripts.extract.datasus.fetch_sim_declaracao_obito_cid9"],
        process_modules=["scripts.process.datasus.process_sim_obitos_cancer_cid9"],
        arquivos_saida=["raw_sim_obitos_cancer_cid9.parquet"],
    ),
    Fonte(
        id="sim_obitos_cancer_cid10",
        nome="SIM - Óbitos por Câncer, CID-10 (1996-atual)",
        descricao="Óbitos com causa básica de neoplasia maligna (CAUSABAS C00-C97), filtrado direto do SIM/DATASUS.",
        tipo="pipeline",
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES",
        extract_modules=["scripts.extract.datasus.fetch_sim_declaracao_obito_cid10"],
        process_modules=["scripts.process.datasus.process_sim_obitos_cancer_cid10"],
        arquivos_saida=["raw_sim_obitos_cancer_cid10.parquet"],
    ),
    Fonte(
        id="sim_obitos_cancer_prelim",
        nome="SIM - Óbitos por Câncer, Preliminar",
        descricao="Mesmo filtro do CID-10 consolidado, aplicado aos dados ainda não fechados/homologados do ano corrente.",
        tipo="pipeline",
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/PRELIM/DORES",
        extract_modules=["scripts.extract.datasus.fetch_sim_declaracao_obito_prelim"],
        process_modules=["scripts.process.datasus.process_sim_obitos_cancer_prelim"],
        arquivos_saida=["raw_sim_obitos_cancer_prelim.parquet"],
        nota="Pode legitimamente ter 0 registros entre ciclos de publicação do DATASUS -- não é erro.",
    ),
    Fonte(
        id="cnes_oncologia_instituicoes",
        nome="CNES - Instituições com Habilitação em Oncologia",
        descricao="Estabelecimentos habilitados em Alta Complexidade em Oncologia (UNACON/CACON/etc.), uma linha por instituição, com sinalizador adulto/pediátrico, endereço/geolocalização, contato e classificação administrativa, já cruzado com o cadastro geral do CNES.",
        tipo="pipeline",
        url_origem="ftp://ftp.datasus.gov.br/dissemin/publicos/CNES/200508_/Dados/HB",
        extract_modules=[
            "scripts.extract.dados_abertos.fetch_cnes_estabelecimentos",  # traz o CSV bruto de referência (não publicado sozinho -- só insumo)
            "scripts.extract.datasus.fetch_cnes_habilitacao",
            "scripts.extract.datasus.fetch_cnes_leitos",  # contagem real de leitos (o NULEITOS de dentro do Habilitação não é confiável)
        ],
        process_modules=["scripts.process.datasus.process_cnes_oncologia_instituicoes"],
        arquivos_saida=["raw_cnes_oncologia_instituicoes.parquet"],
        nota="O CNES de Estabelecimentos não é mais publicado como raw_*.parquet próprio -- "
             "serve só como insumo (lido direto do CSV da Landing) pra enriquecer esta fonte.",
    ),
    Fonte(
        id="inca_cancer_populacional",
        nome="INCA - Registro de Câncer de Base Populacional (RCBP)",
        descricao="Estimativas de incidência de câncer por população.",
        tipo="estatico",
        url_origem="https://www.inca.gov.br/BasePopIncidencias/InicioSolicitacaoBaseExterna.action",
        arquivos_saida=["raw_inca_cancer_populacional.parquet"],
        nota="O INCA descontinuou o download integral desta base (arquivo ficou grande demais). "
             "Snapshot estático trazido manualmente do dataset já publicado no Kaggle.",
    ),
    Fonte(
        id="inca_registro_hospitalar",
        nome="INCA - Registro Hospitalar de Câncer (RHC)",
        descricao="Perfil de atendimento hospitalar de pacientes com câncer, por unidade hospitalar.",
        tipo="estatico",
        url_origem="https://irhc.inca.gov.br/RHCNet/",
        arquivos_saida=["raw_inca_registro_hospitalar.parquet"],
        nota="Download gerado via formulário JS/sessão (sem URL fixa automatizável). "
             "Snapshot estático trazido manualmente do dataset já publicado no Kaggle.",
    ),
    Fonte(
        id="pns_2013_diagnostico_cancer",
        nome="PNS 2013 - Diagnóstico e Tipo de Câncer",
        descricao="Respondentes com diagnóstico médico de câncer autorreferido, tipo (1 categoria por pessoa), idade no diagnóstico e limitação nas atividades.",
        tipo="pipeline_manual",  # process automatizado, extract manual (microdado grande, baixado do IBGE)
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2013_diagnostico_cancer"],
        arquivos_saida=["raw_pns_2013_diagnostico_cancer.parquet"],
        nota="Requer data/landing/ibge/PNS_2013.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2019_diagnostico_cancer",
        nome="PNS 2019 - Diagnóstico e Tipo de Câncer",
        descricao="Mesmo recorte de 2013, mas tipo de câncer é registrado como 16 flags binárias independentes (permite mais de 1 tipo por pessoa); sem variável de idade no diagnóstico (removida nesta edição).",
        tipo="pipeline_manual",
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2019_diagnostico_cancer"],
        arquivos_saida=["raw_pns_2019_diagnostico_cancer.parquet"],
        nota="Requer data/landing/ibge/PNS_2019.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2013_rastreamento_colo_utero",
        nome="PNS 2013 - Rastreamento de Câncer de Colo do Útero",
        descricao="Comportamento de rastreamento (exame preventivo) de todas as mulheres entrevistadas -- não depende de diagnóstico prévio de câncer.",
        tipo="pipeline_manual",
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2013_rastreamento_colo_utero"],
        arquivos_saida=["raw_pns_2013_rastreamento_colo_utero.parquet"],
        nota="Requer data/landing/ibge/PNS_2013.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="pns_2019_rastreamento_colo_utero",
        nome="PNS 2019 - Rastreamento de Câncer de Colo do Útero",
        descricao="Mesmo recorte de 2013, com bloco mais rico: motivo de não ter rastreado, tempo até resultado, encaminhamento após resultado.",
        tipo="pipeline_manual",
        url_origem="https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html",
        process_modules=["scripts.process.ibge.process_pns_2019_rastreamento_colo_utero"],
        arquivos_saida=["raw_pns_2019_rastreamento_colo_utero.parquet"],
        nota="Requer data/landing/ibge/PNS_2019.txt baixado manualmente do IBGE.",
    ),
    Fonte(
        id="portal_transparencia_convenios",
        nome="Portal da Transparência - Convênios (repasses por instituição focada em câncer)",
        descricao="Convênios federais cujo objeto menciona câncer/oncologia, cruzados por CNPJ com o CNES para confirmar instituições habilitadas em oncologia (com sinalizador adulto/pediátrico).",
        tipo="pipeline",
        url_origem="https://portaldatransparencia.gov.br/download-de-dados/convenios",
        extract_modules=["scripts.extract.dados_abertos.fetch_convenios_download_dados"],
        process_modules=["scripts.process.dados_abertos.process_convenios_cancer"],
        arquivos_saida=["raw_convenios_cancer.parquet"],
        nota="Via mecanismo público de Dados Abertos (sem chave de API) -- acumulado desde 1996, "
             "atualizado semanalmente. Depende do CNES Habilitação já processado (cruzamento por CNPJ).",
    ),
]


def get_fonte(id: str) -> Fonte:
    for f in FONTES:
        if f.id == id:
            return f
    raise KeyError(f"Fonte '{id}' não registrada em scripts/config/fontes.py")