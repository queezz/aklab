.. _controlunit:

=====================================================
Controlunit
=====================================================

Use :class:`~aklab.controlunit.Raspi` to read ADC and TC datafiles.

.. code-block::
    :caption: ADC convertion in :func:`~aklab.controlunit.Raspi.convert_signals`

        # 11.46 convert Pfeiffer signal to pressure
        self.pu = 10 ** (1.667 * self.adc["P2"] - 11.46)
        # convert linear IG signal to pressure
        self.pd = self.adc["P1"] * 10 ** self.adc["IGscale"]
        # plasma current from hall sensor
        def iconv(v):
            return 5 / 1 * (v - 2.52)

        self.ip = iconv(self.adc["Ip"])
        self.t = self.adc["date"]

.. jupyter-execute::
     
    %run ../aklab/controlunit.py
    raspi = Raspi(bpath='../data',timestamp='20210219_124135')
    raspi.plot()

:class:`~aklab.controlunit.Raspi` contains two separate :class:`pandas.DataFrame` with ADC and TC data.

.. jupyter-execute::

    fmt = {"date": lambda t: t.strftime("%y%m%d %H:%M:%S"),'pd':'{:.1e}','pu':'{:.1e}'}
    raspi.df_adc.head().style.format(fmt, precision=1)

.. jupyter-execute::

    raspi.df_tc.head().style.format(fmt,precision=1)    