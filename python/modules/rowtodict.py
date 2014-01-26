'''
Go from a pandas data frame to a list of dictionaries with each dict having all the variables for one row
useful for moving between pandas and networkx graphs
'''
import pandas as pd


def df2rowdict(df, columns):
    dictlist = []
    for i in range(df.shape[0]):
        dictlist.append(makedict(df, df.index[i], columns))
    return dictlist

def makedict(df,row, names):
    return {k: df.loc[row][k] for k in names}

def dict2column(df, dic, name):
    #Function to take a dictionary where keys are row ids in a dataframe, and convert it into a column in said data frame
    
    dftmp = pd.DataFrame.from_dict(dic,orient = 'index')
    dftmp.columns = [name]
    df = pd.merge(df,dftmp,left_index = True, right_index = True)
    return df