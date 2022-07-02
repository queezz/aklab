"""
Convertion modules for sensors in use.
"""


def pfeiffer_sg(signal):
    """
    Calculate pressure in Tors (Pa) from Pfeiffer cold cathode Single Gauge. 
    It seems that coefficients are slightly off, tune them for better results.

    `IdealVac Controller TPG361 docs <https://www.idealvac.com/files/brochures/TPG-361a.pdf>`_

    `IdealVac Controller TPG261 docs <https://www.idealvac.com/files/brochures/Pfeiffer_Single_Gauge_TPG261.pdf>`_

    `How to clean the Gauge <https://youtu.be/BiyPY4dFH_s>`_
    
    `IdealVac Gauge docs <https://www.idealvac.com/files/brochures/Pfeiffer_PKR_251_Pirani_ColdCathode.pdf>`_

    Parameters
    ----------
    signal: np.array
        Gauge analogue signal.
    """
    return 10 ** (1.667 * signal - 11.46)


def ionization_gauge(signal, exponent, log=False):
    """
    Calculate pressure in Tors (Pa) from 
    Bayard-alpert ionization vacuum gauge.
    A controller usually has two modes: linear and log outputs.
    In linear mode older converters do not ouotput exponent power, 
    so it must be provided.
    """
    if not log:
        return signal * 10 ** exponent

    # Look up formula for log-scale in the manual.


def hall_sensor(signal):
    """
    Convert Hall-effect current sensor signal to Amps.
    An Arduion or Raspberry Pi sensor based on ACS712
    or a similar chip. 

    Parameters
    ----------
    signal: np.array
        analogue hall-sensor signal
    """
    return 5 / 1 * (signal - 2.52)
