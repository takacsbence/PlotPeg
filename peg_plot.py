import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import datetime, calendar
import matplotlib.dates as mdates
import math

def weeksecondstoutc(gpsweek, gpsseconds, leapseconds):
    datetimeformat = "%Y-%m-%d %H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00", datetimeformat)
    elapsed = datetime.timedelta(days = (gpsweek * 7), seconds = gpsseconds + leapseconds)
    #print(type(epoch + elapsed))
    #return datetime.datetime.strftime(epoch + elapsed, datetimeformat)
    return epoch + elapsed
    

class PosData():
    """
        :param file_name: Pegasus position file name
    """

    def __init__(self, file_name, cols, out_dir):
        """ Initialize instance
        """
        self.file_name = file_name
        self.out_dir = out_dir
        self.cols = cols

        #read first line as header
        with open(file_name, "r") as file:
            buf = file.readline().split(";")
        #print(len(buf))
        buf2 = [s.replace('"','') for s in buf] #remove " characters
        
        #get index of columns to read
        icols = []
        for i in cols:
            ind = buf2.index(i)
            icols.append(ind)
        self.header = cols
        print("index of columns :", icols)
        print("columns name: ", self.header)
        
        #read data in np array
        self.data = np.genfromtxt(file_name, delimiter=';', skip_header=1, encoding=None, usecols=icols, comments='%')
        self.ndata = self.data.shape[0] # nr of rows
        print("{:d} pos data and {:d} columns read from {:s}".format(self.ndata, self.data.shape[1], file_name))

        self.dt = []
        for i in range(self.ndata):
            gpsweek = self.data[i, 0]
            gpsseconds = self.data[i, 1]
            self.dt.append(weeksecondstoutc(gpsweek, gpsseconds, 0))            
    
    def plot(self, cols, ylabel, iname, dtmin, dtmax): 
        iname = iname
        fig, ax = plt.subplots()
        for i in cols:
            icol = self.header.index(i)
            label1 = self.header[icol].replace('NSV_','NS_')
            label1 = label1.replace('NS_','')
            plt.plot(self.dt, self.data[:, icol], label=label1)
        plt.ylabel(ylabel)
        ax.legend()
        plt.xlabel('GPS time [hh:mm]')
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_xlim([dtmin, dtmax])
        plt.grid(True)
        plt.figtext(0.1, 0.0, datetime.datetime.strftime(dtmin, "%Y-%m-%d"))
        fig.set_size_inches(8, 3)
        plt.savefig(self.out_dir + iname, dpi=100, bbox_inches='tight', pad_inches=0.1)
        print(self.out_dir + iname + " saved")
        plt.close()

class RngData():
    """
        :param file_name: Pegasus range file name
    """

    def __init__(self, file_name, cols, out_dir):
        """ Initialize instance
        """
        self.file_name = file_name
        self.out_dir = out_dir
        self.cols = cols

        #read first line as header
        with open(file_name, "r") as file:
            buf = file.readline().split(";")
        #print(len(buf))
        buf2 = [s.replace('"','') for s in buf] #remove " characters
        
        #get index of columns to read
        icols = []
        for i in cols:
            ind = buf2.index(i)
            icols.append(ind)
        self.header = cols
        print("index of columns :", icols)
        print("columns name: ", self.header)
        
        #read data in np array
        self.data = np.genfromtxt(file_name, delimiter=';', skip_header=1, encoding=None, usecols=icols, comments='%')
        self.ndata = self.data.shape[0] # nr of rows
        print("{:d} pos data and {:d} columns read from {:s}".format(self.ndata, self.data.shape[1], file_name))
        self.prnlist = np.unique(self.data[:, 2]).astype(int)
        print('list of satellites ', self.prnlist)

    def plot(self, prn, iname, dtmin, dtmax): #plot SNR and Elevation angle in one plot
        iname = iname
        
        data2 = self.data[self.data[:, 2] == prn]   #filter out prn
        print("{:d} measurements on sat PRN{:02d}".format(data2.shape[0], prn))
        #print(data2)
        
        #convert to datetime
        dt = []
        for i in range(data2.shape[0]):
            gpsweek = data2[i, 0]
            gpsseconds = data2[i, 1]
            dt.append(weeksecondstoutc(gpsweek, gpsseconds, 0))            

        #plot
        fig, ax1 = plt.subplots()
        
        ax2 = ax1.twinx()
        
        icol1 = self.header.index('CNO_L1')
        icol2 = self.header.index('SV_EL')
        plot_1 = ax1.plot(dt, data2[:, icol1], '.', label='SNR [dBHz]', color='C0')
        plot_2 = ax2.plot(dt, data2[:, icol2], '.', label='ele [deg]', color='C1')
        
        ax1.set_ylabel('Signal-to-noise ratio [dBHz]', color='C0')
        ax2.set_ylabel('elevation [deg]', color='C1')
        plt.title('PRN' + str(prn).zfill(2))
        
        lns = plot_1 + plot_2
        labels = [l.get_label() for l in lns]
        #plt.legend(lns, labels, loc=0)
        #plt.legend()
        ax1.set_xlabel('GPS time [hh:mm]')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax1.set_xlim([dtmin, dtmax])
        ax1.set_ylim([15, 60])
        ax2.set_ylim([0, 90])
        ax1.grid(True)
        ax2.grid(None)
        plt.figtext(0.1, 0.0, datetime.datetime.strftime(dtmin, "%Y-%m-%d"))

        fig.set_size_inches(8, 3)
        plt.savefig(self.out_dir + iname, dpi=100, bbox_inches='tight', pad_inches=0.1)
        print(self.out_dir + iname + " saved")
        plt.close()

    def plot2(self, prnlist, iname, dtmin, dtmax): #plot all prn's SNR
        iname = iname

        icol = self.header.index('CNO_L1')

        #plot
        fig, ax1 = plt.subplots()
        ax1.set_ylabel('Signal-to-noise ratio [dBHz]')
        ax1.set_xlabel('GPS time [hh:mm]')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax1.set_xlim([dtmin, dtmax])
        ax1.set_ylim([15, 60])
        ax1.grid(True)
        
        for prn in prnlist:
            data2 = self.data[self.data[:, 2] == prn]   #filter out prn
            print("{:d} measurements on sat PRN{:02d}".format(data2.shape[0], prn))
        
            #convert to datetime
            dt = []
            for i in range(data2.shape[0]):
                gpsweek = data2[i, 0]
                gpsseconds = data2[i, 1]
                dt.append(weeksecondstoutc(gpsweek, gpsseconds, 0))            
        
            ax1.plot(dt, data2[:, icol], '.', label='PRN' + str(prn).zfill(2))
        

        #plt.legend()
        

        print(ax1.get_ylim())
        plt.figtext(0.1, 0.0, datetime.datetime.strftime(dtmin, "%Y-%m-%d"))
        fig.set_size_inches(8, 3)
        plt.savefig(self.out_dir + iname, dpi=100, bbox_inches='tight', pad_inches=0.1)
        print(self.out_dir + iname + " saved")
        plt.close()


if __name__ == "__main__":

    #create output directory if it does not exist
    out_dir='./2022_02_03_pecs/plot/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    #pegasus position file name
    #pos_fname = sys.argv[1]
    pos_fname = '2022_02_03_pecs/pegasus/PildoBox21322034qr_sol.pos'

    #manually set time min and max
    dtmin = datetime.datetime(2022, 2, 3, 17, 0, 0)
    dtmax = datetime.datetime(2022, 2, 3, 18, 0, 0)

    #read Pegasus gnss_solution output position file
    cols = ['RX_WEEK', 'RX_TOM', 'POS_TYPE', 'NSV_USED', 'NSV_LOCK', 'NS_HPL', 'NS_VPL', 'NS_LAT', 'NS_DUP', 'NS_DHOR']
    pos_data = PosData(pos_fname, cols, out_dir)

    #plot xpl, xpe, nsat
    pos_data.plot(['NS_HPL', 'NS_VPL'], 'Protection level [m]', 'xpl.png', dtmin, dtmax)
    pos_data.plot(['NS_DHOR', 'NS_DUP'], 'Position error [m]', 'xpe.png', dtmin, dtmax)
    pos_data.plot(['NSV_USED', 'NSV_LOCK'], 'Number of satellites', 'nsat.png', dtmin, dtmax)

    #range file name
    rng_fname = '2022_02_03_pecs/pegasus/PildoBox21322034qr_sol.rng'
    
    #read Pegasus gnss_solution output range file
    cols = ['RX_WEEK', 'RX_TOM', 'PRN', 'SV_EL', 'CNO_L1']
    rng_data = RngData(rng_fname, cols, out_dir)

    #plot snr and ele
    for prn in rng_data.prnlist:
#    for prn in [72]:
        rng_data.plot(prn, 'snr_ele' + str(prn).zfill(2) + '.png', dtmin, dtmax)

    rng_data.plot2(rng_data.prnlist, 'all_snr.png', dtmin, dtmax)
