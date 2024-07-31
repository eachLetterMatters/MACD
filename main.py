import pandas
import time
import datetime
from matplotlib import pyplot

import customtkinter
from tkinter import messagebox
import random
import numpy as np

# function that retrieves stock price data from finance yahoo
# it requires one argument - ticker - which is an abbreviation for a stock's name
# it returns two arrays - dates and associated with them exchange rates
def get_data(ticker, year1, year2):
    try:
        begin_date = int(time.mktime(datetime.datetime(int(year1),1,1,23,59).timetuple()))
        finish_date = int(time.mktime(datetime.datetime(int(year2),12,31,23,59).timetuple()))
        interval = '1d'
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={begin_date}&period2={finish_date}&interval={interval}&events=history&includeAdjustedClose=true'
        data = pandas.read_csv(query_string)
        # label2.configure(text="")
        return data['Date'].to_list(), data['Close'].to_list()
    except:
        # label2.configure(text="Enter valid values")
        print("Wrong values!")
        return None, None

def create_chart(data1, data2):
    pyplot.xlabel('Date', fontsize=18)
    pyplot.ylabel('Price', fontsize=18)
    pyplot.plot(data1, data2)
    pyplot.show()

class Macd:
    def __init__(self, exc_rates, dates, ticker):
        self.exc_rates = exc_rates
        self.dates = dates
        self.ticker = ticker
        self.macd_values = []
        self.signal_values = []
        self.action_flags = []
        # investor fields
        self.money = 10000.0
        self.money_list = []
        self.bought_units = 0
        # random investor fields
        self.random_money = 10000.0
        self.random_bought_units = 10000.0
        # calculate everything possible during object construction
        self.calculate_macd_values()
        self.calculate_signal_values()
        self.set_action_flags()
        self.invest()
        self.random_invest()


    # calculates Exponential Moving Average - needed for MACD & Signal
    # data -> used for calculation of EMA
    # starting_index -> from which day do we start calculating EMA
    # n -> how many days do we take into account
    def ema(self, data, starting_index, n):
        sample = data[starting_index - n:starting_index+1:1]
        sample.reverse()
        alpha = 2 / (n + 1)
        fraction_counter = 0.0
        fraction_denominator = 0.0
        for i in range(n+1):
            fraction_counter += (1 - alpha ) ** i * sample[i]
            fraction_denominator += (1 - alpha ) ** i
        return fraction_counter / fraction_denominator

    def calculate_macd_values(self):
        for i in range(len(self.exc_rates)):
            if i < 26:
                self.macd_values.append(0.0)
            else:
                ema_12 = self.ema(self.exc_rates, i, 12)
                ema_26 = self.ema(self.exc_rates, i, 26)
                self.macd_values.append(ema_12 - ema_26)

    def calculate_signal_values(self):
        for i in range(len(self.macd_values)):
            if i < 35:
                self.signal_values.append(0)
            else:
                self.signal_values.append(self.ema(self.macd_values, i, 9))

    def set_action_flags(self):
        for i in range(35):
            self.action_flags.append("wait")
        for i in range(35, len(self.macd_values)):
            if self.macd_values[i] >= self.signal_values[i] and self.macd_values[i - 1] < self.signal_values[i - 1]:
                self.action_flags.append("sell")
            elif self.macd_values[i] <= self.signal_values[i] and self.macd_values[i - 1] > self.signal_values[i - 1]:
                self.action_flags.append("buy")
            else:
                self.action_flags.append("wait")

    def invest(self):
        for i in range(len(self.exc_rates)):
            if self.action_flags[i] == "buy":
                if self.money != 0:
                    self.bought_units = float(self.money / self.exc_rates[i])
                    self.money = 0
            elif self.action_flags[i] == "sell":
                if self.bought_units != 0:
                    self.money = self.bought_units * self.exc_rates[i]
                    self.bought_units = 0
            if self.money == 0 and i == len(self.exc_rates) - 1:
                self.money = float(self.bought_units * self.exc_rates[-1])

            self.money_list.append(self.money)

    def random_invest(self):
        for i in range(100):
            temp_money = 10000
            temp_bought_units = 0

            random_days_wait = random.randint(5, 20)
            for i in range(len(self.exc_rates)):
                if random_days_wait <= 0:
                    random_days_wait = random.randint(5, 20)
                    if temp_money != 0:
                        temp_bought_units = float(temp_money / self.exc_rates[i])
                        temp_money = 0
                    else:
                        temp_money = temp_bought_units * self.exc_rates[i]
                        temp_bought_units = 0
                else:
                    random_days_wait -= 1
            if temp_money == 0:
                temp_money = float(temp_bought_units * self.exc_rates[-1])

            self.random_money += temp_money

        self.random_money /= 100



    def show_chart(self):

        #pyplot.style.use('seaborn-dark')
        fig, axs = pyplot.subplots(3, figsize=(10, 7))

        jump = int(len(self.dates)/4)
        test_array = [self.dates[0],self.dates[jump],self.dates[2*jump],self.dates[3*jump],self.dates[-1]]

        fig.suptitle('Charts generated for ' + self.ticker.upper() + '\nMACD profit: ' + str(round(self.money-10000.0,2)) + '\$    Random profit: ' + str(round(self.random_money-10000.0,2)) +'\$')

        axs[0].plot(self.dates, self.macd_values, label="MACD", color='blue')
        axs[0].plot(self.dates, self.signal_values, label="SIGNAL", color='red')
        axs[0].legend()
        axs[0].set_ylabel('Indicators\' values')
        axs[0].set_xticks(test_array)
        axs[0].set_xticklabels(test_array)

        axs[1].plot(self.dates, self.exc_rates, label="EXC RATE", color='black')

        tmp_buy_dates = []
        tmp_buy_exc_rates = []
        tmp_sell_dates = []
        tmp_sell_exc_rates = []

        for i in range(len(self.action_flags)):
            if self.action_flags[i] == 'buy':
                tmp_buy_dates.append(self.dates[i])
                tmp_buy_exc_rates.append(self.exc_rates[i])
            elif self.action_flags[i] == 'sell':
                tmp_sell_dates.append(self.dates[i])
                tmp_sell_exc_rates.append(self.exc_rates[i])

        axs[1].plot(tmp_buy_dates, tmp_buy_exc_rates, 'ro', label="BUY")
        axs[1].plot(tmp_sell_dates, tmp_sell_exc_rates, 'go', label="SELL")
        axs[1].set_xlabel('Date')
        axs[1].set_ylabel('Exchange rate')
        axs[1].legend()
        axs[1].set_xticks(test_array)
        axs[1].set_xticklabels(test_array)

        axs[2].plot(self.dates, self.money_list, label="Investor assets", color='red')
        axs[2].legend()
        axs[2].set_xticks(test_array)
        axs[2].set_xticklabels(test_array)

        pyplot.show()


def run_macd():
    ticker = entry1.get()
    year1 = entry2.get()
    year2 = entry3.get()
    dates, exc_rates = get_data(ticker, year1, year2)
    if dates == None or exc_rates == None:
        pass
    else:
        macd = Macd(exc_rates, dates, ticker)
        macd.show_chart()

def on_closing():
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    root.destroy()
    pyplot.close()



customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.title("MACD simulation")
root.geometry("400x500")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=50, padx=50, expand="True", fill="both")

label3 = customtkinter.CTkLabel(master=frame, text="Choose time period:", font=("Roboto", 24))
label3.pack(pady=(40,10))

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="Enter begining year")
entry2.pack(pady=10)

entry3 = customtkinter.CTkEntry(master=frame, placeholder_text="Enter ending year")
entry3.pack(pady=10)

label = customtkinter.CTkLabel(master=frame, text="Choose ticker:", font=("Roboto", 24))
label.pack(pady=(30,10))

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Enter ticker")
entry1.pack(pady=0)

label2 = customtkinter.CTkLabel(master=frame, text=" ", font=("Roboto", 14),  text_color=("red"))
label2.pack()

button1 = customtkinter.CTkButton(master=frame, text="Execute", command=run_macd)
button1.pack(pady=10)


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# final_macd = 0
# final_random = 0
#
# for t in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'V', 'XOM', 'UNH', 'JNJ', 'WMT']:
#
#     dates, exc_rates = get_data(t, 2012, 2018)
#     if dates == None or exc_rates == None:
#         pass
#     else:
#         macd = Macd(exc_rates, dates, t)
#         final_macd += round(macd.money-10000.0,2)
#         final_random += round(macd.random_money-10000.0,2)
#
# print('Average MACD profit: ' + str((final_macd - final_random)/12 ))


