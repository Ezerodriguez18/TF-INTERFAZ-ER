import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as Toolbar
import matplotlib.pyplot as plt

class Canvas_graficatiempo(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(facecolor='gray')
        super().__init__(self.fig)
        self.ax.grid(True)
        self.ax.margins(x=0)
        self.ax.axhline(0, color='black', linewidth=1)  
        self.ax.axvline(0, color='black', linewidth=1)  

    def plot(self,t,x):
        self.ax.clear()
        self.ax.grid(True)
        self.ax.margins(x=0)
        self.ax.axhline(0, color='black', linewidth=1)  
        self.ax.axvline(0, color='black', linewidth=1)
          
        self.ax.plot(t, x)
        self.ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
        self.ax.xaxis.get_offset_text().set_fontsize(10)  # Tamaño del texto "x10^"
        self.ax.set_title("Gráfica en el dominio del tiempo")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Amplitud")
     
        self.draw()



class Canvas_graficafrecuencia(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(facecolor='gray')
        super().__init__(self.fig)
        self.ax.grid(True)
        self.ax.margins(x=0)
        self.ax.axhline(0, color='black', linewidth=1)  
        self.ax.axvline(0, color='black', linewidth=1)  

    #def plot(self,frecuencias,magnitude):
      #  self.ax.clear()
      #  self.ax.grid(True)
      #  self.ax.margins(x=0)
       # self.ax.plot(frecuencias[:len(frecuencias)//2], magnitude[:len(magnitude)//2]) # grafica fft
      #  #self.ax.stem(frecuencias[:len(frecuencias)//2], magnitude[:len(magnitude)//2])#grafica fft
        #self.ax.plot(frecuencias, magnitude) #si lo pongo en modo log al eje y tengo sfdr
      #  self.ax.set_title("Gráfica en el dominio de la frecuencia")
       # self.ax.set_xlabel("Frecuencia (Hz)")
       # self.ax.set_ylabel("Magnitud")

       # self.draw()
    
    def plot(self,frecuencias,magnitude,findice,famp,spurioindice,spurioamp,diezmado,longitud):
        self.ax.clear()
        self.ax.grid(True)
        self.ax.margins(x=0)
        self.ax.axhline(0, color='black', linewidth=1)  
        self.ax.axvline(0, color='black', linewidth=1)  
        self.ax.plot(frecuencias, magnitude) # grafica fft
        self.ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
        self.ax.xaxis.get_offset_text().set_fontsize(10)  # Tamaño del texto "x10^"
        plt.fill_between((0,60000000/2),(spurioamp,spurioamp),(famp,famp), label = 'SFDR',
                     color = "lightblue")  
        #self.ax.stem(frecuencias[:len(frecuencias)//2], magnitude[:len(magnitude)//2])#grafica fft
        #self.ax.plot(frecuencias, magnitude) #si lo pongo en modo log al eje y tengo sfdr
        self.ax.plot(findice, famp, marker="s", label=f'fundamental =  {famp:.2f}')
        self.ax.plot(spurioindice, spurioamp, marker="s",label =f'spurs =  {spurioamp:.2f} ')
        self.ax.legend()
        self.ax.set_title("Gráfica en el dominio de la frecuencia")
        self.ax.set_xlabel("Frecuencia (Hz)")
        self.ax.set_ylabel("Magnitud")

        self.draw()


