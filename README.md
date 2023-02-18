# Bookworm Reader/Speller
## Plays Bookworm Adventures 1 and 2. Reads the game board, finds the longest possible word, and attacks the enemy with that word.

### Reading Letters
![bookwormGif2](https://user-images.githubusercontent.com/60581053/219832218-ad66381c-6b44-40a5-a461-1262a8e31175.gif)


### Spelling Word
![bookwormGifSpell](https://user-images.githubusercontent.com/60581053/219839062-530425de-de09-4b55-accc-a98fd125b306.gif)

## How does it work?
This program uses image recognition to read the game board. I've gathered screenshots of individual tiles, and the program compares those screenshots to the current game board.

#### Example Board
![exampleBoard](https://user-images.githubusercontent.com/60581053/219835979-3ae9c70c-4572-4811-9bc0-6fb52e3acdd2.png)


### Letter Reading Process
1. Find Locked Tiles\
Locked tiles are tiles which have been constrained by the enemy, and we cannot use them. The program identifies these tiles by clicking on every tile in the board. If a tile does not move (stays the same color), it must be a locked tile.\
![locked-7ejGoL2VB-transformed](https://user-images.githubusercontent.com/60581053/219839978-19753470-6b68-410a-93ef-9ef3e5785f22.png)

2. Find Abnormal Tiles\
Abnormally colored tiles interfere with the image recognition this program relies upon. The gem tiles have a pulsing animation which bleeds into other tiles, so we want to remove them from the board and read the standard tiles in isolation. This results in more consistent readings.

3. Image Comparison\
The program compares many tiles at once, so it usually finishes reading the board in 30 seconds or fewer. The program generates a list of possible letters, then assigns them a position on a virtual letter board. The program sorts these potential letters by confidence, then adds as many as it can.

### Example Reading from the Above Board
Note: Format is ((letter, confidence), column, row)
<pre>
INFO:root:((j, 1.0), 0, 3)
INFO:root:((e, 0.99), 3, 0)
INFO:root:((r, 0.99), 1, 0)
INFO:root:((a, 0.97), 2, 0)
INFO:root:((n, 0.97), 2, 1)
INFO:root:((y, 0.97), 0, 1)

INFO:root:Trying to add letter 'j' in position [0, 3]
INFO:root:            Counted letter 1
INFO:root:

[  '-'  '-'  '-'  '-' ]
[  '-'  '-'  '-'  '-' ]
[  '-'  '-'  '-'  '-' ]
[  'j'  '-'  '-'  '-' ]
[  --   --   --   --  ]
[  --   --   --   --  ]
[  --   --   --   --  ]
[ 1.00  --   --   --  ]

INFO:root:Trying to add letter 'e' in position [3, 0]
INFO:root:            Counted letter 2
INFO:root:
[  '-'  '-'  '-'  'e' ]
[  '-'  '-'  '-'  '-' ]
[  '-'  '-'  '-'  '-' ]
[  'j'  '-'  '-'  '-' ]

[  --   --   --  0.99 ]
[  --   --   --   --  ]
[  --   --   --   --  ]
[ 1.00  --   --   --  ]
</pre>
... etc.

In turn, this list of letters was created by the following checks:
<pre>
DEBUG:root:checking a with confidence 0.95...
DEBUG:root:checking b with confidence 0.95...
DEBUG:root:     Appended ['a', 2, 0]!
DEBUG:root:checking a with confidence 0.96...
DEBUG:root:checking d with confidence 0.95...
DEBUG:root:checking c with confidence 0.95...
DEBUG:root:checking e with confidence 0.95...
DEBUG:root:checking f with confidence 0.95...
DEBUG:root:checking g with confidence 0.95...
DEBUG:root:checking h with confidence 0.95...
DEBUG:root:Removed duplicate in readLetterImproved() ['a', 2, 0]!
DEBUG:root:checking a with confidence 0.97...
DEBUG:root:checking i with confidence 0.95...
DEBUG:root:checking j with confidence 0.95...
DEBUG:root:checking k with confidence 0.95...
DEBUG:root:checking l with confidence 0.95...
DEBUG:root:checking m with confidence 0.95...
DEBUG:root:checking n with confidence 0.95...
DEBUG:root:Letter a may reside in position (2, 0)
DEBUG:root:Confidence in letter a: 0.97
DEBUG:root:checking o with confidence 0.95...
DEBUG:root:checking p with confidence 0.95...
DEBUG:root:checking q with confidence 0.95...
DEBUG:root:     Appended ['e', 3, 0]!
DEBUG:root:checking e with confidence 0.96...
DEBUG:root:checking r with confidence 0.95...
DEBUG:root:checking s with confidence 0.95...
DEBUG:root:checking t with confidence 0.95...
DEBUG:root:checking u with confidence 0.95...
DEBUG:root:checking v with confidence 0.95...
DEBUG:root:checking w with confidence 0.95...
DEBUG:root:checking x with confidence 0.95...
DEBUG:root:     Appended ['j', 0, 3]!
DEBUG:root:checking j with confidence 0.96...
DEBUG:root:checking y with confidence 0.95...
DEBUG:root:checking z with confidence 0.95...
DEBUG:root:     Appended ['n', 2, 1]!
DEBUG:root:checking n with confidence 0.96...
DEBUG:root:Removed duplicate in readLetterImproved() ['e', 3, 0]!
DEBUG:root:checking e with confidence 0.97...
DEBUG:root:     Appended ['r', 1, 0]!
DEBUG:root:checking r with confidence 0.96...
DEBUG:root:Removed duplicate in readLetterImproved() ['j', 0, 3]!
DEBUG:root:checking j with confidence 0.97...
DEBUG:root:     Appended ['y', 0, 1]!
DEBUG:root:checking y with confidence 0.96...
DEBUG:root:Removed duplicate in readLetterImproved() ['n', 2, 1]!
DEBUG:root:checking n with confidence 0.97...
DEBUG:root:Removed duplicate in readLetterImproved() ['e', 3, 0]!
DEBUG:root:checking e with confidence 0.98...
DEBUG:root:Removed duplicate in readLetterImproved() ['r', 1, 0]!
DEBUG:root:checking r with confidence 0.97...
DEBUG:root:Letter n may reside in position (2, 1)
DEBUG:root:Confidence in letter n: 0.97
DEBUG:root:Removed duplicate in readLetterImproved() ['j', 0, 3]!
DEBUG:root:checking j with confidence 0.98...
DEBUG:root:Removed duplicate in readLetterImproved() ['y', 0, 1]!
DEBUG:root:checking y with confidence 0.97...
DEBUG:root:Letter y may reside in position (0, 1)
DEBUG:root:Confidence in letter y: 0.97
DEBUG:root:Removed duplicate in readLetterImproved() ['e', 3, 0]!
DEBUG:root:checking e with confidence 0.99...
DEBUG:root:Removed duplicate in readLetterImproved() ['r', 1, 0]!
DEBUG:root:checking r with confidence 0.98...
DEBUG:root:Letter e may reside in position (3, 0)
DEBUG:root:Confidence in letter e: 0.99
DEBUG:root:Removed duplicate in readLetterImproved() ['j', 0, 3]!
DEBUG:root:checking j with confidence 0.99...
DEBUG:root:Removed duplicate in readLetterImproved() ['r', 1, 0]!
DEBUG:root:checking r with confidence 0.99...
DEBUG:root:Letter r may reside in position (1, 0)
DEBUG:root:Confidence in letter r: 0.99
DEBUG:root:Removed duplicate in readLetterImproved() ['j', 0, 3]!
DEBUG:root:checking j with confidence 1.0...
DEBUG:root:Letter j may reside in position (0, 3)
DEBUG:root:Confidence in letter j: 1.0
</pre>
This particular example generated the following board:
<pre>
[  '-'  'r'  'a'  'e' ]
[  'y'  'n'  'n'  'r' ]
[  'u'  's'  'o'  'e' ]
[  'j'  'q'  'j'  'o' ]

[  --  0.99 0.97 0.99 ]
[ 0.97 0.79 0.97 0.99 ]
[ 0.87 0.93 0.63 0.99 ]
[ 1.00 0.65 0.98 0.63 ]

Took 34.7019077 seconds to read the board

Took 0.0731749999999991 seconds to run regex, removing 150630 words
List shortened to 751 words long
INFO:root:Took 0.015470800000002782 seconds to analyze remaining items, removing 340 words
Took 0.17113460000000202 seconds to find the longest word
</pre>
