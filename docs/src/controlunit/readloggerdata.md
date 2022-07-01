---
file_format: mystnb
kernelspec:
  name: python3
otherkey1: val1
otherkey2: val2
---
# Read Logger Data

Use {class}`~aklab.controlunit.Raspi` to read ADC and TC datafiles.

```{code-cell} ipython3
from aklab.controlunit import Raspi
raspi = Raspi(bpath='../../../data',timestamp='20210219_124135')
raspi.plot()
```

# Signal conversion

```python
# 11.46 convert Pfeiffer signal to pressure
self.pu = 10 ** (1.667 * self.adc["P2"] - 11.46)
# convert linear IG signal to pressure
self.pd = self.adc["P1"] * 10 ** self.adc["IGscale"]
# plasma current from hall sensor
def iconv(v):
    return 5 / 1 * (v - 2.52)

self.ip = iconv(self.adc["Ip"])
self.t = self.adc["date"]
```

# Data format

{class}`~aklab.controlunit.Raspi` contains two separate {class}`pandas.DataFrame` with ADC and TC data.


```{code-cell} ipython3
fmt = {"date": lambda t: t.strftime("%y%m%d %H:%M:%S"),'pd':'{:.1e}','pu':'{:.1e}'}
raspi.df_adc.head().style.format(fmt, precision=1)
```

```{code-cell} ipython3
raspi.df_tc.head().style.format(fmt,precision=1)    
```