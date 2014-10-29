#!/usr/bin/python
import os
import re
import collections
from time import gmtime, strftime
import numpy as np
import TEXT
import DSP
import NMF
fileList = os.listdir('.')

#### ========================== #
#### remove .sort and .np files #
#### ========================== #
###for fileName in fileList :
###	if re.search( "\.np" , fileName ) :
###		os.remove( fileName )

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
		###if os.path.isfile( fileName + '.np' ) :
		###	os.remove( fileName + '.np' )	
		###fileName_preproc = TEXT.PREPROCESS( fileName )
		### .np and .np.sort are generated
		###fileObject = open( fileName_preproc )
		fileObject = open( fileName )
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
wordNum = len(existWordList)
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
modelOrder = 50 
iteraNum   = 5
# ------------------ #
# initialize A and S #
# ------------------ #
A = np.random.ranf( [ wordNum , modelOrder ] ) * 6
S = np.random.ranf( [ modelOrder , fileNum ] ) * 6
# ---------------------------- #
# NMF iteration ( using LSMU ) #
# ---------------------------- #
for cycle in xrange( 0 , iteraNum ) :
	# ------------- #
	# update S part #
	# ------------- #
	for J_Idx_wikiFile in xrange( 0 , fileNum ) :
		print "Cycle No. : %d / %d\tFile No. : %d / %d" %(cycle+1,iteraNum,J_Idx_wikiFile,fileNum)
		# --------------------------------- #
		# obtain the corresponding Y column #
		# --------------------------------- #
		Y_currCol = np.zeros(  wordNum ) #scipy.optimize.nnls uses np.array
		for word in wikiHash[ J_Idx_wikiFile ][ '_wordprofile' ] :
			Y_currCol[ existWordList_hash[word] ] = existWord[ word ][ J_Idx_wikiFile ]
		#A_no_use , S_Jcolumn = NMF.LSMU( Y_currCol , A , S[ : , J_Idx_wikiFile ] , 1 , 1 )
		A_no_use , S_Jcolumn = NMF.LSMU( np.matrix( Y_currCol ).transpose() , A , np.matrix( S[ : , J_Idx_wikiFile ] ).transpose() , 1 , 1 )
		for k in xrange( 0 , modelOrder ) :
			S[ k , J_Idx_wikiFile ] = S_Jcolumn[k]
	# ------------- #
	# update A part #
	# ------------- #	
	Y_currRow = np.zeros( fileNum )
	for I_Idx_existWord in xrange( 0 , wordNum ) :
		print "Cycle No. : %d / %d\tWord No. : %d / %d" %(cycle+1,iteraNum,I_Idx_existWord,wordNum)
		for Idx_wikiFile in xrange( 0 , fileNum ) :
			currFile_wordProfile = wikiHash[ Idx_wikiFile ][ '_wordprofile' ]
			if currFile_wordProfile.has_key( existWordList[I_Idx_existWord] ) :
				Y_currRow[ Idx_wikiFile ] = currFile_wordProfile[ existWordList[ I_Idx_existWord ] ]
				break
		A_Irow , S_no_use = NMF.LSMU( np.matrix( Y_currRow ) , np.matrix( A[ I_Idx_existWord , : ] ) , S , 1 , 0 )
		A[ I_Idx_existWord , : ] = A_Irow
	# ------------- #
	# export result #
	# ------------- #
	DSP.LOG( 'log matrix to file' , 'A_itera'+str(cycle)+'.txt' , A , ' ' )
	DSP.LOG( 'log matrix to file' , 'S_itera'+str(cycle)+'.txt' , S , ' ' )

