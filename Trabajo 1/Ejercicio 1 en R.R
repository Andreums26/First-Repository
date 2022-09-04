y <- runif(20,0,500)

for (i in y) {
if (i <0 & i <= 100) {
  next
    i <-  i^(1/2)
    
} else if (i > 100 & i <= 300) {
    i <- i - 5
  
} else {
      i <- 50
}
  y = i
}

print (y)



