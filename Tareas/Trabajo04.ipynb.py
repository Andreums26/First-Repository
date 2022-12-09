#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 19:28:01 2022

@author: henryandreumarquezsalinas
"""

# Issue4 #

# importamos librerías necesarias
import pandas as pd
import numpy as np
import pyreadr
import os 
import scipy.stats as stats
from scipy.stats import t # t - student 

lista = ['female', 'widowed', 'divorced', 'separated', 'nevermarried']

# Creamos la clase

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
        new_cols_orders = [cols[ -1 ]] + cols[ 0:-7 ] # juntamos listas

            
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

    
###############################################################################

# leemos las base de datos sin cambiar nombre de usuario

user = os.getlogin()   # Username
os.chdir(f"/Users/henryandreumarquezsalinas/Documents")  # Set directorio
cps2012_env = pd.read_excel("Libro2.xlsx") # output formato diccionario  
cps2012_env

ln = cps2012_env.lnw.values
fe = cps2012_env.female.values
wi = cps2012_env.widowed.values
div = cps2012_env.divorced.values
exp1 = cps2012_env.exp1.values
exp2 = cps2012_env.exp2.values
exp3 = cps2012_env.exp3.values
exp4 = cps2012_env.exp4.values
wei = cps2012_env.weight.values

dt = cps2012_env.describe()

    
# Borrar variables constantes: filtra observaciones que tenga varianza diferente a cero 
variance_cols = cps2012_env.var().to_numpy() # to numpy
dataset = cps2012_env.iloc[ :, np.where( variance_cols != 0  )[0] ]     # filtra observaciones que tenga varianza diferente a cero

# genero un dataset con 10 columnas del dataset general
X = dataset.iloc[:, 1:]
y = dataset[['lnw']].squeeze()   # convirtiendo a serie

A = OLSRegClass( X, y, lista)
A.X
A.y
A.reg_beta_OLS()
A.var_stderrors_cfdinterval()
A.robust_var_se_cfdinterval()
A.R2_rootMSE()
A.output()

##########################
# Probando nuestra Class #
##########################

# asignando clase, ya sea por nombre o posición de variables
reg1 = OLSRegClass (X, y, ['female', 'widowed', 'divorced', 'separated', 'nevermarried'])
reg1 = OLSRegClass (X, y, range(0,5))

# Ejecutando Método 1
reg1.beta_OLS_Reg()
beta_OLSs = reg1.beta_OLS

# Ejecutando Método 2
reg1.var_stderrors_cfdinterval()
reg1.var_OLS
reg1.beta_se
reg1.confiden_interval

# Ejecutando Método 3

reg1.robust_var_se_cfdinterval()
reg1.robust_var

# Ejecutando Método 4

reg1.R2_rootMSE()
reg1.R2
reg1.rootMSE    

# Ejecutando Método 5

reg1.output()


# matriz propuesta de White en muestras grandes
V = np.zeros((X.shape[0], X.shape[0]))

y_est    = X @ beta_OLSs                           # y estimado
error    = y - y_est                                   # vector de errores

residuosalcuadrado = []

for i in error.values:
    
    A = i**2
    residuosalcuadrado.append(A)

V = np.fill_diagonal(V, np.diag(residuosalcuadrado))       
        
        
        
        
        
        
        
        
        
        
        
        
        