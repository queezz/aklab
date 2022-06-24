Module aklab.qulee
==================
"Qulee" (pronounced as "KLEE"), is ULVAC's latest model for residual gas analysis. 

Tools to work with Qulee mass spectrometer outputs (CSV) and maybe later with Qulee software?
Created 2021/06/11 by queezz

Functions
---------

    
`customgrid(ax, **kws)`
:   

    
`customticks(ax)`
:   

    
`generate_colors(masslist, **kws)`
:   Generate colors based on masslist

    
`plot_qms_dir(dir='', ls=[], out='batch_qms_plot.pdf', **kws)`
:   Provided dir, reads all converted Quelee *.csv's and plots into a PDF
    ls: list of absolute paths to files to plot
        OR
    dir: directory to scan and plot
    out: output pdf file name or absolute path
    ext = kws.get('ext','CSV')
    figsize = kws.get('figsize',500)
    anchor= kws.get('anhcor',[1,1])
    rasterized = kws.get('rasterized',True)
    ylim = kws.get('ylim',[1e-14,1e-5])

    
`t2s(t)`
:   Converts QMS timing into seconds.

    
`t2sa(ta)`
:   convert an array of strings of the Qulee format: '000:00:00.625' to time in seconds.
    '000:00:00.625' -> 'hhh:mm:ss.ms'

    
`tocsv(filename, **kws)`
:   Convert native binary into csv with Quelee software installed.

Classes
-------

`QMS(datapath)`
:   Class for reading, processing, and storing Qulee QMS data

    ### Methods

    `generate_colors(self)`
    :   Generate colors based on masslist

    `load_data(self)`
    :   Return qms data with proper datetime column for time
        1. parse header using qms_file_parser
        2. read csv file
        Convert time
        3. convert qms time format from '000:00:00.00' to
        a) seconds and append to dataframe, and
        b) proper datetime object with correct time and date

    `plot(self, **kws)`
    :   plot time traces
        kws:
        masslist: specify list of masses to plot. Plots all by default.
        from: starting time, self.start by default.
        to: ending time, self.end by default
        ylim: axis ylims
        gridalpha: transparancy of the grid lines

    `qms_file_parser(self)`
    :   " Given filepath to ULVAC's Qulee BGM QMS file, converted to *.csv,
        Parses the header, extracts column names, QMS settings, and line number where data starts