import os, random, datetime
import numpy as np, pandas as pd


def dfcoltop(df):
	cols=list(df.index)
	newcols =[cols[-1]]+cols[:-1]
	print(newcols)
	dfnew = df.loc[newcols,:]
	
	return dfnew