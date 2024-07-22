import pandas as pd
import numpy as np

def switchInterval(initString,changeTo,changeThis='NO',length=4):
    start=initString.index(changeThis)
    condition = len(initString)>(start+length)
    if condition:
        return initString[0:start]+changeTo+initString[start+4:]
    else:
        return initString[0:start]+changeTo

#assuming all the reversible reactions are of 1st order
def makeRev(df):
    #formázzam a stringbe, hog egységes legyen fileban
    value=df[2]/(60.0)
    formatted_number = f"{value:.3e}"
    return "REV / "+formatted_number+" 0 0 /"

#check if 1st 2nd or 0 order, then convert accordingly
def convertReactionK(df):
    lhs,rhs=df[0].split("=")
    #0 order
    if lhs=="REF":
        value=df[1]*10**(-12)/60.0
        return f"{value:.3e}"
    #2nd order
    elif len(lhs.split("+"))==2:
        if "REF" in lhs.split("+"):
            value=df[1]/60.0
            return f"{value:.3e}"
        else:
            value=df[1]*10**(12)/60.0
            return f"{value:.3e}"
    #1st order
    else:
        value=df[1]/60.0
        return f"{value:.3e}"

path='reactionsICs_w_species.xlsx'
df = pd.read_excel(path,header=None)

df[0] = df[0].str.replace(' ', '')
df[0] = df[0].str.replace(':', '_')

#defining new df
df_clean=df[[0,1]]
new_col=pd.Series(np.empty(len(df_clean),dtype=str))
df_clean=pd.concat([df_clean,new_col,new_col],axis=1)
df_clean.columns=['reactions','k1','k2','k3']

for index,row in df.iterrows():
    #skip NaN rows
    if type(row[0])!=str:
        continue
    #NO## to REF
    if "NO" in row[0]:
        df_clean.iloc[index,0]=switchInterval(row[0],"REF")
    #make REV row belove balance
    if '>' not in row[0]:
        df_clean.iloc[index+1,0]=makeRev(df.iloc[index])
    #convert k according to reaction order
    df_clean.iloc[index,1]=convertReactionK(df_clean.iloc[index])
    df_clean.iloc[index,2]=0
    df_clean.iloc[index,3]=0

df_clean.to_csv("_corrected.csv",index=False)
