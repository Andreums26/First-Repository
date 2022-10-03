#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 18:59:17 2022

@author: henryandreumarquezsalinas
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import t # t - student 
import os 

user = os.getlogin()   # Username
os.chdir(f"/Users/{user}/Documents")
cps2012 = pd.read_excel("cps2012.xlsx")
cps2012

ln = cps2012.lnw.values # se convierte a un array 
wei = cps2012.weight.values
ex1 = cps2012.exp1.values
ex2 = cps2012.exp2.values
ex3 = cps2012.exp3.values

# Generation of data

y = np.log(  ln  ) # lnlnw
c = np.ones( len( y ) ) # Constant
x1 = cps2012.female
x2 = cps2012.widowed
x3 = cps2012.divorced
x4 = cps2012.separated
x5 = cps2012.nevermarried
xw = np.log( wei )
x11 = np.log( ex1 )
x22 = np.log( ex2 ) 
x33 = np.log( ex3 ) 
x12 = np.log( ex1 )*np.log( ex2 )
x13 = np.log( ex1 )*np.log( ex3 ) 
x23 = np.log( ex2 )*np.log( ex3 ) 

columns = [  "ln_lnw", "female", "widowed", "divorced", "separated",
          "nevermarried", "weight", "exp1", "exp2", "exp3", "(exp1)(exp2)", "(exp1)(exp3)", "(exp2)(exp3)" ]

data_val = np.asarray( [ y, x1, x2, x3, x4, x5, xw, x11, x22, x33, x12, x13, x23 ] ).T # se coloca transpuesta para que cada varaible sea una columna 

# np.asarray permite crear una matriz a partir de vectores 

data = pd.DataFrame(  data_val , columns = columns  )
data

# selecting columns
X = data.iloc[ : ,1:]
y = data.ln_lnw
lista = data.iloc[ : , :7]

# Creamos nuestra clase

class OLSRegClass( object ):
    
    def __init__( self, X : pd.DataFrame , y : pd.Series , lista, RobustStandardError = True):
    
        if not isinstance( X, pd.DataFrame ):
            raise TypeError( "X must be a pd.DataFrame." )

        if not isinstance( y , pd.Series ):
            raise TypeError( "y must be a pd.Series." )
            
        # asignando atributos de la clase
        
        self.X = X
        self.y = y
        self.lista = lista
        self.RobustStandardError = RobustStandardError

        self.X[ 'Intercept' ] = 1
        # colcondo la columna Intercept en la primera columna 
        
        cols = self.X.columns.tolist() # nombre de variable a lista 
        new_cols_orders = [cols[ -1 ]] + cols[ 5:-1 ]  # juntamos listas

            
        # [cols[ -1 ]] la jala la ultima fila , cols[ 0:-1 ]  primera fila hasta la fila 9
            
        self.X = self.X.loc[ : , new_cols_orders ] # usamos .loc que filtra por nombre de filas o columnas 

        
        # creando nuevos atributos 
        
        self.X_np = self.X.values  # Dataframe a multi array
        self.y_np = y.values.reshape( -1 , 1 ) # de objeto serie a array columna 
        self.lista = self.X.columns.tolist() # nombre de la base de datos como objeto lista

        
# Creando Métodos #

######################      MÉTODO 1     ###############################################
    
    def reg_beta_OLS( self ):
        # X, y en Matrix, y vector columna respectivamente 
        
        X_np = self.X_np
        y_np = self.y_np

        # beta_ols
        beta_ols = np.linalg.inv( X_np.T @ X_np ) @ ( X_np.T @ y_np )

        # columnas de X
        index_names = self.lista
        # Output
        beta_OLS_output = pd.DataFrame( beta_ols , index = index_names , columns = [ 'Coef.' ] )
        
        # Dataframe de coeffientes como atributo 
        
        self.beta_OLS = beta_OLS_output
        
        return beta_OLS_output
    
    
######################      MÉTODO 2     ###############################################
    
    def var_stderrors_cfdinterval( self ):
        
        ### VARIANZA  ###
        
        # Se corre la función beta_OLS que estima el vector de coeficientes
        self.reg_beta_OLS()
        
        # usaremos atributos pero con un nombre más simple
        X_np = self.X_np
        y_np = self.y_np
        listaf = self.lista
        
        # beta_ols
        beta_OLS = self.beta_OLS.values.reshape( - 1, 1 ) # Dataframe a vector columna 

        # errors
        e = y_np - ( X_np @ beta_OLS )

        # error variance
        N = X_np.shape[ 0 ]
        total_parameters = X_np.shape[ 1 ]
        error_var = ( (e.T @ e)[ 0 ] )/( N - total_parameters )

        # Varianza
        var_OLS =  error_var * np.linalg.inv( X_np.T @ X_np )
        
        # asignando output de la función def reg_var_OLS( self ):   como atributo  self.var_OLS
        index_names = listaf
        var_OLS_output = pd.DataFrame( var_OLS , index = index_names , columns = index_names )
        self.var_OLS = var_OLS_output

        
        ### STANDAR ERRORS  ###
       
        # var y beta
        beta_OLS = self.beta_OLS.values.reshape( -1, 1 )   # -1 significa cualquier número de filas
        var_OLS  = self.var_OLS.values
        
        # standard errors
        beta_stderror = np.sqrt( np.diag( var_OLS ) )
        
        table_data0 = {  "Std.Err." : beta_stderror.ravel()}
        
        # defining index names
        index_names0 = listaf
        
        # defining a pandas dataframe 
        beta_se_output = pd.DataFrame( table_data0 , index = index_names0 )
        self.beta_se = beta_se_output

        ### Confidence interval ###
        
        up_bd = beta_OLS.ravel() + 1.96*beta_stderror
        lw_bd = beta_OLS.ravel() - 1.96*beta_stderror
        
        table_data1 = {"[0.025"   : lw_bd.ravel(),
                       "0.975]"   : up_bd.ravel()}
        
        # defining index names
        index_names1 = listaf
        
        # defining a pandas dataframe 
        confiden_interval_output = pd.DataFrame( table_data1 , index = index_names1 )
        self_confiden_interval = confiden_interval_output
        
        return var_OLS_output, beta_se_output, confiden_interval_output
    
    
######################      MÉTODO 3     ###############################################
    
    def robust_var_se_cfdinterval(self):
    
        # Se corre la función beta_OLS que estima el vector de coeficientes
        self.reg_beta_OLS()
    
        # usaré atributos pero con un nombre más simple
        X_np = self.X_np
        y_np = self.y_np
        listaf = self.lista
        
        beta = np.linalg.inv(X_np.T @ X_np) @ ((X_np.T) @ y )
        y_est = X_np @ beta
        n = X_np.shape[0]
        k = X_np.shape[1] - 1 
        nk = n - k  

        matrix_robust = np.diag(list( map( lambda x: x**2 , y - y_est)))
        Var = np.linalg.inv(X_np.T @ X_np) @ X_np.T @ matrix_robust @ X_np @ np.linalg.inv(X_np.T @ X_np)
        sd = np.sqrt( np.diag(Var) )
        var = sd**2
        t_est = np.absolute(beta/sd)
        lower_bound = beta-1.96*sd
        upper_bound = beta+1.96*sd
        SCR = sum(list( map( lambda x: x**2 , y - y_est)   ))
        SCT = sum(list( map( lambda x: x**2 , y - np.mean(y_est)   )))
        R2 = 1-SCR/SCT
        rmse = (SCR/n)**0.5
        table = pd.DataFrame( {"ols": beta , "standar_error" : sd , "Lower_bound":lower_bound, "Upper_bound":upper_bound} ) 
        
        fit = {"Root_MSE":rmse, "R2": R2}
        
        index_names7 = listaf
        var_robust_output = pd.DataFrame( Var , index = index_names7 , columns = index_names7 )
        self.var_robust = var_robust_output
        
        
        return table, fit, var_robust_output
        
######################      MÉTODO 4     ###############################################  
    
    def R2_rootMSE( self ) :
        
        ############
        ###  R2  ###
        
        # Se corre la función beta_OLS_Reg que estima el vector de coeficientes
        self.reg_beta_OLS()
        
        y_est    = self.X_np @ self.beta_OLS   # y estimado
        error    = self.y_np - y_est           # vector de errores
        self.SCR = np.sum(np.square(error))    # Suma del Cuadrado de los Residuos
        SCT      = np.sum(np.square(self.y_np - np.mean(self.X_np) ))  # Suma de Cuadrados Total

        self.R2  = 1 - self.SCR/SCT

                
        #################
        ### root MSE  ###
        
        for i in error.values:
            
            suma = 0
            suma = np.sqrt( suma + (i**2) / self.X_np.shape[0] )
            
        self.rootMSE = suma.tolist()
        
        return self.R2, self.rootMSE
    

######################      MÉTODO 5     ###############################################
    
    def output( self ):
        
        self.reg_beta_OLS()
        self.R2_rootMSE()
        self.var_stderrors_cfdinterval()
        
        # var y beta
        beta_OLS = self.beta_OLS.values.reshape( -1, 1 )   # -1 significa cualquier número de filas
        var_OLS  = self.var_OLS.values
        
        # standard errors
        beta_stderror = np.sqrt( np.diag( var_OLS ) )
        
        # confidence interval
        up_bd = beta_OLS.ravel() + 1.96*beta_stderror
        lw_bd = beta_OLS.ravel() - 1.96*beta_stderror
        
        table_data2 = {'Coef.'    : beta_OLS.ravel(),
                       'Std.Err.' : beta_stderror.ravel(),
                       '[0.025'   : lw_bd.ravel(),
                       '0.975]'   : up_bd.ravel(),
                       'R2'       : self.R2,
                       'rootMSE'  : self.rootMSE}
        
        return table_data2
    
######################      Probamos la Class     ########################################

A = OLSRegClass( X, y, lista)

# Atributo de las variables 

A.X
A.y
A.reg_beta_OLS()
A.var_stderrors_cfdinterval()
A.robust_var_se_cfdinterval()
A.R2_rootMSE()
A.output()


