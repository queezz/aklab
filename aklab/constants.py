"""
package constants
"""
import os

package_directory = os.path.dirname(os.path.abspath(__file__))


def torr_to_pa(pressure, verbose=True):
    """
    Convert pressure from Torr to Pa

    Parameters
    ----------
    pressure: float
        pressure in Torr
    verbose: bool
        True to print formatted result :.2e
    Returns
    -------
    pressure in Pa
    """
    from scipy.constants import torr

    pressure = pressure * torr  # in Pa
    if verbose:
        print(f"{pressure:.2e} Pa")
    return pressure
