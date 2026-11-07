RONGPAT STUDIO - YOUR LIBRARY
=============================

Everything the app can draw comes from libraries, not from the code, so you can change the bible at any time.

1) ADD YOUR OWN CHARACTER
   Put an .svg file or a transparent .png of the character standing (full body, feet at the bottom)
   into the "characters" folder. The file name becomes the name you type in the scene sheet,
   e.g. characters\dadu-2.svg  ->  type  dadu-2  in the Cast column.
   Optional: a .json file with the same name sets details, e.g. characters\dadu-2.json:
       { "name": "Dadu", "bn": "দাদু", "size": "adult", "description": "Grandfather with a cane" }
   size can be: adult, tall, kid, small-kid, big-animal, animal, small-animal, or a number (adult = 475).

   NEW in 1.2: draw it IN PARTS (groups named head, body, arm-left, arm-right, leg-left, leg-right)
   and the app rigs it automatically: arms do every move, legs walk, the head nods and talks.
   A single flat picture gets a simpler automatic rig (head nods/talks, body breathes and leans).

1b) ADD YOUR OWN OBJECT
   Put an .svg or transparent .png in the "props" folder (e.g. props\umbrella.svg). Optional props\umbrella.json:
       { "name": "Umbrella", "size": "large", "grip": "bottom" }
   Then use it in a scene: Cast "umbrella center", Actions "umbrella: in-hand haridas, throw haridas tuli @1".

2) ADD YOUR OWN PLACE
   Put an .svg, .png or .jpg (landscape is best, e.g. 1600x900) into the "places" folder.
   Optional .json: { "name": "Dadu's shop", "floor": 0.88 }   (floor = where feet stand, 0 = top, 1 = bottom)

3) UPDATE FROM THE BIBLE
   When the Rongpat bible changes, put the changed board files (.dc.html or .html) into "bible-import"
   and double-click "5 - Update Library". Characters and places with the same name are replaced by
   the new versions; everything else stays. Ask Claude for an "update pack" any time the bible changes:
   unzip it into this library folder and run "5 - Update Library".

4) UNDO
   Delete a file from this folder (and run "5 - Update Library") to go back to the built-in version.
