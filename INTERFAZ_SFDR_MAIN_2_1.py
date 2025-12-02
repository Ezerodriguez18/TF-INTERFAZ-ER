from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from INTERFAZ_SFDR1_1_3_2 import *
from Graficos import *
from ORDENAR import ordenar_datos
from DIEZMAR import diezmar_muestras
from Separacion import separar
import serial
#import serial.tools.list_ports
from serial.tools import list_ports
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
        self.graficarycalcular.setEnabled(False)
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
        self.graficarycalcular.clicked.connect(self.grafico)
        self.Calcular.clicked.connect(self.calculo)
        
     #Seleccionar PRNG
    def abrirprng(self):
         archivo, _ = (QtWidgets.QFileDialog.getOpenFileName(self, "Abrir archivo","" ))
         nombre_archivo = os.path.basename(archivo)
         if archivo:
            try:
                with open(archivo, 'r') as f: 
                    lectura = f.read()
                    sin_caracteres = ""  # cadena vacía para ir guardando los bits válidos
                    for caracter in lectura:
                        if caracter == '0' or caracter == '1':
                            sin_caracteres += caracter 
                    num2=int(sin_caracteres,2)
                    cant=len(sin_caracteres)//8
                    self.arreglodeprng = num2.to_bytes(cant, byteorder='big')
                    self.label_5.setText(f"Archivo seleccionado: {nombre_archivo}")
                    self.aplicarajustes.setEnabled(True)
                    self.graficarycalcular.setEnabled(False)
                    self.Calcular.setEnabled(False) 
                    self.label_8.setText("")
            except Exception as e:
                self.label_5.setText("Error al seleccionar el archivo")
                self.aplicarajustes.setEnabled(False)
                self.graficarycalcular.setEnabled(False)
                self.Calcular.setEnabled(False) 
                self.label_8.setText("")
    
    #Enviar parametros
    def enviarajustes(self):
        self.cantmuestras=int(self.comboBox_muestras.currentText())
        self.numdiezmado=1
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
            self.label_6.setText("Enviando parametros")
            QApplication.processEvents()  # fuerza el refresco de la GUI
            self.puerto_serie = serial.Serial(self.com,baudrate=115200,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=1,timeout=400)
            self.puerto_serie.write(bytes.fromhex('23 53 44'))# comando que indica que van las muestras
            self.puerto_serie.write(cantidaddemuestras.to_bytes(1, byteorder='big') ) 
            self.puerto_serie.write(bytes.fromhex('01'))
            self.puerto_serie.write(self.arreglodeprng)
            receptor=self.puerto_serie.read(size=1)
            if int.from_bytes(receptor, byteorder='big') == 0x11: # en hexa 11, aviso de que se lleno la memoria SDRAM
                    self.guardararchivo.setEnabled(True)
                    self.label_6.setText("Muestras alamcenadas en la SDRAM")
                    self.pushButton.setEnabled(True)
                    self.aplicarajustes.setEnabled(False)
                    self.graficarycalcular.setEnabled(False)
                    self.Calcular.setEnabled(False) 
            else:
                    self.label_6.setText("Error en la comunicacion, reiniciar placa de adquisicion y enviar de nuevo")
    
        else:
            self.label_6.setText("el archivo seleccionado no coincide\n con la cantidad de muestras elegidas")

       # Guardado de archivo   
    def guardartimer(self):
        self.label_8.setText("Recibiendo muestras") 
        QApplication.processEvents()  # fuerza el refresco de la GUI
        self.puerto_serie.write(bytes.fromhex('57 18 20'))#Enviar comando para tomar muestras
        doblecantidaddemuestras=self.cantmuestras*2
        lectura=[0]* doblecantidaddemuestras
        for i in range(0, doblecantidaddemuestras):
            lectura[i]=int.from_bytes(self.puerto_serie.read(size=1),byteorder='little')
        self.puerto_serie.close()
        self.pushButton.setStyleSheet(" border-radius: 10px; \n"
                    "background-color: rgb(0, 85, 0);\n"
                    "  border: none;")
        data_in,secuencia=separar(self.cantmuestras,lectura)
        dataord,self.inicio=ordenar_datos(secuencia,data_in,self.cantmuestras)
        self.valoresdemuestras=dataord
        self.label_8.setText("")
        with open('secuencia.txt', 'w') as archivo:
           archivo.write(' '.join(map(str, secuencia)))

        print(os.getcwd())
        archivo2, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Text Files (*.txt);;All Files (*)")
        if archivo2:
            try:
                with open(archivo2, 'w') as f:
                    for i in range(len(self.valoresdemuestras)):
                        f.write(str(self.valoresdemuestras[i]) + " ")
                    self.label_8.setText(f"Archivo guardado en:\n  {archivo2}") 
            except Exception as e:
                self.label_8.setText("Error al guardar el archivo") 
        self.graficarycalcular.setEnabled(True)
        self.Calcular.setEnabled(True)
        self.guardararchivo.setEnabled(False)   
        self.label_6.setText("")
        self.aplicarajustes.setEnabled(True)
        
   
   #grafico y calculo
    def grafico(self):
       # self.valoresdemuestras = np.loadtxt("muestras16384.txt")
        TS=1/(60*1e6)
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
        #Calculo sfdr por densidad espectral para obtener los indices de power spectrum
       # self.valoresdemuestras = np.loadtxt("16k_2.txt")
        signal_no_dc = utils._remove_dc_component(self.valoresdemuestras)
        f, pxx = utils.periodogram(signal_no_dc, 60*1e6//(1), window=('kaiser', 38), method="welch", scaling="density")
        

        origPxx = np.copy(pxx)

        # Remove DC component
        pxx[0] = 2 * pxx[0]
        iHarm, iLeft, iRight = utils._get_tone_indices_from_psd(pxx, f, 0)
        pxx[0:iRight+1] = 0
        # Remove COMPONENT
        mask = f < 50000  
        pxx[mask] = 0  
        # Largest Frequency
        fh_idx = np.argmax(pxx)
        first_harmonic = f[fh_idx]
        iHarm, iLeft, iRight = utils._get_tone_indices_from_psd(pxx, f, first_harmonic)
        signal_pxx = np.copy(pxx[iLeft:iRight + 1])
        signal_f = np.copy(f[iLeft:iRight + 1])
        pxx[iLeft:iRight + 1] = 0.0

        # Remove MSD if greater than 0
        pxx[np.abs(f-first_harmonic) < 0] = 0.0

        # Identify Spurious Bin
        spur_idx = np.argmax(pxx)
        spur_freq = f[spur_idx]
        iHarm, iLeft, iRight =utils._get_tone_indices_from_psd(pxx, f, spur_freq)
        spur_pxx = np.copy(pxx[iLeft:iRight + 1])
        spur_f = np.copy(f[iLeft:iRight + 1])

        #signal_power = utils.bandpower(signal_pxx, signal_f)
        #spur_power = utils.bandpower(spur_pxx, spur_f)
        #sfdr_value=utils.mag2db(signal_power/spur_power)

        # para grafico a partir de power spectrum
        f, pxx =utils.periodogram(self.valoresdemuestras, (60e6)//(self.numdiezmado), window=('kaiser', 38),method="welch", scaling="spectrum")
        Magnitude=10*np.log10(pxx)

        spurioamp=Magnitude[spur_idx] 
        fundamental_power_dB = Magnitude[ fh_idx]
        sfdr_value=fundamental_power_dB-spurioamp
        
        self.graficafrecuencia.plot(f,Magnitude,first_harmonic,fundamental_power_dB,spur_freq,spurioamp,1,len(self.valoresdemuestras),sfdr_value)
        sfdrenveces=10**(sfdr_value/20)
        self.label_9.setText(f"SFDR={sfdrenveces} veces\n SFDR(dB)={sfdr_value} dB")

        
    #encuentra dispositivo
    def listar_puertos(self):
            puertos = serial.tools.list_ports.comports()
            if not puertos:
                    self.label_10.setText("El dispositivo no esta conectado")
                    self.aplicarajustes.setEnabled(False)
                    self.guardararchivo.setEnabled(False)
                    self.graficarycalcular.setEnabled(False)
                    self.Calcular.setEnabled(False) 
                    self.pushButton.setEnabled(False)
            else:
                 for info in puertos:
                    if info.description.startswith('USB Serial Port'):
                        self.label_10.setText("Se conecto el dispositivo")
                        self.com=info.device
                    else:
                        self.label_10.setText("El dispositivo conectado no es la FPGA")
                        self.aplicarajustes.setEnabled(False)
                        self.guardararchivo.setEnabled(False)
                        self.graficarycalcular.setEnabled(False)
                        self.Calcular.setEnabled(False) 
                        self.pushButton.setEnabled(False)
            return


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
