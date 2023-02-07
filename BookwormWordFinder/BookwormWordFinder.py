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
    #1. Variable letter confidences
        #Particularly in Bookworm Adventures version 1, some letters are recognized more often than they should be.
        #To counteract this, these letters are manually given a lower priority/confidence when they are searched for.
        #For more details, see getLetterAdjustment() and clicking functions such as clickLetterMaybe() 
    #2. Searching for "abnormal tiles"
        #Gems, smashed tiles, burning tiles, and other abnormal tiles interfere with the image recognition process, especially when they animate.
            #ex. Gems have a pulsing animation which bleeds into other tiles
        #To counteract this, abnormal tiles are clicked by the program so the 'normal' tiles can be read in isolation.
        #For more details, see clickAbnormalTiles() and readGrid()
    #3. List of potential letters
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

import concurrent.futures
from multiprocessing.pool import Pool

# cv2.cvtColor takes a numpy ndarray as an argument
import numpy as nm
import pytesseract
# importing OpenCV
import cv2
from PIL import ImageGrab

logging.basicConfig(level = logging.INFO)

WORD_LENGTH_MAX = 16
WORD_LENGTH_MIN = 3
WORD_SOURCE = "bookwormWords.txt"

ASCII_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"

PRINTED_WORDS = 10 #prints this many words in the console (beginning of list of longest words)
TIME_BETWEEN_ATTACKS = 0.1

    
#count number of each letter
#this class is used to help find the longest possible word
class LetterAndCount:
    count = 0
    letter = '-'

    def __init__(self, letter, count):
        self.count = count
        self.letter = letter

    def __lt__(self, other):
        return self.letter < other.letter

    def to_string(self):
        return "Letter: " + self.letter + "\n" + "Count: " + str(self.count) + "\n"


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

    if not wildTile:
        pattern = r'^[' + tempBoardLetters + ']+$'
        regex = re.compile(pattern)

        filtered_words = list(filter(regex.search, english_words))
        
    else:
        filtered_words = list()
        #run the same test 26 times with the ? being replaced with a new letter every time
        #note: if the letter is q, need to insert both a q and a u                            
        fancyLetters = getFancyLetters(boardLetters) 
        
        num_removed = 0
        for letter in ASCII_LOWERCASE:
            if letter != 'q':
                pattern = r'^[' + tempBoardLetters + letter + ']+$'
            else:
                pattern = r'^[' + tempBoardLetters + letter + 'u' + ']+$'

            regex = re.compile(pattern)
            temp_filtered_words = list(filter(regex.search, english_words))

            temp_filtered_words.sort(key =len, reverse = True) #sort by length, longer words first

            while len(temp_filtered_words) > 500:
                del temp_filtered_words[-1]
                num_removed = num_removed + 1

            #need to append another letter for every time the program loops through the ? list
            #then remove/decrement that letter at the end

            for fancyLetter in fancyLetters:
                if fancyLetter.letter == letter:
                    fancyLetter.count = fancyLetter.count + 1
                    break
            else:
                fancyLetters.append(LetterAndCount(letter, 1))

            verify_words(temp_filtered_words, fancyLetters)

            for fancyLetter in fancyLetters:
                if fancyLetter.letter == letter:
                    if fancyLetter.count == 1:
                        fancyLetters.remove(fancyLetter)
                    else:
                        fancyLetter.count = fancyLetter.count - 1
                    break


            filtered_words = list(set(filtered_words) | set(temp_filtered_words))
            #print(f"list is now {len(filtered_words)} words long")

        end = time.perf_counter()
        print(f"Took {end-start} seconds to run regex and take out {num_removed} words")
        

    filtered_words.sort(key =len, reverse = True) #sort by length, longer words first

    while len(filtered_words) > 10000:
        del filtered_words[-1]

    print(f"List shortened to {len(filtered_words)} words long")

    return (filtered_words, boardLetters)

def verify_word(word, fancy_letter):
    letter_count = 0
    for letter in word:
        if letter == fancy_letter.letter:
            letter_count = letter_count + 1

        if letter_count > fancy_letter.count:
            return False
    
    return True

def verify_words(words, fancyLetters):
    any_removed = True
    num_removed = 0

    while (any_removed):
        any_removed = False
        
        for word in words:
            for fancy_letter in fancyLetters:
                if not verify_word(word, fancy_letter) and word in words:
                    words.remove(word)
                    any_removed = True
                    num_removed = num_removed + 1

                    break

def verify_words_new(words, letterBoard):
    any_removed = True
    num_removed = 0

    while any_removed:
        any_removed = False

        for word in words:
            if not verify_word_new(word, letterBoard):
                 words.remove(word)
                 any_removed = True
                 num_removed = num_removed + 1

    logging.info(f"Removed {num_removed} items while analyzing words")

def verify_word_new(word, letterBoard):
    #essentially do the same process that the program does when actually spelling a word. If it fails, remove the word
    origWord = word #store the original word so the word confidence print statement stays intact
    if 'q' in word:
        word = fixQsInString(word)

    #don't want to change the inputted letterBoard, so create a copy
    tempLetterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                       [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                       [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                       [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]

    for row in range(4):
        for col in range(4):
            tempLetterBoard[col][row] = letterBoard[col][row]

    for letter in word:
        #find the letter that has the highest confidence rating, then click that one
        mostConfidentLetter = getMostConfidentLetterGrid(letter, tempLetterBoard)

        try:
            letter, grid_x, grid_y = mostConfidentLetter

        except:
            #logging.debug(f"Removed the word {word} while analyzing words")    
            return False

        tempLetterBoard[grid_y][grid_x] = list(('-', 0))
    return True


def findLongestWord(autoInput, boardLetters):
    filtered_words, boardLetters = setup(autoInput, boardLetters)

    #contains LetterAndCount objects, so letter:num pairs
    #ex. string "aabbbc" would have be (a, 2), (b, 3), (c, 1)

    fancyLetters = getFancyLetters(boardLetters)    
    fancyLetters.sort()

    #TODO: THIS IS REPEATED CODE
    tempLetterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                           [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                           [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                           [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]
    lettersQueue = []
    tempBoardLetters = fixQsInString(boardLetters)
    for i in tempBoardLetters:
        lettersQueue.append(i)
    
    for i in range(4):
        for j in range(4):
            if lettersQueue:#if list is not long enough, append '-' chars to the end
                tempLetterBoard[i][j][0] = lettersQueue.pop(0)
                tempLetterBoard[i][j][1] = 1

            else:
                tempLetterBoard[i][j][0] = '-'
                        
    #remove words from long list
    start = time.perf_counter()
    verify_words_new(filtered_words, tempLetterBoard)
    end = time.perf_counter()

    
    return (filtered_words, boardLetters)

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

    

    #if letter has a q in it, change the string to remove the u's right after q's
    #ex. quest ---> qest             aquaqueick ---> aqaqeick
    origWord = word #store the original word so the word confidence print statement stays intact
    if 'q' in word:
        word = fixQsInString(word)

    if inOrder:
        #TODO: DON'T THINK I NEED A TEMP LETTERBOARD ANYMORE, NEED TO VERIFY
        #don't want to change the inputted letterBoard, so create a copy
        tempLetterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                           [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                           [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                           [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]

        for row in range(4):
            for col in range(4):
                tempLetterBoard[col][row] = letterBoard[col][row]

        for letter in word:
            #find letter in tempLetterBoard
            #use coords to click letter
            #remove letter from tempLetterBoard

            #print(letter)

            #find the letter that has the highest confidence rating, then click that one
            mostConfidentLetter = getMostConfidentLetterGrid(letter, tempLetterBoard)

            if mostConfidentLetter[0] == '-':
                #list_of_clicks.sort()
                #furthest_left_and_up = list_of_clicks[0]
                logging.warning("         NOT ENOUGH LETTERS!")    
                return (None, None)

            #mostConfidentLetter stores a tuple with (('letter', confidence), grid_x, grid_y)
            info = clickLetterWithCoords(mostConfidentLetter[1], mostConfidentLetter[2])
            list_of_clicks.append((info[0], info[1]))
            
            
    else:
        for letter in word:
            info = clickLetterForce(letter)#info stores a tuple with (confidence rating, x position of click, y position of click)
            average_confidence = average_confidence + info[0]
            list_of_clicks.append((info[1], info[2]))

            #modify letterBoard
            grid_x, grid_y = clickToGrid(info[1], info[2])
            letterBoard[grid_y][grid_x] = list((letter, 1))

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

    if gameType == 1:
        x_min = 310
        y_min = 320

        x_max = 510
        y_max = 520

        offset = 20
        append = "Clear.png"
        SCALER = 1.5

    if gameType == 2:
        x_min = 650
        y_min = 470

        x_max = 1300
        y_max = 1160

        offset = 50
        append = "2Clear.png"
        SCALER = 1


    pos = None
    confidence_adjustment = 0
    
    letterName = letter + append
    #TODO: REMOVE REPETITION HERE
    while(pos == None):#forces it to find a letter, may click wrong letter
        logging.debug(f"Checking with confidence {1 - confidence_adjustment}")
        pos = pyautogui.locateOnScreen(letterName, region = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset), confidence = 1.0 - confidence_adjustment)
        confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check
    print("Confidence in letter " + letter + ": " + str(1.0 - confidence_adjustment))
    
    center_pos = pyautogui.center(pos)
    new_pos_x, new_pos_y = center_pos

    new_pos_x = new_pos_x * SCALER
    new_pos_y = new_pos_y * SCALER

    print("(" + str(new_pos_x) + ", " + str(new_pos_y) + ")")

    point_x, point_y = clickToGrid(new_pos_x, new_pos_y)
    print("      Conversion to grid points: (" + str(point_x) + ", " + str(point_y) + ")")
     
    mouseSetAndClick(new_pos_x, new_pos_y)
    return ((1.0 - confidence_adjustment, new_pos_x, new_pos_y))

def clickLetterMaybe(letter, min_confidence, locked_tile_positions): #will not click if the confidence rating is too low (0.8)
                                                    #baseline_confidence decreases gradually as the program loops over the same board multiple times
                                                    #with each pass, confidence decreases
                                                    #returns (confidence, pos_x, pos_y) as pixel values, not grid values 
                                                    #ex. (0.67, 356, 258)


    #TODO: REMOVE REPETITION HERE
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        x_min = 310
        y_min = 320

        x_max = 510
        y_max = 520

        offset = 20
        SCALER = 1.5
        append = "Clear.png"#this is appened to the letter so the program can search for the file name


    if gameType == 2:
        x_min = 770
        y_min = 550

        x_max = 1150
        y_max = 950

        offset = 50
        SCALER = 1
        append = "2Clear.png"#this is appened to the letter so the program can search for the file name


    #problem_adjustment is a skewing done because some letters are recognized more often / less often than they should be
    #program very commonly confuses i's for t's, etc without this adjustment
    problem_adjustment = getLetterAdjustment(letter)
    
    if letter == '?':
        letter = "question"#have to make this change because you can't name a file '?2.png'

    letterName = letter + append
    pos = None
    confidence_adjustment = 0.9 - (min_confidence - problem_adjustment)

    if confidence_adjustment < 0:
        confidence_adjustment = 0

    #right side of this inequality determines how far the program goes before giving up
    #the higher the right side is, the further it allows its guesses to stray from the confidence

    while(1 - confidence_adjustment + problem_adjustment > min_confidence and pos == None):#DOES NOT have to click a letter
        logging.debug(f"checking {letter} with confidence {round(1.0 - confidence_adjustment, 2)}...")
        pos = pyautogui.locateOnScreen(letterName, region = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset), confidence = 1.0 - confidence_adjustment)

        if pos!= None:
            logging.debug(f"                Found letter {letter} with confidence {round(1.0 - confidence_adjustment, 2)}!")
            
        confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check

    if pos != None:
       #TODO: REMOVE REPETITION AND CLEAN UP PRINT STATEMENTS 
        center_pos = pyautogui.center(pos)
        new_pos_x, new_pos_y = center_pos

        new_pos_x = new_pos_x * SCALER
        new_pos_y = new_pos_y * SCALER

        letter_x_grid, letter_y_grid = clickToGrid(new_pos_x, new_pos_y)
        #print("Letter resides in position (" + str(letter_x_grid) + ", " + str(letter_y_grid) + ")")

        #if letter is on a locked tile, discard it
        if ((letter_x_grid, letter_y_grid)) in locked_tile_positions:
            #print("         That's a locked tile!")
            return ((1.0 - confidence_adjustment, 0, 0)) #default return values

        else:
            #print("Confidence in letter " + letter + ": " + str(1.0 - confidence_adjustment))
    
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
        popupCoords = (450, 300)#dummy values, this game has no popup if the user mispells words
                                #chose these values because they click on Lex, revealing an easter egg

        find_last_click = lambda c : round(c - 30) #so the program checks the corner of the tile instead of the center
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
    #TODO: SOMETIMES BREAKS BECAUSE GEMS SPILL INTO THE AREA WHICH IT CHECKS
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
    letterCount = 0
    min_confidence = 0.90
    loopCount = 0

    #locate locked tiles
    locked_tile_positions = checkForLocked()
    print("Found " + str(len(locked_tile_positions)) + " locked tiles from checkForLocked()")

    #locate abnormal tiles (gems, smashed tiles, etc) not including locked tiles
    #click these tiles
    clearBoard()
    abnormal_count = clickAbnormalTiles()

    letterCount, loopCount = readLettersImproved(letterBoard, min_confidence, loopCount, letterCount, abnormal_count, locked_tile_positions)

    clearBoard()
    #remove the normal tiles before reading the gems
    if abnormal_count:
        for row in range(4):
            for col in range(4):
                #if tile has been read already, it must be a 'normal' tile. Has a confidence != 0
                if letterBoard[col][row][1] != 0:
                    clickLetterWithCoords(row, col)

    print("Before reading abnormal letters: ...")
    printListLetterBoard(letterBoard)
    print()

    min_confidence = 0.9

    #click on the locked tile positions just in case one was incorrectly read
    #this helps prevent the program from getting stuck on tiles it cannot read
    for pos in locked_tile_positions:
        x, y = pos
        clickLetterWithCoords(x, y)
    
    loopCount = readLettersImproved(letterBoard, min_confidence, loopCount, letterCount, 0, locked_tile_positions)[1]


    #print(f"Took {loopCount} loops to fill the board")

    printListLetterBoard(letterBoard)

    return locked_tile_positions, abnormal_count

def readLetters(letterBoard, min_confidence, loopCount, letterCount, abnormal_count, locked_tile_positions):
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    while letterCount < 16 - abnormal_count - len(locked_tile_positions): #forces program to keep reading until board is full
                            #confidence in guess drops on every pass, intended to account for gems distorting the image
        for letter in ASCII_LOWERCASE + str((gameType - 1) * '?'):#sloppy but it works, doesn't check for ? in Bookworm 1
            if letterCount >= 16 - abnormal_count - len(locked_tile_positions):
                break
            points, confidence_list = readLetter(letter, min_confidence, locked_tile_positions)#points holds all the places (pixel positions) where this letter is found 

            pointIndex = 0
            for point in points:
                grid_x, grid_y = clickToGrid(point[0], point[1]) #fill board with predicted letters from read function
                
                logging.info(f"Trying to add point [{grid_x}, {grid_y}]")
                
                if not letterBoard[grid_y][grid_x][0] == '-': #stops the program from reading the same letter over and over if a window is stopping it from clicking or something like that
                    logging.info("         Spot is taken!")
                    break
                else:
                    letterBoard[grid_y][grid_x][0] = letter
                    letterBoard[grid_y][grid_x][1] = round(confidence_list[pointIndex], 2)

                    pointIndex = pointIndex + 1
                    letterCount = letterCount + 1

                    logging.info("            Counted letter " + str(letterCount))
                    logging.info("\n" + letterBoardString(letterBoard))

        min_confidence = min_confidence - 0.1 #gradually reduce confidence in guesses
        loopCount = loopCount + 1

    return (letterCount, loopCount)

def readLetter(letter, confidence_adjustment, locked_tile_positions):
    findingLetters = True
    points_list = []#list of all the points where this letter exists
    confidence_list = []

    while findingLetters and len(points_list) <= 16:#len argument because otherwise it gets stuck searching for letters when confidence is super low
        info = clickLetterMaybe(letter, confidence_adjustment, locked_tile_positions) #info holds (confidence, pixel_x, pixel_y) where [1] and [2] are locations of the letter
        findingLetters = info[1] #if x val is 0 (default value), no letter has been found
        if info[1] != 0:
            confidence_list.append(info[0])
            points_list.append((info[1], info[2]))

    return ((points_list, confidence_list))#return the list of points and their respective confidence ratings

#----
def readLettersImproved(letterBoard, min_confidence, loopCount, letterCount, abnormal_count, locked_tile_positions):#try to read letters at confidence .95, then 80,... etc.
                                        #if match, then decrease in confidence until no more match within that letter
                                        #should decrease the number of unneeded checks
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    min_confidence = 0.9

    while letterCount < 16 - abnormal_count - len(locked_tile_positions): #forces program to keep reading until board is full
                            #confidence in guess drops on every pass, intended to account for gems distorting the image
        potentialLetters = []
        for letter in ASCII_LOWERCASE + str((gameType - 1) * '?'):#sloppy but it works, doesn't check for ? in Bookworm 1 
            infos = readLetterImproved(letter, min_confidence, locked_tile_positions)
            if infos:
                for info in infos:
                    potentialLetters.append(info)

        #sort by confidence level and select the most confident
        potentialLetters.sort(key = lambda x : x[1], reverse = True)
        for letter in potentialLetters:
            logging.info(letter)

        if not potentialLetters:
            logging.debug("                                             reducing confidence")
            min_confidence -= 0.1
        else:
            logging.debug("                                             not reducing confidence")

        while potentialLetters:
            firstLetter = potentialLetters[0]
            letter = firstLetter[0][0]
            letter_confidence = firstLetter[1]
            grid_x, grid_y = firstLetter[2], firstLetter[3]

            for potentialLetter in potentialLetters:#remove letters which are on the same tile
               if potentialLetter[2] == grid_x and potentialLetter[3] == grid_y:
                   potentialLetters.remove(potentialLetter)

            logging.info(f"Trying to add letter '{letter}' in position [{grid_x}, {grid_y}]")
                
            if not letterBoard[grid_y][grid_x][0] == '-': #stops the program from reading the same letter over and over if a window is stopping it from clicking or something like that
                logging.warning("         Spot is taken!")
                continue
            else:
                letterBoard[grid_y][grid_x][0] = letter
                letterBoard[grid_y][grid_x][1] = round(letter_confidence, 2)

                letterCount = letterCount + 1

                logging.info("            Counted letter " + str(letterCount))
                logging.info("\n" + letterBoardString(letterBoard))
                clickLetterWithCoords(grid_x, grid_y)


           

    return (letterCount, loopCount)
        

def readLetterImproved(letter, min_confidence, locked_tile_positions):
    
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        x_min = 310
        y_min = 320

        x_max = 510
        y_max = 520

        offset = 20
        append = "Clear.png"#this is appened to the letter so the program can search for the file name


    if gameType == 2:
        x_min = 770
        y_min = 550

        x_max = 1150
        y_max = 950

        offset = 50
        append = "2.png"#this is appended to the letter so the program can search for the file name

    problem_adjustment = getLetterAdjustment(letter)
    confidence_adjustment = 0.9 - (min_confidence - problem_adjustment)

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
        pos = pyautogui.locateOnScreen(letterName, region = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset), confidence = 1.0 - confidence_adjustment)

        if pos!= None:
            #only add pos if it is not a duplicate of other ones
            pos_x_grid, pos_y_grid = posToGrid(pos)

            for position in pos_list:
                position_x_grid, position_y_grid = position

                if pos_x_grid == position_x_grid and pos_y_grid == position_y_grid:
                   logging.debug("Removed duplicate in readLetterImproved()!")
                   break
                   pass
            else:
                pos_list.append((pos_x_grid, pos_y_grid))
        confidence_adjustment = confidence_adjustment - 0.01 #slowly decreases the confidence of the check

    if pos_list:
        final_pos_list = []
        for pos in pos_list:
            #TODO: REDUCE REPETITION HERE, CLEAN UP PRINT STATEMENTS
            letter_x_grid, letter_y_grid = pos
            logging.debug(f"Letter {orig_letter} may reside in position ({letter_x_grid}, {letter_y_grid})")

            if not ((letter_x_grid, letter_y_grid)) in locked_tile_positions:
                logging.debug("Confidence in letter " + letter + ": " + str(0.99 - confidence_adjustment))
                final_pos_list.append((orig_letter, 0.99 - confidence_adjustment + problem_adjustment, letter_x_grid, letter_y_grid))
            

            else: #if letter is on a locked tile, discard it
                logging.info("         That's a locked tile!")
                
        return (final_pos_list)

    else:#did not find letter
        return None

def checkForLocked():#TODO: PROGRAM SOMETIMES SEES THE BLACK PIXELS IN THE LETTERS AND GETS CONFUSED (sees that letter is black and background tile is black ----> thinks tile is locked)
    #loop through all grid tiles
    #then, if the color of the click spot is the same before and after the click, tile didn't move so it must be locked

    color2DArray = [[list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0))], 
                    [list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0))], 
                    [list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0))], 
                    [list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0)), list((0, 0, 0))]]

    locked_count = 0
    locked_points = []

    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        x_min = 310
        y_min = 320

        x_max = 510
        y_max = 520

        find_x = lambda x : round((x * 1.5))
        find_y = lambda y : round((y * 1.5) + 50)

        step = 50
    #TODO: STANDARDISE THIS BOUNDARY THING
    if gameType == 2:
        x_min = 800
        y_min = 570

        x_max = 1100
        y_max = 860

        find_x = lambda x : x - 12
        find_y = lambda y : y - 5

        step = 93

    
    col = 0
    for x in range(x_min, x_max, step):
        row = 0
        for y in range(y_min, y_max, step):
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
            color = color2DArray[col][row]
            #color = (0, 0, 0)

            if pyautogui.pixelMatchesColor(x, y, (color), tolerance = 35):
                wrong_color = pyautogui.pixel(x, y)
                locked_count = locked_count + 1
                locked_points.append((col, row))
                print(f"Found locked tile in position (" + str(col) + ", " + str(row) + ")")
                print(f"      expected {color} and saw {wrong_color}")
            row = row + 1
        col = col + 1

    return locked_points
    
def clickAbnormalTiles():#clicks on the tiles which are gems, plagued, smashed, or otherwise discolored
    abnormal_count = 0

    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()
    if gameType == 1:
        x_min = 310
        y_min = 320

        x_max = 510
        y_max = 520

        find_x = lambda x : round((x * 1.5))
        find_y = lambda y : round((y * 1.5) + 50)

        step = 50

    if gameType == 2:
        x_min = 800
        y_min = 570

        x_max = 1100
        y_max = 860

        find_x = lambda x : x
        find_y = lambda y : y 

        step = 93

    pic = pyautogui.screenshot(region = (x_min, y_min, x_max - x_min, y_max - y_min))
    

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
    print(str(abnormal_count) + " abnormal tiles")
    return abnormal_count

def printListLetterBoard(board):#first print letters, then print confidence levels in a separate grid
    print(letterBoardString(board))

def letterBoardString(board):
    output = ""
    for row in range(4):
        output += "[ "
        for col in range(4):
            output += f" '{board[row][col][0]}' "
        output += "]\n"
    output += '\n'
    for row in range(4):
        output += "[ "
        for col in range(4):
            if board[row][col][1] == 0:
                output += " --  "
            else:
                output += "{:.2f}".format(board[row][col][1]) + ' '
        output += "]\n"

    return output
def getLetterAdjustment(letter):
    gameType = inGame()
    while not gameType:
        time.sleep(1)
        gameType = inGame()

    if gameType == 1:
        tooMany = ['c', 'e', 'l', 'p', 'r', 't', 'u']#letters are (incorrectly) recognized too often without this adjustment
        bitTooMany = ['a', 'b', 'd', 'f', 'h', 'j', 'k', 'm', 'n', 'q', 's','x', 'y', 'z']#slight adjustment

        bitNotEnough = ['i','o']
        notEnough = ['k', 'p', 'w']#letters aren't recognized enough if this adjustment isn't made

        if letter in bitTooMany:
            return -0.17
        elif letter in tooMany:
            return -0.20


        elif letter in bitNotEnough:
            return 0.03
        elif letter in notEnough:
            return 0.08

        elif letter == 'g':
            return -0.21

    if gameType == 2:#looks like adjustment is only needed for Bookworm Adventures 1
        #tooMany = []
        #bitTooMany = []

        #notEnough = ['i']

        #if letter == 'i':
        #    return 0.65

        pass

    return 0

def getMostConfidentLetterGrid(letter, letterBoard):#return the grid location of the letter with the highest confidence
                                                    
    lettersToClick = []

    for col in range (4):
        for row in range(4):
            if letterBoard[col][row][0] == letter:
                #print("letter " + letter + " in position (" + str(row) + ", " + str(col) + ")")
                
                #find the letter that has the highest confidence rating, then click that one
                lettersToClick.append((letterBoard[col][row], row, col))
            elif letterBoard[col][row][0] == '?':
                lettersToClick.append((list((letter, 0.01)), row, col))

    lettersToClick.sort(key = lambda x : x[0], reverse = True)

    #print("Potential letters: ")
    #print(lettersToClick)

    if not lettersToClick:
        return list(('-', 0))

    bestLetter = lettersToClick[0]
                    
    bestRow, bestCol = bestLetter[1], bestLetter[2]

    letterBoard[bestCol][bestRow] = list(('-', 0))

    return (bestLetter)


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

    #so, find the color of (270, 30) because this color always remains the same in the game (color of Lex's name, decorative)

    if pyautogui.pixelMatchesColor(0, 0, (115, 109, 90)):
        return 1
    elif pyautogui.pixelMatchesColor(270, 30, (239, 178, 0), tolerance = 15):
        return 2
    else:
        #print(f"Color was {pyautogui.pixel(270, 30)}, expected (239, 178, 0)")
        return 0

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

    letterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                   [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                   [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
                   [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]
    boardLetters = ""


    inOrder = True #if bot knows where every letter is on the board (assumed to be true if input is manual [and correct] or if info is automatically read)

    decision = input("Automatic or manual input? (0 or 1, respectively) --> ")

    if int(decision) == 1:
        manual = True
    else:
        manual = False

    if manual:
        filtered_words, boardLetters = findLongestWord(None, boardLetters)

        decision = input("Are the letters of the input in order? (0 for no, 1 for yes) --> ")

        if int(decision) == 0:
            inOrder = False

        if inOrder:
            #fill letterboard completely
            lettersQueue = []
            boardLetters = fixQsInString(boardLetters)
            for i in boardLetters:
                lettersQueue.append(i)
            
            for i in range(4):
                for j in range(4):
                    if lettersQueue:#if list is not long enough, append '-' chars to the end
                        letterBoard[i][j][0] = lettersQueue.pop(0)
                        letterBoard[i][j][1] = 1

                    else:
                        letterBoard[i][j][0] = '-'


        printListLetterBoard(letterBoard)
 

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
                if letterBoard[i][j][0] != '-':
                    autoInput = autoInput + letterBoard[i][j][0]

        start = time.perf_counter()
        filtered_words = findLongestWord(autoInput, boardLetters)[0]
        end = time.perf_counter()

        print(f"Took {end - start} seconds to find the longest word")

    print()

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

        if not inOrder:#TODO: CHECK IF THIS IS NECESSARY
            letterBoard = [['-', '-', '-', '-'], ['-', '-', '-', '-'], ['-', '-', '-', '-'], ['-', '-', '-', '-']]


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
    print("Took " + str(numberOfAttempts) + " attempts")

#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

if __name__ == '__main__':
    main()
   

######################################################################################################
#CODE TESTING SNIPPETS BELOW

#gameType = inGame()
#while not gameType:
#    time.sleep(1)
#    gameType = inGame()

#letterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
#                   [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
#                   [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
#                   [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]


#clearBoard()
#locked_tile_positions = []
#abnormal_count = clickAbnormalTiles()

#readLettersImproved(letterBoard, abnormal_count, locked_tile_positions)

#printListLetterBoard(letterBoard)

#if gameType == 1:
#    x_min = 310
#    y_min = 320
#    x_max = 510
#    y_max = 520

#    offset = 10

#if gameType == 2:
#    x_min = 770
#    y_min = 550
#    x_max = 1150
#    y_max = 930

#    offset = 0

#pic = pyautogui.screenshot('screenshot.png', region = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset))

   
def deprecated():#this is only here so I can wrap it up/condense it
    
    #####################################################################################

    #if __name__ == '__main__':
    #    main()
        
    #gameType = inGame()
    #while not gameType:
    #    time.sleep(1)
    #    gameType = inGame()
    #if gameType == 1:
    #    x_min = 310
    #    y_min = 320

    #    x_max = 510
    #    y_max = 520

    #    offset = 20
    #    SCALER = 1.5
    #    append = "Clear.png"#this is appened to the letter so the program can search for the file name


    #if gameType == 2:
    #    x_min = 770
    #    y_min = 550

    #    x_max = 1150
    #    y_max = 950

    #    offset = 50
    #    SCALER = 1
    #    append = "2.png"#this is appened to the letter so the program can search for the file name
    #    find_x = lambda x:x
    #    find_y = lambda y:y
    #pic = pyautogui.screenshot(region = (x_min, y_min, x_max - x_min, y_max - y_min))

    #step = 100
    #for x in range(x_min, x_max, step):
    #    for y in range(y_min, y_max, step):
    #        click_x = find_x(x)
    #        click_y = find_y(y)

    #        win32api.SetCursorPos((click_x, click_y))
    #        grid_x, grid_y = clickToGrid(click_x, click_y)
    #        print(f"Clicking in position ({grid_x}, {grid_y})")
    #    print()


    #thread = CustomThread(target = add, args = (7, 4))
    #thread.start()
    #print(thread.join())

    #pool = ThreadPoolExecutor(5)

    #while not inGame():
    #    time.sleep(1)

    #letterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
    #               [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
    #               [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
    #               [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]

    #letterCount = 0
    #while letterCount <16:
    #    threads = []
    #    potentialLetters = []

    #    for letter in ASCII_LOWERCASE:
    #        t = CustomThread(target = checkForLetterThread, args = (letter, ))
    #        t.start()
    #        threads.append(t)

    #    for thread in threads:
    #        potentialLetters.append(thread.join())

    #    nonesRemoved = False
    #    while not nonesRemoved:
    #        nonesRemoved = True
    #        for element in potentialLetters:
    #            if element == None:
    #                potentialLetters.remove(element)
    #                nonesRemoved = False

    #    print(potentialLetters)


    #    if len(potentialLetters):
    #        potentialLetters.sort(key = lambda x : x[1], reverse = True)
    #        for letter in potentialLetters:
    #            print("(" + letter[0] + ", " + str(round(letter[1], 2)) + ")", end = ", ")
    #        print()
    #        bestLetter = potentialLetters[0]

    #        theLetter = (bestLetter[0])[0]
    #        confidence = bestLetter[1]
    #        pos = bestLetter[2]
            
    #        center_pos = pyautogui.center(pos)
    #        new_pos_x, new_pos_y = center_pos

    #        SCALER = 1.5
    #        new_pos_x = new_pos_x * SCALER
    #        new_pos_y = new_pos_y * SCALER

    #        letter_x_grid, letter_y_grid = clickToGrid(new_pos_x, new_pos_y)
    #        #print("Letter resides in position (" + str(letter_x_grid) + ", " + str(letter_y_grid) + ")")

    #        ##if letter is on a locked tile, discard it
    #        #if ((letter_x_grid, letter_y_grid)) in locked_tile_positions:
    #        #    print("         That's a locked tile!")
    #        #    return ((1.0 - confidence_adjustment, 0, 0)) #default return values

    #        #else:
    #        print("Confidence in letter " + theLetter + ": " + str(confidence))
    #        letterCount = letterCount + 1

    #        letterBoard[letter_y_grid][letter_x_grid][0] = theLetter
    #        letterBoard[letter_y_grid][letter_x_grid][1] = confidence
        
    #        mouseSetAndClick(new_pos_x, new_pos_y)#because window resizing does weird things

    #        printListLetterBoard(letterBoard)
    #    else:
    #        min_confidence = min_confidence - 0.04


    #for i in range(50):
    #    t = CustomThread(target = square, args = (i, ))
    #    t.start()
    #    threads.append(t)

    #for thread in threads:
    #    thread.join()

    #thread1 = pool.submit(square, 1)
    #thread2 = pool.submit(square, 2)
    #thread3 = pool.submit(square, 3)
    #thread4 = pool.submit(square, 4)
    #thread5 = pool.submit(square, 5)

    #0000000000000000000000000000000000000000000000000000000000000000

    #attempted to speed up the process and increase the confidence of letters with multiprocessing, was a bit slower and reliability did not improve :(
    #def readLetterNew(letterBoard):
    #    #TODO:NEED TO GIVE THIS FUNCTION A BETTER NAME

    #    #loop through all letters with one confidence level
    #    #if theres a hit
    #    #   sort hits by confidence and return the most confident
    #    min_confidence = 0.95
    #    confidence_adjustment = 0

    #    letterCount = 0
    #    while letterCount < 16:
     
    #        potentialLetters = []

    #        items = [(letter, min_confidence) for letter in ASCII_LOWERCASE]

    #        with Pool() as pool:
    #            for result in pool.starmap(checkForLetterProcess, items):
    #                if result!= None:
    #                    potentialLetters.append(result)

    #        print("         finished this pass")

    #        #nonesRemoved = False
    #        #while not nonesRemoved:
    #        #    nonesRemoved = True
    #        #    for element in potentialLetters:
    #        #        if element == None:
    #        #            potentialLetters.remove(element)
    #        #            nonesRemoved = False

    #            ##print("1 - confidence_adjustment = " + str(1 - confidence_adjustment) + " and min_confidence is " + str(min_confidence))
    #            #while(1 - confidence_adjustment + problem_adjustment > min_confidence and pos == None):#DOES NOT have to click a letter
    #            #    pos = pyautogui.locateOnScreen(letterName, region = (300, 290, 250, 250), confidence = 1.0 - confidence_adjustment)
    #            #    confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check
    #            #    #print("Baseline confidence: --> " + str(round(min_confidence, 2)) + "             Confidence: -->  " + str(round(1 - confidence_adjustment, 2)) + " in letter " + letter)
    #            #    if pos!= None:
    #            #        potentialLetters.append((letter, (1 - confidence_adjustment) + problem_adjustment, pos))
                        

                
    #        if len(potentialLetters):
    #            potentialLetters.sort(key = lambda x : x[1], reverse = True)
    #            for letter in potentialLetters:
    #                print("(" + letter[0] + ", " + str(round(letter[1], 2)) + ")", end = ", ")
    #            print()
    #            bestLetter = potentialLetters[0]

    #            theLetter = (bestLetter[0])[0]
    #            confidence = bestLetter[1]
    #            pos = bestLetter[2]
            
    #            center_pos = pyautogui.center(pos)
    #            new_pos_x, new_pos_y = center_pos

    #            SCALER = 1.5
    #            new_pos_x = new_pos_x * SCALER
    #            new_pos_y = new_pos_y * SCALER

    #            letter_x_grid, letter_y_grid = clickToGrid(new_pos_x, new_pos_y)
    #            #print("Letter resides in position (" + str(letter_x_grid) + ", " + str(letter_y_grid) + ")")

    #            ##if letter is on a locked tile, discard it
    #            #if ((letter_x_grid, letter_y_grid)) in locked_tile_positions:
    #            #    print("         That's a locked tile!")
    #            #    return ((1.0 - confidence_adjustment, 0, 0)) #default return values

    #            #else:
    #            print("Confidence in letter " + theLetter + ": " + str(confidence))
    #            letterCount = letterCount + 1

    #            letterBoard[letter_y_grid][letter_x_grid][0] = theLetter
    #            letterBoard[letter_y_grid][letter_x_grid][1] = confidence
        
    #            mouseSetAndClick(new_pos_x, new_pos_y)#because window resizing does weird things

    #            printListLetterBoard(letterBoard)
    #        else:
    #            min_confidence = min_confidence - 0.05

    #####################################################################################
    #this class was used in an attempt to speed up the program, did not work :(
    #class CustomThread(Thread):
    #    def __init__(self, group = None, target = None, name = None, args = (), kwargs = {}, Verbose = None):
    #        Thread.__init__(self, group, target, name, args, kwargs)
    #        self._return = None

    #    def run(self):
    #        if self._target is not None:
    #            self._return = self._target(*self._args, **self._kwargs)

    #    def join(self):
    #        Thread.join(self)
    #        return self._return


    #this process was used in an attempt to speed up the program, did not work :(
    #def checkForLetterProcess(letter, min_confidence):


    #    #(a, 0.9) ----> 1.00, 0.99, 0.98, ..., 0.9
    #    #(b, 0.5) ----> 0.77, 0.76, 0.75, ..., 0.67 (adjustment is -0.17)
        
    #    pos = None
    #    problem_adjustment =  getLetterAdjustment(letter)
    #    #print(f"problem adjustment for '{letter}' is {problem_adjustment}")
    #    #print(f"testing with min_confidence of {min_confidence}")

    #    confidence_adjustment = 0.9 - (min_confidence - problem_adjustment)
    #    #print(f"confidence adjustment starting at {round(confidence_adjustment, 2)}")
    #    print()
    #    letterName = letter + "Clear.png"

    #    if confidence_adjustment + 0.1 < 0:
    #        #print('nope')
    #        return None

    #    while(1 - confidence_adjustment + problem_adjustment > min_confidence and pos == None):#DOES NOT have to find a letter
    #        pos = pyautogui.locateOnScreen(letterName, region = (300, 290, 250, 250), confidence = 1.0 - confidence_adjustment)
    #        confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check

    #        print(f"checking {letter} with confidence {round(1.0 - confidence_adjustment, 2)}...")
    #        if pos!= None:
    #            print(f"                Found letter {letter} with confidence {round(1.0 - confidence_adjustment, 2)}!")
    #            return (letter, (1 - confidence_adjustment) + problem_adjustment, pos)
    #    return None
    pass