#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import sys
#--------- my modules --------------
import takefiles

class Ionodat(object) :
    """
    Define Clase del objeto dato ionoferico, a partir de los calculos obtenidos con el modelo ionosferico LPIM.
    """

    def __init__(self, path_source, file_type, var_name):
         self.source = path_source # Ubicacion de los archivos salida del LPIM (LPIM-database)
         self.file_type = file_type #str: tipo de archivo salida del LPIM.
         self.name = var_name  # str: nombre del parametro (variable) ionoferica


    def get(self, fecha_inicial, fecha_final):
        """
        Extrae set de datos relacionados con parametro ionoferico deseado de LPIM database.
        Chequea si hay datos disponibles en LPIM database, para las fechas solicitadas por usuario.
        """

# Crea listas con los intervalos de tienpo, años, meses, dias, solicitados por usuario.
        # Lista-año, para intervalo de fechas solicitado
        yran = range(int(fecha_inicial.strftime("%Y")),int(fecha_final.strftime("%Y"))+1)
        yearl = [str(x) for x in yran]

        # Si se solicita un solo año, hace unica lista-mes
        if len(yran) == 1 :
            mran = range(int(fecha_inicial.strftime("%m")),int(fecha_final.strftime("%m"))+1)
            months = [str(x).zfill(2) for x in mran]
            monl = [months]

        # Para varios años, hace una lista-mes por cada año
        else :
            monl = []
            for year in yearl :

                months = ['*']

                if year == fecha_inicial.strftime("%Y") :
                    mran = range(int(fecha_inicial.strftime("%m")),12+1)
                    months = [str(x).zfill(2) for x in mran]

                if year == fecha_final.strftime("%Y") :
                    mran = range(1,int(fecha_final.strftime("%m"))+1)
                    months = [str(x).zfill(2) for x in mran]

                monl.append(months)


        doyl = ['*']
        # si se solicita un unico año y unico mes, crea lista de dias (doys).
        if len(yran) == len(mran) == 1 :
            dran = range(int(fecha_inicial.strftime("%j")),int(fecha_final.strftime("%j"))+1)
            doyl = [str(x).zfill(3) for x in dran]

        print 'Lista de Datos solicitado por usuario'
        print yearl, monl, doyl
        print '  '

# Para  rango de fechas solicitado, lista archivos disponibles en LPIM databe
        procesar = takefiles.LPIMdatbase (self.source, self.file_type, yearl, monl, doyl)
        print 'Total prm files', len(procesar)

# EXtrae las variable ionos solicitada, segun tipo de archivo correspondiente, en LPIM databse.
        if self.file_type == 'prm' :
            # Correspondencia entre nro de columna y variable, en archivo tipo ~prm de LPIM databse.
            columnas = {'NmF2': (6,7), 'hmF2': (10,11), 'HF2': (14,15)} # LPIM(ccir),LPIM(cosmic),ObsCOSMIC
            # Segun variable deseada, seran las columnas extraidas
            if self.name in columnas :
                col = columnas[self.name]
            else :
                print 'No existe variable solicitada en salida tipo ~prm'
                sys.exit()

            dia = []
            abcisa=[]
            ordenada=[]
            par0=[]
            parc=[]
            for prmf in procesar :
                # Leo archivo de datos
                modip, LT = np.loadtxt(prmf, comments = '%', unpack = True, usecols = (3, 5))
                c0, cc = np.loadtxt(prmf, comments = '%', unpack = True, usecols = col)

                # modip:  latitud modip del valor observado
                # LT_Mob : local time del valor observado (Cosmic)
                # c0 : valor calculado LPIM (modo autonomo)
                # cc: valor calculado LPIM + asimilación de datos

                # Extraigo doy number de file name
                doy = prmf[-8:-5]
                # construyo vector de string doy repetido la cantidad de observaciones en el prmf.
                doy_vect = [int(doy)]*len(modip)

                dia.append(doy_vect)
                abcisa.append(LT)
                ordenada.append(modip)
                par0.append(c0)
                parc.append(cc)

            doy = np.concatenate(dia)
            LT = np.concatenate(abcisa)
            modip = np.concatenate(ordenada)
            c0 = np.concatenate(par0)
            cc = np.concatenate(parc)

            print 'cantidad de rops a plotear:', len(c0)
            # print NmF2c0.max(), NmF2c0.min()

            # print doy[:5], LT[:5], modip[:5], c0[:5], cc[:5]

        else: print '[ionodat.Ionodat.get] No existe ese tipo de archivo en LPIM database'

        return doy, LT, modip, c0, cc
