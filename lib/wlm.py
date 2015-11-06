import ctypes, time

class WLM:
    def __init__(self, dll_path='C:\\\\Windows\\System32\\wlmdata.dll', channel=1):
        self.dll = ctypes.WinDLL(dll_path)

        self.dll.GetWavelengthNum.restype   = ctypes.c_double
        self.dll.GetFrequencyNum.restype    = ctypes.c_double
        self.dll.GetSwitcherChannel.restype = ctypes.c_long
        self.dll.SetSwitcherChannel.restype = ctypes.c_long

        self.channel = channel

    def get_switcher_channel(self):
        return self.dll.GetSwitcherChannel(ctypes.c_long(0))

    def set_switcher_channel(self, channel):
        if (channel >= 1 and channel <= 8):
            self.dll.SetSwitcherChannel(ctypes.c_long(channel))

    def get_frequency(self):
        return_value = self.dll.GetFrequencyNum(ctypes.c_long(7), ctypes.c_double(0))
        return self._return_or_raise(return_value)

    def get_frequency_from_switcher(self, channel):
        frequency = 0.
        old_channel = self.get_switcher_channel()

        if (old_channel != channel):
            self.set_switcher_channel(channel)
            time.sleep(0.1)

        frequency = self.get_frequency()

        if (old_channel != channel):
            self.set_switcher_channel(old_channel)

        return frequency

    def get_wavelength(self):
        return_value = self.dll.GetFrequencyNum(ctypes.c_long(7), ctypes.c_double(0))
        return self._return_or_raise(return_value)

    @staticmethod
    def _return_or_raise(code):
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
