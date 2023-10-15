import matplotlib.pyplot as plt
import pandas as pd
import io

def chart_buffer(X: list, Y: list, info: dict):
    fig, ax = plt.subplots()
    ax.plot(X, Y)
    ax.set_xlabel('Time, days')
    ax.set_ylabel('Price, USD')
    if 'title' in info:
        plt.title(info['title'])
    plt.grid()
    buf = io.BytesIO()
    buf.name = "chart.png"
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

def get_data_from_csv(column):
    columns = ["Date","Open","High","Low","Close","Adj Close","Volume"]
    df = pd.read_csv("data/BTC-USD.csv", usecols=columns)
    return df.iloc[:, column].to_list()
