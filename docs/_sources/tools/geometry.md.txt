---
file_format: mystnb
kernelspec:
  name: python3
otherkey1: val1
otherkey2: val2
---

# Geometry

## Examples


```{code-cell} ipython3
import matplotlib.pylab as plt
%matplotlib inline
import numpy as np
from aklab.mpls import vec, plot_circ
```

```{code-cell} ipython3
l = 400
d = 40
a = d*np.sqrt(2)
ax = plt.gca()
x = (l-2*d)/np.sqrt(2)
vec(0,x,c='r')
vec(x,x+a)
vec(x+a,x+a+l*np.exp(1j*np.pi/4*3),c='k')
vec(x,x+(l-2*d)*np.exp(1j*np.pi/4*3),c='k')
vec(0, 1j*(x+a),c='gold')
vec(1j*(d), 1j*d + x-d,c='C0')

plot_circ(r=d,o=x-d+1j*d,ls='-.',c='C2')
ax.set_aspect('equal')
```

```{code-cell} ipython3
from aklab.mpls import show_analog_time
show_analog_time(6,5,r=1,o=np.pi*3/2+0.5j)
x = np.linspace(0,np.pi*2,50)
plt.plot(x,np.sin(x),'C1')
```