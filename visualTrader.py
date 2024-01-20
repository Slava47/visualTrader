import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta

def update_data():
    # Определение тикера и периода времени
    ticker = ticker_entry.get()
    period = '1d'

    # Загрузка данных
    data = yf.download(ticker, period=period, interval='1m')

    # Проверка на пустоту данных
    if data.empty:
        output_text.insert(tk.END, "No data available for this ticker.")
        return

    # Вычисление скользящих средних
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()

    # Определение сигналов
    data['Buy_Signal'] = np.where((data['MA5'] > data['MA20']), 1, 0)
    data['Sell_Signal'] = np.where((data['MA5'] < data['MA20']), 1, 0)

    # Вычисление стоп-лосса
    data['std_dev'] = data['Close'].rolling(window=30).std()
    data['Stop_Loss'] = data['Close'] - 2 * data['std_dev']

    # Вычисление тейк-профита
    data['Take_Profit'] = data['Close'] + 2 * data['std_dev']

    # Вычисление RSI
    data['RSI'] = ta.momentum.rsi(data['Close'], window=24)

    # Проверка последнего сигнала
    last_row = data.iloc[-1]

    output = ""
    if last_row['Buy_Signal'] == 1:
        output += "LONG\n"
        output += "STOP LOSS: " + str(last_row['Stop_Loss']) + "\n"
        output += "TAKE PROFIT: " + str(last_row['Take_Profit']) + "\n"
        output += "RSI: " + str(last_row['RSI']) + "\n"
    elif last_row['Sell_Signal'] == 1:
        output += "SHORT\n"
        output += "STOP LOSS: " + str(last_row['Stop_Loss']) + "\n"
        output += "TAKE PROFIT: " + str(last_row['Take_Profit']) + "\n"
        output += "RSI: " + str(last_row['RSI']) + "\n"
    else:
        output += "NO\n"

    # Вывод последних данных
    output += str(data.tail())

    # Очистка текстового поля и вывод новых данных
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, output)

root = ThemedTk(theme="arc")  # Используем тему "arc", которая имеет современный вид без углов
root.title("assistant trader")
root.geometry("800x600")

style = {'font': ('Arial', 14)}

ticker_label = ttk.Label(root, text="Enter ticker:", font=style['font'])
ticker_label.pack(padx=10, pady=10)

ticker_entry = ttk.Entry(root, font=style['font'])
ticker_entry.pack(padx=10, pady=10)

button = ttk.Button(root, text="Update Data", command=update_data)
button.pack(padx=10, pady=10)

output_text = tk.Text(root, font=style['font'], bg='light grey', fg='black')  # Изменяем цвет фона и текста
output_text.pack(padx=10, pady=10)

root.mainloop()
