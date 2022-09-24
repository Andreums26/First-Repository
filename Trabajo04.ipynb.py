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


# Creamos clase

class RegOLSClass( object ):   # también podemos omitir object, pues es lo mismo
    
    def __init__( self,  X:pd.DataFrame,  y:pd.Series, lista, intercept, RobustStandardError=True ):    # X:pd.DataFrame  indica que debe ser un dataframe
                                                                                                # y:pd.Series  indica que debe ser una serie
        ## CONDICIONAL PARA X:pd.DataFrame ###
        if not isinstance( X, pd.DataFrame ):                  # si X no es dataframe, arroja error
            raise TypeError( "X must be a pd.DataFrame." )
        
        ## CONDICIONAL PARA y:pd.Series    ###
        if not isinstance( y, pd.Series ):                     # si y no es series, arroja error
            raise TypeError( "y must be a pd.Series." )
        
        # ## CONDICIONAL PARA y:pd.Series    ###
        if not isinstance( lista, pd.Series ):                 # si lista no es series, arroja error
            raise TypeError( "lista must be a pd.Series." )
        
        
        self.X = X
        self.y = y
        self.RobustStandardError = RobustStandardError
        self.intercept = intercept
        
        if self.intercept:
            
            # incluyendo columna de unos para el intercepto
            self.X[ 'Intercept' ] = 1   # crea columna Intercept con valores 1 al final del array    
            
            # queremos que la columna Intercept aparezca en la primera columna 
            cols = self.X.columns.tolist()    # convierte el nombre de las columnas a lista
            new_cols_orders = [cols[ -1 ]] + cols[ 0:-1 ]   # mueve la última columna (que sería Intercept) al inicio
                                                    # la manera de hacerlo es ordenando primero cols[-1] y luego cols[0:-1]
                    
            self.X = self.X.loc[ :, new_cols_orders ]   # usamos .loc que filtra por nombre de filas o columnas 

        else:
            pass

        # creando nuevos atributos 
        self.X_np = self.X.values              # pasamos dataframe a multi array
        self.y_np = y.values.reshape( -1 , 1 ) # de objeto serie a array columna 
        self.columns = self.X.columns.tolist() # nombre de la base de datos como objeto lista
        

##################  CREANDO MÉTODOS  ##########################################

##################     MÉTODO 1     ###########################################

    def beta_OLS_Reg( self ):
        # X, y en Matrix, y vector columna respectivamente 
    
        X_np = self.X_np
        y_np = self.y_np
    
        # beta_ols
        beta_ols = np.linalg.inv( X_np.T @ X_np ) @ ( X_np.T @ y_np )
    
    
        # asignando output de la función   def beta_OLS( self ):   como atributo  self.beta_OLS
        # columnas de X
        index_names = self.columns
        # Output
        beta_OLS_output = pd.DataFrame( beta_ols, index = index_names, columns = [ 'Coef.' ] )
        # Dataframe de coeficientes como atributo
        self.beta_OLS = beta_OLS_output
    
        return beta_OLS_output
    
##################     MÉTODO 2     ###########################################

    def var_stderrors_cfdinterval( self ):
    
        #################
        ### VARIANZA  ###
    
        # Se corre la función beta_OLS que estima el vector de coeficientes
        self.beta_OLS_Reg()
    
        # usaré atributos pero con un nombre más simple
        X_np = self.X_np
        y_np = self.y_np
    
        # beta_ols
        beta_OLS = self.beta_OLS.values.reshape( - 1, 1 ) # Dataframe a vector columna 

        # errores
        e = y_np - ( X_np @ beta_OLS )

        # Varianza de los errores
        N = X_np.shape[ 0 ]
        total_parameters = X_np.shape[ 1 ]
        error_var = ( (e.T @ e)[ 0 ] )/( N - total_parameters )

        # Varianza
        var_OLS =  error_var * np.linalg.inv( X_np.T @ X_np )

    
        # asignando output de la función   def reg_var_OLS( self ):   como atributo  self.var_OLS
        index_names = self.columns
        var_OLS_output = pd.DataFrame( var_OLS , index = index_names , columns = index_names )
        self.var_OLS = var_OLS_output

    
        #######################
        ### ERRORES ESTÁNDAR  ###
   
        # var y beta
        beta_OLS = self.beta_OLS.values.reshape( -1, 1 )   # -1 significa cualquier número de filas
        var_OLS  = self.var_OLS.values
    
        # standard errors
        beta_stderror = np.sqrt( np.diag( var_OLS ) )
    
        # test estadístico para cada coeficiente
        table_data0 = {  "Std.Err." : beta_stderror.ravel()}
    
        # defining index names
        index_names0 = self.columns
    
        # defining a pandas dataframe 
        self.beta_se = pd.DataFrame( table_data0 , index = index_names0 )
    
    
        ###########################
        ### Intervalos de confianza (5%) ###
    
        up_bd = beta_OLS.ravel() + 1.96*beta_stderror
        lw_bd = beta_OLS.ravel() - 1.96*beta_stderror
    
        table_data1 = {"[0.025"   : lw_bd.ravel(),
                   "0.975]"   : up_bd.ravel()}
    
        # defining index names
        index_names1 = self.columns
    
        # defining a pandas dataframe 
        var_stderrors_cfdinterval = pd.DataFrame( table_data1 , index = index_names1 )
    
        return var_stderrors_cfdinterval
    
##################     MÉTODO 3     ###########################################
     

    def robust_var_se_cfdinterval(self):
     
        # Se corre la función beta_OLS que estima el vector de coeficientes
        self.beta_OLS_Reg()
         
        # usaré atributos pero con un nombre más simple
        X_np = self.X_np
        y_np = self.y_np

        ####################
        ###  robust var  ###
     
        # matriz propuesta de White en muestras grandes
        V = np.zeros((X_np.shape[0], X_np.shape[0]))
     
        y_est  = X_np @ self.beta_OLS                           # y estimado
        error  = y_np - y_est                                   # vector de errores
     
        residuosalcuadrado = []
     
        for i in error.values:
         
         A = i**2
         residuosalcuadrado.append(A)
     
        V = np.fill_diagonal(V, np.diag(residuosalcuadrado))
     
        self.robust_var = np.linalg.inv( X_np.T @ X_np ) @ ( X_np.T) @ V @ X_np @ np.linalg.inv( X_np.T @ X_np )
           
 ###############      MÉTODO 4     ############################################
    
    def R2_rootMSE( self ) :
        
        ############
        ###  R2  ###
        
        # Se corre la función beta_OLS_Reg que estima el vector de coeficientes
        self.beta_OLS_Reg()
        
        y_est    = self.X_np @ self.beta_OLS                           # y estimado
        error    = self.y_np - y_est                                   # vector de errores
        self.SCR = np.sum(np.square(error))                         # Suma del Cuadrado de los Residuos
        SCT      = np.sum(np.square(self.y_np - np.mean(self.X_np) ))   # Suma de Cuadrados Total

        self.R2  = 1 - self.SCR/SCT

                
        #################
        ### root MSE  ###
        
        for i in error.values:
            
            suma = 0
            suma = np.sqrt( suma + (i**2) / self.X_np.shape[0] )
            
        self.rootMSE = suma.tolist()
        
    
 ###############      MÉTODO 5     ############################################
    
    def output( self ):
        
        self.beta_OLS_Reg()
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

pip install pyreadr
import pyreadr


user = os.getlogin()   # Username
os.chdir(f"/Users/henryandreumarquezsalinas/Documents/GitHub/First-Repository")  # Set directorio
cps2012_env = pyreadr.read_r(".../data/cps2012.RData")    # output formato diccionario
cps2012 = cps2012_env[ 'data' ]    # extrae iformación almacenada en la llave data del diccionario cps2012_env
dt = cps2012.describe()
    
# Borrar variables constantes: filtra observaciones que tenga varianza diferente a cero 
variance_cols = cps2012.var().to_numpy() # to numpy
dataset = cps2012.iloc[ :, np.where( variance_cols != 0  )[0] ]     # filtra observaciones que tenga varianza diferente a cero

# genero un dataset con 10 columnas del dataset general
X = dataset.iloc[:, 1:]
y = dataset[['lnw']].squeeze()   # convirtiendo a serie


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





# solo faltaría metodo 3           
        
        
        
        
        
        
        
        
        
        
        
        
        
        