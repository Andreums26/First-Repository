##Usamos libería para poder subir archivos excel
library(readxl) 
##Adaptamos el directorio
user <- Sys.getenv("USERNAME")  # username
print(user)
setwd( paste0("C:/Users/",user,"/Documents/GitHub/1ECO35_2022_2/Lab3") ) # set directorio
junin_data <- read_excel("../data/Region_Junin.xlsx")
##reemplazamos vacíos por missing
junin_data <- read_excel("../data/Region_Junin.xlsx", na="")

# Filas y columnas
dim(junin_data) 

# Clase de estructura de objeto

class(junin_data)

##para convertir cada columna como objeto
attach(junin_data)

# InformaciÃ³n de cada variable

str(junin_data)

# 

lapply(junin_data, class) # lapply(x, FUN):: list()

str(lapply)

sapply(junin_data, class) # sapply(x, FUN):: vector, Datrame, 

summary(junin_data) # 

### ***Exploring a DataFrame***:

class( junin_data["Place"] ) # Dataframe
junin_data["Place"]

class( junin_data[Place,] )

class( junin_data$Place ) # lista o vector

#-----------------------------------------------------------------------

## revisando missing values

" En R, tenemos dos formas de missing, en general, NA y Null "
unique(Place) 

any( is.na(junin_data["Place"]) ) # Salió TRUE: por lo menos hay un missing value

any(is.na(junin_data["total_write"])) #TRUE

any(is.na(junin_data$Region)) #False: no hay ningún missing value en region

any(is.na(women_read))  #  al menos una observación  es Missing

any(is.na(total_read)) #False

any(is.na(whites)) #TRUE

any(is.na(natives)) #True

## cantidad de missing 

sum(is.na(Place)) #Hay 11 missings

## Manipulando missing values
install.packages("tidyr")
library(tidyr)
junin_data %>% drop_na() 

junin_data2 <- junin_data %>% drop_na()  # borras todas las filas con missig values

junin_data2 <- junin_data %>% drop_na(Place)

# borras observaciones con missing values de la columna Place

junin_data2 <- junin_data %>% replace_na(list(Place = "Place1"))

"En R debe asignarse el objeto alterado a uno nuevo. En este caso a Netflix2"
#----------------------------------------------------------------------------

#Cambiamos los nombres de las variables
names(junin_data) #verificamos cuales son los nombres de las variables

junin_data <- rename(junin_data, c("comunidad"="Place", "homxlee" = "men_not_read", "mujerxlee" = "women_not_read", "totalxlee" = "total_not_read" ))
                     
names(junin_data) #verificamos el cambio de nombre de la variables
