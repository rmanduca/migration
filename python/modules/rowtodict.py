'''
Go from a pandas data frame to a list of dictionaries with each dict having all the variables for one row
useful for moving between pandas and networkx graphs
'''



def df2rowdict(df, columns):
    dictlist = []
    for i in range(df.shape[0]):
        dictlist.append(makedict(df, df.index[i], columns))
    return dictlist

def makedict(df,row, names):
    return {k: df.loc[row][k] for k in names}
