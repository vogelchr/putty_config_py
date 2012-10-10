putty_config_py
===============

Short command-line utility to handle putty configuration (stored in the windows registry).

My main use-case is to programmatically change the font/size for all
putty sessions that are configured.

Usage:

	C:\Users\cvogel\Programs>python putty_config.py --list
	6 session(s) in total.
		com1_19200
		com7_115200
		Default%20Settings
		linux
		sc-linux-20120606
		tort

	C:\Users\cvogel\Programs>python putty_config.py --list "li*"
	6 session(s) in total, 1 match filter "li*".
		linux

	C:\Users\cvogel\Programs>python putty_config.py --get Font "com*"
	6 session(s) in total, 2 match filter "com*".

	Session              Parameter Font
	--------------------:----------------------------------------
	com1_19200           Source Code Pro
	com7_115200          Source Code Pro

	C:\Users\cvogel\Programs>python putty_config.py --set Font=Courier "com*"
	6 session(s) in total, 2 match filter "com*".
	Updating parameter 'Font' to value 'Courier'.
		com1_19200          : ok
		com7_115200         : ok
	No command given. Maybe you should try --help?

