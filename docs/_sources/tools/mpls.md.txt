---
file_format: mystnb
kernelspec:
  name: python3
otherkey1: val1
otherkey2: val2
---
# Matplotlib Tools

## Examples

All in one

```{code-cell} ipython3
import matplotlib.pyplot as plt
from aklab import mpls as akmp
akmp.font_setup(size=14)
fig, axs = plt.subplots(3, 1)
fig.set_size_inches(akmp.set_size(500, ratio=1))
plt.subplots_adjust(top=0.99, bottom=0.01, hspace=0.3, wspace=0.1)

akmp.ticks_visual(axs[0])
akmp.grid_visual(axs[1])
txt = f"$x={akmp.ltexp(1.23e29)}$"
axs[2].text(0.5, 0.5, txt,transform=axs[2].transAxes, ha="center")
plt.gcf().set_facecolor('w')
```
### {func}`~aklab.mpls.figprep`

```{code-cell} ipython3
akmp.font_setup(size=6)
akmp.figprep(200,subplots=[3,1],dpi=100,ratio=2)
plt.gcf().set_facecolor('w')
```