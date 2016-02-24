"""
Joseph Kabariti
Goal: Passive dendrite with standard params calculating tau of the
membrane and resistance of the inputs based on membrane capacitance
and voltage.
"""

# Headers
from neuron import h, gui, rxd       #Neuron module for dendrite modeling

import os
import sys
import datetime

from matplotlib import pyplot as pp
from math import ceil,floor,e


# Global Variables
date = datetime.date.today().strftime("%d""%b""%y")
# date in 2 digit day, 3 letter month, 2 digit year format
dend = h.Section(name='dend')
stim = h.IClamp(dend(0.5))  #Stim connected to provide electron flow
t_vec, v_vec = h.Vector(), h.Vector()  #Time and voltage vectors



# Figure saving
def initsaving(date):
    """
    Initializes file name for saving the figure. Utilizes datetime
    and sys module.
    """
    cwd = os.getcwd()
    if len(sys.argv) == 2:
        date += '_' + str(sys.argv[1])
    else:
        if os.path.exists("figs"): # if figs folder exists
            num = os.listdir("figs")
            os.chdir("figs")
            if num == []:          # and is empty, set num to 01
                num = "01"
            else:     # if not, find the latest figure, and
                      # add one to its count
                num = max(num, key=os.path.getctime)
                num = num.split("_")
                num = num[1].strip(".png")
                if num == "09":
                    num = "10"
                elif num[0] == "0":
                    num = int(num)
                    num += 1
                    num = "0" + str(num)
                else:
                    num = int(num)
                    num += 1
                    num = str(num)
            os.chdir(cwd)
        else:
            os.mkdir("figs")
            num = "01"
        date += '_' + num
    

# dendrite morphology
def initdend():
    """
    Initializes all dendrite & channel params, and stim clamps.
    """
    dend.insert('pas') #Passive channel- leak
    dend.L = 200   # Length
    dend.Ra = 100  # Axial resistance
    dend.diam = 2  # Diameter

    # ion channels
    dend.g_pas = 1e-5  # Low conductance to keep channel effectively closed
    dend.e_pas = -65   # v = e, channel effectively closed

    # stim params
    stim.dur = 10000   # Duration at 10 s or 10000 ms
    stim.amp = -0.001  # Standard amp level (ohms)
    stim.delay = 500   # To verify the difference between baseline and
                       # regular activity (.5 s)


# calculations of rin and tau
def calculateRT():
    """
    Calculates rin and tau using two methods: Using results and
    using equations.
    """
    rin = dend(0.5).area() # dend(0.5).area() equals full area because
                           # only one segment (nseg = 1).
    # Later on, need to calculate full area in order to get rin
    rin *= 1e-8            # square microns, to convert to square cm multiply by 1e-8
    rin *= dend.g_pas      # puts units at 1/Siemens, or ohms.
    rin = 1/rin            # original equation is r membrane / A.
                       # Translated into 1/g_pas * 1/A, 1/(g_pas*A)

    # Measurements of rin
    vi = v_vec.max() # V initial, or the highest point of the curve
    vf = v_vec.min() # V final, or the lowest point of the curve
    dv = vf-vi # dv, or the change in voltage
    di = stim.amp # di or the change in current

    # calculation of tau membrane
    tau = dend.cm/ dend.g_pas # tau = rm * cm, where rm is inverse of g_pas
    tau *= 1e-6 # using units, (microfarads/siemens) * 1e-6 = seconds

    # Measurements of tau
    vtau = dv * (1-(1/e)) # tau = rc, where tau is the time at which ~63% voltage is filled
    vtau += vi            # to get time closest to tau, we need the
                          # point at which voltage was ~63%
    index = {}
    for i in range(int(v_vec.size())):
        # to find the exact time tau, consider the closest to ~63%
        # and then the closest time to that point
        if v_vec[i] < ceil(vtau) and v_vec[i] > floor(vtau) and t_vec[i] <= (stim.delay+stim.dur):
            index[i] = abs(vtau - v_vec[i])

    taum = t_vec[min(index, key=index.get)] - stim.delay 
    #tau = time of .632*vi minus the stim delay


    # Printing rin
    print("Calculated rin is " + "{:,}".format(rin) + " or " + str(rin*1e-6) + " Mega ohms.")
    #ohm's law states that r = dv/di. units states that mV/nA = 1 Mohm 
    print("Measured rin is equal to " + str(dv/di) + " Mega ohms.")

    # Printing tau
    print("Tau calculated is " + str(tau) + " seconds.")
    print("Tau measured is " + str(taum*1e-3) + " seconds.")

# run and plot
def run():
    """
    Runs sim and plots figures, saves to outfig
    """
    t_vec.record(h._ref_t)
    v_vec.record(dend(0.5)._ref_v)
    h.tstop = 20000       #stop sim at 20000 ms or 20 s

    h.run()  # run sim
    outfig = "v" + date + ".png"
    pp.plot(t_vec, v_vec)    # plot time versus voltage
    pp.savefig(outfig)       # save figure using outfig

    

# Main program
initsaving(date)  # Initializes date variable
initdend()    # Initializes dendrite morphology
run()         # Run sim
calculateRT()  # Calculates R and tau
