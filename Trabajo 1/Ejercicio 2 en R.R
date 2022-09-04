## Para la matriz

sample <- runif(5000,0,500)

M <- matrix(sample, 100, 50) 

if(! is.matrix(M)) stop("M must be a matrix")

calculator <- function (M,h,z) {
  h <- apply(M, 2, min)
  z <- apply(M, 2, max)

  result = (M - h) / (z - h)
  return(result)
}

calculator(M, h, z) [1]


# Para el vector

y <- runif(100,0,500)

if(! is.vector(y)) stop("y must be a vector")

calculator1 <- function (y,k,l) {
  k <- apply(y, 1, min)
  l <- apply(y, 1, max)
  
  result = (y - k) / (l - k)
  return(result)
}

calculator1(y, k, l) [1]
