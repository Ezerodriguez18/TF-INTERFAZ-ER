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
        self.ax.set_xlim(0, t[-1]) 
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
    
    def plot(self,frecuencias,magnitude,findice,famp,spurioindice,spurioamp,diezmado,longitud):
        self.ax.clear()
        self.ax.grid(True)
        self.ax.margins(x=0)
        self.ax.set_xlim(0, 60e6/(diezmado*2))
        self.ax.axhline(0, color='black', linewidth=1)  
        self.ax.axvline(0, color='black', linewidth=1)  
        self.ax.plot(frecuencias, magnitude) # grafica fft
        self.ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
        self.ax.xaxis.get_offset_text().set_fontsize(10)  # Tamaño del texto "x10^"
        plt.fill_between((0,60000000/(diezmado*2)),(spurioamp,spurioamp),(famp,famp), label = 'SFDR',
                     color = "lightblue")  
        self.ax.plot(findice, famp, marker="s", label=f'fundamental =  {famp:.2f}')
        self.ax.plot(spurioindice, spurioamp, marker="s",label =f'spurs =  {spurioamp:.2f} ')
        self.ax.legend()
        self.ax.set_title("Gráfica en el dominio de la frecuencia")
        self.ax.set_xlabel("Frecuencia (Hz)")
        self.ax.set_ylabel("Magnitud")

        self.draw()


