import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

def update_data():
    # ����������� ������ � ������� �������
    ticker = ticker_entry.get()
    period = '5d'

    # �������� ������
    data = yf.download(ticker, period=period, interval='1h')

    # �������� �� ������� ������
    if data.empty:
        output_text.insert(tk.END, "No data available for this ticker.")
        return

    # ���������� ��������� � ������ ������� ���������
    data.fillna(data.mean(), inplace=True)

    # ���������� ���������� �������
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()

    # ����������� ��������
    data['Buy_Signal'] = np.where((data['MA5'] > data['MA20']), 1, 0)
    data['Sell_Signal'] = np.where((data['MA5'] < data['MA20']), 1, 0)

    # ���������� ����-�����
    data['std_dev'] = data['Close'].rolling(window=30).std()
    data['Stop_Loss'] = data['Close'] - 2 * data['std_dev']

    # ���������� ����-�������
    data['Take_Profit'] = data['Close'] + 2 * data['std_dev']

    # ���������� RSI
    data['RSI'] = ta.momentum.rsi(data['Close'], window=24)

    # ���������� ������ ��� ������ �������
    X = data[['Open', 'High', 'Low', 'Volume', 'RSI']]
    y = data['Close']

    # ���������� ������ �� ��������� � �������� ������
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # �������� ������
    model = DecisionTreeRegressor()
    model.fit(X_train, y_train)

    # ������ ������
    score = model.score(X_test, y_test)

    # ��������������� ��� �� �����
    predictions = model.predict(X_test)

    # �������� ���������� �������
    last_row = data.iloc[-1]

    output = ""
    if last_row['Buy_Signal'] == 1:
        output += "LONG\n"
        output += "STOP LOSS: " + str(last_row['Stop_Loss']) + "\n"
        output += "TAKE PROFIT: " + str(last_row['Take_Profit']) + "\n"
        output += "RSI: " + str(last_row['RSI']) + "\n"
        output += "Predicted Price: " + str(predictions[-1]) + "\n"
    elif last_row['Sell_Signal'] == 1:
        output += "SHORT\n"
        output += "STOP LOSS: " + str(last_row['Stop_Loss']) + "\n"
        output += "TAKE PROFIT: " + str(last_row['Take_Profit']) + "\n"
        output += "RSI: " + str(last_row['RSI']) + "\n"
        output += "Predicted Price: " + str(predictions[-1]) + "\n"
    else:
        output += "NO\n"

    # ����� ��������� ������
    output += str(data.tail())

    # ������� ���������� ���� � ����� ����� ������
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, output)

root = ThemedTk(theme="equilux")  # ���������� ���� "equilux", ������� ����� ����������� � �������� ���
root.title("Analytic App")
root.geometry("800x600")

style = {'font': ('Arial', 14)}

ticker_label = ttk.Label(root, text="Enter ticker:", font=style['font'])
ticker_label.pack(padx=10, pady=10)

ticker_entry = ttk.Entry(root, font=style['font'])
ticker_entry.pack(padx=10, pady=10)

button = ttk.Button(root, text="Update Data", command=update_data)
button.pack(padx=10, pady=10)

output_text = tk.Text(root, font=style['font'], bg='light grey', fg='black')  # �������� ���� ���� � ������
output_text.pack(padx=10, pady=10)

root.mainloop()

