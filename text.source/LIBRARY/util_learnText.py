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
fileObject = open ( 'dictionary_np' )
dictList   = fileObject.read().splitlines()
fileObject.close()
dictHash = {}
for i in xrange( len( dictList ) ) :
	dictHash[ dictList[i] ] = i
#----------------------------
del fileObject , i , dictList
#----------------------------

# ============================= #
# obtain wiki article word hash #
# ============================= #
wikiFileList = os.listdir('.')
wikiHash = {}
Idx_processedFile = 0
for Idx_wikiFile in range( len(wikiFileList) ) :
	fileName = wikiFileList[ Idx_wikiFile ]
	if re.search( "text\." , fileName ) :
		fileHash = {}
		print "now processing : %s" %(fileName)
		if os.path.isfile( fileName + '.np' ) :
			os.remove( fileName + '.np' )	
		fileName_preproc = TEXT.PREPROCESS( fileName )
		# .np and .np.sort are generated
		fileObject = open( fileName_preproc )
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
for Idx_wikiFile in xrange( fileNum ) :
	singleFile_wordProfile = wikiHash[ Idx_wikiFile ][ '_wordprofile' ]
	for word_n_freq in singleFile_wordProfile.iteritems() :	
		word = word_n_freq[0]
		if not existWord.has_key( word ) :
			existWordList.append( word )
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
for Idx_word in xrange( len( existWordList ) ) :
	currWord = existWordList[ Idx_word ]
	existWordList_hash[ currWord ] = Idx_word
	print Idx_word , currWord
	for Idx_wikiFile in xrange( fileNum ) :
		wordProfile_ofCurrWikiFile = wikiHash[ Idx_wikiFile ][ '_wordprofile' ]
		if wordProfile_ofCurrWikiFile.has_key( currWord ) :
			existWord[ currWord ][ Idx_wikiFile ] = wordProfile_ofCurrWikiFile[ currWord ]	
#-------------------------------------------------------
del Idx_word , Idx_wikiFile , wordProfile_ofCurrWikiFile
#-------------------------------------------------------


# =========================================== #
# Log Y matrix to Y.txt , Yt matrix to Yt.txt #
# =========================================== #
if not os.path.isfile( 'Y.txt' ) :
	fileObject = open( 'Y.txt' , 'w' )
	Y_currRow = np.zeros( fileNum )
	for I_Idx_existWord in xrange( wordNum ) :
		print "Writing file Y.txt : %d / %d ..." %(I_Idx_existWord,wordNum)
		for J_Idx_wikiFile in xrange( fileNum ) :
			currFile_wordProfile = wikiHash[ J_Idx_wikiFile ][ '_wordprofile' ]
			if currFile_wordProfile.has_key( existWordList[ I_Idx_existWord ] ) :
				Y_currRow[ J_Idx_wikiFile ] = currFile_wordProfile[ existWordList[ I_Idx_existWord ] ]
				break
		for i in xrange( len( Y_currRow ) ) :
			fileObject.write( str( Y_currRow[i]  ) + ' ' )
		fileObject.write('\n')
	fileObject.close()
	#--------------------------------------------------------------------------------------
	del fileObject , Y_currRow , I_Idx_existWord , J_Idx_wikiFile , currFile_wordProfile , i
	# --------------------------------------------------------------------------------------
if not os.path.isfile( 'Yt.txt' ) :
	fileObject = open( 'Yt.txt' , 'w' )
	Yt_currRow = np.zeros( wordNum )
	for I_Idx_wikiFile in xrange( fileNum ) :
		print "Writing file Yt.txt : %d / %d ..." %(I_Idx_wikiFile,fileNum)	
		currFile_wordProfile = wikiHash[ I_Idx_wikiFile ][ '_wordprofile' ]
		for J_Idx_existWord in xrange( wordNum ) :
			if currFile_wordProfile.has_key( existWordList[ J_Idx_existWord ] ) :
				Yt_currRow[ J_Idx_existWord ] = currFile_wordProfile[ existWordList[ J_Idx_existWord ] ]
		for i in xrange( len( Yt_currRow ) ) :
			fileObject.write( str( Yt_currRow[i] ) + ' ' )
		fileObject.write('\n')
	fileObject.close()
	#----------------------------------------------------------------------------------------
	del fileObject , Yt_currRow , I_Idx_wikiFile , J_Idx_existWord , currFile_wordProfile , i
	#----------------------------------------------------------------------------------------

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
iteraNum   = 15
# ------------------ #
# initialize A and S #
# ------------------ #
if os.path.isfile( 'A_init.txt' ) :
	print "Read initial matrix from A_init.txt !"
	A = DSP.READMATRIX( 'A_init.txt' , ' ' )
else :
	print "no previous initial A matrix is found !"
	A = np.random.ranf( [ wordNum , modelOrder ] )
	DSP.LOG( 'log matrix to file' , 'A_init.txt' , A , ' ' )
	print "initial matrix A is generated and logged to file A_init.txt !"
if os.path.isfile( 'S_init.txt' ) :
	print "Read initial matrix from S_init.txt !"
	S = DSP.READMATRIX( 'S_init.txt' , ' ' )
else :
	print "no previous initial S matrix is found !"
	S = np.random.ranf( [ modelOrder , fileNum ] )
	DSP.LOG( 'log matrix to file' , 'S_init.txt' , S , ' ' )
	print "initial matrix S is generated and logged to file S_init.txt !"

# ~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-= #
# define a step size for each round of NMF process #
# ~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-=~-= #
#NMF_OPERATION_STEPSIZE_inJ = 500
#NMF_OPERATION_STEPSIZE_inI = 8000
NMF_OPERATION_STEPSIZE_inJ = 1
NMF_OPERATION_STEPSIZE_inI = 1

# ------------- #
# NMF iteration #
# ------------- #
for cycle in xrange( iteraNum ) :
	# ------------- #
	# update S part #
	# ------------- #
	J_IDX_OPERATION_SUBSECTION_STARTING_INDEX = range( fileNum )[ ::NMF_OPERATION_STEPSIZE_inJ ]
	for J_Idx_wikiFile in J_IDX_OPERATION_SUBSECTION_STARTING_INDEX :
		print "Cycle No. : %d / %d\tFile No. : %d-%d / %d" %(cycle+1,iteraNum,J_Idx_wikiFile+1,np.min( [ J_Idx_wikiFile+NMF_OPERATION_STEPSIZE_inJ , fileNum ] ),fileNum )
		if J_Idx_wikiFile + NMF_OPERATION_STEPSIZE_inJ < fileNum : Y_blockWidth = NMF_OPERATION_STEPSIZE_inJ
		else : Y_blockWidth = fileNum - J_Idx_wikiFile
		Y_currCol = np.zeros( [ wordNum , Y_blockWidth ] )
		# --------------------------------------- #
		# obtain the corresponding Y column block #
		# --------------------------------------- #
		smallValueAsgn_cnt = 0
		for J_Idx_wikiFile_subIndexOffset in xrange( Y_blockWidth ) :
			for word in wikiHash[ J_Idx_wikiFile ][ '_wordprofile' ] :
				if existWord[ word ].has_key( J_Idx_wikiFile + J_Idx_wikiFile_subIndexOffset ) :
					Y_currCol[ existWordList_hash[word] , J_Idx_wikiFile_subIndexOffset ] = existWord[ word ][ J_Idx_wikiFile + J_Idx_wikiFile_subIndexOffset ]
			if np.max( Y_currCol[ : , J_Idx_wikiFile_subIndexOffset ] ) == 0.0 :
				Y_currCol[ : , J_Idx_wikiFile_subIndexOffset ] = 0.000000001
				smallValueAsgn_cnt += 1
		#print ""
		#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		#print "no. of all zeros column that  "
		#print "are assignment to a very small"
		#print "non-negative value : %d/%d" %(smallValueAsgn_cnt,Y_blockWidth)
		#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		#print ""
		#S_Jcolumn = NMF.HALS_CORE( np.matrix( Y_currCol ).transpose() , np.matrix( S[ : , J_Idx_wikiFile : J_Idx_wikiFile + Y_blockWidth ] ).transpose() , A.transpose() , modelOrder ).transpose()
		#print "Please stop here and perform manual LSMU"
		#print "Press any key to continue ..."
		#raw_input()
		S_Jcolumn = NMF.LSMU_CORE( np.matrix( Y_currCol ).transpose() , np.matrix( S[ : , J_Idx_wikiFile : J_Idx_wikiFile + Y_blockWidth ] ).transpose() , A.transpose() ).transpose()
		for k in xrange( modelOrder ) :
			for J_assignmentOffset in xrange( Y_blockWidth ) :
				S[ k , J_Idx_wikiFile + J_assignmentOffset ] = S_Jcolumn[ k , J_assignmentOffset ]
		# -------------------------------------- #
		# end of enforcing Sum To One constraint #
		# -------------------------------------- #
	#logFileName = 'S_HALS_itera'+str(cycle+1)+'.txt'
	logFileName = 'S_LSMU_itera'+str(cycle+1)+'.txt'
	DSP.LOG( 'log matrix to file' , logFileName , S , ' ' )
	print "S has been logged in cycle %d" %(cycle+1)
	DSP.STOP()
	# ------------- #
	# update A part #
	# ------------- #
	I_IDX_OPERATION_SUBSECTION_STARTING_INDEX = range( wordNum )[ ::NMF_OPERATION_STEPSIZE_inI ]
	for I_Idx_existWord in I_IDX_OPERATION_SUBSECTION_STARTING_INDEX :
		print "Cycle No. : %d / %d\tWord No. : %d-%d / %d" %(cycle+1,iteraNum,I_Idx_existWord+1,np.min( [ I_Idx_existWord+NMF_OPERATION_STEPSIZE_inI , wordNum ] ),wordNum)
		if I_Idx_existWord+NMF_OPERATION_STEPSIZE_inI < wordNum :
			Y_blockHeight = NMF_OPERATION_STEPSIZE_inI
		else :
			Y_blockHeight = wordNum - I_Idx_existWord
		# ------------------------------------ #
		# obtain the corresponding Y row block #			
		# ------------------------------------ #			
		#Y_currRow = np.zeros( fileNum )  			
		Y_currRow = np.zeros( [ Y_blockHeight , fileNum ] )
		for Idx_wikiFile in xrange( fileNum ) :
			currFile_wordProfile = wikiHash[ Idx_wikiFile ][ '_wordprofile' ]
			for I_Idx_existWord_subIndexOffset in xrange( Y_blockHeight ) :
				if currFile_wordProfile.has_key( existWordList[I_Idx_existWord] ) :
					Y_currRow[ I_Idx_existWord_subIndexOffset , Idx_wikiFile ] = currFile_wordProfile[ existWordList[ I_Idx_existWord + I_Idx_existWord_subIndexOffset ] ]
					break
		#A_Irow = NMF.HALS_CORE( np.matrix( Y_currRow ) , np.matrix( A[ I_Idx_existWord : I_Idx_existWord + Y_blockHeight , : ] ) , S , modelOrder )
		A_Irow = NMF.LSMU_CORE( np.matrix( Y_currRow ) , np.matrix( A[ I_Idx_existWord : I_Idx_existWord + Y_blockHeight , : ] ) , S )
		for I_assignmentOffset in xrange( Y_blockHeight ) :
			A[ I_Idx_existWord + I_assignmentOffset , : ] = A_Irow[ I_assignmentOffset , : ]
	#logFileName = 'A_HALS_itera'+str(cycle+1)+'.txt'
	logFileName = 'A_LSMU_itera'+str(cycle+1)+'.txt'
	DSP.LOG( 'log matrix to file' , logFileName , A , ' ' )
	print "A has been logged in cycle %d" %(cycle+1)
	print "Cycle %d has finished.  A and S has been logged." %(cycle+1)
	DSP.STOP()
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
del cycle , logFileName
del J_IDX_OPERATION_SUBSECTION_STARTING_INDEX , J_Idx_wikiFile  , Y_blockWidth  , Y_currCol ,                                       smallValueAsgn_cnt , J_Idx_wikiFile_subIndexOffset  , word , S_Jcolumn , k , J_assignmentOffset
del I_IDX_OPERATION_SUBSECTION_STARTING_INDEX , I_Idx_existWord , Y_blockHeight , Y_currRow , Idx_wikiFile , currFile_wordProfile ,                      I_Idx_existWord_subIndexOffset ,        A_Irow        , I_assignmentOffset
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

