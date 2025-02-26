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
st.set_page_config(layout="wide", page_title="Velocidade de Internet nas Escolas São Paulo capital")

# --------------------------------------------------------------------
# TOGGLE SWITCH MODERNO (substitui o radio antigo)
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
            padding: 2px;  /* Reduz o padding */
            display: inline-flex;
            gap: 0;
            position: relative;
            width: 80px;  /* Largura total do toggle */
            height: 30px;  /* Altura total do toggle */
            align-items: center;  /* Centraliza os ícones verticalmente */
        }

        /* Estilo dos botões (sol e lua) */
        div[role=radiogroup] label {
            margin: 0;
            padding: 4px 12px;  /* Ajusta o padding dos ícones */
            cursor: pointer;
            z-index: 1;
            transition: color 0.3s;
            font-size: 14px;  /* Tamanho dos ícones */
            display: flex;
            align-items: center;  /* Centraliza os ícones verticalmente */
            justify-content: center;  /* Centraliza os ícones horizontalmente */
            width: 50%;  /* Cada ícone ocupa metade do container */
        }

        /* Ajuste específico para o ícone do sol (alinhar à esquerda) */
        div[role=radiogroup] label:first-child {
            padding-left: 4px;  /* Alinha o sol à esquerda */
            justify-content: flex-start;  /* Alinha o conteúdo à esquerda */
        }

        /* Ajuste específico para o ícone da lua (alinhar à direita) */
        div[role=radiogroup] label:last-child {
            padding-right: 4px;  /* Alinha a lua à direita */
            justify-content: flex-end;  /* Alinha o conteúdo à direita */
        }

        /* Efeito de slider (parte deslizante) */
        div[role=radiogroup]:after {
            content: "";
            position: absolute;
            width: 42px;  /* Largura do slider */
            height: 34px;  /* Altura do slider */
            background-color: #4CAF50;  /* Cor do slider */
            top: 3px;
            left: 3px;
            border-radius: 16px;
            transition: transform 0.3s;
        }

        /* Movimento do slider baseado na seleção */
        input[value="☀️"]:checked ~ div[role=radiogroup]:after {
            transform: translateX(0);
        }

        input[value="🌙"]:checked ~ div[role=radiogroup]:after {
            transform: translateX(38px);  /* Ajuste para o movimento */
        }

        /* Cor do texto quando selecionado */
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
    plot_bgcolor = "#0e1118"    # Fundo dos gráficos
    paper_bgcolor = "#0e1118"   # Fundo externo dos gráficos
    font_color = "white"        # Cor dos textos, legendas e números
    sidebar_bg = "#383838"      # Fundo da sidebar
    card_bg = "#383838"
    card_text = "white"
else:
    # Modo Claro
    plot_bgcolor = "#ffffff"
    paper_bgcolor = "#ffffff"
    font_color = "#000000"      # Textos do gráfico agora ficam pretos
    sidebar_bg = "#fff9f9"      # Fundo off-white na sidebar
    card_bg = "#fff9f9"
    card_text = "#0e1118"

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
# INJETAR CSS PARA ALTERAR O FUNDO DA APLICAÇÃO E DA SIDEBAR
# --------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    /* Definir cor de fundo e texto da aplicação */
    .stApp {{
        background-color: {plot_bgcolor} !important;
        color: {font_color} !important;
    }}
    /* Alterar fundo da sidebar */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    /* Alterar cor dos textos na sidebar */
    [data-testid="stSidebar"] * {{
        color: {font_color} !important;
    }}
    /* Alterar cor dos labels, escalas e legendas do gráfico */
    .plotly .main-svg {{
        color: {font_color} !important;
        fill: {font_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------------------
# CSS PARA ALTERAR A COR DA BARRA SUPERIOR ("Running")
# --------------------------------------------------------------------
if tema == "🌙":
    header_bg = "#383838"  # Modo escuro
else:
    header_bg = "#fff9f9"  # Modo claro

# Injetar CSS para alterar a cor do header com base no tema
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
q1, q2, q3 = np.percentile(escolas['Velocidade_Internet'], [25, 50, 75])
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
# MAPAS INTERATIVOS e CARDS
####################################
st.title("Velocidade de Internet nas Escolas São Paulo capital")

# Define os tiles do mapa conforme o tema (claro ou escuro)
tiles_map = 'cartodb positron' if tema == "☀️" else 'cartodb dark_matter'

# Calcular as métricas dos cards com base no DataFrame filtrado
if not filtered_escolas.empty:
    media_escolas = filtered_escolas['Velocidade_Internet'].mean()
    # Para a velocidade média dos distritos, agrupamos por distrito e depois calculamos a média geral
    media_distritos = filtered_escolas.groupby('DISTRITO')['Velocidade_Internet'].mean().mean() \
                      if filtered_escolas['DISTRITO'].nunique() > 0 else 0
else:
    media_escolas = 0
    media_distritos = 0

# --- Cards (mesma proporção que os mapas: 2:3) ---
card_left, card_right = st.columns([2, 3])
with card_left:
    st.markdown(f"""
    <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="color: {card_text}; margin: 0;">Velocidade média das escolas</h3>
        <p style="font-size: 24px; color: {card_text}; margin: 0;">
            {media_escolas:.2f} Mbps 
            <span style="color: {'green' if media_escolas > media_distritos else 'red'}; font-size: 20px;">
                {'&#8593;' if media_escolas > media_distritos else '&#8595;'}
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
with card_right:
    st.markdown(f"""
    <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="color: {card_text}; margin: 0;">Velocidade média dos distritos</h3>
        <p style="font-size: 24px; color: {card_text}; margin: 0;">
            {media_distritos:.2f} Mbps 
            <span style="color: {'red' if media_escolas > media_distritos else 'green'}; font-size: 20px;">
                {'&#8595;' if media_escolas > media_distritos else '&#8593;'}
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- Layout dos Mapas ---
# Organiza os mapas em duas colunas com proporção [2, 3]
col_left, col_right = st.columns([2, 3])

# Mapa das Escolas (coluna da esquerda)
with col_left:
    st.header("Localização das Escolas")
    mapa_escolas = folium.Map(
        location=[-23.5505, -46.6333],
        zoom_start=10,
        tiles=tiles_map
    )
    cluster = MarkerCluster(options={'maxClusterRadius': 10}).add_to(mapa_escolas)
    for _, row in filtered_escolas.iterrows():
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=(row['Velocidade_Internet'] / 10) * 1.5,  # Aumenta o tamanho do círculo
            weight=0,               # Remove a borda
            color=None,             # Sem cor de borda
            fill=True,
            fill_color='#fa4c4d',   # Nova cor dos marcadores
            fill_opacity=0.5,
            popup=folium.Popup(
                f"{row['NOMES']}<br>IDEB: {row['IDEB']:.2f}<br>Velocidade: {row['Velocidade_Internet']:.2f} Mbps",
                max_width=300
            ),
        ).add_to(cluster)
    folium_static(mapa_escolas)

# Coluna da direita: subdividida em duas (mapa de distritos e tabela de velocidade)
with col_right:
    # Divide a coluna da direita em duas: mapa de distritos (2/3) e tabela (1/3)
    mapa_col2, tabela_col = st.columns([2, 1])
    
    # Mapa de Distritos (coluna da esquerda interna)
with mapa_col2:
    st.header("Velocidade de Internet por Distrito")
    # Calcula a velocidade média por distrito
    velocidade_por_distrito = escolas.groupby('DISTRITO')['Velocidade_Internet'].mean().reset_index()
    # Mescla os dados do GeoDataFrame com a velocidade média por distrito
    distritos_gdf = distritos_gdf.merge(
        velocidade_por_distrito, left_on='NOME_DIST', right_on='DISTRITO', how='left'
    )
    # Preenche valores NaN com a média geral
    distritos_gdf['Velocidade_Internet'].fillna(distritos_gdf['Velocidade_Internet'].mean(), inplace=True)
    # Cria o colormap com base no intervalo dos valores
    colormap = linear.Reds_09.scale(
        distritos_gdf['Velocidade_Internet'].min(), 
        distritos_gdf['Velocidade_Internet'].max()
    )
    # Cria o mapa de distritos usando os tiles definidos pelo tema,
    # definindo explicitamente a largura e altura para garantir alinhamento
    mapa_distritos = folium.Map(
        location=[-23.5505, -46.6333],
        zoom_start=10,
        tiles=tiles_map,
        width="100%",    # Força a largura a 100%
        height="600px"   # Define a altura para 600px
    )
    
    # Se algum filtro estiver selecionado, define os distritos destacados; caso contrário, nenhum é destacado
    if (st.session_state.get("DRE", []) or 
        st.session_state.get("SUBPREF", []) or 
        st.session_state.get("TIPOESC", []) or 
        st.session_state.get("BAIRRO", []) or 
        st.session_state.get("DISTRITO", []) or 
        st.session_state.get("NOMES", [])):
        highlighted_distritos = filtered_escolas['DISTRITO'].unique().tolist()
    else:
        highlighted_distritos = []
    
    # Função de estilo para os polígonos dos distritos
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
    
    # Define o caption do colormap como texto simples
    colormap.caption = 'Velocidade Média de Internet (Mbps)'
       
    # Adiciona o colormap ao mapa e renderiza o mapa de distritos
    colormap.add_to(mapa_distritos)
    folium_static(mapa_distritos)
    
    # Tabela de Velocidade por Distrito (coluna da direita interna)
    with tabela_col:
        st.header("Velocidade Média por Distrito")
        # Agrupa os dados filtrados por distrito, calcula a média e ordena de forma decrescente
        df_distritos = filtered_escolas.groupby('DISTRITO')['Velocidade_Internet'].mean().reset_index()
        df_distritos = df_distritos.rename(columns={'DISTRITO': 'Distrito', 'Velocidade_Internet': 'Velocidade'})
        df_distritos = df_distritos.sort_values('Velocidade', ascending=False)
    
        st.dataframe(
            df_distritos,
            column_order=("Distrito", "Velocidade"),
            hide_index=True,
            use_container_width=True,  # A tabela ocupará toda a largura do container
            height=600,                # Define a altura (ajuste conforme necessário)
            column_config={
                "Distrito": st.column_config.TextColumn("Distrito"),
                "Velocidade": st.column_config.ProgressColumn(
                "Velocidade (Mbps)",
                    format="%.2f",
                    min_value=0,
                    max_value=df_distritos["Velocidade"].max()
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
