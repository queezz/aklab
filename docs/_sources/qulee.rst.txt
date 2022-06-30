.. _qms:

=====================================================
Qulee QMS
=====================================================

Read and plot
-------------

Use :class:`~aklab.qulee.QMS` to read a converted `*.csv` QMS file.

.. jupyter-execute::
     
    from aklab.qulee import QMS
    qms = QMS('../data/S1_210208_131938.CSV')
    qms.plot()

Data formatting
---------------

Data is formatted as in this example. :code:`.iloc[:,:8]` is used to reduce the output table size.

.. jupyter-execute::
         
    fmt = {i:'{:.1e}' for i in qms.data.keys()[4:]}
    fmt['date'] = lambda t: t.strftime("%y%m%d %H:%M:%S")
    qms.data.head(5).iloc[:,:8].style.format(fmt,precision=2)

Use :meth:`~aklab.qulee.QMS.slice` to get a portion of the data.

.. jupyter-execute::
     
    from datetime import datetime as dt
    sliced = qms.slice([dt(2021,2,8,13,19,40),dt(2021,2,8,13,19,41)])
    sliced.iloc[:,:8].style.format(fmt,precision=2)