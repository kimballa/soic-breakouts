# Panelization script for SOIC / TSSOP breakouts
#
# 0. Finish updating the main PCB.
# 1. Edit the parameters in the 'configuration section' at the top of this file
# 2. Open a KiCad Command Prompt to this dir
# 3. Run `python panelize.py`. This will write to the output file (out\soic.kicad_pcb) 
#    which you can then open with `start pcbnew out\soic.kicad_pcb` to generate Gerbers.


from kikit.units import *
from kikit.panelize import Panel, extractSourceAreaByAnnotation, Origin
from pcbnewTransition.pcbnew import (LoadBoard, VECTOR2I, BOX2I)
from shapely.geometry import (LineString, box)

import os
import os.path
import sys

### CONFIGURATION SECTION ###
#
# Adjust these to make the script do what you want.

# File to read input boards from
IN_FILENAME="soic breakouts.kicad_pcb"

# File to save to.
OUT_FILENAME = "out\\tssop.kicad_pcb"

# Position of the (0, 0) board in the output drawing sheet
START_X = 50*mm
START_Y = 50*mm

# Pick one set.
SOIC_BOARD_REFS = ["B1","B2","B3"]
TSSOP_BOARD_REFS = ["B4","B5","B6"]
BOARD_REFS = TSSOP_BOARD_REFS  

NUM_COLS = 8

# TITLE = "SOIC 8/14/16 breakout rev 2"
TITLE = "TSSOP 8/14/16 breakout rev 2"

FOOTER = "JLCJLCJLCJLC"

# Airgap between columns
COL_SPACE = 2*mm

# Ht of top/bottom edge rails.
RAIL_THICKNESS = 5*mm

# mouse bite size config
BITE_WIDTH = 5*mm
BITE_DIA = 0.5*mm
BITE_SPACING = 0.7*mm
BITE_PROLONG = 2*mm
TAB_SIZE = 2*mm # height of mouse-bitten spacer between adj. boards


### End configuration section ###

print(f"Creating panel from board references: {BOARD_REFS}")

out_dir = os.path.dirname(OUT_FILENAME)
if out_dir:
	os.makedirs(out_dir, exist_ok=True)

panel = Panel(OUT_FILENAME)

# Determine the bounding boxes of the sub-boards we want to include.
board_in = pcbnew.LoadBoard(IN_FILENAME)

# src_areas are the bounding boxes of the subboards in the same order as BOARD_REFS.
src_areas = []
for ref in BOARD_REFS:
	area = extractSourceAreaByAnnotation(board_in, ref)
	src_areas.append(area)


cur_col_x = START_X
cur_row_y = START_Y

next_col_x = -1
next_row_y = -1

for c in range(0, NUM_COLS):
	# Add boards to panel stacked in a column. 
	for r in range(0, len(BOARD_REFS)):
		print(f"Adding board col={c} row={r}")
		ref = BOARD_REFS[r]
		src_area = src_areas[r]

		# Add each board to panel 
		# Returns the bounding box (BOX2I) in the new panel board.
		bb = panel.appendBoard(filename=IN_FILENAME,
			destination=pcbnew.VECTOR2I(cur_col_x, cur_row_y),
			sourceArea=src_area,
			origin=Origin.TopLeft,
			tolerance=2*mm)

		next_row_y = max(cur_row_y, max(next_row_y, bb.GetBottom()))
		next_col_x = max(cur_col_x, max(next_col_x, bb.GetRight()))

		# Add spacer tab substrate below this board
		board_ctr_x = int((bb.GetRight() - bb.GetLeft()) / 2 + bb.GetLeft())
		x1 = int(board_ctr_x - BITE_WIDTH/2)
		y1 = bb.GetBottom()
		x2 = int(board_ctr_x + BITE_WIDTH/2)
		y2 = bb.GetBottom() + TAB_SIZE
		panel.appendSubstrate(box(x1, y1, x2, y2))

		# Add mouse bite between the board and the spacer.
		cut = LineString([[x1, int(bb.GetBottom() - BITE_DIA/4)], [x2, int(bb.GetBottom() - BITE_DIA/4)]])
		panel.makeMouseBites([cut], BITE_DIA, BITE_SPACING, prolongation=BITE_PROLONG)

		if r > 0:
			# We're in the 2nd row or beyond; add the mouse bite at the top
			# of the board.
			top_y = bb.GetTop()
			cut = LineString([[x1, int(top_y - 3 * BITE_DIA / 4)], [x2, int(top_y - 3 * BITE_DIA / 4)]])
			panel.makeMouseBites([cut], BITE_DIA, BITE_SPACING, prolongation=BITE_PROLONG)
		else:
			# In the top row, add a spacer above the board, to connect
			# to the top frame rail with a mouse bite.
			top_y = bb.GetTop()
			panel.appendSubstrate(box(x1, top_y - TAB_SIZE, x2, top_y))
			
			cut = LineString([[x1, int(top_y - 3 * BITE_DIA / 4)], [x2, int(top_y - 3 * BITE_DIA / 4)]])
			panel.makeMouseBites([cut], BITE_DIA, BITE_SPACING, prolongation=BITE_PROLONG)

		cur_row_y = next_row_y + TAB_SIZE
		next_row_y = -1

	cur_col_x = next_col_x + COL_SPACE
	cur_row_y = START_Y  # Reset to top of next column.
	next_col_x = -1


# Final polish
print("Finishing up...")

# If we just add the automatic rails directly, it gets confused about the board substrate
# chunks we added above the top-most row for mouse-bite purposes, and fuses them all together.
# Manually add a small full-width header above that.
final_x = cur_col_x - COL_SPACE # the iterator above left us positioned for a col we didn't render.
header_box = box(START_X, int(START_Y - TAB_SIZE - 0.5 * mm), final_x, START_Y - TAB_SIZE)
panel.appendSubstrate(header_box)

panel.makeRailsTb(thickness=RAIL_THICKNESS)

(panel_min_x, panel_min_y, panel_max_x, panel_max_y) = panel.panelBBox()
ctr_x = int((panel_max_x - panel_min_x) / 2 + panel_min_x)

panel.addCornerFiducials(fidCount=4, horizontalOffset=6*mm,
	verticalOffset=3.85*mm,
	copperDiameter=1*mm, openingDiameter=2*mm)
panel.addCornerTooling(holeCount=4, 
	horizontalOffset=3*mm, verticalOffset=2.5*mm,
	diameter=2*mm)
panel.addMillFillets(millRadius=int(0.55*mm))


panel.addText(TITLE, VECTOR2I(ctr_x, int(panel_min_y + 2.5*mm)))
panel.addText(FOOTER, VECTOR2I(ctr_x, int(panel_max_y - 2.5*mm)), 
	width=1*mm, height=1*mm, thickness=int(0.15*mm))


#panel.debugRenderBoundingBoxes()
#panel.debugRenderBackboneLines()
#panel.debugRenderPartitionLines()

# Commit the output
print(f"Saving output board: {OUT_FILENAME}")
panel.save(refillAllZones=True)

if panel.hasErrors():
	print("Error: the panel has recorded at least one error:\n")
	for err in panel.errors:
		print(err)
	
	sys.exit(1)

print("Finished!")