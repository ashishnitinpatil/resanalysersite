Result Analyser (Website)
=========================

**Author**  - Ashish Nitin Patil<br>
**Created** - 24/06/2013<br>
**Licence** - Creative Commons Attribution 4.0 Unported License.

### Important ###
-----------------
The college publicly displays the results which is not quite right.<br>
Not everyone is as open as one wants to be. Respect that. Please.

### Notes ###
-------------
- Use Python 2.7.x for site rendering (GAE), for everything else use 3.x.
- Highcharts v3.0.2
- Result pdfs have image garbage (black highlighted text, Notepad++) at about posn 2%-5% of the pdf which needs to be removed.

### Project Summary ###
-----------------------
The `ResAnalyser.py` extracts data from result pdfs in the Results folder.<br>
It then stores it systematically (json format) in txt files.<br>
`main.py` is the main Google App Engine server app.<br>
The Url Handlers fetch reqd. data & render it in the html templates.
