import ctypes

class WLM:
    def __init__(self, dll_path='C:\\\\Windows\\System32\\wlmdata.dll', channel=1):
        self.dll = ctypes.WinDLL(dll_path)

        self.dll.GetWavelengthNum.restype = ctypes.c_double
        self.dll.GetFrequencyNum.restype  = ctypes.c_double
        self.dll.Instantiate.restype      = ctypes.c_long

        self.channel = channel

    def get_frequency(self):
        return_value = self.dll.GetFrequencyNum(ctypes.c_long(7), ctypes.c_double(0))
        return self.return_or_raise(return_value)

    def get_wavelength(self):
        return_value = self.dll.GetFrequencyNum(ctypes.c_long(7), ctypes.c_double(0))
        return self.return_or_raise(return_value)

    @staticmethod
    def return_or_raise(code):
        if code <= 0:
            if code == 0.0:
                raise Exception('No signal')
            if code == -3.0:
                raise Exception('Underexposured')
            if code == -4.0:
                raise Exception('Overexposured')
            if code == -5.0:
                raise Exception('Wavemeter application not running')

            raise Exception('Unknown error')
        else:
            return code

if __name__ == "__main__":
    wlm = WLM(channel=7)
    print "wavelength meter listening on channel %i" % wlm.channel
    try:
        wlm.get_frequency()
    except Exception, e:
        print "Error: %s" % e
