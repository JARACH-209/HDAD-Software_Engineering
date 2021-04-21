import seaborn as sns
import matplotlib.pyplot as plt, mpld3
import numpy as np
import sys
from io import BytesIO
import base64
def create_graphs(patient_id, feature_name, feature_data, date_data, single_feature=True,feature_name2 = None):
    '''
    patient_id = number or string
    feature_data = Primary featuredata
    date_data = Dates if single_feature=True (default)
        otherwise enter data of feature2
    if single_feature = True then provide feature_name2
    '''
    plt.style.use("seaborn")
    # plt.tick_params(axis='both',labelsize=20)
    figure,ax = plt.subplots()
    
    # ax.yaxis.set_tick_params(labelsize=20)
    ax.grid(False)
    ax.autoscale(enable=True)

    if single_feature:
        if len(feature_data)!= len(date_data):
            raise Exception("The date and data have different lengths")
        line1 = ax.plot(date_data,feature_data,marker='o',markerfacecolor= 'black',ls="--",lw=3,)
        
        ax.set_xlabel("Date-Time Stamp",fontsize=14)
        ax.set_ylabel(feature_name,fontsize=14)
        title = feature_name+" data for "+str(patient_id)
       



        ax.set_title(title,fontsize=16)
    else:
        line1 = ax.scatter(date_data,feature_data,c='black',marker="o",ls='-')
        ax.set_xlabel(feature_name2,fontsize=12)
        ax.set_ylabel(feature_name,fontsize=12)
        title = feature_name+" vs "+ feature_name2 + " data for "+str(patient_id)
        ax.set_title(title,fontsize=16)
        if len(feature_data)!= len(date_data):
            raise Exception("The feature 1 and 2 have different lengths")
    html_graph = mpld3.fig_to_html(figure)
   
    return html_graph

sys.modules[__name__] = create_graphs