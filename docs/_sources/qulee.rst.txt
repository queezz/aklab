.. _intro_chapter:

=====================================================
Qulee QMS parsing and converting
=====================================================

Use :class:`~aklab.qulee.QMS` to read a converted `*.csv` QMS file.

.. jupyter-execute::
     
    from aklab.qulee import QMS
    qms = QMS('../data/S1_210208_131938.CSV')
    qms.plot()

.. jupyter-execute::
         
    fmt = {i:'{:.1e}' for i in qms.data.keys()[4:]}
    qms.data.head(5).style.format(fmt)

Use :meth:`~aklab.qulee.QMS.slice` to get a portion of the data.

.. jupyter-execute::
     
    from datetime import datetime as dt
    sliced = qms.slice([dt(2021,2,8,13,19,40),dt(2021,2,8,13,19,41)])
    sliced.style.format(fmt,precision=2) 