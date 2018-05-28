import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import time
import datetime
import calendar
#---------------- my modules  -----------------
import ionodat
import ionomap


def main():

    '''
        Version de prueba: reduccion del programa principal del Ionos Poroject.
        Realiza mapas de la variabilidad media del parametro elegido de capa ionoferica F2, calculado con
    el LPIM (La Plata Ionospheric Model). Para un total de 3 meses de datos del anno 2011.
        Parametro elegido es la densidad electronica maxima de la capa ionosferica F2 ('NmF2').
    Se grafica la variabilidad respecto al Tiempo Local y la latitud geomagnetica.
    '''

# Ubicacion de archivos de entrada (LPIM-database) y salida del main

    source = 'LPIMdata/'
    # Aqui guarda las figuras:
    savepath = 'Image'

# Obtengo el paquete de datos a plotear segun el parametro deseado.

    file_type = 'prm' # tipo de archivo salida del LPIM
    var_name = 'NmF2' # nombre de variable ionosferica deseada
    # Creo una instancia de Clase Ionodat
    dato = ionodat.Ionodat(source, file_type, var_name)
    # Intervalo de tiempo que se desea graficar
    fecha_inicial = datetime.datetime(2011, 1, 1)
    fecha_final = datetime.datetime(2011, 3, 31)
    # Consigo datos en un intervalo de tiempo solicitado, segun disponibilidad en LPIM database.
    doy, LT, modip, NmF2c0, NmF2cc = dato.get(fecha_inicial, fecha_final)

#-----------------------------------------------------
#Creo ionomapas de Nmfc0 - LPIM en modo autonomo (CCIR).
    x = LT
    y = modip
    param = NmF2c0
    ptext=[ var_name+'c0', '2011', 'LT [hours]', 'Modip [degrees] ', '10e10 m(-3)']
    i = 0
    # Creo una instancia de Clase Ionomap
    mapa = ionomap.Ionomap(x, y, param, ptext, fignumber=i, savepath=savepath)

    # Ploteo DATOS crudos.
    metodo = 'verdata'
    mapa.make(metodo=metodo, subplot=121)

    # Suavizo data original, promediando por bin (uso binsize por default).
    X, Y, Z_binned = mapa.bindata()
    # Reemplazo atributos de la instancia por los datos promediados.
    mapa.x, mapa.y, mapa.param = X, Y, Z_binned

    # Ploteo los datos suavizados.
    metodo = 'verdata'
    mapa.make(metodo=metodo, subplot=122)
    #Guardo figura
    save_name = mapa.par_name +'_' +mapa.time +'_' +mapa.xlabel[:2] +'_' +metodo +'.png'
    plt.savefig(os.path.join(savepath, save_name))
    # plt.close()

    # Comparo distintos metodos de la instancia 'mapa', en nueva figura.
    i += 1
    mapa.fig_number = i # modifico atributos relacionados con la nueva figura
    mapa.fig_dimension = [22,6]
    mapa.make(metodo='griddata', interpol='cubic', subplot=132)
    mapa.make(metodo='SBS', smooth=0.01, subplot=133)
    mapa.make(metodo='verimshow', interpol= 'bilinear', subplot=131)
    # Guardo figura
    save_name = mapa.par_name +'_' +mapa.time +'_' +mapa.xlabel[:2] +'_metodos.png'
    plt.savefig(os.path.join(savepath, save_name))
    # plt.close()

    # Pruebo opciones de interpocion de un mismo metodo de la instancia 'mapa', en nueva figura.
    i += 1
    mapa.fig_number = i
    mapa.fig_dimension = [18,12]
    metodo = 'verimshow'
    mapa.make(metodo=metodo,  interpol= 'nearest', subplot=221)
    mapa.make(metodo=metodo,  interpol= 'hamming', subplot=223)
    mapa.make(metodo=metodo,  interpol= 'bicubic', subplot=222)
    mapa.make(metodo=metodo,  interpol= 'spline16', subplot=224)            # Xig, Yig = np.meshgrid(xi, yi)bplot=224)
    save_name = mapa.par_name +'_' +mapa.time +'_' +mapa.xlabel[:2] +'_imcompare.png'
    plt.savefig(os.path.join(savepath, save_name))
    # plt.close()

    #-------------------------------------------------
    # Creo ionomapas con NmF2cc - LPIM en modo asimilacion de datos

    x, y, param = doy, modip, NmF2cc
    ptext = [ var_name+'cc', '2011', 'DOY', 'Modip [degrees] ', '10e10 m(-3)']
    i += 1
    # Creo otra instancia de Clase Ionomap, en nueva figura.
    mapa = ionomap.Ionomap(x, y, param, ptext, fignumber=i, color='plasma')

    # Pruebo un metodo de la instancia con diferentes binneados de data, en nueva figura.
    mapa.fig_dimension = [24,10]
    metodo = 'griddata'
    # Suavizo DATA original, promediando por bin, cambio el tamanno de bin por default.
    mapa.x, mapa.y, mapa.param = x, y, param
    mapa.x, mapa.y, mapa.param = mapa.bindata(binsize=[6,10])
    finegrid_size=[2,1]
    # Grafico binned data interpolada y original
    mapa.make(metodo=metodo, interpol='cubic', finegrid_size=finegrid_size, subplot=231)
    mapa.make(metodo='verdata', subplot=234)
    # Promedio data con diferente tamanno de bin
    mapa.x, mapa.y, mapa.param = x, y, param
    mapa.x, mapa.y, mapa.param = mapa.bindata(binsize=[4,8])
    finegrid_size=[2,1]
    ## Grafico binned data interpolada y original
    mapa.make(metodo=metodo, interpol='cubic', finegrid_size=finegrid_size, subplot=232)
    mapa.make(metodo='verdata', subplot=235)
    # Promedio data con diferente tamanno de bin
    mapa.x, mapa.y, mapa.param = x, y, param
    mapa.x, mapa.y, mapa.param = mapa.bindata(binsize=[2,4])
    finegrid_size=[2,1]
    # Grafico binned data interpolada y original
    mapa.make(metodo=metodo, interpol='cubic', finegrid_size=finegrid_size, subplot=233)
    mapa.make(metodo='verdata', subplot=236)
    # Guardo figura
    save_name = mapa.par_name +'_' +mapa.time +'_' +mapa.xlabel[:2] +'_gridcompare.png'
    plt.savefig(os.path.join(savepath, save_name))
    # plt.close()

    plt.show()


if __name__ == "__main__":
    main()
