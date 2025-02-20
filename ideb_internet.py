import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from branca.colormap import linear
import plotly.express as px

# Configurar o layout da página
st.set_page_config(layout="wide", page_title="Velocidade de Internet nas Escolas SP")

#####################################
# FUNÇÕES DE CARREGAMENTO DE DADOS  #
#####################################

@st.cache_data
def load_escolas():
    url = ("http://dados.prefeitura.sp.gov.br/dataset/8da55b0e-b385-4b54-9296-d0000014ddd5/"
           "resource/533188c6-1949-4976-ac4e-acd313415cd1/download/escolas122024.csv")
    df = pd.read_csv(url, sep=";", encoding="ISO-8859-1")
    df.columns = df.columns.str.strip()
    df['LATITUDE'] /= 1_000_000
    df['LONGITUDE'] /= 1_000_000
    np.random.seed(42)
    df['IDEB'] = np.random.uniform(3.0, 7.0, len(df))
    df['Velocidade_Internet'] = np.random.uniform(1.0, 100.0, len(df))
    return df

@st.cache_data
def load_distritos_shapefile():
    shp_path = "LAYER_DISTRITO/DEINFO_DISTRITO.shp"  # Caminho relativo
    gdf = gpd.read_file(shp_path)
    if gdf.crs is None or gdf.crs.to_epsg() != 29193:
        gdf.set_crs(epsg=29193, inplace=True)
    gdf = gdf.to_crs(epsg=4326)
    # Converte colunas de data para string
    for col in gdf.select_dtypes(include=['datetime64']).columns:
        gdf[col] = gdf[col].dt.strftime('%Y-%m-%d')
    return gdf

# Carregar os dados
escolas = load_escolas()
distritos_gdf = load_distritos_shapefile()

####################################
# FILTRAGEM E WIDGETS NA BARRA LATERAL
####################################
st.sidebar.header("Filtros de Velocidade de Internet")
min_speed, max_speed = escolas['Velocidade_Internet'].min(), escolas['Velocidade_Internet'].max()
speed_range = st.sidebar.slider("Selecione a faixa de Velocidade (Mbps)",
                                min_speed, max_speed, (min_speed, max_speed), step=0.5)

# Calcular os quartis para categorizar a velocidade
q1, q2, q3 = np.percentile(escolas['Velocidade_Internet'], [25, 50, 75])
categoria_velocidade = {
    "Muito Baixa": escolas['Velocidade_Internet'] <= q1,
    "Baixa": (escolas['Velocidade_Internet'] > q1) & (escolas['Velocidade_Internet'] <= q2),
    "Média": (escolas['Velocidade_Internet'] > q2) & (escolas['Velocidade_Internet'] <= q3),
    "Alta": escolas['Velocidade_Internet'] > q3
}

# Filtro de categorias de velocidade
selected_categories = st.sidebar.multiselect(
    "Selecione as categorias de velocidade",
    options=["Muito Baixa", "Baixa", "Média", "Alta"],
    default=["Muito Baixa", "Baixa", "Média", "Alta"],
)

# Construir máscara para velocidade (slider) e para categorias
mask_speed = escolas['Velocidade_Internet'].between(speed_range[0], speed_range[1])
mask_cat = pd.Series(False, index=escolas.index)
for cat in selected_categories:
    mask_cat |= categoria_velocidade[cat]

# Filtros adicionais
dre = st.sidebar.multiselect("DRE", sorted(escolas['DRE'].unique()))
subpref = st.sidebar.multiselect("Subprefeitura", sorted(escolas['SUBPREF'].unique()))
tipoesc = st.sidebar.multiselect("Tipo de Escola", sorted(escolas['TIPOESC'].unique()))
bairro = st.sidebar.multiselect("Bairro", sorted(escolas['BAIRRO'].unique()))
distrito = st.sidebar.multiselect("Distrito", sorted(escolas['DISTRITO'].unique()))
nome_escola = st.sidebar.multiselect("Nome da Escola", sorted(escolas['NOMES'].unique()))

mask_adicional = (
    (escolas['DRE'].isin(dre) if dre else np.ones(len(escolas), dtype=bool)) &
    (escolas['SUBPREF'].isin(subpref) if subpref else np.ones(len(escolas), dtype=bool)) &
    (escolas['TIPOESC'].isin(tipoesc) if tipoesc else np.ones(len(escolas), dtype=bool)) &
    (escolas['BAIRRO'].isin(bairro) if bairro else np.ones(len(escolas), dtype=bool)) &
    (escolas['DISTRITO'].isin(distrito) if distrito else np.ones(len(escolas), dtype=bool)) &
    (escolas['NOMES'].isin(nome_escola) if nome_escola else np.ones(len(escolas), dtype=bool))
)

# Aplicar todos os filtros combinados
filtered_escolas = escolas[mask_speed & mask_cat & mask_adicional]
st.sidebar.markdown(f"### Total de escolas filtradas: {len(filtered_escolas)}")

####################################
# MAPAS INTERATIVOS
####################################
st.title("Velocidade de Internet nas Escolas São Paulo capital")
mapa_col1, mapa_col2 = st.columns(2)
# Mapa das Escolas
with mapa_col1:
    st.header("Localização das Escolas")
    mapa_escolas = folium.Map(location=[-23.5505, -46.6333], zoom_start=12,
                              tiles='cartodb positron', width='100%', height='600px')
    cluster = MarkerCluster().add_to(mapa_escolas)
    for _, row in filtered_escolas.iterrows():
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=row['Velocidade_Internet'] / 10,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.5,
            popup=folium.Popup(f"{row['NOMES']}<br>IDEB: {row['IDEB']:.2f}<br>Velocidade: {row['Velocidade_Internet']:.2f} Mbps", max_width=300),
        ).add_to(cluster)
    folium_static(mapa_escolas)
# Mapa de Distritos
with mapa_col2:
    st.header("Velocidade de Internet por Distrito")
    # Calcular a velocidade média de internet por distrito
    velocidade_por_distrito = escolas.groupby('DISTRITO')['Velocidade_Internet'].mean().reset_index()
    # Mesclar os dados com o GeoDataFrame dos distritos
    distritos_gdf = distritos_gdf.merge(velocidade_por_distrito, left_on='NOME_DIST', right_on='DISTRITO', how='left')
    # Preencher valores NaN com a média geral
    distritos_gdf['Velocidade_Internet'].fillna(distritos_gdf['Velocidade_Internet'].mean(), inplace=True)
    # Criar o colormap para representar a velocidade de internet
    colormap = linear.Reds_09.scale(distritos_gdf['Velocidade_Internet'].min(), distritos_gdf['Velocidade_Internet'].max())
    # Criar o mapa de distritos
    mapa_distritos = folium.Map(
        location=[-23.5505, -46.6333], 
        zoom_start=12,
        tiles='cartodb positron', 
        width='100%', 
        height='600px'
    )
    # Função para estilizar os distritos no mapa
    def style_function(feature):
        if "selected_district" in st.session_state and feature['properties']['NOME_DIST'] == st.session_state["selected_district"]:
            return {
                'fillColor': colormap(feature['properties']['Velocidade_Internet']),
                'color': 'black', 
                'weight': 2, 
                'fillOpacity': 0.9
            }
        else:
            return {
                'fillColor': colormap(feature['properties']['Velocidade_Internet']),
                'color': 'black', 
                'weight': 0.5, 
                'fillOpacity': 0.5
            }
    # Adicionar distritos ao mapa com tooltip exibindo nome e velocidade média
    folium.GeoJson(
        distritos_gdf,
        name="Distritos",
        tooltip=folium.GeoJsonTooltip(
            fields=["NOME_DIST", "Velocidade_Internet"],  
            aliases=["Distrito:", "Velocidade Média (Mbps):"],  
            localize=True,
            sticky=True,
            labels=True,
            style="background-color: white; color: black; font-size: 12px; padding: 5px;"
        ),
        style_function=style_function,
        highlight_function=lambda x: {"fillColor": "yellow", "fillOpacity": 0.5},
    ).add_to(mapa_distritos)
    # Adicionar legenda ao mapa
    colormap.caption = 'Velocidade Média de Internet (Mbps)'
    colormap.add_to(mapa_distritos)
    # Exibir mapa no Streamlit
    folium_static(mapa_distritos)

####################################
# GRÁFICO DE BARRAS HORIZONTAL INTERATIVO
####################################
st.header("Velocidade de Internet por Escola")

# Ordenar escolas por velocidade (maior para menor) e remover duplicatas
filtered_escolas = (
    filtered_escolas.groupby('NOMES', as_index=False)['Velocidade_Internet'].mean()
    .sort_values('Velocidade_Internet', ascending=False)
)

# Criar gráfico de barras com cores em degradê vermelho
fig = px.bar(
    filtered_escolas,
    y='Velocidade_Internet',  # Eixo Y: Velocidade da Internet
    x='NOMES',  # Eixo X: Nome das Escolas
    orientation='v',  # Barras verticais
    color='Velocidade_Internet',  # Definir cor pelo valor da velocidade
    color_continuous_scale='Reds',  # Degradê vermelho escuro → claro
    labels={'Velocidade_Internet': 'Velocidade da Internet (Mbps)', 'NOMES': 'Escola'}
)

# Definir exibição inicial (30 escolas) e permitir rolagem horizontal
fig.update_layout(
    plot_bgcolor='black',  # Fundo preto
    paper_bgcolor='black',  # Fundo preto
    font_color='white',  # Texto branco
    yaxis_title='Velocidade da Internet (Mbps)',  # Título do eixo Y
    xaxis_title='Escola',  # Título do eixo X
    xaxis=dict(
        categoryorder='total descending',  # Ordenação das escolas
        tickangle=45,  # Inclina os rótulos para melhor visualização
        tickfont=dict(size=10),  # Ajusta o tamanho dos nomes das escolas
        automargin=True,  # Margens automáticas
        range=[0, 30],  # Mostra apenas 30 escolas por vez e permite rolagem
        rangeslider=dict(visible=True),  # Ativar barra de rolagem horizontal
        type="category"  # Permite rolagem horizontal
    ),
    height=900,  # Altura do gráfico
    width=1000,  # Largura maior para permitir rolagem
    margin=dict(l=50, r=50, t=50, b=150)  # Ajusta margens
)

# Ajustar a espessura das barras
fig.update_traces(marker=dict(line=dict(width=0.7, color='gray')))

# Exibir o gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)

####################################
# INTERAÇÃO ENTRE MAPAS
####################################
def on_click_distrito(event):
    distrito_selecionado = event['properties']['NOME_DIST']
    st.session_state["selected_district"] = distrito_selecionado
    st.write(f"Distrito Selecionado: {distrito_selecionado}")
    escolas_no_distrito = filtered_escolas[filtered_escolas['DISTRITO'] == distrito_selecionado]
    if not escolas_no_distrito.empty:
        escola_selecionada = escolas_no_distrito.iloc[0]
        folium.Marker([escola_selecionada['LATITUDE'], escola_selecionada['LONGITUDE']],
                      popup="Escola Selecionada").add_to(mapa_escolas)
        folium_static(mapa_escolas)

# Adicionar interação de clique nos distritos
folium.GeoJson(
    distritos_gdf,
    name="Distritos",
    tooltip=folium.GeoJsonTooltip(fields=["NOME_DIST"], aliases=["Distrito: "]),
    on_click=on_click_distrito
).add_to(mapa_distritos)

if distrito:
    distrito_selecionado = distrito[0]
    st.session_state["selected_district"] = distrito_selecionado
    st.write(f"Distrito Selecionado: {distrito_selecionado}")
    escolas_no_distrito = filtered_escolas[filtered_escolas['DISTRITO'] == distrito_selecionado]
    if not escolas_no_distrito.empty:
        escola_selecionada = escolas_no_distrito.iloc[0]
        folium.Marker([escola_selecionada['LATITUDE'], escola_selecionada['LONGITUDE']],
                      popup="Escola Selecionada").add_to(mapa_escolas)
        folium_static(mapa_escolas)
