#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import os
import glob
import time
import datetime
import calendar

## @package takefiles
# Funciones para la obtencion de datos ionoféricos de La Plata Ionospherico Model (LPIM)
# Grupo GESA, Factultad de Ciencias Astronómicas y Geofísicas
# @author Ayelen E. Volk


##  Verifica disponibilidad de datos solicitados y devuelve lo encontrado en el directorio dado (path).
# @param data_wanted : list[str] : nombres de archivos solicitados por usuario (path absoluto + name_archivo)
# @param path : str : path al directorio que contiene nombres de arch solicitados
# @return data_given  : list[str] : parte disponible de los archivos solicitados (path absoluto + archivo)
def ask_avaiability(data_wanted, path):

    #Data disponible en el directorio indicado
    data_avail = os.listdir(path)
    # print data_wanted
    # print set(data_wanted).issubset(set(data_avail))

    if data_wanted[0] == '*' :
        data_given = data_avail
    else:
        data_given = []
        if set(data_avail)&set(data_wanted) :
            if  set(data_wanted).issubset(set(data_avail)) :
                 data_given = data_wanted
            else:
                print 'takefiles.ask_avaiability warning: '
                print 'PARTE de los datos solicitados NO estan disponibles'
                print ' '
                for element in set(data_avail)&set(data_wanted) :
                    data_given.append(element) # lista data seleccionada
        else:
            print 'takefiles.ask_avaiability warning: '
            print ('NO HAY DATOS disponibles para la fecha')
            print data_wanted
            quit()

    return data_given


## Extraer de la base de datos LPIM los nombres de los archivos con la data solicitada por usuario, con path absoluto.
# @param path0 : str : path al directorio que contiene los archivos fuente de datos (LPIMdatase)
# @param file_type : str : tipo de archivo que contiene la data solicitada
# @param year_select :list[str] : rango de años de la data solicitada por usuario
# @param mon_select : list[list[str]] : lista de  meses en correspondencia con los años solicitados.
# @param doy_select : list[str] : rango de dias solictados (solo valido si usuario pide un mes en particular)
# @return procesar : list[str] : lista de nombres de los archivos disponibles (path absoluto + archivo), para rango de fechas solicitados
# @note Tipos de archivo disponibles en LPIMdatabase: 'prm', 'loc', 'est'.
def LPIMdatbase (path0, file_type, year_select, mon_select, doy_select):

    # Enumero lista-años solicitada.
    yenum = [(idx, year) for idx, year in enumerate(year_select)]

    # Verifico disponibilidad de años solicitados en LPLIM data-base.
    # Me quedo con lo que pueda encontrar, dentro del rango pedido.
    year_process = ask_avaiability(year_select, path0)
    # print year_process

    print  'Datos disponibles en LPIM database'
    procesar = []
    time_range = []
    for year in year_process:
        # Filtro la lista-años solicitada de acuerdo a la disponibilidad de base de datos
        # Importante conservar el orden para guardar correspondencia con lista-mes
        msk = [(x[1] == year) for x in yenum]
        yenum_process = [yenum[i] for i in xrange(len(yenum)) if msk[i]]
        indx = yenum_process[0][0]
        # print indx, type(indx)
        # print mon_select[indx]

        mon_process = ask_avaiability(mon_select[indx], os.path.join(path0, year))
        # print mon_process

        for month in mon_process:

            if doy_select[0] == '*' :
                # Toma todas las salidas del tipo prm del directorio month
                dirfiles = os.listdir(os.path.join(path0, year, month))
                msk = [(x[1:4] == 'prm') for x in dirfiles]
                doy_process = [dirfiles[i] for i in xrange(len(dirfiles)) if msk[i]]

            else :
                # Toma salidas de acuerdo al rango de doys solicitado
                fil_select = []
                for doy in doy_select :
                    fil_select.append('~'+file_type+str(doy).zfill(3)+'0'+'.'+year[2:]+'o')
                    doy_process = ask_avaiability(fil_select, os.path.join(path0, year, month))

            for doy in doy_process :
                procesar.append(os.path.join(path0, year, month, doy))

        time_range.append([year, mon_process[0], mon_process[-1]])
        print year, mon_process, doy_select
    print ' '
    print 'INTERVALO DE TIEMPO DISPONIBLE ', time_range
    print 'INICIO ', time_range[0][1], 'FINAL', time_range[-1][2]
    return procesar
