import sys
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier




df = pd.read_excel("0_8_all_ion__high.sensitivity.troponin_BNP_creatine.kinase_cystatin_cholesterol combined.xlsx")



Y = df['congestive.heart.failure'].to_numpy()
X = pd.DataFrame(df.drop(columns = ['congestive.heart.failure' ])).to_numpy()


Y = Y.astype(int)
Y = Y.reshape(-1)

scaler = preprocessing.StandardScaler().fit(X)




clf = RandomForestClassifier(n_estimators=5000,n_jobs=-1)
clf.fit(X,Y)



def model(x):
    return clf.predict(x)

sys.modules[__name__] = model

