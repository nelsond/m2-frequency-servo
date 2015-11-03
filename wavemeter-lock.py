from WLM import WLM
from M2 import M2
from PID import PID
import time

# Channel number on wavemeter multiplexer
CHANNEL = 7

# IP address and port for M2 control
M2_ADDR = ('128.138.107.135', 39933)

# IP address of the computer running this script
HOST_ADDR = '128.138.107.101'

# Frequency setpoint [THz]
FREQ_SETPOINT = 368.54265

# Frequency to resonator tune percentage [THz/%]
FREQ_TO_TUNE = 266.e-6

# Default, aximum and minimum resonator tune percentage [%]
DEFAULT, MAX, MIN = 50., 80., 20.

# Digits for feedback on resonator tune
PRECISION = 4

# Duration between discrete ticks of the PID [s]
STEP_DURATION = 10

wlm = WLM(channel=CHANNEL)
m2  = M2(M2_ADDR)
pid = PID(
        setpoint=FREQ_SETPOINT,
        prop_gain=2.5e-1/FREQ_TO_TUNE,
        int_gain=5e-2/FREQ_TO_TUNE,
        diff_gain=0.0/FREQ_TO_TUNE)

if (m2.connect_from(HOST_ADDR)):
    try:
        while True:
            start_time = time.clock()

            try:
                current_freq = wlm.get_frequency()
                feedback = pid.tick(current_value=current_freq) + DEFAULT

                if feedback > MAX: feedback = MAX
                if feedback < MIN: feedback = MIN

                feedback = round(feedback, PRECISION)

                if (m2.set('tune_resonator', feedback)):
                    print 'error %.3f MHz, feedback %.4f' % ((FREQ_SETPOINT-current_freq)*1e6, feedback)
                else:
                    print 'Error (M2): Couldn\'t set tune resonator value'

            except Exception, e:
                print 'Error (Wavemeter): %s' % e
                pass

            elapsed_time = (time.clock() - start_time)

            print "%.2f ms" % (elapsed_time*1e3)

            time.sleep(STEP_DURATION-elapsed_time)

    except KeyboardInterrupt:
        m2.close_connection()

else:
    raise Exception('Error (M2): Can\'t connect')
