#Separacion 
def separar(cantmuestras, lectura):
    contador = 0#el valor de adc que tengo corresponde a la muestra siguiente
    posic = 0
    data_in = [0]*cantmuestras
    secuencia = [0]*cantmuestras 
    #Ciclo para ir realizando la grafica paso a paso
    while (contador < len(lectura)) and (posic<cantmuestras):
        data_in [ posic ] = lectura [ contador+1] 
        #data_in [ posic ] = (lectura [ contador+1] -127.5)*2*10/255
        secuencia [ posic ] = lectura [ contador] 
        contador = contador +2
        posic = posic +1
    return data_in,secuencia