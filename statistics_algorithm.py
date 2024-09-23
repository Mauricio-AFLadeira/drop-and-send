import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from scipy.stats import norm
from statsmodels.tsa.stattools import kpss
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense

# Função para gerar estatísticas descritivas
def generate_statistics(df, data_column):
    return df[data_column].describe()

# Função para plotar gráficos
def plot_graphics(df, data_column, pdf):
    plt.figure()
    plt.hist(df[data_column], bins=100, density=True, rwidth=0.8, color='blue')
    plt.xlabel('Segundos')
    plt.ylabel(data_column)
    plt.title(f'Histograma de {data_column}')
    pdf.savefig()

    plt.figure()
    df.plot()
    plt.xlabel('Segundos')
    plt.ylabel(data_column)
    plt.title(data_column)
    plt.grid(True)
    pdf.savefig()

    plt.figure()
    plt.boxplot(df[data_column])
    plt.title('Boxplot de ' + data_column)
    pdf.savefig()

    plt.close('all')

# Função para análise de normalidade e estacionariedade
def analyze_normality_stationarity(df, data_column):
    sh_stat, sh_p_value = stats.shapiro(df[data_column])
    kpss_stat, kpss_p_value, _, _ = kpss(df[data_column])
    
    return {
        'shapiro_stat': sh_stat,
        'shapiro_p_value': sh_p_value,
        'kpss_stat': kpss_stat,
        'kpss_p_value': kpss_p_value
    }

# Função para realizar suavizações
def smoothing_and_modeling(df, data_column, pdf):
    plt.figure()
    fit1 = SimpleExpSmoothing(df[data_column]).fit(smoothing_level=0.2, optimized=False)
    fcast1 = fit1.forecast(12).rename(r'$alpha=0.2$')
    fcast1.plot(marker='.', color='blue', legend=True)
    fit1.fittedvalues.plot(marker='.', color='red')
    plt.title('Suavização Exponencial Simples')
    pdf.savefig()

    plt.figure()
    fit2 = Holt(df[data_column]).fit(smoothing_level=0.8, smoothing_trend=0.2, optimized=False)
    fcast2 = fit2.forecast(12).rename("Holt's linear trend")
    fcast2.plot(marker='.', color='blue', legend=True)
    fit2.fittedvalues.plot(marker='.', color='red')
    plt.title('Suavização de Holt')
    pdf.savefig()

    plt.figure()
    fit4 = ExponentialSmoothing(df[data_column], seasonal_periods=12, trend='additive', seasonal='additive').fit()
    fcast4 = fit4.forecast(24).rename("Holt Winters Aditivo")
    fcast4.plot(marker='.', color='blue', legend=True)
    fit4.fittedvalues.plot(marker='.', color='red')
    plt.title('Holt Winters Aditivo')
    pdf.savefig()

    plt.close('all')

# Função para treinamento da rede neural
# def train_neural_network(df, data_column, pdf):
#     data = df[data_column].values.astype('float32')
#     train = data[:350]
#     test = data[350:]

#     def prepare_data(data, lags=1):
#         X, Y = [], []
#         for row in range(len(data) - lags - 1):
#             a = data[row:(row + lags)]
#             X.append(a)
#             Y.append(data[row + lags])
#         return np.array(X), np.array(Y)

#     lags = 1
#     X_train, Y_train = prepare_data(train, lags)
#     X_test, Y_test = prepare_data(test, lags)

#     md1 = Sequential()
#     md1.add(Dense(3, input_dim=lags, activation='relu'))
#     md1.add(Dense(1))
#     md1.compile(loss='mean_squared_error', optimizer='adam')
#     md1.fit(X_train, Y_train, epochs=200, batch_size=2, verbose=2)

#     train_predict = md1.predict(X_train)
#     test_predict = md1.predict(X_test)

#     plt.figure()
#     plt.plot(X_train, color='blue')
#     plt.plot(train_predict, color='red')
#     plt.title('Previsão - Dados de Treino')
#     pdf.savefig()

#     plt.figure()
#     plt.plot(X_test, color='blue')
#     plt.plot(test_predict, color='red')
#     plt.title('Previsão - Dados de Teste')
#     pdf.savefig()

#     plt.close('all')
