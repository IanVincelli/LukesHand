import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import serial
import pathlib


def import_data():
    try: 
        arduino = serial.Serial("COM3", timeout=1)
    except:
        print('please check port')

    rawdata = []
    count = 0 

    while count<50:
        rawdata.append(arduino.readline())
        count+=1

    return rawdata

def clean_data(raw):
    cleaned = []
    for i in range(len(raw)):
        test = str(raw[i]).split(';')
        L = len(test)-1
        test[0] = test[0][2:]
        test[L] = test[L][:len(test[L])-5]
        if len(test) == 8:
            cleaned.append(test)
    return cleaned

def to_pandas(data):
    df = pd.DataFrame(data).rename(
        index=str, 
        columns={
            0:'raw',
            1:'R',
            2:'SHID',
            3:'SIG',
            4:'E',
            5:'M',
            6:'t_b',
            7:'t_a'
            }
        )
    return df

def create_dict(freq,amp,title):
    dict_ = {'Freq_'+title:freq.tolist(),'Amp_'+title:amp.tolist()}
    return dict_


def norm(x):
    max = np.max(x)
    min = np.min(x)
    z = [(i-min)/(max-min) for i in x]
    return z

def get_fourier(df):

    _list = ['raw','R','SIG','SHID','E','M']

    norm_dict = {}

    for item in _list:
        norm_dict.update({item:norm([float(i) for i in df[item].tolist()])})

    fs = 100

    x = np.linspace(0,0.5,500)
    S = np.sin(40 * 2 * np.pi * x) + 0.5 * np.sin(90 * 2 * np.pi * x)

    four_dict = {}

    for item in _list:
        x, freq, amp = fourier(norm_dict[item])
        four_dict.update({item:{'x':x,'freq':freq,'amp':amp}})

    i = 0
    for item in _list:
        i=i+1
        graph(norm_dict[item],
              four_dict[item]['x'],
              four_dict[item]['freq'],
              four_dict[item]['amp'],
              item,
              i
            )

    _dict = {}

    for item in _list:
        _dict.update({'freq_'+item:freq.tolist(),'amp_'+item:amp.tolist()})

    df_fourier = pd.DataFrame(_dict)

    #plt.show()

    return df_fourier

def graph(y,x,freq,amp,title,count):
    """
    Graphs the fourier transformed data

    Parameters
    ----------
    x 

    Returns
    -------
    N/A

    """

    plt.figure(count)
    fig,ax = plt.subplots(2,1)
    ax[0].plot(x,y,color='blue',linewidth = 0.5, marker='.', markersize = 0.5)
    ax[0].set_title('pre_fft_'+title)
    ax[1].plot(freq,amp,color='blue',linewidth = 0.5, marker='.', markersize = 0.5)
    ax[1].set_title('fft_'+title)


def fourier(s):  

    x = np.linspace(0,0.5,len(s))
    s = np.array(s)
    fft = np.fft.fft(s)
    #print(fft.real())
    T = x[1] - x[0]
    N = s.size
    f = np.linspace(0,1/T,N)
    freq = f[:N // 2]
    amp = np.abs(fft)[:N // 2] * 1 / N

    return x,freq,amp


def save_data(df):

    try:
        pd.read_csv("C://Users//ianvi//OneDrive//Documents//Projects//Hand//unlabelled_test.csv")
        new = False
    except:
        print("no existing data, creating new")
        new = True

    path = pathlib.Path(__file__).parent.resolve()
    df.to_csv(path_or_buf=path)

def data_processing():
    rawdata = import_data()
    cleaned = clean_data(rawdata)
    df = to_pandas(cleaned)
    df_fourier = get_fourier(df)
    save_data(df_fourier)


data_processing()

