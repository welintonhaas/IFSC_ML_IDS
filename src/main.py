import streamlit as st
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix

st.title('IFSC ML IDS')
st.write("Software para detectar tentativas de instrusão usando Machine Learning através de um modelo")

# Importa o CSV
file_buffer = st.file_uploader("Upload do arquivo csv", type=["csv"])

if file_buffer is not None:
    logs = pd.read_csv(file_buffer)

    # Tratamento dos dados Importados
    colIpsDest = logs['destination.ip'].str.split('.', expand=True)
    colIpsSrc = logs['source.ip'].str.split('.', expand=True)
    colIpsDest.rename(columns={
        0:'ipd0',
        1:'ipd1',
        2:'ipd2',
        3:'ipd3'
    }, inplace = True )
    colIpsSrc.rename(columns={
        0:'ips0',
        1:'ips1',
        2:'ips2',
        3:'ips3'
    }, inplace = True )
    previsores = logs[['destination.port', 'source.port', 'pf.packet.length', 'network.transport', 'pf.ipv4.ttl','event.action']]

    previsores = previsores.join(colIpsDest)
    previsores = previsores.join(colIpsSrc)

    previsores = previsores.dropna()
    classe = previsores['event.action']
    previsores = previsores.drop(columns='event.action')

    # Conversão de strings em números
    labelencoder0 = LabelEncoder()
    previsores["network.transport"] = labelencoder0.fit_transform(previsores["network.transport"])

    # Carrega o modelo 
    modelo = pickle.load(open('../model/modelo.sav', 'rb'))

    # Faz a previsão a partir do modelo criado 
    result = modelo.predict(previsores)

    confusao = confusion_matrix(classe, result)
    confusao
    fppf = previsores[(classe != result.T).T]
    fppf['destination.ip'] = fppf['ipd0'].map(str) + '.' + fppf['ipd1'].map(str) + '.' + fppf['ipd2'].map(str) + '.' + fppf['ipd3'].map(str)
    fppf['source.ip'] = fppf['ips0'].map(str) + '.' + fppf['ips1'].map(str) + '.' + fppf['ips2'].map(str) + '.' + fppf['ips3'].map(str)
    fppf = fppf.drop(columns=['ipd0','ipd1','ipd2','ipd3','ips0','ips1','ips2','ips3'])
    fppf