# Instalar paquetes

install.packages("dplyr")
install.packages("readr")
install.packages("tidyr")

# Usamos libería para poder subir archivos excel

library(dplyr)
library(tidyr)
library(readxl)

# Adaptamos el directorio

user <- Sys.getenv("USERNAME")  # username
print(user)
setwd( paste0("/Users/", user, "/Documents/GitHub/First-Repository") ) # set directorio
junin_data <- read_excel("/Users/", user, "/Documents/GitHub/First-Repository/Region_Junin.xlsx")

# reemplazamos vacíos por missing
junin_data <- read_excel("/Users/", user,"/Documents/GitHub/First-Repository/Region_Junin.xlsx", na="")

# Filas y columnas
dim(junin_data)

# Clase de estructura de objeto

class(junin_data)

# Para convertir cada columna como objeto
attach(junin_data)

# -------------------------------------------------------

# 1. Información de cada variable

str(junin_data)

# 

lapply(junin_data, class) # lapply(x, FUN):: list()

str(lapply)

sapply(junin_data, class) # sapply(x, FUN):: vector, Datrame, 

summary(junin_data) # 

### 2. ***Exploring a DataFrame***:

class( junin_data["Place"] ) # Dataframe
junin_data["Place"]

class( junin_data[Place,] )

class( junin_data$Place ) # lista o vector

#-----------------------------------------------------------------------

## 3. Revisando missing values

" En R, tenemos dos formas de missing, en general, NA y Null "
unique(Place) 

any( is.na(junin_data["Place"]) ) # Sali? TRUE: por lo menos hay un missing value

any(is.na(junin_data["total_write"])) #TRUE

any(is.na(junin_data$Region)) #False: no hay ning?n missing value en region

any(is.na(women_read))  #  al menos una observaci?n  es Missing

any(is.na(total_read)) #False

any(is.na(whites)) #TRUE

any(is.na(natives)) #True

## cantidad de missing 

sum(is.na(Place)) #Hay 11 missings

## Manipulando missing values

junin_data %>% drop_na() 

junin_data2 <- junin_data %>% drop_na()  # borras todas las filas con missig values

junin_data2 <- junin_data %>% drop_na(Place)

# borras observaciones con missing values de la columna Place

junin_data2 <- junin_data %>% replace_na(list(Place = "Place1"))

"En R debe asignarse el objeto alterado a uno nuevo. En este caso a junin_data2"

#----------------------------------------------------------------------------

# 4. Cambiamos los nombres de las variables

install.packages("reshape")

names(junin_data) #verificamos cuales son los nombres de las variables

require(reshape)
junin_data <- rename(junin_data, c(Place = "Comunidad", men_not_read = "homxlee", women_not_read = "mujerxlee", total_not_read = "totalxlee" ))
                     
names(junin_data) #verificamos el cambio de nombre de la variables

#----------------------------------------------------------------------------

# 5. Valores únicos de las siguientes variables ( comunidad , District)

junin_data2 <- junin_data[,c('Comunidad','District')] # seleccionar variables

unique(junin_data2) #mostrar valores únicos de ambas variables

# Ahora por variable
# Para Comunidad

junin_data2 <- junin_data[,c('Comunidad')] # seleccionar variable

unique(junin_data2) #mostrar valores únicos

# Para District

junin_data2 <- junin_data[,c('District')] # seleccionar variable

unique(junin_data2) #mostrar valores únicos


#----------------------------------------------------------------------------

# 6. Crear columnas con la siguiente información

mujer_noescribenilee <- junin_data$mujerxlee/ junin_data$totalxlee
hombre_noescribenilee <- junin_data$homxlee/ junin_data$totalxlee
nativos_total <- junin_data$natives/(peruvian_men + peruvian_women + foreign_men + foreign_women)

junin_data <- cbind(junin_data[, c(1, 3)],mujer_noescribenilee, hombre_noescribenilee, nativos_total)

#----------------------------------------------------------------------------

# 7. Nueva base de datos