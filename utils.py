import pandas as pd
import requests
import streamlit as st


@st.cache_data
def convert_df(df: pd.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def processing_data(df: pd.DataFrame, date_column: str, salary_column: str):
    # remover columnas innecesarias
    df = df[[date_column, salary_column]]

    # importante, ordenar cronologicamente
    df = df.sort_values(by=date_column, ascending=True)

    df_group = df.groupby(date_column)[salary_column].agg(["sum", "count"]).reset_index()
    df_group.columns = ["periodo", "salario", "cantidad de ingresos"]

    # incluioms inflacion
    df_inf = pd.read_csv("data/inflacion.csv")

    df_res = pd.merge(df_group, df_inf, how="inner")
    del df, df_inf

    # el primer mes, el sueldo es coincidente
    df_res.at[0, "salario_ajustado"] = df_res.at[0, "salario"]

    # calcular el salario_ajustado y actualizar el DataFrame
    for i in range(1, df_res.shape[0]):
        df_res.at[i, "salario_ajustado"] = df_res.at[i - 1, "salario_ajustado"] * (
            1 + df_res.at[i - 1, "indice_inflacion"] / 100
        )

    # chequeo de calculo
    for i in range(df_res.shape[0] - 1):
        df_res.at[i, "check_infla"] = df_res.at[i + 1, "salario_ajustado"] / df_res.at[i, "salario_ajustado"]

    # indice salarial
    for i in range(df_res.shape[0] - 1):
        df_res.at[i, "indice_salarial"] = ((df_res.at[i + 1, "salario"] / df_res.at[i, "salario"]) - 1) * 100

    return df_res
