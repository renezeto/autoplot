Autoplot v0.1 (old, stable)
========
Autoplot is a small python program for efficiently creating report quality plots from instrument data. It allows for easier access to matplotlib callss, while keeping a faster workflow by avoiding using a GUI. Instead of a GUI, Autoplot uses a config/jobs file, which it will read and process to generate the desired plots. An example is given below:

    data="scope_data/filter_lp.CSV" xlabel="Frequency (Hz)" ylabel="Signal strength (dB)" xscale="log" yscale="log" title="Low pass filter transmission function." "plot_kwargs": "{'color':'r'}"
    data="scope_data/filter_hp.CSV" xlabel="Frequency (Hz)" ylabel="Signal strength (dB)" xscale="log" yscale="log" title="High pass filter transmission function." "plot_kwargs": "{'color':'b'}"
    
    data="resistance_data/ohmtest.CSV" xlabel="Voltage (V)" ylabel="Current (A)" title="Testing Ohm's law for a 5 kOhm carbon film resistor." theory="x/5000"
    

