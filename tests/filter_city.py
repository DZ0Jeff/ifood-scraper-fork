import pandas as pd


def filter_data(df, column="menu", filter_target="Shampoo Monange|Condicionador Monange Hidrata com Poder"):
    return df.loc[df[column].str.contains(filter_target)]

df = pd.read_csv('data/coordinates_list.csv')
data = filter_data(df, column="municipio", filter_target="São Bernardo do Campo|Santo André|São Caetano do Sul")
data.to_csv('data/coordinates_list_filtered.csv', index=False)