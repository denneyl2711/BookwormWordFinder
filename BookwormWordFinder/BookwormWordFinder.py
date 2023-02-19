#The goal of this program is to read a 4x4 grid of letters on the screen, find the longest possible word from those letters, and click those letters
#This program is designed to be compatible with both Bookworm Adventures 1 and 2, although it is more reliable with the second version
#The program reads letters using image recognition from PIL/pyautogui, or with manual user input

#How does the letter reading work?
    #The program takes advantage of pyautogui's variable tolerance when searching for images.
    #This program contains screenshots of each letter a-z, so the program compares the current game board to screenshots of those letters
    #In short, program checks each letter at the same confidence, only clicking the letter if it is relatively confident is is correct
    #Program creates a list of letters in order of confidence, then clicks the most confident ones
    #For more details, visit readLettersImproved() and readLetterImproved()

#What have you done to make the letter-reading process more reliable?
    #1. Searching for "abnormal tiles"
        #Gems, smashed tiles, burning tiles, and other abnormal tiles interfere with the image recognition process, especially when they animate.
            #ex. Gems have a pulsing animation which bleeds into other tiles
        #To counteract this, abnormal tiles are clicked by the program so the 'normal' tiles can be read in isolation.
        #For more details, see clickAbnormalTiles() and readGrid()
    #2. List of potential letters
        #When reading letters, the program creates a list of letters it may click.
        #It stores the letter, its confidence in that letter, and its position on the board
            #ex. ('a', 0.84, 1, 2), ('y', 0.73, 3, 3), ('b', 0.72, 3, 1), ('o', 0.70, 1, 2)
        #Then, the program adds letters to its game board and clicks the letters on the screen.
        #In this case, the program would add, 'a', 'y', and 'b' while clicking those respective spots on screen.
        #This would generate the following board

            #[  '-'  '-'  '-'  '-' ]
            #[  '-'  'a'  '-'  '-' ]
            #[  '-'  '-'  '-'  '-' ]
            #[  '-'  'b'  '-'  'y' ]

            #[ 1.00 0.84 1.00 1.00 ]
            #[ 1.00 1.00 1.00 1.00 ]
            #[ 1.00 1.00 1.00 1.00 ]
            #[ 1.00 0.72 1.00 0.73 ]
        #Notice how 'o' was not added. This is because it was predicted to reside in the same place as 'a', which the program had higher confidence in.
        #Therefore, that letter was removed from the list of potential letters
        #For more details, see readLettersImproved() and readLetterImproved()


#Word dictionary for Bookworm Adventures 1 taken from https://github.com/FarukIb/word-unscrambler
    #NOTE: BOOKWORM ADVENTURES 2 USES A DIFFERENT DICTIONARY. THERE IS OVERLAP BETWEEN THE TWO BUT IT IS NOT A PERFECT MATCH
#List of 3,000 most common English words taken from https://www.ef.edu/english-resources/english-vocabulary/top-3000-words/
#List of all English words taken from https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt

import re
import random
import pyautogui
import keyboard
from pynput.keyboard import Listener, KeyCode
import win32api
import win32con
from pynput.mouse import Controller, Button
from threading import Thread
import time
import logging
import copy

import concurrent.futures
from multiprocessing.pool import Pool

# cv2.cvtColor takes a numpy ndarray as an argument
import numpy as nm
import pytesseract
# importing OpenCV
import cv2
from PIL import ImageGrab

logging.basicConfig(level = logging.DEBUG)
#INFO prints out board states as the program reads the board, 
    #also the number of words removed while searching for longest word
    #also miscellaneous info which is only printed a few times

#DEBUG prints out individual letter confidences as it tries to read them
    #also info for the 2d color array in checkForLocked(info for the 2d color array in checkForLocked())

WORD_LENGTH_MAX = 16
WORD_LENGTH_MIN = 3
WORD_SOURCE = "bookwormWords.txt"

ASCII_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"

PRINTED_WORDS = 10 #prints this many words in the console (beginning of list of longest words)
TIME_BETWEEN_ATTACKS = 0.1

    
#count number of each letter in a word
#ex. "Salads" would have ('s', 2), ('a', 2), ('l', 1), ('d', 1)
#this class is used to help find the longest possible word
class LetterAndCount:
    count = 0
    letter = '-'

    def __init__(self, letter, count):
        self.count = count
        self.letter = letter

    def __lt__(self, other):
        return self.letter < other.letter

    def __str__(self):
        return f"({self.letter}, {self.count})"

class Tile:
    confidence = 0
    letter = '-'
    def __init__(self, *args):
       if len(args) == 0:
           self.confidence = 0
           self.letter = '-'

       else:
           if isinstance(args[0], Tile):#if tile is argument
               tile = args[0]
               self.letter = tile.get_letter()
               self.confidence = tile.get_confidence()

           if isinstance(args[0], str) and (isinstance(args[1], float) or isinstance(args[1], int)):#if (letter, confidence) is argument
               self.letter = args[0]
               self.confidence = args[1]
       

    def get_letter(self):
        return self.letter
   
    def get_confidence(self):
        return self.confidence

    def set_letter(self, letter):
        self.letter = letter

    def set_confidence(self, confidence):
        self.confidence = confidence

    def __lt__(self, other):
        return self.confidence < other.confidence

    def __str__(self):
        return f"Letter is {self.letter}, confidence is {self.confidence}."
    
    def __repr__(self):
        return f"({self.letter}, {self.confidence})"

   

class LetterBoard:
    def __init__(self, *args):
        self.board = [[Tile() for i in range(4)] for j in range(4)]

        if args:
            if isinstance(args[0], str):
                lettersQueue = []
                letters = args[0]
                letters = fixQsInString(letters)
                    
                for letter in letters:
                    lettersQueue.append(letter)

                
                for i in range(4):
                    for j in range(4):
                        if lettersQueue:#if list is not long enough, append '-' chars to the end
                            self.board[i][j] = Tile(lettersQueue.pop(0), 1)

                        else:
                            self.board[i][j] = Tile('-', 0)

    def __str__(self):
        output = ""
        for row in range(4):
            output += "[ "
            for col in range(4):
                output += f" '{self.board[row][col].get_letter()}' "
            output += "]\n"
        output += '\n'
        for row in range(4):
            output += "[ "
            for col in range(4):
                if self.board[row][col].get_confidence() == 0:
                    output += " --  "
                else:
                    output += "{:.2f}".format(self.board[row][col].get_confidence()) + ' '
            output += "]\n"
        return output

    def get_letters(self):
        letters = ""
        for i in range(4):
            for j in range(4):
                if self.board[i][j].letter != '-':
                    letters+= self.board[i][j].letter

        return letters

def load_dictionary():
    with open(WORD_SOURCE) as word_file:
        semi_valid_words = set(word_file.read().split())
        valid_words = set()

        for word in semi_valid_words:
            if len(word) <= WORD_LENGTH_MAX and len(word) >= WORD_LENGTH_MIN:
                valid_words.add(word)

    return valid_words

def setup(autoInput, boardLetters):
    global english_words
    english_words = load_dictionary()

    
    if autoInput == None:
        boardLetters = input("Enter all 16 letters: --> ")
    else:
        boardLetters = autoInput

    #remove '-' from string, which indicate locked tiles or other tiles which won't be used
    #put this into regex but not other places
    tempBoardLetters = ""
    
    wildTile = False

    for letter in boardLetters:
        if letter != '-':
            if letter == '?':
                wildTile = True
            else:
                tempBoardLetters = tempBoardLetters + letter

    start = time.perf_counter()
    num_removed = 0
    if not wildTile:
        pattern = r'^[' + tempBoardLetters + ']+$'
        regex = re.compile(pattern)

        pre_size = len(english_words)
        filtered_words = list(filter(regex.search, english_words))
        post_size = len(filtered_words)
        num_removed += pre_size - post_size
    else:
        filtered_words = list()
        #run the same test 26 times with the ? being replaced with a new letter every time
        #note: if the letter is q, need to insert both a q and a u                            
        
       
        for letter in ASCII_LOWERCASE:
            if letter != 'q':
                pattern = r'^[' + tempBoardLetters + letter + ']+$'
            else:
                pattern = r'^[' + tempBoardLetters + letter + 'u' + ']+$'

            regex = re.compile(pattern)

            pre_size = len(english_words)
            temp_filtered_words = list(filter(regex.search, english_words))
            post_size = len(temp_filtered_words)
            num_removed += pre_size - post_size

            temp_filtered_words.sort(key =len, reverse = True) #sort by length, longer words first

            while len(temp_filtered_words) > 500:
                del temp_filtered_words[-1]
                #num_removed += 1

            #need to append another letter for every time the program loops through the ? list
            #then remove/decrement that letter at the end

            #Make tempLetterBoard using the letters (except for ?), then append each individual letter on every pass
            tempLetterBoard = LetterBoard(tempBoardLetters + letter)

            filtered_words = list(set(filtered_words) | set(temp_filtered_words))
            #print(f"list is now {len(filtered_words)} words long")

    end = time.perf_counter()
    print(f"Took {end-start} seconds to run regex, removing {num_removed} words")
        

    filtered_words.sort(key =len, reverse = True) #sort by length, longer words first

    while len(filtered_words) > 10000:
        del filtered_words[-1]

    print(f"List shortened to {len(filtered_words)} words long")

    return (filtered_words, boardLetters)

def verify_words_new(words, letterBoard):
    any_removed = True
    num_removed = 0

    start = time.perf_counter() 
    while any_removed:
        any_removed = False

        for word in words:
            if not verify_word_new(word, letterBoard):
                 words.remove(word)
                 any_removed = True
                 num_removed = num_removed + 1
    end = time.perf_counter()

    logging.info(f"Took {end-start} seconds to analyze remaining items, removing {num_removed} words")
    return num_removed

def verify_word_new(word, letterBoard):
    #essentially do the same process that the program does when actually spelling a word (with the LetterBoard). If it fails, remove the word
    origWord = word #store the original word so the word confidence print statement stays intact
    if 'q' in word:
        word = fixQsInString(word)

    letters = [*letterBoard.get_letters()]

         
    for letter in word: #Try to find letter, or '?' if that letter not found
        try:
            letters.remove(letter)
        except:
            try:
                letters.remove('?')
            except:
                return False
        
        
       
    return True

def findLongestWords(autoInput, boardLetters):
    filtered_words, boardLetters = setup(autoInput, boardLetters)
    tempLetterBoard = LetterBoard(boardLetters)

    #remove bad words from long list
    start = time.perf_counter()
    verify_words_new(filtered_words, tempLetterBoard)
    end = time.perf_counter()

    
    return (filtered_words, boardLetters)

#qu is stored as a single tile in the Bookworm Games, so this function helps deal with that
def fixQsInString(word):
    newWord = ""

    #if q then add q but not the next letter    

    avoidNext = False
    for letter in word:
        if not avoidNext:
            newWord = newWord + letter

        avoidNext = False

        if letter == 'q':
            avoidNext = True
    #don't need to worry about weird words with a q followed by a non-u because those aren't in the bookworm dictionary

    return newWord

def spellWord(word, letterBoard, inOrder):
    average_confidence = 0
    count = 0
    info = None
    list_of_clicks = []

    origWord = word #store the original word so the word confidence print statement stays intact
    if 'q' in word:
        word = fixQsInString(word)

    if inOrder:
        tempLetterBoard = copy.deepcopy(letterBoard)

        for letter in word:
            #find letter in tempLetterBoard, use coords to click letter, remove letter from tempLetterBoard

            #find the letter that has the highest confidence rating, then click that one
            mostConfidentLetter = getMostConfidentLetterGrid(letter, tempLetterBoard)

            if mostConfidentLetter[0] == '-':
                logging.warning("         NOT ENOUGH LETTERS!")    
                return (None, None)

            #mostConfidentLetter stores a tuple with (('letter', confidence), grid_x, grid_y)
            info = clickLetterWithCoords(mostConfidentLetter[1], mostConfidentLetter[2])
            list_of_clicks.append((info[0], info[1]))
            
            
    else:
        for letter in word:
            if letter not in letterBoard.get_letters():
                #TODO: PROGRAM BREAKS HERE FOR SOME MANUAL & UNORDERED INPUT
                    #I believe this is a qu issue
                info = clickLetterForce('?')
                print(f"letter {letter} not found, getting '?' instead")
                letter = letter.upper()
            else:
                info = clickLetterForce(letter)#info stores a tuple with (confidence rating, x position of click, y position of click)
            average_confidence = average_confidence + info[0]
            list_of_clicks.append((info[1], info[2]))

            #modify letterBoard
            grid_x, grid_y = clickToGrid(info[1], info[2])
            letterBoard.board[grid_y][grid_x] = Tile(letter, 1)

            count = count + 1


        average_confidence = average_confidence / count
        print ("Word confidence for " + origWord + ": " + str(average_confidence))

    list_of_clicks.sort()
    furthest_left_and_up = list_of_clicks[0]

    return (furthest_left_and_up)#return coordinates of last click as a tuple

def clickLetterForce(letter):
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    x_min, y_min, x_max, y_max, offset, step, SCALER = getBoundaries(gameType)
    if gameType == 1:
        append = ".png"

    if gameType == 2:
        append = "2.png"

    boundaries = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset)

    pos = None
    confidence_adjustment = 0

    if letter == '?':
       letter = "question"#have to make this change because you can't name a file '?2.png'
    
    letterName = letter + append

    while(pos == None):#forces it to find a letter, may click wrong letter
        logging.debug(f"checking {letter} with confidence {round(1.0 - confidence_adjustment, 2)}...")
        pos = pyautogui.locateOnScreen(letterName, region = boundaries, confidence = 1.0 - confidence_adjustment)
        confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check

    print("Confidence in letter " + letter + ": " + str(1.0 - confidence_adjustment))
    
    grid_x, grid_y = posToGrid(pos)
    new_pos_x, new_pos_y = gridToClick(grid_x, grid_y)

    logging.debug("(" + str(new_pos_x) + ", " + str(new_pos_y) + ")")
    logging.debug("      Conversion to grid points: (" + str(grid_x) + ", " + str(grid_y) + ")")
     
    mouseSetAndClick(new_pos_x, new_pos_y)
    return ((1.0 - confidence_adjustment, new_pos_x, new_pos_y))

def clickLetterMaybe(letter, min_confidence, locked_tile_positions): #will not click if the confidence rating is too low (0.8)
                                                    #baseline_confidence decreases gradually as the program loops over the same board multiple times
                                                    #with each pass, confidence decreases
                                                    #returns (confidence, pos_x, pos_y) as pixel values, not grid values 
                                                    #ex. (0.67, 356, 258)


    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    x_min, y_min, x_max, y_max, offset, step, SCALER = getBoundaries(gameType)

    if gameType == 1:
        append = ".png"#this is appened to the letter so the program can search for the file name

    if gameType == 2:
        append = ".png"#this is appened to the letter so the program can search for the file name

    boundaries = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset)

        
    if letter == '?':
        letter = "question"#have to make this change because you can't name a file '?2.png'

    letterName = letter + append
    confidence_adjustment = 0.9 - min_confidence

    if confidence_adjustment < 0:
        confidence_adjustment = 0

    #right side of this inequality determines how far the program goes before giving up
    #the higher the right side is, the further it allows its guesses to stray from the confidence
    pos = None
    while(1 - confidence_adjustment > min_confidence and pos == None):#DOES NOT have to click a letter
        logging.debug(f"checking {letter} with confidence {round(1.0 - confidence_adjustment, 2)}...")
        pos = pyautogui.locateOnScreen(letterName, region = boundaries, confidence = 1.0 - confidence_adjustment)

        if pos!= None:
            logging.debug(f"                Found letter {letter} with confidence {round(1.0 - confidence_adjustment, 2)}!")
            
        confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check

    if pos != None:
        letter_x_grid, letter_y_grid = posToGrid(pos)

        #if letter is on a locked tile, discard it
        if ((letter_x_grid, letter_y_grid)) in locked_tile_positions:
            logging.debug("         That's a locked tile!")
            return ((1.0 - confidence_adjustment, 0, 0)) #default return values

        else:
            logging.debug("Confidence in letter " + letter + ": " + str(1.0 - confidence_adjustment))
    
            mouseSetAndClick(new_pos_x, new_pos_y)#because window resizing does weird things
            return ((1.0 - confidence_adjustment, new_pos_x, new_pos_y))

    else:#did not find letter, return confidence and default position values
        return ((1.0 - confidence_adjustment, 0, 0))

def clickLetterWithCoords(grid_coord_x, grid_coord_y):

    click_x, click_y = gridToClick(grid_coord_x, grid_coord_y)

    mouseSetAndClick(click_x, click_y)

    return ((click_x, click_y))

def clearBoard():
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        coords = (570, 210)
    elif gameType == 2:
        coords = (980, 280)

    for _ in range(9):
        pyautogui.click(coords)

def attack(last_click_x, last_click_y):
    
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gametype = inGame()

    if gameType == 1:
        attackCoords = (520, 850)
        popupCoords = (600, 400)
        find_last_click = lambda c: round(c / 1.5)

    if gameType == 2:
        attackCoords = (950, 1100)
        popupCoords = (450, 300)#dummy values, version 2 has no popup if the user mispells words
                                #chose these values because they click on Lex, revealing an easter egg

        find_last_click = lambda c : round(c - 30) #-30 so the program checks the corner of the tile instead of the center
                                            #without this change, program would see the black of the letter instead of the tile color
    
    #clicks the attack button, doesn't always register for whatever reason...
    mouseSetAndClickCoords(attackCoords)
    mouseSetAndClickCoords(attackCoords)
    mouseSetAndClickCoords(attackCoords)

    
    #if cell is still empty after click, then the attack didn't work (word was misspelled), so return false
    adjusted_last_click_x = find_last_click(last_click_x)
    adjusted_last_click_y = find_last_click(last_click_y)


    mouseSetAndClickCoords(popupCoords) #sometimes there is a popup which you have to clear if you misspell too many words
    time.sleep(0.3)
    logging.info("Place of last click: --> ("  + str(adjusted_last_click_x) + ", " + str(adjusted_last_click_y) + ")")
    win32api.SetCursorPos((adjusted_last_click_x, adjusted_last_click_y))
    logging.info(f"Color detected: --> {(pyautogui.pixel(adjusted_last_click_x, adjusted_last_click_y))}")

    
    #empty cell is 15, 12, 0 rgb roughly
    #if cell is still empty after attack, then attack failed (board wasn't refilled with new letters)
    if pyautogui.pixelMatchesColor(adjusted_last_click_x, adjusted_last_click_y, (15, 12, 0), tolerance = 35):
        return False
    else:
        return True

def clickToGrid(click_x, click_y):#converts the click coordinates to indices for the 2d array
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        grid_x = round((click_x - 490) / 75)
        grid_y = round((click_y - 480) / 75)
    if gameType == 2:
        grid_x = round((click_x - 805) / 90) 
        grid_y = round((click_y - 600) / 85) 

    return ((grid_x, grid_y))

def gridToClick(grid_x, grid_y):
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        click_x = (75 * grid_x) + 470
        click_y = (75 * grid_y) + 480

    if gameType == 2:
        click_x = (78 * grid_x) + 835
        click_y = (85 * grid_y) + 610

    return ((click_x, click_y))

def posToGrid(pos):
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        SCALER = 1.5
    if gameType == 2:
        SCALER = 1

    center_pos = pyautogui.center(pos)
    new_pos_x, new_pos_y = center_pos

    new_pos_x = new_pos_x * SCALER
    new_pos_y = new_pos_y * SCALER

    letter_x_grid, letter_y_grid = clickToGrid(new_pos_x, new_pos_y)

    return (letter_x_grid, letter_y_grid)

def readGrid(letterBoard):#remove abnormal tiles, read the normal ones, then read the abnormal tiles
                            #abnormal tiles are removed because the gem tiles have an animation which bleeds into other tiles
                            #this bleeding effect intereferes with the image recognition for the other tiles
                            #(abnormal tiles are simply found using color values)
    #locate locked tiles
    locked_tile_positions = checkForLocked()
    print(f"Found {len(locked_tile_positions)} locked tiles from checkForLocked()")

    #locate abnormal tiles (gems, smashed tiles, etc) not including locked tiles
    #click these tiles
    clearBoard()

    abnormal_count = clickAbnormalTiles()
    letterCount = 0
    min_confidence = 0.85

    letterCount = readLettersImproved(letterBoard, min_confidence, letterCount, abnormal_count, locked_tile_positions)

    clearBoard()
    #remove the normal tiles before reading the gems
    if abnormal_count:
        for row in range(4):
            for col in range(4):
                #if tile has been read already, it must be a 'normal' tile. Has a confidence != 0
                if letterBoard.board[col][row].get_confidence() != 0:
                    clickLetterWithCoords(row, col)

    print("Before reading abnormal letters: ...")
    print(letterBoard)
    print()

   
    min_confidence = 0.75 #start at a lower confidence because abnormal tiles won't be recognized at higher confidences anyway
    readLettersImproved(letterBoard, min_confidence, letterCount, 0, locked_tile_positions)

    print(letterBoard)

    return locked_tile_positions, abnormal_count


def readLettersImproved(letterBoard, min_confidence, letterCount, abnormal_count, locked_tile_positions):#try to read letters at confidence .95, then 80,... etc.
                                        #if match, then decrease in confidence until no more match within that letter
                                        #should decrease the number of unneeded checks
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()


    while letterCount < 16 - abnormal_count - len(locked_tile_positions): #forces program to keep reading until board is full
                            #confidence in guess drops on every pass
       
        potentialTiles = []
                  
        items = [(letter, min_confidence, locked_tile_positions) for letter in ASCII_LOWERCASE + str((gameType - 1) * '?')]

        clickLockedTiles(locked_tile_positions)#click on locked tiles just in case some tiles were incorrectly labeled locked
        #move mouse out of the way of the image recognition
        win32api.SetCursorPos((30, 30)) 

        with Pool() as pool:
           for result in pool.starmap(readLetterImproved, items):
               if result!= None:
                   for tile in result:
                        potentialTiles.append(tile)

        #sort by confidence level and select the most confident
        potentialTiles.sort(reverse = True)
        for tile in potentialTiles:
            logging.info(tile)

        #if not potentialTiles:
        if len(potentialTiles) <= 2:
            logging.debug("                                             reducing confidence")
            min_confidence -= 0.1
        else:
            logging.debug("                                             not reducing confidence")

        while potentialTiles:
            first_tile = potentialTiles[0]
            tile = first_tile[0]

            tile_letter = tile.get_letter()
            tile_confidence = tile.get_confidence()
            grid_x, grid_y = first_tile[1], first_tile[2]

            logging.info(f"Trying to add letter '{tile_letter}' in position [{grid_x}, {grid_y}]")
                
            if not letterBoard.board[grid_y][grid_x].get_letter() == '-': #stops the program from reading the same letter over and over if a window is stopping it from clicking or something like that
                logging.warning("         Spot is taken!")
                potentialTiles.remove(first_tile)
                continue
            else:
                letterBoard.board[grid_y][grid_x] = Tile(tile_letter, tile_confidence)
                letterCount = letterCount + 1

                logging.info("            Counted letter " + str(letterCount))
                logging.info("\n" + letterBoard.__str__())
                clickLetterWithCoords(grid_x, grid_y)

                for potentialTile in potentialTiles:#remove letters which are on the same tile
                    if potentialTile[1] == grid_x and potentialTile[2] == grid_y:
                        potentialTiles.remove(potentialTile)

    return letterCount
        
def readLetterImproved(letter, min_confidence, locked_tile_positions):
    
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    x_min, y_min, x_max, y_max, offset, step, SCALER = getBoundaries(gameType)
    boundaries = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset)

    if gameType == 1:
        append = ".png"#this is appened to the letter so the program can search for the file name

    if gameType == 2:
        append = "2.png"#this is appended to the letter so the program can search for the file name

    confidence_adjustment = 0.9 - min_confidence

    if confidence_adjustment < 0:
        confidence_adjustment = 0

    orig_letter = letter
    if letter == '?':
        letter = "question"#have to make this change because you can't name a file '?2.png'
    letterName = letter + append

    pos = 1
    pos_list = []
    while(pos != None):#searches until it doesn't find a match
        logging.debug(f"checking {orig_letter} with confidence {round(1.0 - confidence_adjustment, 2)}...")
        pos = pyautogui.locateOnScreen(letterName, region = boundaries, confidence = 1.0 - confidence_adjustment)

        if pos!= None:
            #only add pos if it is not a duplicate of other ones
            pos_x_grid, pos_y_grid = posToGrid(pos)

            for position in pos_list:
                position_x_grid, position_y_grid = position

                if pos_x_grid == position_x_grid and pos_y_grid == position_y_grid:
                   logging.debug(f"Removed duplicate in readLetterImproved() ['{letter}', {pos_x_grid}, {pos_y_grid}]!")
                   break
            else:
                if not ((pos_x_grid, pos_y_grid)) in locked_tile_positions:
                    pos_list.append((pos_x_grid, pos_y_grid))
                    logging.debug(f"     Appended ['{letter}', {pos_x_grid}, {pos_y_grid}]!")

                else: #if letter is on a locked tile, discard it
                    logging.info("         That's a locked tile!")
                    break
        confidence_adjustment = confidence_adjustment - 0.01 #slowly decreases the confidence of the check

    if pos_list:
        final_pos_list = []
        for pos in pos_list:
            letter_x_grid, letter_y_grid = pos
            logging.debug(f"Letter {orig_letter} may reside in position ({letter_x_grid}, {letter_y_grid})")
            logging.debug("Confidence in letter " + letter + ": " + str(0.99 - confidence_adjustment))
            tile_adding = Tile(orig_letter, 0.99 - confidence_adjustment)
            final_pos_list.append((tile_adding, letter_x_grid, letter_y_grid))
                
        return final_pos_list

    else:#did not find letter
        return None

def checkForLocked():
    #loop through all grid tiles
    #then, if the color of the click spot is the same before and after the click, tile didn't move so it must be locked

    color2DArray = [[list((0, 0, 0)) for i in range (4)] for j in range(4)]

    locked_count = 0
    locked_points = []

    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    x_min, y_min, x_max, y_max, offset, step, SCALER = getBoundaries(gameType)
   

    if gameType == 1:
        find_x = lambda x : round((x * 1.5))
        find_y = lambda y : round((y * 1.5) + 50)

    if gameType == 2:
        find_x = lambda x : x - 12
        find_y = lambda y : y - 5
         #checkForLocked() boundaries are different because getBoundaries() gives boundaries slightly outside of the board
        x_min += 30
        y_min += 20
        x_max -= 50
        y_max -= 90

    col = 0#scan from top to bottom instead of left to right
    for y in range(y_min, y_max, step):
        row = 0
        for x in range(x_min, x_max, step):

            click_x = find_x(x)
            click_y = find_y(y)
            logging.debug("Entering info for cell (" + str(row) + " , " + str(col) + ")")
            color2DArray[col][row] = list((pyautogui.pixel(x, y)))
            logging.debug(f"color is {color2DArray[col][row]}")

            #win32api.SetCursorPos((click_x, click_y))
            #time.sleep(0.5)

            mouseSetAndClick(click_x, click_y)
            row = row + 1
        print()
        col = col + 1


    time.sleep(0.3)#program clicks so fast it needs to wait a bit before reading colors here


    col = 0
    for x in range(x_min, x_max, step):
        row = 0
        for y in range(y_min, y_max, step):
            #color = color2DArray[col][row] #remove the not in the color check below if choosing this color option
            color = (0, 0, 0)

            other_color = pyautogui.pixel(x, y)
            logging.info(f"  expected {color} and saw {other_color} in position (" + str(col) + ", " + str(row) + ")")

            if not pyautogui.pixelMatchesColor(x, y, (color), tolerance = 35):
                locked_count = locked_count + 1
                locked_points.append((col, row))
                print(f"Found locked tile in position (" + str(col) + ", " + str(row) + ")")
            row = row + 1
        col = col + 1

    return locked_points
    
def clickAbnormalTiles():#clicks on the tiles which are gems, plagued, smashed, or otherwise discolored
    abnormal_count = 0

    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    x_min, y_min, x_max, y_max, offset, step, SCALER = getBoundaries(gameType)

    

    if gameType == 1:
        find_x = lambda x : round((x * 1.5))
        find_y = lambda y : round((y * 1.5) + 50)

    if gameType == 2:
        find_x = lambda x : x
        find_y = lambda y : y 
        #abnormalTiles() boundaries are different because getBoundaries() gives boundaries slightly outside of the board
        x_min += 30
        y_min += 20
        x_max -= 50
        y_max -= 90

    for x in range(x_min, x_max, step):
        for y in range(y_min, y_max, step):
            click_x = find_x(x)
            click_y = find_y(y)

            win32api.SetCursorPos((click_x, click_y))
            #time.sleep(0.5)

            tile_color = 255, 235, 181
            if not pyautogui.pixelMatchesColor(x, y, (tile_color), tolerance = 60) and not pyautogui.pixelMatchesColor(x, y, (0, 0, 0), tolerance = 10):
                grid_x, grid_y = clickToGrid(click_x, click_y)
                print(f"Abnormal color found: {pyautogui.pixel(x, y)} in position ({grid_x}, {grid_y}) (tile color is {tile_color})")
                mouseSetAndClick(click_x, click_y)
                abnormal_count = abnormal_count + 1
    print(f"{abnormal_count} abnormal tiles")
    return abnormal_count

def getMostConfidentLetterGrid(letter, letterBoard):#return the grid location of the letter with the highest confidence
                                                    
    lettersToClick = []

    for col in range (4):
        for row in range(4):
            if letterBoard.board[col][row].get_letter() == letter:
                #print("letter " + letter + " in position (" + str(row) + ", " + str(col) + ")")
                
                #find the letter that has the highest confidence rating, then click that one
                lettersToClick.append((letterBoard.board[col][row], row, col))
            elif letterBoard.board[col][row].get_letter() == '?':
                lettersToClick.append((Tile(letter.upper(), 0.01), row, col))

    lettersToClick.sort(key = lambda x : x[0], reverse = True)

    #print("Potential letters: ")
    #print(lettersToClick)

    if not lettersToClick:
        return Tile()

    bestLetter = lettersToClick[0]
                    
    bestRow, bestCol = bestLetter[1], bestLetter[2]

    letterBoard.board[bestCol][bestRow] = Tile()

    return (bestLetter)

def clickLockedTiles(locked_tile_positions):
     #click on the locked tile positions just in case one was incorrectly read
    #this helps prevent the program from getting stuck on tiles it cannot read
    for pos in locked_tile_positions:
        x, y = pos
        clickLetterWithCoords(x, y)

def getFancyLetters(word):
    #load fancyLetters into []
    #fancyLetters are letter/count pairs
    #ex. if string is aaabccddddd then cooresponding pairs are (a, 3), (b, 1), (c, 2), (d, 5)

    fancyLetters = []
    for letter in word:
        for fancyLetter in fancyLetters:
            if fancyLetter.letter == letter:
                fancyLetter.count = fancyLetter.count + 1
                break

        else:
             fancyLetters.append(LetterAndCount(letter, 1))

    return fancyLetters

def inGame():
    #color of top left corner of Bookworm 1 is (115, 109, 90)
    #color of corner in the second edition is (0, 0, 0) because the game processes resolution differently 
               #(adds black bars but doesn't change resolution like 1st edition does)

    #so, find the color in location (270, 30) because this color always remains the same in the game (color of Lex's name, decorative)

    bookworm_1_color =(115, 109, 90)
    bookworm_2_color = (239, 178, 0)
    if pyautogui.pixelMatchesColor(0, 0, bookworm_1_color):
        return 1
    elif pyautogui.pixelMatchesColor(270, 30, bookworm_2_color, tolerance = 15):
        return 2
    else:
        #print(f"Color was {pyautogui.pixel(270, 30)}, expected (239, 178, 0)")
        return 0

def getBoundaries(gameType):
    if gameType == 1:
        x_min = 310
        y_min = 320

        x_max = 510
        y_max = 520

        offset = 20
        step = 50
        SCALER = 1.5

    if gameType == 2:
        x_min = 770
        y_min = 550

        x_max = 1150
        y_max = 950

        offset = 50
        step = 93
        SCALER = 1

    #return (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset)
    return (x_min, y_min, x_max, y_max, offset, step, SCALER)
def mouseSetAndClick(x, y):
    win32api.SetCursorPos((round(x), round(y)))

    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0 ,0)
    time.sleep(0.01)#in case the click is too fast
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0 ,0)

def mouseSetAndClickCoords(coords):
    x, y = coords
    mouseSetAndClick(x, y)



#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

def main():
    locked_tile_positions = []
    abnormal_count = -1

    letterBoard = LetterBoard()
    boardLetters = ""


    inOrder = True #if bot knows where every letter is on the board (assumed to be true if input is manual [and correct] or if info is automatically read)

    decision = input("Automatic or manual input? (0 or 1, respectively) --> ")

    if int(decision) == 1:
        manual = True
    else:
        manual = False

    if manual:
        filtered_words, boardLetters = findLongestWords(None, boardLetters)
       
        decision = input("Are the letters of the input in order? (0 for no, 1 for yes) --> ")

        if int(decision) == 0:
            inOrder = False
        
        #fill letterboard completely
        letterBoard = LetterBoard(boardLetters) #inOrder version also uses this board, but as a dummy version so it can read boardLetters

        print(letterBoard)
 

    else:#automated input
        print("Preparing automation...")

        gameType = inGame
        while not gameType:
            time.sleep(1)
            gameType = inGame()

        clearBoard()
        start1 = time.perf_counter()
        locked_tiles_positions, abnormal_count = readGrid(letterBoard)
        end1 = time.perf_counter()
        print(f"Took {end1 - start1} seconds to read the board\n\n")

        #remove '-' chars from input
        autoInput = ""
        for i in range(4):
            for j in range(4):
                if letterBoard.board[i][j].get_letter() != '-':
                    autoInput = autoInput + letterBoard.board[i][j].get_letter()

        start = time.perf_counter()
        filtered_words = findLongestWords(autoInput, boardLetters)[0]
        end = time.perf_counter()

        print(f"Took {end - start} seconds to find the longest word")

    print()
    
    #Print words and attack----------------------------------------------------------------------------

    #print the longest words (or all the words if the list is not that many words long)
    if len(filtered_words) >= PRINTED_WORDS:
        for i in range (PRINTED_WORDS):
            if i == 0:
                longest_word = filtered_words[i]
            print(filtered_words[i])

    else:
        for i in range(len(filtered_words)):
            print(filtered_words[i])


    success = False #variable tells if successful attack (word was spelled correctly)
    wordIndex = 0
    
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    numberOfAttempts = 0
    while not success:
        clearBoard()


        #attack, hope it works
        attack_word = filtered_words[wordIndex]
        print("Spelling word ----> " + attack_word)
        last_click_x, last_click_y = spellWord(attack_word, letterBoard, inOrder)

        #attack with a different word if it doesn't work
        wordIndex = wordIndex + 1
        numberOfAttempts = numberOfAttempts + 1

        if last_click_x is None:#move onto the next word if the current word cannot be spelled (only happens when ? word creation algorithm goes wrong)
            continue

        time.sleep(0.2)
        success = attack(last_click_x, last_click_y)

        time.sleep(TIME_BETWEEN_ATTACKS)
    
    
    logging.info(f"This board has {len(locked_tile_positions)} locked tiles and {abnormal_count} abnormal tiles")
    print()
    print("Attack successful! ----> " + attack_word)
    print(f"Took {numberOfAttempts} attempts")

#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

if __name__ == '__main__':
    main()
  
