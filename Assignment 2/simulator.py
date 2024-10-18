import math as m
class Transducer():
    def __init__(self, x, y, t_array):
        self.x = x
        self.y = y
        self.t_array = t_array
        self.signal = len(self.t_array)*[0]
class Receiver(Transducer):
    def __init__(self, x, y, t_array):
        super().__init__(x, y, t_array)
class Emitter(Transducer):
    def __init__(self, x, y, t_array):
        super().__init__(x, y, t_array)
    def generate_signal(self, f_c, n_cycles, amplitude): #Making sinusoisal wave signal
        self.signal = []
        domain = n_cycles/f_c
        if len(self.t_array)-domain >0:
            for i in self.t_array:
                if i<=domain:
                    self.signal.append(amplitude*m.sin(2*m.pi*f_c*(i)))
                else:
                    self.signal.append(0.0)
        else:
            for i in self.t_array:
                self.signal.append(amplitude*m.sin(2*m.pi*f_c*(i)))
        return self.signal
    
class SoundSimulator:
    def __init__(self, emitters = [], receivers = [], t_array = [], sos = 1500.0):
        self.emitters = emitters
        self.receivers = receivers
        self.t_array = t_array
        self.sos = sos
    def run(self):
        gapinv = 1/(self.t_array[1]-self.t_array[0])
        siggylist = []
        sosinv = 1/self.sos
        for i in self.receivers:
            for j in self.emitters:
                siggy = []
                dist = m.sqrt((i.x-j.x)**2+(i.y-j.y)**2) #distance between individual emitter and receiver
                tdelay = dist*sosinv #since amplitude decreases by 1/dist, just multiply each term in array by that later
                mult = int(tdelay*gapinv) #Multiplier value for how many delay values we include (aligned with t_array)
                if dist==0: 
                    siggy = [0.0]*mult + j.signal
                    i.signal = [i.signal[p]+siggy[p] for p in range(len(self.t_array))]
                else:                  
                    siggy = [0.0]*mult + [i/dist for i in j.signal]
                    i.signal = [i.signal[p]+siggy[p] for p in range(len(self.t_array))] #Updating the i.signal value each iteration
                
            i.signal = i.signal[:len(self.t_array)]         
            siggylist.append(i)
        return siggylist

class BeamFormer:
    def __init__(self, receivers = [], x_array = [], y_array = [], t_array = [], sos:float = 1500.0):
        self.receivers = receivers
        self.x_array = x_array
        self.y_array = y_array
        self.t_array = t_array
        self.sos = sos
        field = [[[0.0 for k in range(len(t_array))] for j in range(len(x_array))] for i in range(len(y_array))]
        self.field = field

    def generate_field(self): #Visualisation of emitter signals from the receiver signals only
        gapinv = 1/(self.t_array[1]-self.t_array[0]) # reciprocal values
        sosinv =1/self.sos
        tarraylength = len(self.t_array) #length of arrays
        receivelength = len(self.receivers)
        reclengthinv = 1/receivelength
        for a,i in enumerate(self.y_array):
            for b,j in enumerate(self.x_array):
                dlist = [(m.sqrt((i-rec.y)**2+(j-rec.x)**2)) for rec in self.receivers] #distance of each receiver from a specific location
                tmin = min(dlist)*sosinv #smallest time delay from the closest receiver
                for num, rec in enumerate(self.receivers):
                    d = dlist[num]
                    trel = (d*sosinv)-tmin #relative time delay (signal delay - minimum delay)
                    for c,k in enumerate(self.t_array):
                        inptime = k+trel #this is the relative time with relative shift to input
                        ind = int((inptime)*gapinv) #Index time shift
                        if ind<tarraylength:
                            ref = rec.signal[ind]
                            if ref!=0.0: #0 values dont have to be altered
                                self.field[a][b][c] += d*ref*reclengthinv
                            else:
                                continue
                        else:
                            break
        return self.field