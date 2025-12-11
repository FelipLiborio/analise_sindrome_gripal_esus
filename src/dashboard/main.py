import streamlit as st
import pandas as pd
import plotly.express as px
import json
import urllib.request
from db import query
from queries import *

st.set_page_config(page_title="Dashboard Síndrome Gripal ESUS", layout="wide")

st.title("Dashboard Interativo - Análise de Síndrome Gripal (ESUS)")


# Carregar dados
@st.cache_data
def load_data(query_str):
    return query(query_str)


# Dados principais
df_confirmados = load_data(Q_EVOLUCAO_CONFIRMADOS)
df_suspeitos = load_data(Q_EVOLUCAO_SUSPEITOS)
df_obitos = load_data(Q_EVOLUCAO_OBITOS)
df_total = load_data(Q_EVOLUCAO_TOTAL)
df_distribuicao = {
    "Sexo": {
        "Confirmados": load_data(Q_DISTRIBUICAO_CONFIRMADOS_SEXO),
        "Suspeitos": load_data(Q_DISTRIBUICAO_SUSPEITOS_SEXO),
        "Notificações": load_data(Q_DISTRIBUICAO_TOTAL_SEXO),
        "Óbitos": load_data(Q_DISTRIBUICAO_OBITOS_SEXO),
    },
    "Faixa Etária": {
        "Confirmados": load_data(Q_DISTRIBUICAO_CONFIRMADOS_IDADE),
        "Suspeitos": load_data(Q_DISTRIBUICAO_SUSPEITOS_IDADE),
        "Notificações": load_data(Q_DISTRIBUICAO_TOTAL_IDADE),
        "Óbitos": load_data(Q_DISTRIBUICAO_OBITOS_IDADE),
    },
    "Raça/Cor": {
        "Confirmados": load_data(Q_DISTRIBUICAO_CONFIRMADOS_RACA),
        "Suspeitos": load_data(Q_DISTRIBUICAO_SUSPEITOS_RACA),
        "Notificações": load_data(Q_DISTRIBUICAO_TOTAL_RACA),
        "Óbitos": load_data(Q_DISTRIBUICAO_OBITOS_RACA),
    },
    "Ocupação": {
        "Confirmados": load_data(Q_DISTRIBUICAO_CONFIRMADOS_OCUPACAO),
        "Suspeitos": load_data(Q_DISTRIBUICAO_SUSPEITOS_OCUPACAO),
        "Notificações": load_data(Q_DISTRIBUICAO_TOTAL_OCUPACAO),
        "Óbitos": load_data(Q_DISTRIBUICAO_OBITOS_OCUPACAO),
    },
}
df_vacinacao = load_data(Q_VACINACAO_CONFIRMACAO)
df_testes = load_data(Q_TESTES_TIPO_FABRICANTE)
df_mapa = load_data(Q_MAPA_CALOR)
df_mapa_confirmados = load_data(Q_MAPA_CALOR_CONFIRMADOS)
df_mapa_suspeitos = load_data(Q_MAPA_CALOR_SUSPEITOS)
df_mapa_obitos = load_data(Q_MAPA_CALOR_OBITOS)


# Mapeamento de regiões do Pará
def get_regiao(municipio):
    regioes = {
        "Metropolitana de Belém": [
            "Belém",
            "Ananindeua",
            "Marituba",
            "Benevides",
            "Santa Bárbara do Pará",
            "Castanhal",
        ],
        "Nordeste": [
            "Bragança",
            "Capanema",
            "Capitão Poço",
            "Igarapé-Açu",
            "Nova Timboteua",
            "Ourém",
            "Peixe-Boi",
            "Primavera",
            "Quatipuru",
            "Santa Luzia do Pará",
            "Santo Antônio do Tauá",
            "Tracuateua",
            "Viseu",
        ],
        "Sudeste": [
            "Marabá",
            "Parauapebas",
            "Canaã dos Carajás",
            "Curionópolis",
            "Eldorado do Carajás",
            "Paragominas",
            "Redenção",
            "São Félix do Xingu",
            "Tucuruí",
            "Xinguara",
            "Conceição do Araguaia",
        ],
        "Marajó": [
            "Soure",
            "Salvaterra",
            "Cachoeira do Arari",
            "Santa Cruz do Arari",
            "Chaves",
            "Ponta de Pedras",
            "Curralinho",
            "São Sebastião da Boa Vista",
        ],
        "Baixo Amazonas": [
            "Santarém",
            "Alenquer",
            "Monte Alegre",
            "Prainha",
            "Juruti",
            "Óbidos",
            "Oriximiná",
        ],
        "Oeste": [
            "Altamira",
            "Itaituba",
            "Jacareacanga",
            "Novo Progresso",
            "Trairão",
            "Rurópolis",
        ],
    }
    for regiao, municipios in regioes.items():
        if municipio in municipios:
            return regiao
    return "Outros"


df_regioes = df_mapa.copy()
df_regioes["regiao"] = df_regioes["municipio"].apply(get_regiao)
df_regioes = df_regioes.groupby("regiao")["total_notificacoes"].sum().reset_index()

# Adicionar coordenadas para mapa geográfico
coordenadas = {
    "Metropolitana de Belém": {"lat": -1.4558, "lon": -48.5044},
    "Nordeste": {"lat": -1.05, "lon": -46.77},
    "Sudeste": {"lat": -5.37, "lon": -49.12},
    "Marajó": {"lat": -0.72, "lon": -48.52},
    "Baixo Amazonas": {"lat": -2.44, "lon": -54.71},
    "Oeste": {"lat": -3.20, "lon": -52.21},
    "Outros": {"lat": -2.5, "lon": -49.5},
}
df_regioes["lat"] = df_regioes["regiao"].map(
    lambda x: coordenadas.get(x, {"lat": -2.5, "lon": -49.5})["lat"]
)
df_regioes["lon"] = df_regioes["regiao"].map(
    lambda x: coordenadas.get(x, {"lat": -2.5, "lon": -49.5})["lon"]
)


# Baixar GeoJSON dos municípios do Pará
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-15-mun.json"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())


geojson_para = load_geojson()

# Gráfico 1: Linha - Evolução Temporal
st.header("Evolução Temporal")
tipo_dado = st.selectbox(
    "Escolha o tipo de dado:",
    ["Confirmados", "Suspeitos", "Óbitos", "Total Notificações"],
)
all_municipios = (
    df_confirmados["municipio"].unique()
    if tipo_dado == "Confirmados"
    else (
        df_suspeitos["municipio"].unique()
        if tipo_dado == "Suspeitos"
        else (
            df_obitos["municipio"].unique()
            if tipo_dado == "Óbitos"
            else df_total["municipio"].unique()
        )
    )
)
municipio_select = st.selectbox(
    "Escolha um município (ou 'Todos'):", ["Todos"] + list(all_municipios)
)

# Filtro de período
if tipo_dado == "Confirmados":
    meses_disponiveis = sorted(df_confirmados["mes"].unique())
elif tipo_dado == "Suspeitos":
    meses_disponiveis = sorted(df_suspeitos["mes"].unique())
elif tipo_dado == "Óbitos":
    meses_disponiveis = sorted(df_obitos["mes"].unique())
else:
    meses_disponiveis = sorted(df_total["mes"].unique())

mes_inicio, mes_fim = st.select_slider(
    "Selecione o período:",
    options=meses_disponiveis,
    value=(meses_disponiveis[0], meses_disponiveis[-1]),
)

if tipo_dado == "Confirmados":
    df_base = df_confirmados
    y_col = "total_confirmados"
    title = "Evolução de Casos Confirmados"
    color_col = None
elif tipo_dado == "Suspeitos":
    df_base = df_suspeitos
    y_col = "total_suspeitos"
    title = "Evolução de Casos Suspeitos"
    color_col = None
elif tipo_dado == "Óbitos":
    df_base = df_obitos
    y_col = "total_obitos"
    title = "Evolução de Óbitos"
    color_col = None
else:  # Total Notificações
    df_base = df_total
    y_col = "total_notificacoes"
    title = "Evolução de Total Notificações"
    color_col = None

if df_base.empty:
    st.write(f"Nenhum dado encontrado para {tipo_dado.lower()}.")
else:
    if municipio_select == "Todos":
        df_plot = df_base.groupby("mes")[y_col].sum().reset_index()
        df_plot = df_plot[(df_plot["mes"] >= mes_inicio) & (df_plot["mes"] <= mes_fim)]
        fig_linha = px.line(
            df_plot,
            x="mes",
            y=y_col,
            title=f"{title} - Total ({mes_inicio} a {mes_fim})",
            color_discrete_sequence=(
                ["blue"]
                if tipo_dado == "Confirmados"
                else (
                    ["orange"]
                    if tipo_dado == "Suspeitos"
                    else ["red"] if tipo_dado == "Óbitos" else ["green"]
                )
            ),
        )
    else:
        df_plot = df_base[df_base["municipio"] == municipio_select]
        df_plot = df_plot[(df_plot["mes"] >= mes_inicio) & (df_plot["mes"] <= mes_fim)]
        fig_linha = px.line(
            df_plot,
            x="mes",
            y=y_col,
            title=f"{title} em {municipio_select} ({mes_inicio} a {mes_fim})",
            color_discrete_sequence=(
                ["blue"]
                if tipo_dado == "Confirmados"
                else (
                    ["orange"]
                    if tipo_dado == "Suspeitos"
                    else ["red"] if tipo_dado == "Óbitos" else ["green"]
                )
            ),
        )
    st.plotly_chart(fig_linha, width="content")

# Gráfico 2: Barra - Distribuições
st.header("Distribuições")
tipo_barra = st.selectbox(
    "Escolha o tipo:", ["Confirmados", "Suspeitos", "Notificações", "Óbitos"]
)
categoria = st.selectbox("Escolha a categoria:", list(df_distribuicao.keys()))
df_bar = df_distribuicao[categoria][tipo_barra]
x_col = df_bar.columns[0]
if tipo_barra == "Confirmados":
    y_col = "total_confirmados"
elif tipo_barra == "Suspeitos":
    y_col = "total_suspeitos"
elif tipo_barra == "Notificações":
    y_col = "total_notificacoes"
else:  # Óbitos
    y_col = "total_obitos"
titulo_tipo = tipo_barra
fig_barra = px.bar(
    df_bar,
    x=x_col,
    y=y_col,
    title=f"Distribuição de {titulo_tipo} por {categoria}",
    color=x_col,
)
st.plotly_chart(fig_barra, width="content")

# Gráfico 3: Scatter - Testes
st.header("Análise de Testes")
fig_testes = px.bar(
    df_testes,
    x="tipo_teste",
    y="total_testes",
    color="fabricante",
    title="Testes por Tipo e Fabricante",
    barmode="group",
    hover_data=["positivos", "taxa_positividade"],
)
st.plotly_chart(fig_testes, width="content")

# Gráfico 4: Mapa de Calor por Município
st.header("Mapa de Calor - Densidade por Município")
tipo_mapa = st.selectbox(
    "Escolha o tipo de dado para o mapa:",
    ["Notificações", "Confirmados", "Suspeitos", "Óbitos"],
)

if tipo_mapa == "Notificações":
    df_mapa_atual = df_mapa
    coluna_cor = "total_notificacoes"
    titulo = "Densidade de Notificações por Município do Pará"
elif tipo_mapa == "Confirmados":
    df_mapa_atual = df_mapa_confirmados
    coluna_cor = "total_confirmados"
    titulo = "Densidade de Casos Confirmados por Município do Pará"
elif tipo_mapa == "Suspeitos":
    df_mapa_atual = df_mapa_suspeitos
    coluna_cor = "total_suspeitos"
    titulo = "Densidade de Casos Suspeitos por Município do Pará"
else:  # Óbitos
    df_mapa_atual = df_mapa_obitos
    coluna_cor = "total_obitos"
    titulo = "Densidade de Óbitos por Município do Pará"

fig_mapa_geo = px.choropleth(
    df_mapa_atual,
    geojson=geojson_para,
    locations="municipio",
    featureidkey="properties.name",
    color=coluna_cor,
    color_continuous_scale="Reds",
    title=titulo,
    hover_name="municipio",
    hover_data=[coluna_cor],
)
fig_mapa_geo.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig_mapa_geo, width="content")

# Gráfico 5: Barra Agrupada - Vacinação
st.header("Vacinação vs Confirmação")
fig_vacina = px.bar(
    df_vacinacao,
    x="recebeu_vacina",
    y="total",
    color="status_confirmacao",
    title="Relação Vacinação-Confirmação",
    barmode="group",
)
st.plotly_chart(fig_vacina, width="content")
