import streamlit as st
import pandas as pd
import json, os

with open('config.json', 'r') as f:
    CONFIG = json.load(f)
    
CHARTS_PARAMS = {
    'theme' : None, 
    'config' : CONFIG, 
    'use_container_width' : False
}

# ------------ CACHE DATA

# GENERAL
@st.cache_data
def general():
    """ Retourne les données générales """
    COLS = [
        # 'id_election',
        # 'id_brut_miom',
        'Code du département',
        # 'Libellé du département',
        'Code de la commune',
        # 'Libellé de la commune',
        'Code du b.vote',
        'Inscrits',
        'Abstentions',
        # '% Abs/Ins',
        'Votants',
        # '% Vot/Ins',
        'Blancs',
        # '% Blancs/Ins',
        # '% Blancs/Vot',
        'Nuls',
        # '% Nuls/Ins',
        # '% Nuls/Vot',
        'Exprimés',
        # '% Exp/Ins',
        # '% Exp/Vot',
        # 'Code de la circonscription',
        # 'Libellé de la circonscription',
        # 'Code du canton',
        # 'Libellé du canton'
    ]
    df = pd.read_csv('data/general-results.csv', sep=';', usecols=COLS)
    return df

@st.cache_data
def general_fr():
    df = pd.read_csv('data/general-france.csv')
    return df

@st.cache_data
def general_regions():
    df = pd.read_csv('data/general-regions.csv')
    return df

@st.cache_data
def general_departement():
    df = pd.read_csv('data/general-departements.csv', dtype={'Code du département':'object'})
    return df

# CANDIDATS

@st.cache_data
def candidat_list() :
    """ Retourne les données de la liste des candidats """
    df =  pd.read_csv('data/candidats.csv')
    return df

@st.cache_data
def candidat() :
    """ Retourne les données des candidats """
    COLS = [
        # 'id_election',
        # 'id_brut_miom',
        'Code du département',
        'Code de la commune',
        'Code du b.vote',
        # 'N°Panneau',
        'Libellé Abrégé Liste',
        # 'Libellé Etendu Liste',
        # 'Nom Tête de Liste',
        'Voix',
        # '% Voix/Ins',
        # '% Voix/Exp',
        # 'Sexe',
        # 'Nom',
        # 'Prénom',
        # 'Nuance',
        # 'Binôme',
        # 'Liste'
    ]

    df = pd.read_csv('data/candidats-results.csv', usecols=COLS)
    return df

@st.cache_data
def candidat_fr() :
    """ Retourne les données des candidats au niveau Nationnal """
    df =  pd.read_csv('data/candidats-france.csv')
    return df

@st.cache_data
def candidat_regions():
    df = pd.read_csv('data/candidats-regions.csv')
    return df

@st.cache_data
def candidat_departement():
    df = pd.read_csv('data/candidats-departements.csv', dtype={'Code du département':'object'})
    return df

# ------------ FUNCTIONS

def format_k_M(value, digits : int = 2):
    """ 1000 -> 1M, 587 -> 5,87k """
    value = int(value)
    if value < 0 : return '-' + format_k_M(-value, digits)
    if value < 1_000 : return str(value)
    if value < 1_000_000 : return f'{round(value/1000, digits)}k'
    if value < 1_000_000_000 : return f'{round(value/1_000_000, digits)}M'
    return str(value)

# ------------ CHARTS

def bar_chart(
        data : pd.DataFrame, *args, x : str =  'Nom', y : str = 'Voix', color : str = "", 
        _text : bool = False, **kwargs
    ):
    """ Retourne un bar chart (basé Sur vega lite) """
    col = {} if not color else { "color" : {"field":color, "type": "nominal", "legend":None, "sort":"-color"}}

    return st.vega_lite_chart(data, {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "transform": [{"calculate": f"datum.{y}/{data[y].sum()}", "as": "percent"}],
        "encoding": {
            "y": {"field": x, "type": "nominal", "axis": {"labelAngle": -0}, "sort":f"-x"},
            "x": {"field": y, "type": "quantitative", "axis":{"format":"~s", "title":y, "orient": "top"}, 'aggregate':'sum'},
            "tooltip" : [
                {"field": x, "type": "nominal"},
                {"field": y, "type": "quantitative", "format":".3~s", 'aggregate':'sum', 'title':y},
                {"field":"percent", "type": "quantitative", "format":".1%", 'title':'Part'},
                *[{ "field": f, "type": "nominal"} for f in args]
            ],
            **col
        },
        "layer": [
            {"mark": {"type":"bar"}},
            {
            "mark": {"type": "text", "align": "right","baseline": "middle","dx": -5, "fill":"white", "fontSize":18},
            "encoding": {"text": {"field": "percent", "format": ".1%"}} if _text else {}
            }
        ]
    }, **CHARTS_PARAMS, **kwargs)

def pie_chart(data : pd.DataFrame, theta : str, color : str = "", sort : bool = False, **kwargs):
    """ Retourne un pie chart (basé Sur vega lite) """
    order = {"order": {"field": theta, "type": "quantitative", "sort": "descending", "aggregate":"sum"}} if sort else {}
    return st.vega_lite_chart(data, {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "transform": [{"calculate": f"datum.{theta}/{data[theta].sum()}", "as": "percent"}],
        "layer" : [
            {
                "params": [{"name": "select", "select": {"type": "point", "fields": ["Libellé Abrégé Liste"]}}],
                "mark": {"type" : "arc", "strokeWidth":3, "stroke":"white", "innerRadius":90},
                "encoding": {
                    "color": {"field": color, "type": "nominal"},
                    "theta": {"field": theta, "type": "quantitative", "aggregate":"sum"},
                    **order,
                    "tooltip" : [
                        {"field": color},
                        {"field": theta, "type": "quantitative", "aggregate":"sum", "format":".3~s", "title":theta},
                        {"field":"percent", "type": "quantitative", "aggregate":"sum", "format":".1%", "title":'Part'},
                    ]
                }
            },
            {
                "mark": {
                    "type": "text",
                    "fontSize": 15,
                    "y":200,
                    "tooltip": False
                },
                "encoding": {
                    "text":{
                        "field":color
                    },
                    "color": {"field": color, "type": "nominal"},
                    "fillOpacity":{
                        "condition": {"param": "select", "value": 1, "empty": False},
                        "value": 0
                    }
                }
            },
            {
                "mark": {
                    "type": "text",
                    "fontSize": 42,
                    "tooltip": False
                },
                "encoding": {
                    "text":{
                        "field":"percent", "format":".1%"
                    },
                    "fillOpacity":{
                        "condition": {"param": "select", "value": 1, "empty": False},
                        "value": 0
                    }
                }
            }
        ],
    }, **CHARTS_PARAMS, **kwargs)

def percent_kpi_chart(
        value : float, 
        total : float, 
        tooltip_value : str = 'value',
        tooltip_total : str = 'total',
        _text : str = 'percent',
        **kwargs
    ) :
    """ Retourne un KPI façon pourcentage (basé sur un pie plot vega lite) """
    df = pd.DataFrame({
        'value': [value], 'total': [total]
    })
    
    percent = value / total
    text = f"{percent:.1%}" if _text == 'percent' else format_k_M(value)
    return st.vega_lite_chart(df, {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        # "width" : 700,
        # 'title' : 'Taux',
        "layer": [
            {
                "mark": {
                    "type": "arc", "theta":0, "theta2":2*3.14,
                    "color" : "#eeeeee", "cornerRadius":0,
                    "tooltip" : f"{total:,} {tooltip_total}".replace(',', ' ')
                }
            },
            {
                "mark": {
                    "type": "arc", "theta":-1.7, 
                    "theta2":percent*2*3.14-1.7,
                    "color" : "#00a67d",
                    "tooltip" : f"{value:,} {tooltip_value}".replace(',', ' ')
                }
            },
            {
                "mark":{
                    "type": "text", "fontSize":42, 
                    "text": text,
                    "tooltip":False,
                }
            }   
        ]
    },
        **CHARTS_PARAMS, **kwargs
    )

def map_chart(
        data : pd.DataFrame, 
        geojson : str,
        join_key : str, 
        *fields,
        _filter : dict = {},
        object_key : str|None = 'map',
        on_select = 'rerun',
    ) :
    """ 
    Retourne une carte.

    `geojson` :
    - departements-version-simplifiee
    - regions-version-simplifiee
    - communes-version-simplifiee

    """
    
    if isinstance(geojson, str) :
        if not geojson.startswith('http') :
            geojson = f'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/{geojson}.geojson'
        data_geojson = {"url": geojson, "format": {"type": "json", "property": "features"}, "name": "departements"}
    
    elif isinstance(geojson, list) :
        data_geojson = {
            "values":{
                "type": "FeatureCollection",
                "features": geojson
            }, 
            "format": {"type": "json", "property": "features"}, 
            "name": "departements"
        }
        print(data_geojson)
    # else : raise Exception('geojson type is bad')

    fields = list(fields)
    fill = {"fill": { "field": fields[0], "type": "quantitative"}} if len(fields) else {}
    fill = {}

    return st.vega_lite_chart( None,
        {
            "data": data_geojson,
            "params": [
                # {"name": "interval_selection", "select": "interval"},
                {
                    "name": "point_selection",
                    "select": {"type": "point", "fields": ["nomRegion", "codeRegion"]},
                },
            ],
            "transform": [
                {"calculate": "datum.properties.nom", "as": "nomRegion"},
                {"calculate": "datum.properties.code", "as": "codeRegion"},
                {
                    "lookup": "properties.code",
                    "from": {
                        "data": {"values": data.to_json(orient="records")},
                        "key": join_key,
                        # "fields": ['Votants'],
                        "fields": fields,
                    },
                },
                _filter,
            ],
            # "width": 350,
            "height": 300,
            "mark": {
                "type": "geoshape",
                "stroke": "#333",
                "fill": "#00a67d",
                "filled": True,
                # "tooltip": {"content": "data"},
                "cursor": "pointer",
            },
            "projection": {"type": "mercator"},
            "encoding": {
                "opacity": {
                    "condition": {
                        "param": "point_selection",
                        # "field": 'Votants',
                        # "type": "quantitative",
                        "value":1
                    }, "value" :.3
                },
                **fill,
                "tooltip": [
                    { "field": "properties.nom", "type": "nominal", "title": "Région"},
                    *[{ "field": f, "type": "quantitative", "format":".3~s"} for f in fields]
                ],
            },
        },
        key=object_key,
        on_select=on_select,
        **CHARTS_PARAMS,
        # use_container_width=True,
        # theme=None
    )