import streamlit as st
from streamlit_lottie import st_lottie

import plotly.express as px
import plotly.graph_objects as go

# from plotly.subplots import make_subplots

import pandas as pd

from utils import *

# Titulo y descripción del proyecto
st.set_page_config(
    page_title="SalariApp - Analizador de sueldo",
    page_icon=":money_with_wings:",
    # layout="wide",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "Hola! este es un proyecto personal que te permite visualizar tu salario mes a mes y compararlo contra algunas variables macroeconómicas como la inflación (oficial) del país.",
    },
)

lottie_book = load_lottieurl("https://lottie.host/81245fc2-7cab-4a5d-9075-3521944f9c93/fM1lCLA86z.json")
st_lottie(lottie_book, speed=1, height=200, key="initial")

st.markdown(
    """
    # Hola! :raising_hand:

    SalariApp te permite visualizar tu salario mes a mes y compararlo contra su valor ajustado por la [inflación informada por BCRA](https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables_datos.asp?serie=7931&detalle=Inflaci%F3n%20mensual%A0(variaci%F3n%20en%20%))

    *Ultima Actualización: 24/01/2024* 
    """
)
with st.expander(":soon: **Ideas para el futuro**"):
    st.markdown(
        """
        - Agregar otras variables como el dolar oficial
        - Analizar mejora en los gráficos
        - Carga de archivos Excel 
        """
    )
with st.expander(":nerd: **Explicación técnica del cálculo**"):
    st.markdown(
        """
            :one: Primero que nada preprocesamos tus datos. Puede pasar que para un mismo mes tengas más de un ingdf_reso (bono, aguinaldo, etc.). Es por esto, que sumamos todos los ingdf_resos mensuales y luego generamos una columna adicional 'Cantidad de Ingdf_resos' que contabiliza cuantos ingdf_resos se tuvo durante ese mes.
            
            :two: ¿Como ajustamos el salario mes a mes? A partir de tu primer sueldo, vamos acumulando el efecto de la inflación histórica. Ejemplo:

            
            | Indice | Mes     | Sueldo | Inflacion | Ajustado                     |
            |--------|---------|--------|-----------|------------------------------|
            | 0      | 2021-03 | 10,000 | 10%       | 10,000                       |
            | 1      | 2021-04 | 10,500 | 15%       | 10,000 x (1 + 0.10) = 11,000 |
            | 2      | 2021-05 | 10,950 | 12%       | 11,000 x (1 + 0.15) = 12,650 |

            :information_source: En este caso, se puede observar como el sueldo quedó por debajo de la inflación 
            """
    )

with st.sidebar:
    # cargamos archivo CSV de ejemplo por defecto
    st.subheader("Suba sus datos")
    types = ["csv"]  # ["csv", "xlsx"]
    uploaded_file = st.file_uploader(
        "Easter egg?", type=types, help="Arrastra los archivos aquí", label_visibility="collapsed"
    )

    # si se subió un archivo...
    if uploaded_file is not None:
        file_extention = uploaded_file.type
        try:
            if file_extention == "text/csv":
                df = pd.read_csv(uploaded_file, sep=None, engine="python")
            elif file_extention == "xlsx":
                df = pd.read_excel(uploaded_file)
            else:
                raise ValueError

            st.success("Archivo cargado con éxito.")
        except Exception as e:
            st.error(f"Error al cargar archivo: {e}")

    # si el archivo fue cargado correctamente...
    if "df" in locals():
        st.subheader("Seleccione las columnas a utilizar")
        col1a, col1b = st.columns(2)
        with col1a:
            date_column = st.selectbox("Columna FECHA:", df.columns, index=None)
        with col1b:
            salary_column = st.selectbox("Columna SUELDO:", df.columns, index=None)


# si las columnas fueron seleccionadas...
if "df" in locals() and date_column is not None and salary_column is not None:
    try:
        df_res = processing_data(df, date_column, salary_column)
        processing = "complete"
    except Exception as e:
        processing = "error"
        raise e

st.divider()

if "processing" in locals() and processing == "complete":
    # Gráfico con los montos
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_res["periodo"],
            y=df_res["salario_ajustado"],
            name="Salario Ajustado",
            # mode="lines+markers+text",
            # text=df_res["salario_ajustado"],
            # textposition="top center",
            fill="tozeroy",
        )
    )  # tonexty fill to trace0 y
    fig.add_trace(
        go.Scatter(
            x=df_res["periodo"],
            y=df_res["salario"],
            name="Salario Real",
            fill="tonexty",
        )
    )  # fill down to xaxis
    fig.update_layout(
        title="Evolución de los Salarios",
        xaxis_title="Fecha",
        yaxis_title="Monetario ($)",
    )
    st.plotly_chart(fig)

    # Gráfico con los índices
    df_ind = df_res[df_res["periodo"] != max(df_res["periodo"])]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_ind["periodo"],
            y=df_ind["indice_inflacion"],
            name="Indice inflación",
            # mode="lines+markers+text",
            # text=df_res["salario_ajustado"],
            # textposition="top center",
            # fill="tozeroy",
        )
    )  # tonexty fill to trace0 y
    fig.add_trace(
        go.Bar(
            x=df_ind["periodo"],
            y=df_ind["indice_salarial"],
            name="Índice salarial",
            # fill="tonexty",
        )
    )  # fill down to xaxis
    fig.update_layout(
        title="Evolución de los Índices",
        xaxis_title="Fecha",
        yaxis_title="Porcentual (%)",
    )
    st.plotly_chart(fig)
    with st.expander("**:information_source: Ver datos subsayecentes**"):
        st.dataframe(df_res)
        csv = convert_df(df_res)
        st.download_button(
            label="Descargar datos", data=csv, file_name="salariapp_datos.csv", mime="text/csv", type="primary"
        )

    # TODO: Agrega aquí el código para graficar otras variables económicas como la inflación y el dólar oficial

    # fig.add_trace(go.Scatter(x=df_res["periodo"], y=df_res["salario"], name="Salario", mode="lines"))
    # fig.add_trace(
    #     go.Scatter(x=df_res["periodo"], y=df_res["salario_ajustado"], name="Ajustado por Inflación", mode="lines")
    # )
    # # Segundo gráfico con eje y secundario
    # fig.add_trace(
    #     go.Scatter(x=df_res["periodo"], y=df_res["indice_inflacion"], name="Inflación", mode="lines"),
    #     secondary_y=True,
    # )
    # fig = px.area(
    #     df_res[df_res["periodo"] != max(df_res["periodo"])],
    #     x="periodo",
    #     y=["check_infla", "indice_salarial"],
    #     labels={"value": "Salario", "variable": "Tipo de Salario"},
    #     fill="tozeroy"
    #     # markers=True,
    # )
