from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QTimer
from INTERFAZ_SFDR1_1_3 import *
from Graficos import *
from ORDENAR import ordenar_datos
from DIEZMAR import diezmar_muestras
from Separacion import separar
import serial
import serial.tools.list_ports
import os
import numpy as np
from pysnr import utils

class MainWindow (QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setWindowState(QtCore.Qt.WindowMaximized) 
        self.setMinimumSize(400, 300)  
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Intervalo en milisegundos (1000 ms = 1 segundos)
        self.timer.timeout.connect(self.listar_puertos)  # Conectar la señal timeout al método de escaneo
        self.timer.start()
        self.com=None 

        #ajuste de variables y pushbuttons
        self.inicio=None   
        self.frecuencias=None
        self.Magnitude=None 

        self.guardararchivo.setEnabled(False)
        self.graficar.setEnabled(False)
        self.Calcular.setEnabled(False) 
        self.pushButton.setEnabled(False)
        self.aplicarajustes.setEnabled(False)


        self.arreglodeprng=None
        self.valoresdemuestras=None
        # Creacion de clases para las graficas
        self.graficatiempo = Canvas_graficatiempo(self)
        self.toolbar_tiempo = Toolbar(self.graficatiempo, self)
        
        self.graficafrecuencia = Canvas_graficafrecuencia(self)
        self.toolbar_frecuencia = Toolbar(self.graficafrecuencia, self)

        # Agregar Canvas y Toolbar al layout
        self.verticalLayout.addWidget(self.toolbar_tiempo)
        self.verticalLayout.addWidget(self.graficatiempo)
        
        self.verticalLayout_2.addWidget(self.toolbar_frecuencia)
        self.verticalLayout_2.addWidget(self.graficafrecuencia)

        
        #defino las funciones para cada pushbutton
        self.seleccionarprng.clicked.connect(self.abrirprng)
        self.aplicarajustes.clicked.connect(self.enviarajustes)
        self.guardararchivo.clicked.connect(self.guardartimer)
        self.graficar.clicked.connect(self.grafico)
        self.Calcular.clicked.connect(self.calculo)
        
     #Seleccionar PRNG
    def abrirprng(self):
         archivo, _ = (QtWidgets.QFileDialog.getOpenFileName(self, "Abrir archivo","" ))
         nombre_archivo = os.path.basename(archivo)
         if archivo:
            try:
                with open(archivo, 'r') as f: 
                    lectura = f.read()
                    sinespacios=lectura.replace(" ","")#elimina el espacioas
                    num2=int(sinespacios,2)
                    cant=len(sinespacios)//8
                    self.arreglodeprng = num2.to_bytes(cant, byteorder='big')
                    self.label_5.setText(f"Archivo seleccionado: {nombre_archivo}")
                    self.aplicarajustes.setEnabled(True)
            except Exception as e:
                self.label_5.setText("Error al seleccionar el archivo")
    
    #Enviar parametros
    def enviarajustes(self):
        self.cantmuestras=int(self.comboBox_muestras.currentText())
        self.numdiezmado=int((self.comboBox_frecuencia.currentText()))
        self.label_6.setText("Preparando ajustes")
        if self.cantmuestras==1024:
               cantidaddemuestras=1
        
        elif  self.cantmuestras==16384:
               cantidaddemuestras=2
        
        elif self.cantmuestras==65536:
               cantidaddemuestras=3
        
        elif self.cantmuestras==262144:
               cantidaddemuestras=4
        elif self.cantmuestras==524288:
               cantidaddemuestras=5
        if (len(self.arreglodeprng*8)==self.cantmuestras):
            
            self.puerto_serie = serial.Serial(self.com,baudrate=115200,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=1,timeout=400)# preguntar self.com
            self.puerto_serie.write(bytes.fromhex('23 53 44'))# comando que indica que van las muestras
            self.puerto_serie.write(cantidaddemuestras.to_bytes(1, byteorder='big') ) 
            self.puerto_serie.write(bytes.fromhex('01'))
            self.puerto_serie.write(self.arreglodeprng)
            self.label_6.setText("Parametros enviados")
            receptor=self.puerto_serie.read(size=1)
            if int.from_bytes(receptor, byteorder='big') == 0x11: # en hexa 11, aviso de que se lleno la memoria SDRAM
                self.guardararchivo.setEnabled(True)
                self.label_6.setText("Muestras tomadas en la memoria")
                self.pushButton.setEnabled(True)
                self.aplicarajustes.setEnabled(False)
        else:
                self.label_6.setText("el archivo seleccionado no coincide\n con la cantidad de muestras elegidas")

       # Guardado de archivo   
    def guardartimer(self):
        self.puerto_serie.write(bytes.fromhex('57 18 20'))#Enviar comando para tomar muestras
        doblecantidaddemuestras=self.cantmuestras*2
        lectura=[0]* doblecantidaddemuestras
        for i in range(0, doblecantidaddemuestras):
            lectura[i]=int.from_bytes(self.puerto_serie.read(size=1),byteorder='little')
        self.puerto_serie.close()
        data_in,secuencia=separar(self.cantmuestras,lectura)
        dataord,self.inicio=ordenar_datos(secuencia,data_in,self.cantmuestras)
        datosreales,long=diezmar_muestras(dataord,self.inicio,self.numdiezmado)
        self.valoresdemuestras=datosreales
        with open('datosoriginales2711.txt', 'w') as archivo:
           archivo.write(' '.join(map(str, secuencia)))

        print(os.getcwd())
        archivo2, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Text Files (*.txt);;All Files (*)")
        if archivo2:
             with open(archivo2, 'w') as f:
                for i in range(len(self.valoresdemuestras)):
                   f.write(str(self.valoresdemuestras[i]) + " ")
                self.label_8.setText(f"Archivo guardado en:\n  {archivo2}")
                self.graficar.setEnabled(True)
                self.Calcular.setEnabled(True)
                self.guardararchivo.setEnabled(False)
                self.pushButton.setStyleSheet(" border-radius: 10px; \n"
                    "background-color: rgb(0, 85, 0);\n"
                    "  border: none;")        
        self.label_6.setText("")
        self.aplicarajustes.setEnabled(True)
        
   
   #grafico y calculo
    def grafico(self):
        TS=1/(60*1e6//(self.numdiezmado))
        t = np.linspace(0,TS*(len(self.valoresdemuestras)-1) , num=len(self.valoresdemuestras))  # inicio, final, cantidad de muestras en ese tiempo.
        x=self.valoresdemuestras
        self.graficatiempo.plot(t,x)
        self.guardararchivo.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton.setStyleSheet(" border-radius: 10px; \n"
"background-color: rgb(255, 0, 0);\n"
"  border: none;")

    #Calculo sfdr
    def calculo(self):
        #Calculo sfdr por potencia espectral utilizando parte de del codigo pysnr
        signal_no_dc = utils._remove_dc_component(self.valoresdemuestras)
        f, pxx = utils.periodogram(signal_no_dc, 60*1e6//(self.numdiezmado), window=('kaiser', 38), method="welch", scaling="espectrum")
        originpxx=pxx
        Magnitude=10*np.log10(originpxx)
        # Elimino continua y componente menores a 50 Khz
        mask = f < 50000  
        pxx[mask] = 0  
        #Identifico bin principal y lo elimino del vector
        fund_idx = np.argmax(pxx)
        fund_freq = f[fund_idx]
        fund_pow = pxx[fund_idx]
        leftBinFund, rightBinFund = utils.get_peak_border(pxx, f, fund_freq, fund_idx, 0)
        pxx[leftBinFund: rightBinFund+1] = 0.0
        # Identifico bin espurio y su potencia
        spur_idx = np.argmax(pxx)
        spur_pow = pxx[spur_idx]
        spur_freq = f[spur_idx]
        spurioamp=10*np.log10(spur_pow)
        fundamental_power_dB = 10*np.log10(fund_pow)
        sfdr_value=fundamental_power_dB-spurioamp
        
        self.graficafrecuencia.plot(f,Magnitude, fund_freq,fundamental_power_dB,spur_freq,spurioamp,self.numdiezmado,len(self.valoresdemuestras))
        
        sfdrenveces=10**(sfdr_value/20)
        self.label_9.setText(f"SFDR={sfdrenveces} veces\n SFDR(dB)={sfdr_value} dB")
        self.graficar.setEnabled(False)
        self.Calcular.setEnable(False)
        
    #encuentra dispositivo
    def listar_puertos(self):
            puertos = serial.tools.list_ports.comports()
            if not puertos:
                    self.label_10.setText("El dispositivo no esta conectado")
                    self.aplicarajustes.setEnabled(False)
            else:
                 for info in puertos:
                    if info.description.startswith('USB Serial Port'):
                        self.label_10.setText("Se conecto el dispositivo")
                        self.com=info.device
            return


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()