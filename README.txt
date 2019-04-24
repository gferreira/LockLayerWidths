Lock Glyph Layers
=================

A tool to lock layer widths while editing glyphs in RoboFont.

Introduction
------------

- use this tool to keep layer widths in synch while designing
- the tool does not ‘correct’ different layer widths automatically. it just observes any changes to glyph widths and propagates them to the other layers

Workflow
--------

1. Open the dialog, and choose a lock mode.

2. If glyph-level mode: use the buttons to lock/unlock selected glyphs. A lock icon will be shown for glyphs with locked layer widths (in Glyph Window, Font Overview and Space Center).

3. When the width of a glyph changes (in any layer), the new width is copied to all other layers of the glyph.

At the moment it is still necessary to keep the dialog open all the time while editing, which is not very practical. This will change soon.

Modes
-----

### All unlocked

Default RoboFont 3 behavior. The tool is off, all glyph layer widths can be edited independently.

### All locked

Replicates RoboFont 1 behavior: all layers of a glyph have the same width. This is a global setting for all glyphs in all fonts.

When the width of a glyph changes (in any layer), the new width is copied to all other layers of the glyph.

### Glyph-level locks

This mode introduces a glyph-level lock setting, so that some glyphs can have layer widths locked, while others can remain unlocked.
