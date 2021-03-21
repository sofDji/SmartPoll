#Implementation of Shamir Secret Sharing Scheme 
   
import random 
from math import ceil 
from decimal import *
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

import os
import util.bigprimerand as bigprime

class SSS(object):

    def __init__(self, psswrd):

        self.S = int.from_bytes(psswrd , "big")
     
        bitLenght=self.S.bit_length()
        self.p=bigprime.generate_big_prime (bitLenght)
        self.n = 2
        self.t = 1
        self.shares=[]
    
        #Generation des mini secrets
        self.shares = self.generateShares(self.p,self.n, self.t+1, self.S) 

       
    def get_Shares(self):
        return self.shares
	
    def polynom(self,p,x,coeff): 
        #ici donc on cacule f(i)=i^1*r1+secret%p
        return sum([(x**(len(coeff)-i-1) * coeff[i])%p for i in range(len(coeff))]) 
   
    def coeff(self,p,t,secret): 
        #polynome avec les coeff ri, randomly entre 1 et p-1, de degré t-1(can on a passée t+1 dans les param en bas donc ici c le t du cours) et une cst=secret
        coeff = [random.randrange(1,p-1) for _ in range(t-1)] 
        coeff.append(secret) 
        return coeff 
   
    def generateShares(self,p,n,m,secret): 
        #genrer les coeff ri pour le polynome f(x)
        cfs = self.coeff(p,m,secret) #we have this f(x)= s+r1x1 
        shares = [] 
    
        #generer les si
        #on génére n partages,n petits secrets à partager
        for i in range(1,n+1): 
            #r = random.randrange(1, p-1) 
            shares.append([i, self.polynom(p,i,cfs),p]) 
      
        return shares 
    
    def reconstructSecret(self,shares): 
        sums, prod_arr = 0, [] 
        for j in range(len(shares)): 
            xj, yj = shares[j][0],shares[j][1] 
            prod = 1
          
            for i in range(len(shares)): 
                xi = shares[i][0] 
                if i != j: prod *= (xi)//(xi-xj)
                  
            prod *= yj 
            sums += prod
          
        return int(sums%shares[0][2]) 

