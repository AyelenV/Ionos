# coding: utf-8

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d
from scipy.interpolate import griddata
from scipy.interpolate import interp2d
from scipy.interpolate import SmoothBivariateSpline


class Ionomap(object) :
    """
    Define una clase de visualizacion de paramentros ionofericos.
    Las instancias tipo ionomaps muestran variabilidad representada en clave de color,
     de un parametro ionosferico sobre plano (x,y).
    """

    def __init__(self, x, y, param, plot_text,
            color='jet',fignumber=0, dimension=[18,6], savepath = '/media/ayelen/DATA/LOC-win/graph/POO/Image'):

         # self.ax = self.fig.add_subplot(111)
         self.x = x
         self.y = y
         self.param = param
         self.par_name = plot_text[0]
         self.time = plot_text[1]
         self.xlabel = plot_text[2]
         self.ylabel = plot_text[3]
         self.clblabel = plot_text[4]
         self.fig_number = fignumber
         self.fig_dimension = dimension # [ancho, alto]

         # Clave de color elegida
         self.cm = plt.cm.get_cmap(color)
         # Define los limites de la escala de color
         self.vmin = abs(self.param.min())
         self.vmax = abs(self.param.max())
         # Donde se guardan los graficos
         self.savepath = savepath

    def bindata(self, binsize=[1,5], statis='mean') :

            '''
            Calcula un estadistico de la data original, dividida en bins de tamanno ajustable, binsize = [dx,dy].
            El estadistico puede ser la media o la mediana.
            Devuelve la data media en forma de grilla (matrices) para abcisa (X), ordenada(Y) y parametro(Z_binned).
            '''

            # Calcula cant de segmentos en x y en y, segun el tamaño de bin ingresado por usuario.
            nbx = int(abs(self.x.max() - self.x.min())/binsize[0])
            nby = int(abs(self.y.max()- self.y.min())/binsize[1])
            print 'bins number: ', nbx, nby

            '''
            ATENCION: argumentos de scipy.stats.binned_statistic_2d: y,y,z en ese orden!
            NOTE: bin s= [nrobinsx,nrobinsy] or bins = [xedges,yedges]
            '''

            H = binned_statistic_2d(self.y, self.x, self.param, statistic= statis, bins=[nbx,nby])# , range=Non)
    #         print np.shape(H), H  #H[2]#,H[0],H[1]
    #         print np.shape(H[0]), H[0]
    #         print np.shape(H[1]), H[1]
    #         print np.shape(H[2]), H[2]

            yedges = H[1].copy()
            xedges = H[2].copy()
            Z_binned = H[0] #mean bin data : matriz(nby,nbx)
            # print Z_binned

            # print Z_binned.shape, type(Z_binned), len(xedges),len(yedges)

            # NOTE: dimension Z_binned : (y,x)
            # Asigno cada valor Z_binned al centro del bin.
            xcenters = xedges[:-1] + 0.5 * (xedges[1:] - xedges[:-1])
            ycenters = yedges[:-1] + 0.5 * (yedges[1:] - yedges[:-1])
            X, Y = np.meshgrid(xcenters, ycenters) # X e Y 2D array

            print 'bins center: ', X.shape, Y.shape, Z_binned.shape

            # Me fijo elementos de Z_binned con valor nan
            fillbin = np.where(~np.isnan(Z_binned))
            # Cambio limites de escala de color de la instancia original
            self.vmin = abs(Z_binned[fillbin].min())
            self.vmax = abs(Z_binned[fillbin].max())
            print 'Ionomap.bindata mensaje: atributos vmax, vmin fueron modificados '

            return X, Y, Z_binned


    def clbnormalization(self, clbnormal):
        '''
        Normaliza escala de colores, fijando limites de colorbar segun fecha de datos.
        '''

        # Si quiero normalizacion, hay definada limites de color para ciertos caso.
        if clbnormal :
            if  self.time == '2011' and self.xlabel == 'LT [hours]': self.vmin, self.vmax = 5, 180
            elif self.time == '2011' and self.xlabe == 'Month': self.vmin, self.vmax = 5, 170
            elif self.time == '2008' and self.xlabe == 'LT [hours]': self.vmin, self.vmax = 5, 120
            elif self.time == '2008' and self.xlabe == 'Month': self.vmin, self.vmax = 5, 85
            else:
                print 'NO HAY normalizacion preestablecida p/ COLORBAR en año requerido'

        return


    def make (self, metodo='verdata', subplot = 111, clbnormal=False,
        interpol='linear', finegrid_size=[0.05, 0.05], smooth=0.01):

        '''
        Plotea parametro ionosfericos sobre mapa (x,y).
        El usuario elige metodo de graficado y tipo de interpolacion segun corresponda y
        la ubicacion del plot dentro de la figura.
        '''

        # Crea una figura y un subplot dentro de la figura
        fig = plt.figure(self.fig_number, figsize = self.fig_dimension) #largo,alto
        fig.suptitle('Class ionomap')
        ax = fig.add_subplot(subplot)
        plt.cla() # limpio ejes

        # Configura limites de barra de color segun normalizacion.
        self.clbnormalization(clbnormal)
        # Configuracion base del plot
        ax.axis([self.x.min(), self.x.max(), -70, 70])
        ax.set_title(self.par_name + ' - ' + self.time)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        if self.xlabel == 'Month':
            start, end = ax.get_xlim()
            stepsize = 30.41
            ax.xaxis.set_ticks(np.arange(start,end, stepsize))
            # plt.setp(ax, xticks=[np.arange(start,end, stepsize)],
            ax.set_xticklabels(['1', '2', '3','4','5','6','7','8','9','10','11','12'])

        # Diccionario de metodos para instancia Ionomap
        dic_metodos = {'verdata': (self.verdata,()), 'griddata': (self.griddata,(interpol, finegrid_size)),
                'SBS': (self.SBS,(smooth, finegrid_size)), 'verimshow': (self.verimshow,(interpol,)),
                'verinterp2d' : (self.verinterp2d,(interpol, finegrid_size)) }

        # Ploteo con metodo elegido
        if metodo in dic_metodos :
            pc = dic_metodos[metodo][0](ax,*dic_metodos[metodo][1]) # nombrefuncion(*argumentos)
            # colorbar setttings
            clb = plt.colorbar(pc, ax=ax)
            clb.set_label(self.clblabel, labelpad=-30, y=1.05, rotation=0)

        else :
            print 'Ionomap.make Error: metodo NO valido'
            exit()

        return



    def verdata (self, ax) :

        '''
        Genera un scatter plot 2D en clave color.
        El tamaño de marcador es variable, segun cantidad de data a plotear.
        '''

        if  self.param.size < 5000:
            s = 40
            tipo = 'binned data'
        else :
            s = 5
            tipo = 'original data'

        pc = ax.scatter(self.x, self.y, marker='o', s=s, c=self.param, alpha=0.7, cmap=self.cm, vmax=self.vmax, vmin=self.vmin)
        # Perzonalizo titulo del plot
        ax.set_title(self.par_name + ' - ' + self.time + ' '+ tipo +' points: '+str(self.param.size))
	


        return pc


    def griddata (self, ax, interpol, finegrid_size):

        '''
        Genera objeto plot tipo pcolormesh de z-data interpolada con scipy.interpolate.griddata.
        El tipo de interpolacion y la correspondiente grilla de interpolacion, son ajustadas por usuario.
        '''

        # Tipos de interpolacion disponibles para scipy.griddata
        interpol_list = ['nearest', 'linear', 'cubic']

        # Elimino data con valores 'nan'
        fillbin = np.where(~np.isnan(self.param))
        # Convierto arreglos 2D a 1D
        xf = self.x[fillbin].ravel()
        yf = self.y[fillbin].ravel()
        zf = self.param[fillbin].ravel()

        # Grilla fina regularmente espaciada
        dx, dy = finegrid_size[0], finegrid_size[1]
        xi = np.arange(xf.min(), xf.max(), dx)
        yi = np.arange(yf.min(), yf.max(), dy)
        Xig, Yig = np.meshgrid(xi, yi)

        if interpol in interpol_list:
            # Interpolo z-data con scipy.interpolate.griddata
            Zi = griddata((xf, yf), zf, (Xig, Yig), method=interpol)
            # print Zi.shape, xi.shape, yi.shape
            # Crea objeto plot
            pc = ax.pcolormesh(xi, yi, Zi, cmap=self.cm, vmax=self.vmax, vmin=self.vmin)
            ax.set_title(self.par_name + ' - ' + self.time + ' griddata: '+ interpol)
        else :
            print 'ionomap.intgriddata error: Metodo de interpolacion NO VALIDO'
            exit()
	print 'griddata', type(pc)
        return pc

    def SBS(self, ax, smooth, finegrid_size):

        '''
        Genera objeto plot tipo pcolormesh de z-data interpolada con scipy.interpolate.SmoothBivariateSpline.
        La grilla fina de interpolacion y el coeficiente de suavizado 'smooth', son ajustadas por usuario.
        '''

        # Elimino data con valores 'nan'
        fillbin = np.where(~np.isnan(self.param))
        # Convierto arreglos 2D a 1D
        xf = self.x[fillbin].ravel()
        yf = self.y[fillbin].ravel()
        zf = self.param[fillbin].ravel()
        # print zf.shape, xf.shape, yf.shape

        # Grilla fina regularmente espaciada
        dx, dy = finegrid_size[0], finegrid_size[1]
        xi = np.arange(xf.min(), xf.max(), dx)
        yi = np.arange(yf.min(), yf.max(), dy)

        # Use SmoothBivariateSpline interpolation
        z2sum = np.sum( zf**2 )
        kx, ky = 3, 3
        # Spline s = smooth * z2sum, see note
        # s is a target for sum (Z() - spline())**2  ~ Ndata and Z**2;
        # smooth is relative, s absolute
        '''
        NOTE: BivariateSpline y and x to be passed in this order (opposite to that of interp2d.)
        This issue is related to the way that meshgrid is indexed which is based on the conventions of MATLAB.
        '''

        fit = SmoothBivariateSpline(yf, xf, zf, kx=kx, ky=ky, s=smooth*z2sum)
        Zspline = fit(yi,xi)
        # Plot
        pc = ax.pcolormesh(xi, yi, Zspline, cmap=self.cm, vmax=self.vmax, vmin=self.vmin)
        ax.set_title(self.par_name + ' - ' + self.time + ' SBSpline '+ str(smooth))
	
	print 'SBS', type(pc)
        return pc


    def verimshow(self, ax, interpol):

        '''
        Genera objeto plot tipo imshow de z-data interporlada por imshow (de matplotlib.pyplot).
        El tipo de interpolacion es elegido por usuario.
        El parametro a plotear debe ser un arreglo en 2D (z data en grillla)
        '''

        # Tipos de interpolacion disponible en matplotlib.imshow
        interpol_list = [ 'nearest', 'bilinear', 'bicubic', 'spline16', 'spline36', 'hanning',
        'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

        if interpol in interpol_list:

            # cobertura de la imagen
            extent = [self.x.min(),self.x.max(),self.y.min(),self.y.max()]

            Z = self.param # Z es matriz (data en grilla)
            im = ax.imshow(Z, cmap=self.cm, interpolation=interpol, origin='low',
                extent=extent, aspect='auto')
            ax.set_title(self.par_name + ' - ' + self.time + ' imshow: '+ interpol)

        else :
            print 'Ionomap.verimshow error: Metodo de interpolacion NO VALIDO'
            exit()
	print 'imshow', type(im)
        return im


    def verinterp2d(self, ax, interpol, finegrid_size):

            '''
            Genera objeto plot tipo pcolormesh de z-data interpolada con scipy.interpolate.interp2d
            El tipo de interpolacion y la grilla fina de interpolacion son ajustadas por usuario.
            '''

            # Tipos de interpolacion disponible en scipy.interpolate.interp2d
            interpol_list = ['linear', 'cubic', 'quintic']

            # elimino z-data con valor 'nan'
            fillbin = np.where(~np.isnan(self.param))
            # Convierto arreglos 2D en 1D
            xf = self.x[fillbin].ravel() #Flat input into 1d vector
            yf = self.y[fillbin].ravel()
            zf = self.param[fillbin].ravel()

            # Grilla fina regulamente espaciada.
            dx, dy = finegrid_size[0], finegrid_size[1]
            xi = np.arange(xf.min(), xf.max(), dx)
            yi = np.arange(yf.min(), yf.max(), dy)

            if interpol in interpol_list:
                f = interp2d(xf, yf, zf, kind=interpol)
                Zi = f(xi,yi)
                # Crea objeto Plot
                pc = ax.pcolormesh(xi, yi, Zi, cmap=self.cm, vmax=self.vmax, vmin=self.vmin)
                # Personaliza titulo de plot
                ax.set_title(self.par_name + ' - ' + self.time + ' interp2d: '+ interpol)

            else :
                print 'Ionomap.verinterp2d error: metodo de interpolacion NO VALIDO'
                exit()
	
            return  pc
