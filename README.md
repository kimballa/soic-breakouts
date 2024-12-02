
SOIC Breakouts
==============

Breakout boards for {8, 14, 16}-pin SOIC and TSSOP ICs
that fit in a standard DIP width on a breadboard.

The IC itself sits to the side of the pin headers rather than between them, to achieve a
narrow breakout board profile (10.3mm) that does not straddle an extra row of pins on one
or the other side of the breadboard centerline. 

A separate through-hole exists in each SOIC board, connected to the ground plane. Solder a
resistor leg or other thin wire from the `GND` hole to top of the header pin that
represents ground for the IC. (Or leave floating if there is no appropriate ground pin for
the IC.)


## Gerber files

The latest gerber files for submitting to a board fab are in the `rtm/` directory.

If submitting to JLCPCB, select 'panel by customer', 'number of designs' = 3. 

## Panelization

The main project file includes one of each representative breakout board. Panels with 8 of
each SOIC or 8 of each TSSOP format were generated using KiKit. If you change the main PCB
CAD file, you should then open a KiCad Command Prompt in this directory and run `python
panelize.py`. You can edit `panelize.py` first to set variables related to the output file
to generate. You need to edit the script to select B1-B3 (SOIC), or B4-B6 (TSSOP boards)
for panelization.

### Script notes:

The current layout (n=8) is intended to fit in the 100x100 mm area that offers the best
deal for JLCPCB, but you can extend wider. The script would need to be modified to include
more than one row of each board. The script also assumes that all boards are the same
width, and may misalign columns if not accounted-for in any future modification that
changes some of the board widths.
