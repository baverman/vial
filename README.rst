Vial editor
###########

What about snaked?
==================

I've realized I'll never reimplement even a small subset of VIM features.

Snaked is good for me for its action contexts and overall feel. But
gtksourceview… It suits only for notepad clones. Painfully slow, creepy
syntax highlight spec, unusable buffer/view separation.

More over there is a bunch of excellent plugins for VIM. I want to have this
functionality in my editor but have no time.


Why not just GVIM?
==================

I want fancy GUI popups and ability to extend editor in normal language.


Do you know about PIDA and a8?
==============================

Yeah. These projects try to bury VIM power under feeble decorations.


What Vial is and what it is not
===============================

Features which will be borrowed from snaked:
--------------------------------------------

- Sessions and projects.

- Actions menu.

- External tools.

- Quick open dialog.

- Outline dialog.

Integration with VIM:
---------------------

- Per-session VIM settings.

- xptemplate.

- Omni-completion.

- Buffer list.

- Window list.

- High level python api.

- Console, python repl and test runner will be implemented as usual vim buffers
  So one can arrange them in any window layout. 

- (?) Supplement will provide omnifunc for plain VIM users. 

That's all.
