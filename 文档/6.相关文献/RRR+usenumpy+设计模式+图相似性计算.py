from numpy import *
import numpy as  np
from numpy import linalg as LA
np.seterr(divide='ignore', invalid='ignore')

def getnext(B,A,ZK):
    temp= B.dot(ZK).dot(A.T)+B.T.dot(ZK).dot(A)
    # print LA.norm(temp,1)
    if LA.norm(temp,1)==0:
        return temp
    else:
        ZKN=temp/LA.norm(temp,1)
        return ZKN

def similar(B,A):
    Z0 = ones((B.shape[0], A.shape[1]))
    Z=Z0
    ZN=Z0
    while(True):
        ZN=getnext(B,A,Z)
        if (ZN==Z).all():
            return ZN
        Z=ZN
GP=array( [ (0,0), (1,0) ] )
AP=array([(0,0),(1,0)])

GB=array( [ (0,0,0), (1,0,0),(0,1,0) ] )
AB=array([(0,0,0),(0,0,0),(1,0,0)])
print (similar(B=GB,A=GP)+similar(B=AB,A=AP))
GB=array([(0,0),(1,0)])
AB=array([(0,0),(0,0)])
print (similar(B=GB,A=GP)+similar(B=AB,A=AP))
