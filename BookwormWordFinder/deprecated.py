######################################################################################################
#CODE TESTING SNIPPETS BELOW



#letterBoard = LetterBoard("boardgame")
#print(letterBoard)

#newBoard = copy.deepcopy(letterBoard)
#print(newBoard)

#letterBoard.board[3][3].set_letter('f')
#print(letterBoard)

#letterAndCount = LetterAndCount('a', 1)
#print(letterAndCount)
#tile = Tile()
#print(f"Printing blank tile:\n{tile}")

#filledTile = Tile('a', 0.83)
#print(f"Printing filled tile:\n{filledTile}")
#board = LetterBoard()
#print(board)

#filledBoard = LetterBoard("oadofkjsdokfna;sodkfn;aoskdnfansdofi")
#print(filledBoard)


#tempLetterBoard = [[list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
#                              [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
#                              [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))], 
#                              [list(('-', 0)), list(('-', 0)), list(('-', 0)), list(('-', 0))]]

#tempBoardLetters = "abcdefghijkl"
#letter = "?"

#row = 0
#col = 0
#for letter in tempBoardLetters + letter:
#    tempLetterBoard[col][row] = list((letter, 1))

#    row +=1
#    if row > 3:
#        row = 0
#        col += 1
#    if col > 3:
#        col = 0

#printListLetterBoard(tempLetterBoard)

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

#def printListLetterBoard(board):#first print letters, then print confidence levels in a separate grid
#    print(letterBoardString(board))

#def letterBoardString(board):
#    output = ""
#    for row in range(4):
#        output += "[ "
#        for col in range(4):
#            output += f" '{board[row][col][0]}' "
#        output += "]\n"
#    output += '\n'
#    for row in range(4):
#        output += "[ "
#        for col in range(4):
#            if board[row][col][1] == 0:
#                output += " --  "
#            else:
#                output += "{:.2f}".format(board[row][col][1]) + ' '
#        output += "]\n"

#    return output

#def verify_word(word, fancy_letter):
#    letter_count = 0
#    for letter in word:
#        if letter == fancy_letter.letter:
#            letter_count = letter_count + 1

#        if letter_count > fancy_letter.count:
#            return False
    
#    return True

#def verify_words(words, fancyLetters):
#    any_removed = True
#    num_removed = 0

#    while (any_removed):
#        any_removed = False
        
#        for word in words:
#            for fancy_letter in fancyLetters:
#                if not verify_word(word, fancy_letter) and word in words:
#                    words.remove(word)
#                    any_removed = True
#                    num_removed = num_removed + 1

#                    break

#def readLetters(letterBoard, min_confidence, loopCount, letterCount, abnormal_count, locked_tile_positions):
#    gameType = inGame()
#    while not gameType:
#        time.sleep(1)
#        gameType = inGame()

#    while letterCount < 16 - abnormal_count - len(locked_tile_positions): #forces program to keep reading until board is full
#                            #confidence in guess drops on every pass, intended to account for gems distorting the image
#        for letter in ASCII_LOWERCASE + str((gameType - 1) * '?'):#sloppy but it works, doesn't check for ? in Bookworm 1
#            if letterCount >= 16 - abnormal_count - len(locked_tile_positions):
#                break
#            points, confidence_list = readLetter(letter, min_confidence, locked_tile_positions)#points holds all the places (pixel positions) where this letter is found 

#            pointIndex = 0
#            for point in points:
#                grid_x, grid_y = clickToGrid(point[0], point[1]) #fill board with predicted letters from read function
                
#                logging.info(f"Trying to add point [{grid_x}, {grid_y}]")
                
#                if not letterBoard[grid_y][grid_x][0] == '-': #stops the program from reading the same letter over and over if a window is stopping it from clicking or something like that
#                    logging.info("         Spot is taken!")
#                    break
#                else:
#                    letterBoard[grid_y][grid_x][0] = letter
#                    letterBoard[grid_y][grid_x][1] = round(confidence_list[pointIndex], 2)

#                    pointIndex = pointIndex + 1
#                    letterCount = letterCount + 1

#                    logging.info("            Counted letter " + str(letterCount))
#                    logging.info("\n" + letterBoardString(letterBoard))

#        min_confidence = min_confidence - 0.1 #gradually reduce confidence in guesses
#        loopCount = loopCount + 1

#    return (letterCount, loopCount)

#def readLetter(letter, confidence_adjustment, locked_tile_positions):
#    findingLetters = True
#    points_list = []#list of all the points where this letter exists
#    confidence_list = []

#    while findingLetters and len(points_list) <= 16:#len argument because otherwise it gets stuck searching for letters when confidence is super low
#        info = clickLetterMaybe(letter, confidence_adjustment, locked_tile_positions) #info holds (confidence, pixel_x, pixel_y) where [1] and [2] are locations of the letter
#        findingLetters = info[1] #if x val is 0 (default value), no letter has been found
#        if info[1] != 0:
#            confidence_list.append(info[0])
#            points_list.append((info[1], info[2]))

#    return ((points_list, confidence_list))#return the list of points and their respective confidence ratings

#def getLetterAdjustment(letter):



#    #TODO: FOR TESTING ONLY
#    return 0

#    gameType = inGame()
#    while not gameType:
#        time.sleep(1)
#        gameType = inGame()

#    if gameType == 1:
#        #tooMany = ['c', 'e', 'l', 'p', 'r', 't', 'u']#letters are (incorrectly) recognized too often without this adjustment
#        #bitTooMany = ['a', 'b', 'd', 'f', 'h', 'j', 'k', 'm', 'n', 'q', 's','x', 'y', 'z']#slight adjustment

#        #bitNotEnough = ['i','o']
#        #notEnough = ['k', 'p', 'w']#letters aren't recognized enough if this adjustment isn't made

#        #if letter in bitTooMany:
#        #    return -0.17
#        #elif letter in tooMany:
#        #    return -0.20


#        #elif letter in bitNotEnough:
#        #    return 0.03
#        #elif letter in notEnough:
#        #    return 0.08

#        #elif letter == 'g':
#        #    return -0.21

#        notEnough = ['i', 'o']
#        tooMany = ['g']

#        if letter in notEnough:
#            return 0.18
#        elif letter in tooMany:
#            return -0.1

#    if gameType == 2:#looks like adjustment is only needed for Bookworm Adventures 1
#        #tooMany = []
#        #bitTooMany = []

#        #notEnough = ['i']

#        #if letter == 'i':
#        #    return 0.65

#        pass

#    return 0


#def clickLetterMaybe(letter, min_confidence, locked_tile_positions): #will not click if the confidence rating is too low (0.8)
#                                                    #baseline_confidence decreases gradually as the program loops over the same board multiple times
#                                                    #with each pass, confidence decreases
#                                                    #returns (confidence, pos_x, pos_y) as pixel values, not grid values 
#                                                    #ex. (0.67, 356, 258)


#    gameType = inGame()
#    while not gameType:
#        time.sleep(1)
#        gameType = inGame()

#    x_min, y_min, x_max, y_max, offset, step, SCALER = getBoundaries(gameType)

#    if gameType == 1:
#        append = ".png"#this is appened to the letter so the program can search for the file name

#    if gameType == 2:
#        append = ".png"#this is appened to the letter so the program can search for the file name

#    boundaries = (x_min - offset, y_min - offset, x_max - x_min + offset, y_max - y_min + offset)

        
#    if letter == '?':
#        letter = "question"#have to make this change because you can't name a file '?2.png'

#    letterName = letter + append
#    confidence_adjustment = 0.9 - min_confidence

#    if confidence_adjustment < 0:
#        confidence_adjustment = 0

#    #right side of this inequality determines how far the program goes before giving up
#    #the higher the right side is, the further it allows its guesses to stray from the confidence
#    pos = None
#    while(1 - confidence_adjustment > min_confidence and pos == None):#DOES NOT have to click a letter
#        logging.debug(f"checking {letter} with confidence {round(1.0 - confidence_adjustment, 2)}...")
#        pos = pyautogui.locateOnScreen(letterName, region = boundaries, confidence = 1.0 - confidence_adjustment)

#        if pos!= None:
#            logging.debug(f"                Found letter {letter} with confidence {round(1.0 - confidence_adjustment, 2)}!")
            
#        confidence_adjustment = confidence_adjustment + 0.01 #slowly decreases the confidence of the check

#    if pos != None:
#        letter_x_grid, letter_y_grid = posToGrid(pos)

#        #if letter is on a locked tile, discard it
#        if ((letter_x_grid, letter_y_grid)) in locked_tile_positions:
#            logging.debug("         That's a locked tile!")
#            return ((1.0 - confidence_adjustment, 0, 0)) #default return values

#        else:
#            logging.debug("Confidence in letter " + letter + ": " + str(1.0 - confidence_adjustment))
    
#            mouseSetAndClick(new_pos_x, new_pos_y)#because window resizing does weird things
#            return ((1.0 - confidence_adjustment, new_pos_x, new_pos_y))

#    else:#did not find letter, return confidence and default position values
#        return ((1.0 - confidence_adjustment, 0, 0))
