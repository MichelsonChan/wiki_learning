#!/usr/bin/python
import os
import re
import collections
from time import gmtime, strftime
import numpy as np
import TEXT
import DSP
fileList = os.listdir('.')

# ========================== #
# remove .sort and .np files #
# ========================== #
for fileName in fileList :
	if re.search( "\.np" , fileName ) :
		os.remove( fileName )

# ======================================= #
# prepare dictionary hash first for later #
# filtering unpopular words / nonenglish  #
# ======================================= #
fileObject = open ( 'dictionary.np' )
dictList   = fileObject.read().splitlines()
fileObject.close()
dictHash = {}
for i in xrange( len( dictList ) ) :
	dictHash[ dictList[i] ] = i
#---------------
del dictList , i
#---------------

# ============================= #
# obtain wiki article word hash #
# ============================= #
wikiFileList = os.listdir('.')
wikiHash = {}
Idx_processedFile = 0
for Idx_wikiFile in range( 0 , len(wikiFileList) ) :
	fileName = wikiFileList[ Idx_wikiFile ]
	#if re.search( "text\." , fileName ) :
	if re.search( "\.sort" , fileName ) :
		fileHash = {}
		print "now processing : %s" %(fileName)
		if os.path.isfile( fileName + '.np' ) :
			os.remove( fileName + '.np' )	
		fileName_preproc = TEXT.PREPROCESS( fileName )
		 .np and .np.sort are generated
		fileObject = open( fileName_preproc )
		#fileObject = open( fileName )
		wordList   = fileObject.read().splitlines()
		fileObject.close()
		wordHash = {}
		for word in wordList :
			if dictHash.has_key( word ) :
			# to ensure only popular words / english are included
				if wordHash.has_key( word ) : wordHash[ word ] += 1
				else                        : wordHash[ word ]  = 1
		#-------
		del word
		#-------
		fileHash[ '_wordprofile' ] = wordHash
		fileHash[ '_title' ] = fileName
		wikiHash[ Idx_processedFile ] = fileHash
		Idx_processedFile += 1
fileNum = Idx_processedFile
#------------------------------------------------
del Idx_wikiFile , wordHash , fileHash , fileName
#------------------------------------------------

# ============================ #
# initialize the BIG DATA HASH #
# ============================ #
existWord     = {}
existWordList = []
for Idx_wikiFile in xrange( 0 , fileNum ) :
	singleFile_wordProfile = wikiHash[ Idx_wikiFile ][ '_wordprofile' ]
	for word_n_freq in singleFile_wordProfile.iteritems() :	
		word = word_n_freq[0]
		if not existWord.has_key( word ) :
			existWordList.append( word )
			#existWord[ word ] = np.zeros( fileNum , dtype=np.uint8 )
			existWord[ word ] = {} # will store word occurance
#-------------------------------------------------------------
del Idx_wikiFile , singleFile_wordProfile , word_n_freq , word
#-------------------------------------------------------------

# ========================= #
# fill in the BIG DATA HASH #
# ========================= #
existWordList.sort()
existWordList_hash = {} # for reverse index retrieval in NNLS
for Idx_word in xrange( 0 , len( existWordList ) ) :
	currWord = existWordList[ Idx_word ]
	existWordList_hash[ currWord ] = Idx_word
	print Idx_word , currWord
	for Idx_wikiFile in xrange( 0 , fileNum ) :
		wordProfile_ofCurrWikiFile = wikiHash[ Idx_wikiFile ][ '_wordprofile' ]
		if wordProfile_ofCurrWikiFile.has_key( currWord ) :
			existWord[ currWord ][ Idx_wikiFile ] = wordProfile_ofCurrWikiFile[ currWord ]	
#-------------------------------------------------------
del Idx_word , Idx_wikiFile , wordProfile_ofCurrWikiFile
#-------------------------------------------------------

# ============================================== #
# perform Alternating Non-Negative Least Squares #
# ============================================== #
# 
# ------------------------------------------- #
# Y = A * S , S <- min || Y-A*S ||F s.t. S>=0 #
# Y := big data matrix                        #
# A := learned library matrix                 #
# S := abundance distribution matrix          #
# ------------------------------------------- #
# 
# ---------------------------------------- #
# strategy :                               #
# update S matrix first in min ||Y-A*S||   #
# then update A matrix in min ||Y'-S'*A'|| #
# the NNLS is performed in column-wise     #
# i.e. min || Y[:,j]  - A  * S[:,j]  ||    #
# and  min || Y[i,:]' - S' * A[i,:]' ||    #
# ---------------------------------------- #
modelOrder = 8 
# ------------------ #
# initialize A and S #
# ------------------ #
A = np.random.ranf( [ len(existWordList) , modelOrder ] ) * 6
S = np.zeros( [ modelOrder , fileNum ] )
# -------------- #
# recover S part #
# -------------- #
for Idx_wikiFile in xrange( 0 , fileNum ) :
	print "Wikipedia File no.: %d" %(Idx_wikiFile)
	print Y_currCol[ existWordList_hash[word] , 0 ] = existWord[ word ][ Idx_wikiFile ]trftime("%Y-%m-%d %H:%M:%S", gmtime())
	# --------------------------------- #
	# obtain the corresponding Y column #
	# --------------------------------- #
	#Y_currCol = np.zeros( [ len(existWordList) , 1 ] )
	Y_currCol = np.zeros(  len(existWordList) ) #scipy.optimize.nnls requires np.array
	for word in wikiHash[ Idx_wikiFile ][ '_wordprofile' ] :
		#if existWord[ word ].has_key( Idx_wikiFile ] :
		#Y_currCol[ existWordList_hash[word] , 0 ] = existWord[ word ][ Idx_wikiFile ]
		Y_currCol[ existWordList_hash[word] ] = existWord[ word ][ Idx_wikiFile ]
	S_Jcolumn = DSP.NNLS( Y_currCol , A )
	S[ : , Idx_wikiFile:Idx_wikiFile+1 ] = S_Jcolumn
#----------------------------------
del Idx_wikiFile , word , S_Jcolumn
#----------------------------------
# -------------- #
# recover A part #
# -------------- #

