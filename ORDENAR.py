#ORDENAR
def ordenar_datos(secuencia,data_in,cantmuestras):
    inicio = 0
    data_ord = [0]*len(secuencia)
    for i in range(0,len(secuencia)): 
        m=1
        x = secuencia [ i ] 
        cycles_count = 0
        while cycles_count < 4:
 #( Operando a 50 MHZ) Si el indice (m) supera el valor 50 quiere decir queal adc le llego un pulso de 1 Mhz que es lo minimo permitido
            if ( m > 50) or ( i + m >= len(secuencia) ):
                if i == 0:
                    data_ord [i] = 0
                else:
                    data_ord [ i ] = data_ord [i -1] 
                break
            if secuencia[i+m]==x:
                cycles_count = cycles_count +1
            if cycles_count == 4:
                data_ord[i]=(data_in[i+m]-127.5)*2*10/255 # inicia mandando la posicion del prng
                if i == 0:
                    inicio = m 
            m = m + 1
    data_ord=data_ord[inicio:(len(data_ord)-15)]#recorto los ultimos valores que se repiten
    
    
    return data_ord,inicio
