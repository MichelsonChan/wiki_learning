# ======= #
# TEXT.py #
# ======= #

# ====== #
# import #
# ====== #
import os
import string
import numpy as np

# ==================== #
# functions definition #
# ==================== #

def PREPROCESS_DICT( dictionaryFileNameStr ) :
	outputTextFileNameStr = dictionaryFileNameStr + "_np"
	# ----------------------- #
	# check file availability #
	# ----------------------- #
	if not os.path.isfile(  dictionaryFileNameStr ) :
	        print "Error @ TEXT.PREPROCESS_DICT() :"
	        print dictionaryFileNameStr  + " is not found !"
	        print "Error exit."
	        return
	if     os.path.isfile( outputTextFileNameStr ) :
	        print "Error @ TEXT.PREPROCESS_DICT() :"
	        print outputTextFileNameStr + " already exists !"
	        print "Do you want to overwrite it ? [ y / n ]"
	        userReply = raw_input()
	        if userReply == 'n' :
	                return
	        else :
	                os.remove( outputTextFileNameStr )
	# -------------------- #
	# read dictionary file #
	# -------------------- #
	fileObject = open( dictionaryFileNameStr , 'r' )
	dictLines  = fileObject.read().split()
	fileObject.close()
	# ----------------------------------- #
	# punctuation and white space removal #
	# ----------------------------------- #
	for k in range( 0 , len( dictLines ) ) :
		dictLines[k] = dictLines[k].replace('.','')
		dictLines[k] = dictLines[k].replace(',','')
		dictLines[k] = dictLines[k].replace('/','')
		dictLines[k] = dictLines[k].replace('-','')
		dictLines[k] = dictLines[k].replace('_','')
		dictLines[k] = dictLines[k].replace('\'','')
		dictLines[k] = dictLines[k].replace('\"','')
		dictLines[k] = dictLines[k].replace('`','')
		dictLines[k] = dictLines[k].replace('&','')
		dictLines[k] = dictLines[k].replace(' ','')
		dictLines[k] = dictLines[k].replace('(','')
		dictLines[k] = dictLines[k].replace(')','')
	# -------------------------- #
	# remove duplicates and sort #
	# -------------------------- #	
	dictLines  = list( set( dictLines ) )
	dictLines.sort()
	
	# -------------- #
	# export to file #
	# -------------- #
	fileObject = open( outputTextFileNameStr , 'w' )
	for k in range( 0 , len( dictLines ) ) :
		fileObject.write( dictLines[k] + "\n" )
	fileObject.close()
	# ------ #
	# finish #
	# ------ #
	return

def PREPROCESS( inputTextFileNameStr ) :
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
	# this function generates 2 files                 #
	# one is a file with vectorized content           #
	# and whereas no punctuations exist               #
	# the file name is <inputTextFileNameStr>.np      #
	#                                                 #
	# one is a sorted version of the above            #
	# file with all contents casted to lower case     #
	# the file name is <inputTextFileNameStr>.np.sort #
	#                                                 #
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
	# ============================================ #
	# Part I : punctuation removal & vectorization #
	# ============================================ #
	outputTextFileNameStr = inputTextFileNameStr + ".np"
        # ----------------------- #
        # check file availability #
        # ----------------------- #
        if not os.path.isfile(  inputTextFileNameStr ) :
                print "Error @ TEXT.PREPROCESS() :"
                print inputTextFileNameStr  + " is not found !"
                print "Error exit."
                return
        if     os.path.isfile( outputTextFileNameStr ) :
                print "Error @ TEXT.PREPROCESS() :"
                print outputTextFileNameStr + " already exists !"
                print "Do you want to overwrite it ? [ y / n ]"
                userReply = raw_input()
                if userReply == 'n' :
                        return
                else :
                        os.remove( outputTextFileNameStr )
	# -------------------- #
        # read input text file #
        # -------------------- #
        fileObject = open(  inputTextFileNameStr , 'r' )
        inputStr   = fileObject.read()
        fileObject.close()
        # ------------------- #
        # punctuation removal #
        # ------------------- #
        strTransLogic = ''.join( chr(c)  if chr(c).isupper() or chr(c).islower() else '\n' for c in range(256) )
        outputStr     = inputStr.translate( strTransLogic )
        outputStr     = outputStr.lower()
	# ---------------------------- #
	# export punctuation free file #
	# ---------------------------- #
	fileObject = open( outputTextFileNameStr , 'w' )
	fileObject.write( outputStr )
	fileObject.close()
	# ======================================================== #
	# Part II : sort the vectorized punctuation-free text file #
	# ======================================================== #
	# --------------------------------- #
	# update the input output file name #
	# --------------------------------- #
	inputTextFileNameStr  = outputTextFileNameStr
	outputTextFileNameStr =  inputTextFileNameStr + '.sort'
        # ----------------------- #
        # check file availability #
        # ----------------------- #
        if not os.path.isfile(  inputTextFileNameStr ) :
                print "Error @ TEXT.PREPROCESS() :"
                print inputTextFileNameStr  + " is not found !"
                print "Error exit."
                return
        if     os.path.isfile( outputTextFileNameStr ) :
                print "Error @ TEXT.PREPROCESS() :"
                print outputTextFileNameStr + " already exists !"
                print "Do you want to overwrite it ? [ y / n ]"
                userReply = raw_input()
                if userReply == 'n' :
                        return
                else :
                        os.remove( outputTextFileNameStr )
	# ----------------- #
	# alphabetical sort #
	# ----------------- #
	fileObject       = open( inputTextFileNameStr  , 'r' )
	lines            = fileObject.readlines()
	lines.sort()
	fileObject.close()
	# ============================= #
	# Part III: empty lines removal #
	# ============================= #
	lines_noEmptyLine = []
	for line in lines :
		if not line.strip() :
			continue
		else :
			lines_noEmptyLine.append( line )
	sortedFileObject = open( outputTextFileNameStr , 'w' )
	sortedFileObject.writelines( lines_noEmptyLine )
	sortedFileObject.close()
	# ====== #
	# finish #
	# ====== #
	return outputTextFileNameStr


def FORMVECTOR( inputTextFileNameStr , dictioaryFileNameStr ) :
	# =============================================================== #
	# this function generates a vector file and return a vector       #
	# the vector file named <inputTextFileNameStr>.vec contains       #
	# a column vector indicating the frequency of occurance of        #
	# every existing words in the passage.                            #
	# these words correspond to the index from the dictionary.np.sort #
	# meanwhile, the column vector of type numpy array is returned    #
	# =============================================================== #
	outputTextFileNameStr = inputTextFileNameStr + ".vec"
	# ----------------------- #
	# check file availability #
	# ----------------------- #
	if not os.path.isfile(  inputTextFileNameStr ) :
		print "Error @ TEXT.FORMVECTOR() :"
		print inputTextFileNameStr  + " is not found !"
		print "Error exit."
		return
	if     os.path.isfile( outputTextFileNameStr ) :
		print "Error @ TEXT.FORMVECTOR() :"
		print outputTextFileNameStr + " already exists !"
		print "Do you want to overwrite it ? [ y / n ]"
		userReply = raw_input()
		if userReply == 'n' :
			return
		else :
			os.remove( outputTextFileNameStr )
	# ======================================= #
	# Part I : read input file and dictionary #
	# ======================================= #
	fileObject          = open( inputTextFileNameStr , 'r' )
	inputFileLines      = fileObject.readlines()
	fileObject.close()
	fileObject          = open( dictioaryFileNameStr , 'r' )
	dictLines           = fileObject.readlines()
	fileObject.close()
	# ======================= #
	# Part II : create vector #
	# ======================= #
	vector = np.zeros( len( dictLines ) )
	Idx_inputFile = 0  # index for input file transversal
	Idx_dict      = 0  # index for dictionary transversal
	inputFileSize = len( inputFileLines )
	dictSize      = len( dictLines )
	wordNotFound  = False # for handling words from input text not found from dictionary
	print "inputFileSize = %d" %(inputFileSize)
	print "dictSize      = %d" %(dictSize)
	print ""
	while Idx_inputFile < inputFileSize :
		#print "status: %d / %d" %(Idx_inputFile,inputFileSize)
		#print "@ position 1"
		#print "Idx_inputFile = %d" %(Idx_inputFile)
		#print "Idx_dict      = %d" %(Idx_dict)
		#print ""
		backup_Idx_inputFile = Idx_inputFile # backup . used to restore index position
		backup_Idx_dict      = Idx_dict      # when the word is not found from dictionary
		while inputFileLines[ Idx_inputFile ] != dictLines[ Idx_dict ] :
			#print "@ position 2"
			#print "Idx_inputFile = %d" %(Idx_inputFile)
                        #print "Idx_dict      = %d" %(Idx_dict)
			#print ""
			if Idx_dict + 1 < dictSize :
				Idx_dict   += 1
			else :
				wordNotFound = True
				#print "Word Is Unfound From Dictionary !!!"
				#print ""
				break # exit from looping dictionary process
		if wordNotFound :
			Idx_dict      = backup_Idx_dict
			Idx_inputFile = backup_Idx_inputFile + 1
			wordNotFound  = False # reset back to default value
			#print "@ position 3"
			#print "Idx_inputFile = %d" %(Idx_inputFile)
			#print "Idx_dict      = %d" %(Idx_dict)
			#print ""
			continue # exit from matching word obtained from input tex
			         # and continue to match the next word
		else :
			vector[ Idx_dict ] += 1
			Idx_inputFile      += 1
			#print "vector updated !!!"
			#print ""
			while Idx_inputFile < inputFileSize and inputFileLines[ Idx_inputFile ] == inputFileLines[ Idx_inputFile - 1 ] :
				# check if the index is not out of bound
				# and check if the word is the same as the previous one.
				vector[ Idx_dict ] += 1
				Idx_inputFile      += 1
				#print "vector updated !!!"
				#print ""
	# ================================ #
	# Part III : export vector to file #
	# ================================ #
	fileObject = open( outputTextFileNameStr , 'w' )
	for k in range( 0 , vector.size ) :
		fileObject.write( "%d\n" %(vector[k]) )
	fileObject.close()
	return vector


def WORD2NUM( inputTextFileNameStr ) :
	# ==================================== #
	# this function convert the English    #
	# words in a vectorized text file      #
	# into numbers with a purpose for      #
	# easy and convenient dicionary search #
	# e.g. apple  becomes 1.16.16.12.5     #
	# e.g. banana becomes 3.1.14.1.14.1    #
	# lastly this function will generate a #
	# file named fileNameStr.w2n as output #
	# ==================================== #
	outputTextFileNameStr = inputTextFileNameStr + ".w2n"
	# ======================= #
	# check file availability #
	# ======================= #
	if not os.path.isfile( inputTextFileNameStr ) :
		print "Error @ DSP.WORD2NUM() :"
		print inputTextFileNameStr  + " is not found !"
		print "Error exit."
		return
	if     os.path.isfile( outputTextFileNameStr ) :
		print "Error @ DSP.WORD2NUM() :"
		print outputTextFileNameStr + " already exists !"
        	print "Do you want to overwrite it ? [ y / n ]"
        	userReply = raw_input()
        	if userReply == 'n' :
        		return
        	else :
        		os.remove( outputTextFileNameStr )
	# ==================== #
	# read input text file #
	# ==================== #
	fileObject = open(  inputTextFileNameStr , 'r' )
	inputStr   = fileObject.read().lower()
	fileObject.close()
	# ============== #
	# transformation #
	# ============== #
	inputStr = inputStr.replace( 'a'   , '.0'  )
	inputStr = inputStr.replace( 'b'   , '.1'  )
	inputStr = inputStr.replace( 'c'   , '.2'  )
	inputStr = inputStr.replace( 'd'   , '.3'  )
	inputStr = inputStr.replace( 'e'   , '.4'  )
	inputStr = inputStr.replace( 'f'   , '.5'  )
	inputStr = inputStr.replace( 'g'   , '.6'  )
	inputStr = inputStr.replace( 'h'   , '.7'  )
	inputStr = inputStr.replace( 'i'   , '.8'  )
	inputStr = inputStr.replace( 'j'   , '.9'  )
	inputStr = inputStr.replace( 'k'   , '.10' )
	inputStr = inputStr.replace( 'l'   , '.11' )
	inputStr = inputStr.replace( 'm'   , '.12' )
	inputStr = inputStr.replace( 'n'   , '.13' )
	inputStr = inputStr.replace( 'o'   , '.14' )
	inputStr = inputStr.replace( 'p'   , '.15' )
	inputStr = inputStr.replace( 'q'   , '.16' )
	inputStr = inputStr.replace( 'r'   , '.17' )
	inputStr = inputStr.replace( 's'   , '.18' )
        inputStr = inputStr.replace( 't'   , '.19' )
        inputStr = inputStr.replace( 'u'   , '.20' )
        inputStr = inputStr.replace( 'v'   , '.21' )
        inputStr = inputStr.replace( 'w'   , '.22' )
        inputStr = inputStr.replace( 'x'   , '.23' )
        inputStr = inputStr.replace( 'y'   , '.24' )
        inputStr = inputStr.replace( 'z'   , '.25' )
	inputStr = inputStr.replace( '\n.' , '\n'  )
	# ====================================== #
	# handle the first '.' in the first line #
	# ====================================== #
	inputStr = inputStr.replace( '.'   , '', 1 )
	# ====================== #
	# write output text file #
	# ====================== #
	fileObject = open( outputTextFileNameStr , 'w' )
	fileObject.write( inputStr )
	fileObject.close()
	# ====== #
	# finish #
	# ====== #
	return outputTextFileNameStr

