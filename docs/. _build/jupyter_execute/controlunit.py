#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('run', '../aklab/controlunit.py')
raspi = Raspi(bpath='../data',timestamp='20210219_124135')
raspi.plot()


# In[2]:


fmt = {"date": lambda t: t.strftime("%y%m%d %H:%M:%S"),'pd':'{:.1e}','pu':'{:.1e}'}
raspi.df_adc.head().style.format(fmt, precision=1)


# In[3]:


raspi.df_tc.head().style.format(fmt,precision=1)

