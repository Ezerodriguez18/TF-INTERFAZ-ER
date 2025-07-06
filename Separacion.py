#Separacion 
def separar(cantmuestras, lectura):
    contador = 0#el valor de adc que tengo corresponde a la muestra siguiente
    posic = 0
    data_in = [0]*cantmuestras
    secuencia = [0]*cantmuestras 
    while (contador < len(lectura)) and (posic<cantmuestras):
        data_in [ posic ] = lectura [ contador+1] 
        secuencia [ posic ] = lectura [ contador] 
        contador = contador +2
        posic = posic +1
    return data_in,secuencia