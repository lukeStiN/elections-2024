import streamlit as st 
import pandas as pd

import json, time

from utils import format_k_M, percent_kpi_chart, bar_chart, pie_chart, map_chart
from utils import general_fr, general_regions, general_departement, candidat_list, candidat_fr, candidat_regions, candidat_departement 

DATA_PATH = "C:\\Users\\Luc\\Documents\\data\\elections-euro\\2019-clean\\"
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

COLNAMES = [
    'Votants',
    'Inscrits',
    'Abstentions',
    'Blancs',
    'Nuls',
    'Exprimés',
]

if 'step' not in st.session_state : st.session_state.step = 0 # 0 -> nationnal; 1 -> regional; 2 -> departemental
if 'selection_view' not in st.session_state : st.session_state.selection_view = [None, None]

st.set_page_config("Carte interractive - Elections européennes 2024", '🗳️', 'wide', 'collapsed', {})
# ":rainbow-background[Elections européennes 2024]"
# ":gray[Elections européennes 2024]"

def selection(v : int) :
    """ Definit l'etape """
    st.session_state.step = v

@st.experimental_dialog("Données", width='large')
def view_data(*dataframes):
    """ Affiche les données """
    tabs = st.tabs([f'Tableau {i+1}' for i in range(len(dataframes))])

    for i, df in enumerate(dataframes) :
        with tabs[i] :
            st.dataframe(df, hide_index=True)
            st.download_button(
                label="Télécharger les données",
                data=df.to_csv().encode("utf-8"),
                file_name=f"data-{i}.csv", mime="text/csv",
            )

@st.experimental_dialog("Informations", width='large')
def view_informations():
    """ Affiche les données """
    tabs = st.tabs(['Sources', 'Vocabulaire', 'Formules', 'Créateur'])

    for i, info in enumerate(['info-source', 'info-vocab', 'info-formules', 'creator']) :
        with tabs[i] :
            with open(f'infos/{info}.md', 'r', encoding='utf-8') as infos :
                st.markdown(infos.read())

colname = []

main_columns_1, main_columns_2, main_columns_3 = st.columns([2, 2, 3], gap='large')
global_map = main_columns_1.empty()

# REGIONS
with global_map.container() :    
    # map
    "## France métropolitaine"
    buttons_1, buttons_2 = st.columns(2)

    event = map_chart(general_regions(), 'regions-version-simplifiee', 'REG', *colname, 
                      on_select=lambda : selection(1))

# DEPARTEMENTS
if event['selection']['point_selection'] and st.session_state.step >= 1:
    with global_map.container() :

        s_region = event['selection']['point_selection'][0]['nomRegion']
        s_region_code = event['selection']['point_selection'][0]['codeRegion']
        st.session_state.selection_view = [s_region_code, None]

        # map
        title = st.empty()
        title.markdown(f"## {s_region}")
        buttons_1, buttons_2 = st.columns(2)
        event = map_chart(general_departement(), 'departements-version-simplifiee', 'DEP', *colname, 'REG',
                _filter={"filter":f"datum.REG == {s_region_code}"}, object_key='dep', on_select=lambda : selection(2))

        # retour
        if st.button('Retour', help='Retourner au découpage régional', use_container_width=False) : 
            selection(0)
            st.session_state.selection_view = [None, None] 
            st.rerun()

        if event['selection']['point_selection'] :
            s_dep = event['selection']['point_selection'][0]['nomRegion']
            s_dep_code = event['selection']['point_selection'][0]['codeRegion']
            st.session_state.selection_view = [s_region_code, s_dep_code]
            title.markdown(f"## {s_dep}")


# ------ DATA
match st.session_state.selection_view:
    case [None, None] : # FRANCE
        data_general = general_fr()
        data_candidat = candidat_fr()

    case [str() as first, None]: # REGIONS
        # st.markdown(f'## {first}')
        data_general = general_regions()[general_regions()['REG'] == int(first)]
        data_candidat = candidat_regions()[candidat_regions()['REG'] == int(first)]

    case [str() as first, str() as second]: # DEPARTEMENT
        # st.markdown(f'## {second}')
        data_general = general_departement()[general_departement()['DEP'] == second]
        data_candidat = candidat_departement()[candidat_departement()['DEP'] == second]

    case _ : st.error('une erreur est survenue')

# ------ OVERVIEW
# GENERAL
with main_columns_2 : 
    st.markdown('## Participation')

    N = 2 # KPI's
    cols = st.columns(N, gap='medium')
    for i, m in enumerate(['Votants','Abstentions','Blancs','Nuls']) :
        _v = data_general[m].sum()
        cols[i%N].metric(m, format_k_M(_v, 1), help=f'{_v:,} {m}'.replace(',', ' '))

    # Taux
    st.markdown('---\n#### Taux de participation')
    percent_kpi_chart(data_general['Votants'].sum(), data_general['Inscrits'].sum(), 'Votants', 'Inscrits', action=False)

# CANDIDATS
with main_columns_3 :
    st.markdown('## Resultats')
    _principales = st.checkbox('Principales listes uniquement', True)
    
    _data = data_candidat.merge(candidat_list(), how='inner', left_on='PANNEAU', right_on='PANNEAU').drop('PANNEAU', axis=1)
    if _principales :
        _value = _data[_data['Liste'] == 'Autre']['Voix'].sum() # Total Autre
        _data = _data[_data['Liste'] == 'Principale']
        if 'REG' in _data.columns : _data = _data.drop('REG', axis=1)
        if 'DEP' in _data.columns : _data = _data.drop('DEP', axis=1)
        _data.loc[len(_data)] = [_value, 'Autre', 'Autre', 'Autre']
    
    bar_chart(
        _data, 'Libellé de la liste',
        _text=_principales, 
        height=500 if _principales else 800, width=450
    )
    
if buttons_1.button('Informations', use_container_width=True) : 
    view_informations()

if buttons_2.button('Données', use_container_width=True) : 
    view_data(data_general, data_candidat, candidat_list().drop('Liste', axis=1))