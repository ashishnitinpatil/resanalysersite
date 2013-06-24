#-------------------------------------------------------------------------------
# Name:        Result Analyser (Website)
#
# Author:      Asis aka !mmorta!
#
# Created:     24/06/2013
#
# Licence:     Creative Commons Attribution 3.0 Unported License.
#-------------------------------------------------------------------------------

# Want to join in on the development? Great!
# Email me - cool_asis_is@yahoo.in

IMPORTANT -
# The college publicly displays the results which is not quite right.
# Not everyone is as open as one wants to be. Respect that. Please.

Notes -
# Python version 2.7.x
# Require Highcharts javascript files. (And ofcourse Result pdfs / analysed txts)
# Result pdfs need to be UTF-8 converted, then patch of garbage (black highlighted text, Notepad++)
# is to be removed (found at about posn 2%-5% of the pdf). (Else gives decode error in reading)

Project Summary -
# The ResAnalyser.py extracts data from result pdfs in the Results folder.
# It then stores it systematically (json) in 3 txt files.
# The main.py is the app that runs on the GAE server, rendering reqd. data accordingly.
# The Url Handlers fetch reqd. data & render it in the html templates.

Guidelines for newbs -
# Backup is something everyone MUST have.
# PyScripter is a great IDE, use it for editing python code.
# The ResAnalyser.py is tried to be kept as current as possible (with relevant changes).
# Help yourself, if you can't move on even after a few hours, seek !mmorta!'s help.
# Things have been tried to be kept simple. Do the same.
# Happy open sourcing! :)
