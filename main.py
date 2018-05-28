#!/usr/bin/env python
# -*- coding: utf-8 -*-
## @package ionodat
# Programa principal de Proyecto Ionos
# @author Ayelen E. Volk

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
        Realiza mapas de la variabilidad media global del parametro ionoferico de capa F2, calculados con
    el LPIM (La Plata Ionospheric Model). El tipo de mapa depende del tipo de archivo de salida en LPIM data base y
    la disponibilidad de datos en las fechas solicitadas.
    Parametro elegido es la densidad electronica maxima de la capa ionosferica F2 ('NmF2').
        Se pueden elegir otros parametros en Clase Ionodat:
            'hmF2': altura del pico de densidad de capa F2
            'HF2' : Altura de escala de la capa F2

        Se grafican dos formas de calcular NmF2: c0, LPIM usa coeficientes de ITU-R y cc,
    LPIM usa coeficientes ajustados con observaciones satelitales. Uno en variabilidad temporal (Local Time) y el otro espacial (DOY)
        El intervalo de tiempo solicitado es el anno 2011 completo. Se puede elegir otras fechas de datos.
    Para disferentes annos solo pueden elegirse intervalo de meses completos.
    Para un anno y un mes dados, puede elegirse un intervalo de dias (en DOY: Day of Year).

        Los graficos realizados muestran todos los metodos de ploteo disponibles en la Clase Ionomapas,
    combinando con tipos de interpolacion de data en 2D, propios de cada metodo.
    '''

# Ubicacion de archivos de entrada (LPIM-database) y salida del main

    source = '/media/ayelen/DATA/LOC-win/work/DAT/GLP/'
    # Aqui guarda las figuras:
    savepath = '/media/ayelen/DATA/LOC-win/graph/POO/Image'

# Obtengo el paquete de datos a plotear segun el parametro deseado.

    file_type = 'prm' # tipo de archivo salida del LPIM
    var_name = 'NmF2' # nombre de variable ionosferica deseada
    # Creo una instancia de Clase Ionodat
    dato = ionodat.Ionodat(source, file_type, var_name)
    # Intervalo de tiempo que se desea graficar
    fecha_inicial = datetime.datetime(2011, 1, 1)
    fecha_final = datetime.datetime(2011, 12, 31)
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
    plt.close()

    # Comparo distintos metodos de la instancia 'mapa', en nueva figura.
    i += 1
    mapa.fig_number = i # modifico atributos relacionados con la nueva figura
    mapa.fig_dimension = [18,12]
    mapa.make(metodo='griddata', interpol='cubic', subplot=221)
    mapa.make(metodo='SBS', smooth=0.002, subplot=222)
    mapa.make(metodo='verimshow', interpol= 'bilinear', subplot=223)
    mapa.make(metodo='verinterp2d', interpol= 'linear', subplot=224)
    # Guardo figura
    save_name = mapa.par_name +'_' +mapa.time +'_' +mapa.xlabel[:2] +'_metodos.png'
    plt.savefig(os.path.join(savepath, save_name))
    plt.close()

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
    plt.close()

#-------------------------------------------------
# Creo ionomapas con NmF2cc - LPIM en modo asimilacion de datos

    x, y, param = doy, modip, NmF2cc
    ptext = [ var_name+'cc', '2011', 'Month', 'Modip [degrees] ', '10e10 m(-3)']
    i += 1
    # Creo otra instancia de Clase Ionomap, en nueva figura.
    mapa = ionomap.Ionomap(x, y, param, ptext, fignumber=i, color='jet')

    # Pruebo un metodo de la instancia con diferentes binneados de data, en nueva figura.
    mapa.fig_dimension = [24,10]
    metodo = 'verinterp2d'
    # Suavizo DATA original, promediando por bin, cambio el tamanno de bin por default.
    mapa.x, mapa.y, mapa.param = x, y, param
    mapa.x, mapa.y, mapa.param = mapa.bindata(binsize=[26,14])
    finegrid_size=[2,1]
    # Grafico binned data interpolada y original
    mapa.make(metodo=metodo, interpol='cubic', finegrid_size=finegrid_size, subplot=231)
    mapa.make(metodo='verdata', subplot=234)
    # Promedio data con diferente tamanno de bin
    mapa.x, mapa.y, mapa.param = x, y, param
    mapa.x, mapa.y, mapa.param = mapa.bindata(binsize=[15,10])
    finegrid_size=[2,1]
    ## Grafico binned data interpolada y original
    mapa.make(metodo=metodo, interpol='linear', finegrid_size=finegrid_size, subplot=232)
    mapa.make(metodo='verdata', subplot=235)
    # Promedio data con diferente tamanno de bin
    mapa.x, mapa.y, mapa.param = x, y, param
    mapa.x, mapa.y, mapa.param = mapa.bindata(binsize=[7.6,3.2])
    finegrid_size=[2,1]
    # Grafico binned data interpolada y original
    mapa.make(metodo=metodo, finegrid_size=finegrid_size, subplot=233)
    mapa.make(metodo='verdata', subplot=236)
    # Guardo figura
    save_name = mapa.par_name +'_' +mapa.time +'_' +mapa.xlabel[:2] +'_int2dcompare.png'
    plt.savefig(os.path.join(savepath, save_name))
    plt.close()

    plt.show()


if __name__ == "__main__":
    main()
