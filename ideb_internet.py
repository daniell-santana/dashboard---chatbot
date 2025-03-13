# Importações de bibliotecas
import streamlit as st  # Framework para criar aplicações web interativas de forma rápida.
import pandas as pd  # Manipulação e análise de dados tabulares (DataFrames).
import numpy as np  # Computação numérica eficiente com arrays multidimensionais.
import geopandas as gpd  # Extensão do pandas para manipulação de dados geoespaciais.
import folium  # Biblioteca para criar mapas interativos.
from streamlit_folium import folium_static  # Integra mapas do folium com o Streamlit.
from branca.colormap import linear  # Gera colormaps para visualizações em mapas.
import plotly.express as px  # Cria gráficos interativos de forma simples e rápida.
import plotly.graph_objects as go  # Cria gráficos personalizados e complexos com Plotly.
import openai  # Integração com a API da OpenAI para uso de modelos de IA.
import faiss  # Biblioteca para busca eficiente de vetores (útil para embeddings).
import json  # Manipulação de dados no formato JSON.
import os  # Interação com o sistema operacional (leitura de arquivos, variáveis de ambiente, etc.).
from dotenv import load_dotenv  # Carrega variáveis de ambiente de um arquivo .env.
import time  # Controle de tempo e delays no código.
import ast  # Converte strings para objetos Python (útil para embeddings armazenados como strings).

# Configurar o layout da página
st.set_page_config(layout="wide", page_title="Conectividade das Escolas de São Paulo capital")

# --------------------------------------------------------------------
# TOGGLE SWITCH MODERNO
# --------------------------------------------------------------------
col1, col2, col3 = st.columns([8, 8, 2])
with col3:
    tema = st.radio(
        "", 
        ["☀️", "🌙"], 
        index=0, 
        horizontal=True, 
        label_visibility="collapsed"  # Esconde o label padrão
    )

    # CSS para estilizar o toggle switch
    st.markdown(
        """
        <style>
        /* Esconde os radio buttons padrão */
        div[role=radiogroup] > label > div:first-child {
            display: none;
        }
        /* Estilo do container do toggle (versão horizontal) */
        div[role=radiogroup] {
            background-color: #555;
            border-radius: 20px;
            padding: 2px;
            display: inline-flex;
            gap: 0;
            position: relative;
            width: 80px;
            height: 30px;
            align-items: center;
        }
        /* Estilo dos botões (sol e lua) */
        div[role=radiogroup] label {
            margin: 0;
            padding: 4px 12px;
            cursor: pointer;
            z-index: 1;
            transition: color 0.3s;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 50%;
        }
        div[role=radiogroup] label:first-child {
            padding-left: 4px;
            justify-content: flex-start;
        }
        div[role=radiogroup] label:last-child {
            padding-right: 4px;
            justify-content: flex-end;
        }
        /* Efeito de slider (parte deslizante) */
        div[role=radiogroup]:after {
            content: "";
            position: absolute;
            width: 42px;
            height: 34px;
            background-color: #4CAF50;
            top: 3px;
            left: 3px;
            border-radius: 16px;
            transition: transform 0.3s;
        }
        input[value="☀️"]:checked ~ div[role=radiogroup]:after {
            transform: translateX(0);
        }
        input[value="🌙"]:checked ~ div[role=radiogroup]:after {
            transform: translateX(38px);
        }
        input:checked + label {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------------------------
# DEFINIR AS VARIÁVEIS DE CORES CONFORME O TEMA SELECIONADO
# --------------------------------------------------------------------
if tema == "🌙":
    # Modo Escuro
    plot_bgcolor = "#0e1118"
    paper_bgcolor = "#0e1118"
    font_color = "white"
    sidebar_bg = "#383838"
    input_bg = "#2d2d2d"
    input_font_color = "white"
    input_border = "1px solid #fff"
    button_bg = "#4CAF50"
    button_font_color = "white"
    button_border = "1px solid #fff"
    separator_color = "#555"
else:
    # Modo Claro
    plot_bgcolor = "#ffffff"
    paper_bgcolor = "#ffffff"
    font_color = "#000000"
    sidebar_bg = "#fff9f9"
    input_bg = "#ffffff"      # Fundo branco para a caixa de entrada
    input_font_color = "#000000"
    input_border = "1px solid #000"
    button_bg = "#ffffff"      # Fundo branco para o botão
    button_font_color = "#000000"
    button_border = "1px solid #000"
    separator_color = "#ccc"

# Atualizar cores do toggle com base no tema
st.markdown(
    f"""
    <style>
    div[role=radiogroup] {{
        background-color: {sidebar_bg if tema == "🌙" else "#f0f0f0"};
    }}
    div[role=radiogroup]:after {{
        background-color: {font_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------------------
# INJETAR CSS PARA ALTERAR O FUNDO DA APLICAÇÃO, SIDEBAR E HEADER
# --------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {plot_bgcolor} !important;
        color: {font_color} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {font_color} !important;
    }}
    .plotly .main-svg {{
        color: {font_color} !important;
        fill: {font_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

if tema == "🌙":
    header_bg = "#383838"
else:
    header_bg = "#fff9f9"

st.markdown(
    f"""
    <style>
    [data-testid="stHeader"] {{
        background-color: {header_bg};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------------------
# CSS PARA A ÁREA DO CHAT
# --------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    /* Container centralizado para a área de chat */
    .chat-container {{
        max-width: 600px;
        margin: 20px auto;
        padding: 10px;
    }}
    /* Estilo para o label "Digite sua pergunta:" */
    label[for="user_input"],
    div.stTextArea label {{
        color: {font_color} !important;
        font-size: 16px;
        font-weight: 500;
    }}
    /* Estilo para a caixa de entrada (textarea) */
    div.stTextArea textarea {{
        background-color: {input_bg} !important;
        color: {input_font_color} !important;
        border: {input_border} !important;
        border-radius: 8px !important;
        padding: 10px !important;
        width: 100%;
    }}
    /* Estilo para o botão "Enviar" */
    div.stButton > button {{
        background-color: {button_bg} !important;
        color: {button_font_color} !important;
        border: {button_border} !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }}
    /* Estilo para as linhas de separação entre mensagens */
    hr {{
        border: 1px solid #ccc !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Exibir a nota logo abaixo do título com um componente nativo
st.caption("Nota: Os dados aqui utilizados foram simulados. Não correspondem a realidade")
# --------------------------------------------------------------------

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
# Carregar o arquivo GeoJSON do Distrito de Sao Paulo
sao_paulo_gdf = gpd.read_file("LAYER_DISTRITO/geojs-35-mun.json")
escolas = load_escolas()
distritos_gdf = load_distritos_shapefile()

####################################
# FILTRAGEM E WIDGETS NA BARRA LATERAL
####################################
st.sidebar.header("Filtros de Velocidade de Internet")

# 1. Filtro de Velocidade (Slider)
min_speed, max_speed = escolas['Velocidade_Internet'].min(), escolas['Velocidade_Internet'].max()
speed_range = st.sidebar.slider(
    "Selecione a faixa de Velocidade (Mbps)",
    min_speed, max_speed, (min_speed, max_speed), step=0.5
)

# 2. Categorias de Velocidade (Calculadas a partir dos dados originais)
q1, q2, q3 = np.percentile(escolas['Velocidade_Internet'], [25, 50, 75]) #quartis
# Cada categoria é definida com base na condição
categoria_velocidade = {
    "Muito Baixa": escolas['Velocidade_Internet'] <= q1,
    "Baixa": (escolas['Velocidade_Internet'] > q1) & (escolas['Velocidade_Internet'] <= q2),
    "Média": (escolas['Velocidade_Internet'] > q2) & (escolas['Velocidade_Internet'] <= q3),
    "Alta": escolas['Velocidade_Internet'] > q3
}

selected_categories = st.sidebar.multiselect(
    "Selecione as categorias de velocidade",
    options=["Muito Baixa", "Baixa", "Média", "Alta"],
    default=["Muito Baixa", "Baixa", "Média", "Alta"],
)

# Máscara global (aplicando velocidade e categorias) – esta máscara será usada para restringir todas as opções
mask_speed = escolas['Velocidade_Internet'].between(speed_range[0], speed_range[1])

# Máscara de categorias de velocidade
if not selected_categories:
    # Se nenhuma categoria for selecionada, não aplicar filtro (todos os registros passam)
    mask_cat = pd.Series(True, index=escolas.index)
else:
    mask_cat = pd.Series(False, index=escolas.index)
    for cat in selected_categories:
        if cat == "Muito Baixa":
            mask_cat |= (escolas['Velocidade_Internet'] <= q1)
        elif cat == "Baixa":
            mask_cat |= ((escolas['Velocidade_Internet'] > q1) & (escolas['Velocidade_Internet'] <= q2))
        elif cat == "Média":
            mask_cat |= ((escolas['Velocidade_Internet'] > q2) & (escolas['Velocidade_Internet'] <= q3))
        elif cat == "Alta":
            mask_cat |= (escolas['Velocidade_Internet'] > q3)

global_mask = mask_speed & mask_cat

# Função auxiliar: retorna as opções disponíveis para a coluna 'col'
# Aplicando a máscara global e, adicionalmente, filtrando pelos outros filtros já selecionados.
def available_options(col, exclude_filter, current_filters):
    mask = global_mask.copy()
    # Para cada filtro (exceto o atual), se houver seleção, aplicar essa condição
    for key, sel in current_filters.items():
        if key != exclude_filter and sel:
            mask &= escolas[key].isin(sel)
    return sorted(escolas.loc[mask, col].unique())

# Inicializar (ou obter) os valores atuais dos filtros interativos do session_state.
# Se ainda não estiverem definidos, eles serão listas vazias.
current_filters = {
    "DRE": st.session_state.get("DRE", []),
    "SUBPREF": st.session_state.get("SUBPREF", []),
    "TIPOESC": st.session_state.get("TIPOESC", []),
    "BAIRRO": st.session_state.get("BAIRRO", []),
    "DISTRITO": st.session_state.get("DISTRITO", []),
    "NOMES": st.session_state.get("NOMES", [])
}

# Calcular as opções disponíveis para cada filtro com base no global_mask e nos outros filtros:
available_dre      = available_options("DRE", "DRE", current_filters)
available_subpref  = available_options("SUBPREF", "SUBPREF", current_filters)
available_tipoesc  = available_options("TIPOESC", "TIPOESC", current_filters)
available_bairro   = available_options("BAIRRO", "BAIRRO", current_filters)
available_distrito = available_options("DISTRITO", "DISTRITO", current_filters)
available_nome     = available_options("NOMES", "NOMES", current_filters)

# Criar os widgets de filtro com as opções calculadas e atualizar o session_state
selected_dre = st.sidebar.multiselect("DRE", available_dre, default=current_filters["DRE"], key="DRE")
selected_subpref = st.sidebar.multiselect("Subprefeitura", available_subpref, default=current_filters["SUBPREF"], key="SUBPREF")
selected_tipoesc = st.sidebar.multiselect("Tipo de Escola", available_tipoesc, default=current_filters["TIPOESC"], key="TIPOESC")
selected_bairro = st.sidebar.multiselect("Bairro", available_bairro, default=current_filters["BAIRRO"], key="BAIRRO")
selected_distrito = st.sidebar.multiselect("Distrito", available_distrito, default=current_filters["DISTRITO"], key="DISTRITO")
selected_nome = st.sidebar.multiselect("Nome da Escola", available_nome, default=current_filters["NOMES"], key="NOMES")

# Atualiza o dicionário current_filters com as seleções atuais
current_filters = {
    "DRE": selected_dre,
    "SUBPREF": selected_subpref,
    "TIPOESC": selected_tipoesc,
    "BAIRRO": selected_bairro,
    "DISTRITO": selected_distrito,
    "NOMES": selected_nome
}

# Construir a máscara final interativa combinando todos os filtros
mask_interactive = global_mask.copy()
if selected_dre:
    mask_interactive &= escolas['DRE'].isin(selected_dre)
if selected_subpref:
    mask_interactive &= escolas['SUBPREF'].isin(selected_subpref)
if selected_tipoesc:
    mask_interactive &= escolas['TIPOESC'].isin(selected_tipoesc)
if selected_bairro:
    mask_interactive &= escolas['BAIRRO'].isin(selected_bairro)
if selected_distrito:
    mask_interactive &= escolas['DISTRITO'].isin(selected_distrito)
if selected_nome:
    mask_interactive &= escolas['NOMES'].isin(selected_nome)

filtered_escolas = escolas[mask_interactive]

st.sidebar.markdown(f"### Total de escolas filtradas: {len(filtered_escolas)}")

# CSS para ajustar os iframes dos mapas e os títulos
st.markdown(
    '''
    <style>
    iframe {
        width: 100% !important;
        height: 600px !important;
    }
    h2 {
        font-size: 20px !important;
    }
    h1 {
        font-size: 28px !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)
####################################
# MAPAS INTERATIVOS e VELOCÍMETROS
####################################
st.title("Conectividade das Escolas de São Paulo capital")

# Define os tiles do mapa conforme o tema (claro ou escuro)
tiles_map = 'cartodb positron' if tema == "☀️" else 'cartodb dark_matter'

# Calcular as métricas com base no DataFrame filtrado
if not filtered_escolas.empty:
    media_escolas = filtered_escolas['Velocidade_Internet'].mean()

    # Encontrar os distritos das escolas filtradas
    distritos_selecionados = filtered_escolas['DISTRITO'].unique()

    # Calcular a média de velocidade dos distritos considerando TODAS as escolas do distrito
    media_distritos = escolas[escolas['DISTRITO'].isin(distritos_selecionados)]['Velocidade_Internet'].mean()
else:
    media_escolas = 0
    media_distritos = 0

# Cores das categorias (com transparência)
cores = {
    "Muito Baixa": 'rgba(250, 76, 77, 0.8)',  # 80% opaco
    "Baixa": 'rgba(255, 127, 14, 0.8)',
    "Média": 'rgba(44, 160, 44, 0.8)',
    "Alta": 'rgba(31, 119, 180, 0.8)'
}

# Cálculo das categorias (quartis)
q1, q2, q3 = np.percentile(escolas['Velocidade_Internet'], [25, 50, 75])
categorias = {
    "Muito Baixa": q1,
    "Baixa": q2,
    "Média": q3,
    "Alta": 100  # Definimos o limite máximo como 100 Mbps
}

# Função para criar o velocímetro
def criar_velocimetro(valor, valor_referencia, categorias, cores, titulo):
    # Determinar a cor com base no valor
    if valor <= categorias["Muito Baixa"]:
        cor = cores["Muito Baixa"]
    elif valor <= categorias["Baixa"]:
        cor = cores["Baixa"]
    elif valor <= categorias["Média"]:
        cor = cores["Média"]
    else:
        cor = cores["Alta"]

    # Determinar a seta (para cima ou para baixo)
    seta = "▲" if valor > valor_referencia else "▼"
    
    # Criar o velocímetro
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        number={
            'suffix': " Mbps",
            'font': {'size': 24, 'color': font_color},
            'valueformat': '.2f',  # Formato com duas casas decimais
        },
        title={
            'text': f"{titulo}<br>{seta}",  # Título com a seta
            'font': {'size': 12, 'color': font_color},
        },
        gauge={
            'axis': {'range': [0, categorias["Alta"]], 'tickwidth': 1, 'tickcolor': "darkblue", 'tickfont': {'color': font_color}},
            'bar': {'color': 'rgba(0,0,0,0)'},  # Barra transparente (sem sobreposição)
            'steps': [
                {'range': [0, categorias["Muito Baixa"]], 'color': cores["Muito Baixa"], 'name': 'Muito Baixa'},
                {'range': [categorias["Muito Baixa"], categorias["Baixa"]], 'color': cores["Baixa"], 'name': 'Baixa'},
                {'range': [categorias["Baixa"], categorias["Média"]], 'color': cores["Média"], 'name': 'Média'},
                {'range': [categorias["Média"], categorias["Alta"]], 'color': cores["Alta"], 'name': 'Alta'},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': valor
            },
            'bgcolor': plot_bgcolor,  # Fundo do velocímetro
        }
    ))
    fig.update_layout(
        paper_bgcolor=paper_bgcolor,  # Fundo externo do gráfico
        font={'color': font_color},   # Cor dos textos
        margin=dict(t=35, b=15),      # Reduzir margens para diminuir o tamanho
        height=200,                   # Altura do gráfico
    )
    return fig

# Criar os velocímetros
velocimetro_escolas = criar_velocimetro(
    media_escolas, media_distritos, categorias, cores, "Velocidade média das escolas"
)
velocimetro_distritos = criar_velocimetro(
    media_distritos, media_escolas, categorias, cores, "Velocidade média dos distritos"
)

# Exibir os velocímetros (proporção 2:3)
col1, col2 = st.columns([2, 3])
with col1:
    # Título acima do velocímetro das escolas
    st.markdown("<h5 style='text-align: center; font-size: 20px;'>Velocidade média das escolas</h5>", unsafe_allow_html=True)
    
    # Exibir o gráfico
    st.plotly_chart(velocimetro_escolas, use_container_width=True)
    
    # Legenda para o velocímetro das escolas (abaixo do gráfico, com espaçamento reduzido)
    st.markdown("""
    <div style="text-align: center; margin-top: -20px;">
        <span style="color: #fa4c4d;">● Muito Baixa</span> &nbsp;
        <span style="color: #ff7f0e;">● Baixa</span> &nbsp;
        <span style="color: #2ca02c;">● Média</span> &nbsp;
        <span style="color: #1f77b4;">● Alta</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Título acima do velocímetro dos distritos
    st.markdown("<h5 style='text-align: center; font-size: 20px;'>Velocidade média dos distritos</h5>", unsafe_allow_html=True)
    
    # Exibir o gráfico
    st.plotly_chart(velocimetro_distritos, use_container_width=True)
    
    # Legenda para o velocímetro dos distritos (abaixo do gráfico, com espaçamento reduzido)
    st.markdown("""
    <div style="text-align: center; margin-top: -20px;">
        <span style="color: #fa4c4d;">● Muito Baixa</span> &nbsp;
        <span style="color: #ff7f0e;">● Baixa</span> &nbsp;
        <span style="color: #2ca02c;">● Média</span> &nbsp;
        <span style="color: #1f77b4;">● Alta</span>
    </div>
    """, unsafe_allow_html=True)

# =====================================================

# --- Layout dos Mapas ---
# Organiza os mapas em duas colunas com proporção [2, 3]
col_left, col_right = st.columns([2, 3])

# Mapa das Escolas (coluna da esquerda)
# Adicionando camadas de categorias de velocidade ao mapa
with col_left:
    # Container principal para organização do layout
    with st.container():
        st.header("Localização das Escolas")
        
        # Cria o mapa base
        mapa_escolas = folium.Map(
            location=[-23.5505, -46.6333],  # Coordenadas do centro de SP
            zoom_start=11,                   # Zoom inicial
            tiles=tiles_map,                 # Estilo do mapa (definido pelo tema)
            width='100%',                    # Largura total do container
            height=600                       # Altura fixa para alinhamento
        )

        # =====================================================
        # CAMADA DO MUNICÍPIO DE SÃO PAULO
        # =====================================================
        folium.GeoJson(
            sao_paulo_gdf,  # GeoDataFrame com os limites do município
            name="Município de SP",
            style_function=lambda x: {
                'fillColor': '#808080',  # Cinza
                'color': '#000000',      # Cor do contorno
                'weight': 2,            # Espessura da linha
                'fillOpacity': 0.2,      # 20% de transparência
                'dashArray': '5, 5'      # Linha pontilhada
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name"],  # Campo com o nome do município
                aliases=["Município:"],
                localize=True
            )
        ).add_to(mapa_escolas)

        # =====================================================
        # CAMADAS DE VELOCIDADE (FEATURE GROUPS)
        # =====================================================
        for categoria, condicao in categoria_velocidade.items():
            # Filtra escolas por categoria
            escolas_categoria = filtered_escolas[condicao]
            
            if not escolas_categoria.empty:
                # Cria grupo de camadas
                feature_group = folium.FeatureGroup(name=f"Velocidade {categoria}")
                
                # Adiciona marcadores circulares
                for _, row in escolas_categoria.iterrows():
                    folium.CircleMarker(
                        location=[row['LATITUDE'], row['LONGITUDE']],
                        radius=(row['Velocidade_Internet'] / 10) * 1.01,  # Tamanho proporcional
                        weight=0,               # Sem borda
                        color=None,
                        fill=True,
                        fill_color='#fa4c4d' if categoria == "Muito Baixa" else 
                                  '#ff7f0e' if categoria == "Baixa" else 
                                  '#2ca02c' if categoria == "Média" else 
                                  '#1f77b4',    # Cores por categoria
                        fill_opacity=0.5,       # 50% de transparência
                        popup=folium.Popup(     # Popup com informações
                            f"""
                            <b>{row['NOMES']}</b><br>
                            IDEB: {row['IDEB']:.2f}<br>
                            Velocidade: {row['Velocidade_Internet']:.2f} Mbps
                            """,
                            max_width=300
                        ),
                    ).add_to(feature_group)
                
                # Adiciona o grupo ao mapa
                feature_group.add_to(mapa_escolas)

        # =====================================================
        # CONTROLE DE CAMADAS
        # =====================================================
        folium.LayerControl(
            position='topright'  # Posição do controle
        ).add_to(mapa_escolas)

        # Renderiza o mapa
        folium_static(mapa_escolas)

# Coluna da direita: subdividida em duas (mapa de distritos e tabela de velocidade)
with col_right:
    # Divide a coluna da direita em duas: mapa de distritos (2/3) e tabela (1/3)
    mapa_col2, tabela_col = st.columns([2, 1])
       
# Mapa de Distritos (coluna da esquerda interna)
with mapa_col2:
    st.header("Velocidade de Internet por Distrito")
    
    # 1. Processamento dos dados
    velocidade_por_distrito = escolas.groupby('DISTRITO')['Velocidade_Internet'].mean().reset_index()
    distritos_gdf = distritos_gdf.merge(
        velocidade_por_distrito, left_on='NOME_DIST', right_on='DISTRITO', how='left'
    )
    distritos_gdf['Velocidade_Internet'].fillna(distritos_gdf['Velocidade_Internet'].mean(), inplace=True)

    # 2. Criação do colormap
    colormap = linear.Reds_09.scale(
        distritos_gdf['Velocidade_Internet'].min(), 
        distritos_gdf['Velocidade_Internet'].max()
    )

    # 3. Ajustes de tamanho do colormap
    colormap.width = 350  # Largura da barra de cores
    colormap.height = 40   # Altura da barra de cores

    # 4. Criação do mapa
    mapa_distritos = folium.Map(
        location=[-23.5505, -46.6333],
        zoom_start=10,
        tiles=tiles_map,
        width="100%",
        height="600px"
    )

    # 5. Lógica de distritos destacados
    filtros_disponiveis = ["DRE", "SUBPREF", "TIPOESC", "BAIRRO", "DISTRITO", "NOMES"]
    filtros_ativos = any(st.session_state.get(filtro, []) for filtro in filtros_disponiveis)
    highlighted_distritos = (
        filtered_escolas['DISTRITO'].unique().tolist()
        if filtros_ativos and 'filtered_escolas' in globals()
        else []
    )

    # 6. Estilo dos polígonos
    def style_function(feature):
        if feature['properties']['NOME_DIST'] in highlighted_distritos:
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

    # 7. Adiciona camada GeoJson
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

    # 8. Configurações do colormap
    colormap.caption = 'Velocidade Média de Internet (Mbps)'

    # 9. Adiciona colormap ao mapa
    colormap.add_to(mapa_distritos)
    folium_static(mapa_distritos)

# Tabela de Velocidade por Distrito (coluna da direita interna)
    with tabela_col:
        # Ajusta o espaçamento do título com CSS
        st.markdown(
            """
            <style>
            /* Reduz o espaçamento do título */
            .stHeader {
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }

            /* Reduz o tamanho da fonte da coluna Distrito */
            div[data-testid="stDataFrame"] table td:first-child {
                font-size: 8px !important;
            }

            /* Ajusta o padding das células para melhorar a densidade */
            div[data-testid="stDataFrame"] table td {
                padding-top: 1px !important;
                padding-bottom: 1px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown("**Velocidade Média por Distrito**")  # Usando markdown para o título

        # Agrupa os dados do DataFrame completo para calcular a média de velocidade por distrito
        df_distritos = escolas.groupby('DISTRITO')['Velocidade_Internet'].mean().reset_index()

        # Renomeia as colunas para facilitar a visualização na tabela
        df_distritos = df_distritos.rename(columns={'DISTRITO': 'Distrito', 'Velocidade_Internet': 'Velocidade'})

        # Se houver filtros ativos (por exemplo, por DRE, subprefeitura, etc.), filtra a tabela para exibir apenas os distritos destacados
        if filtros_ativos:
            df_distritos = df_distritos[df_distritos["Distrito"].isin(highlighted_distritos)]

        # Ordena os distritos por velocidade média de forma decrescente
        df_distritos = df_distritos.sort_values('Velocidade', ascending=False)
        
        # Exibe a tabela com ajustes de altura e fonte
        st.dataframe(
            df_distritos,
            column_order=("Distrito", "Velocidade"),
            hide_index=True,
            use_container_width=True,  # A tabela ocupará toda a largura do container
            height=600,                # Ajuste a altura para corresponder ao mapa
            column_config={
                "Distrito": st.column_config.TextColumn(
                    "Distrito",
                    width="small",  # Altere para "small" para uma largura menor
                ),
                "Velocidade": st.column_config.ProgressColumn(
                    "Velocidade (Mbps)",
                    format="%.2f",
                    min_value=0,
                    max_value=escolas["Velocidade_Internet"].max()
                )
            }
        )

####################################
# GRÁFICO DE DISPERSÃO ESCOLAS 
####################################
st.header("Velocidade de Internet por IDEB")

# Ordenar as escolas por IDEB (crescente)
filtered_escolas = filtered_escolas.sort_values('IDEB', ascending=True)

# Criar gráfico de dispersão
fig = px.scatter(
    filtered_escolas,
    x='IDEB',  # Eixo X: IDEB das Escolas
    y='Velocidade_Internet',  # Eixo Y: Velocidade da Internet
    size='Velocidade_Internet',  # Tamanho do ponto baseado na velocidade
    color='Velocidade_Internet',  # Cor do ponto baseado na velocidade
    color_continuous_scale='Reds',  # Degradê vermelho escuro → claro
    labels={'Velocidade_Internet': 'Velocidade da Internet (Mbps)', 'IDEB': 'IDEB'},
    hover_name='NOMES' if 'NOMES' in filtered_escolas.columns else None  # Exibe o nome da escola ao passar o mouse
)

# Ajustar layout do gráfico
fig.update_layout(
    plot_bgcolor=plot_bgcolor,
    paper_bgcolor=paper_bgcolor,
    font=dict(color=font_color),  # Ajusta a cor de todos os textos do gráfico
    xaxis=dict(
        tickfont=dict(color=font_color),
        title=dict(text="IDEB", font=dict(color=font_color)),  # Título do eixo X
    ),
    yaxis=dict(
        tickfont=dict(color=font_color),
        title=dict(text="Velocidade da Internet (Mbps)", font=dict(color=font_color))  # Título do eixo Y
    ),
    legend=dict(
        font=dict(color=font_color),
        title=dict(text="Legenda", font=dict(color=font_color))  # Corrige a cor do título da legenda
    ),
    coloraxis_colorbar=dict(  # Corrigindo a chave
        title=dict(text="Velocidade (Mbps)", font=dict(color=font_color)),  # Título da escala
        title_side='right',  # Posiciona o título da escala na vertical
        orientation='v',  # Orientação vertical da barra de cores
        yanchor='middle',  # Centraliza o título verticalmente
        y=0.5,  # Ajusta a posição do título
        tickfont=dict(color=font_color)  # Cor dos valores da escala
    ),
    height=700,
    width=900,
    margin=dict(l=50, r=50, t=50, b=150)
)

# Ajustar a aparência dos pontos
fig.update_traces(
    marker=dict(line=dict(width=1, color='gray')),
    hovertemplate='<b>%{hovertext}</b><br>IDEB: %{x:.2f}<br>Velocidade: %{y:.2f} Mbps<extra></extra>',
)

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
        # folium_static(mapa_escolas)

# Adicionar interação de clique nos distritos
folium.GeoJson(
    distritos_gdf,
    name="Distritos",
    tooltip=folium.GeoJsonTooltip(fields=["NOME_DIST"], aliases=["Distrito: "]),
    on_click=on_click_distrito
).add_to(mapa_distritos)

####################################
# CHATBOT COM RAG - Versão Híbrida
####################################

# Lê a chave da OpenAI das variáveis de ambiente do Github
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define a chave na biblioteca da OpenAI
openai.api_key = openai_api_key

# ================== Carregar FAQ ==================
@st.cache_data(show_spinner=True)
def carregar_faq():
    """Carrega o arquivo CSV de perguntas e respostas do FAQ, se existirem."""
    file_path = "faq_data.csv"  # Caminho relativo ao diretório raiz
    
    if os.path.exists(file_path):
        # Carrega o CSV com o separador correto
        faq_data = pd.read_csv(file_path, encoding="utf-8", sep=',')
        
        # Verifica se a coluna 'embedding' existe
        if 'embedding' not in faq_data.columns:
            st.error("A coluna 'embedding' não foi encontrada no arquivo CSV.")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
        
        # Converte a coluna 'embedding' de string para lista
        try:
            faq_data['embedding'] = faq_data['embedding'].apply(ast.literal_eval)
        except (ValueError, SyntaxError) as e:
            st.error(f"Erro ao converter a coluna 'embedding': {e}")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    else:
        st.error(f"O arquivo FAQ não foi encontrado no caminho: {file_path}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    
    return faq_data

# Carregar o FAQ
faq_data = carregar_faq()
df = pd.DataFrame(faq_data)

# ================== Carregar Embeddings ==================
@st.cache_data(show_spinner=True)
def carregar_embeddings():
    """Carrega os embeddings pré-computados do FAQ, se existirem."""
    file_path = "faq_embeddings.json"  # Caminho relativo ao diretório raiz
    
    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        st.warning(f"O arquivo {file_path} não foi encontrado. Gerando embeddings...")
        return None
    
    try:
        # Tenta abrir e carregar o arquivo JSON
        with open(file_path, "r", encoding="utf-8") as f:
            embeddings = json.load(f)
            
            # Verifica se o conteúdo é um dicionário
            if not isinstance(embeddings, dict):
                st.error(f"O arquivo {file_path} não está no formato correto (esperado: dicionário).")
                return None
            
            return embeddings
    except json.JSONDecodeError as e:
        st.error(f"Erro ao decodificar o arquivo {file_path}: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao carregar {file_path}: {e}")
        return None

# Carregar embeddings
faq_embeddings = carregar_embeddings()


# ================== Gerar Embeddings ==================
@st.cache_data(show_spinner=True)
def gerar_embedding(texto):
    """Gera embeddings para um determinado texto usando OpenAI."""
    response = openai.embeddings.create(input=texto, model="text-embedding-3-small")
    return response.data[0].embedding

# Se os embeddings não existirem, criá-los
if 'pergunta' in df.columns:
    perguntas = df['pergunta'].tolist()  # Converte a coluna 'pergunta' em uma lista
    total_perguntas = len(perguntas)
    progress_bar = st.progress(0)  # Inicializa a barra de progresso
    
    for i, pergunta in enumerate(perguntas):
        faq_embeddings[pergunta] = gerar_embedding(pergunta)
        # Atualiza a barra de progresso
        progress_bar.progress((i + 1) / total_perguntas)
        time.sleep(0.1)  # Simulando tempo de resposta para cada requisição (opcional)
    
    # Salvar os embeddings no arquivo JSON
    with open("faq_embeddings.json", "w", encoding="utf-8") as f:
        json.dump(faq_embeddings, f, ensure_ascii=False, indent=4)

# ================== Carregar FAISS Index ==================
@st.cache_data(show_spinner=True)
def carregar_faiss_index(caminho):
    """Carrega o índice FAISS, se existir."""
    if os.path.exists(caminho):
        try:
            index = faiss.read_index(caminho)
            return index
        except Exception as e:
            st.error(f"Erro ao carregar o índice FAISS: {e}")
            return None
    else:
        st.warning(f"Arquivo de índice FAISS não encontrado em: {caminho}")
        return None

# Define o caminho absoluto para o arquivo de índice
faq_index_path = os.path.abspath("faq_index.faiss")

# Carrega o índice FAISS
faq_index = carregar_faiss_index(faq_index_path)

# Caso o índice não exista, cria-se um novo índice com normalização
if faq_index is None:
    # Verifica a dimensão dos embeddings
    sample_emb = next(iter(faq_embeddings.values()))
    dimension = len(sample_emb)
    faq_index = faiss.IndexFlatL2(dimension)  # Cria um novo índice com a dimensão correta
    for pergunta, emb in faq_embeddings.items():
        emb_array = np.array([emb], dtype=np.float32)
        norm = np.linalg.norm(emb_array)
        if norm != 1.0:  # Verifica se o embedding já está normalizado
            faiss.normalize_L2(emb_array)
        faq_index.add(emb_array)  # Adiciona o embedding ao índice
    faiss.write_index(faq_index, faq_index_path)  # Salva o índice para reutilização
    
# ================== Busca no FAQ com Similaridade ==================
@st.cache_data(show_spinner=True)
def buscar_resposta_faq(pergunta_usuario, max_palavras=150, limiar_distancia=0.5):
    """Busca a resposta mais similar no FAQ com base em embeddings.
       Retorna None se a distância for maior que o limiar."""
    embedding_pergunta = np.array(gerar_embedding(pergunta_usuario)).reshape(1, -1).astype(np.float32)
    faiss.normalize_L2(embedding_pergunta)  # Normaliza o embedding da pergunta do usuário
    
    distancias, indices = faq_index.search(embedding_pergunta, k=1)  # Busca no índice FAISS
    # Para debug: st.write("Distância calculada:", distancias[0][0])
    
    # Se a distância for maior que o limiar, não há correspondência adequada no FAQ.
    if distancias[0][0] > limiar_distancia:
        return None
    
    melhor_pergunta = df.iloc[indices[0][0]]['pergunta']
    melhor_resposta = df[df['pergunta'] == melhor_pergunta]['resposta'].values[0]
    
    return limitar_resposta(melhor_resposta, max_palavras)

# ================== Limitar Resposta ==================
@st.cache_data(show_spinner=True)
def limitar_resposta(resposta, max_palavras):
    palavras = resposta.split()
    return ' '.join(palavras[:max_palavras]) + ('...' if len(palavras) > max_palavras else '')

# ================== Busca Híbrida ==================
@st.cache_data(show_spinner=False)
def buscar_resposta_hibrida(pergunta_usuario, max_palavras=150):
    resposta_faq = buscar_resposta_faq(pergunta_usuario, max_palavras)
    if resposta_faq:
        return resposta_faq  # Se a similaridade for alta, retorna a resposta do FAQ
    
    # Se não encontrar uma correspondência adequada, consulta o GPT-3.5-Turbo
    contexto = (
    "Você é um assistente educacional especializado em infraestrutura de internet escolar e educação em São Paulo. "
    "Sua missão é fornecer respostas precisas, detalhadas e fundamentadas em dados reais e referências confiáveis. "
    "Utilize as informações a seguir para embasar suas respostas, levando em conta tanto os desafios técnicos quanto as implicações pedagógicas:\n"
    "\n"
    "1. Conectividade e Qualidade de Internet:\n"
    "- Segundo o NIC.br, 99% das escolas públicas de São Paulo estão conectadas à internet, embora a qualidade e a estabilidade dessas conexões possam variar, afetando a experiência de ensino e aprendizagem.\n"
    "- Um levantamento do CGI.br apontou desafios significativos na qualidade da internet nas escolas, incluindo problemas de velocidade insuficiente e instabilidade, o que impede uma utilização plena das tecnologias digitais.\n"
    "\n"
    "2. Iniciativas e Metas Governamentais:\n"
    "- O projeto 'Escolas Conectadas', divulgado pelo gov.br/SECOM, já levou acesso à internet a 1.046 instituições de ensino, marcando um importante avanço na democratização do acesso digital.\n"
    "- O SPTIC indica que 1.927 escolas já possuem acesso à internet para uso pedagógico, mas ressalta a necessidade de melhorias contínuas na infraestrutura e na capacitação dos profissionais.\n"
    "- O MEC definiu metas ambiciosas para garantir que todas as escolas tenham acesso a conexões de alta velocidade até 2025, incentivando investimentos em infraestrutura e na formação de professores.\n"
    "\n"
    "3. Educação e Integração Digital:\n"
    "- Além da infraestrutura, é essencial promover a integração efetiva das tecnologias educacionais no currículo, garantindo que o acesso à internet seja utilizado para inovar práticas pedagógicas e melhorar a qualidade do ensino.\n"
    "- A capacitação de professores e a criação de ambientes digitais interativos são fundamentais para transformar a conectividade em uma ferramenta de aprendizagem eficaz.\n"
    "\n"
    "4. Dados do Painel:\n"
    "- Para perguntas que envolvem métricas, estatísticas ou categorias de velocidade (por exemplo, muito baixa, baixa, média e alta) e informações relacionadas ao IDEB, se esses dados não estiverem disponíveis no FAQ, informe que eles podem ser visualizados no próprio painel.\n"
    "\n"
    "Utilize essas informações para elaborar respostas que esclareçam os desafios e avanços na conectividade das escolas de São Paulo, considerando tanto os aspectos técnicos quanto as necessidades e inovações na área da educação."
    )

    resposta_gpt = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": pergunta_usuario}
        ],
        max_tokens=max_palavras * 2
    )
    
    return limitar_resposta(resposta_gpt.choices[0].message.content, max_palavras)

 # ================== Interface do Chatbot ==================

st.title("Assistente de análise de dados do painel")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for user_message, bot_response in st.session_state.chat_history:
    st.write(f"**Você:** {user_message}")
    st.write(f"**Chatbot:** {bot_response}")
    st.write("---")

with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    user_input = st.text_area("Digite sua pergunta:", key="user_input", height=80)
    submit_button = st.button("Enviar")
    st.markdown('</div>', unsafe_allow_html=True)

if submit_button and user_input:
    st.session_state.chat_history.append((user_input, "Processando..."))
    resposta = buscar_resposta_hibrida(user_input)
    st.session_state.chat_history[-1] = (user_input, resposta)
    st.rerun()
