Result Analyser (Website)
=========================
**Author**  - Ashish Nitin Patil

**Created** - 24/06/2013

**Licence** - Creative Commons Attribution 4.0 Unported License.

### IMPORTANT ###

The college publicly displays the results which is not quite right.

Not everyone is as open as one wants to be. Respect that. Please.

### Notes ###
- Use Python 2.7.x for site rendering (GAE), for everything else use 3.x.
- Highcharts v3.0.2
- Result pdfs have image garbage (black highlighted text, Notepad++) at about posn 2%-5% of the pdf which needs to be removed.

### Project Summary ###
The ResAnalyser.py extracts data from result pdfs in the Results folder.

It then stores it systematically (json format) in txt files.

main.py is the main Google App Engine server app.

The Url Handlers fetch reqd. data & render it in the html templates.
