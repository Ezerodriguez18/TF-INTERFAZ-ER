#Diezmar
def diezmar_muestras(dataord,inicio,numdiezmado):
    longitud=len(dataord)
    diezmado=numdiezmado
    l=0
    datosreales = [0] * ((longitud-inicio+1)//diezmado+1)
    
    for i in range(inicio+1,longitud,diezmado):
        datosreales[l]=dataord[i]
        l=l+1
    longdatosreales=len(datosreales)
   
    return datosreales,longdatosreales