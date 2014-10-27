# ======================= #
# util_clusterTextMain.py #
# ======================= #
# 
# matrix model : 
#          article ->
#              ar.1   ar.2   ar.3  ...
#                --------------------------------- 
# word profile  | |    | |    | |                 | 
#       |       | |    | |    | |                 | 
#       v       | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#               | |    | |    | |                 | 
#                ---------------------------------
import os
import numpy as np
import DSP
import NMF

# ==================================================== #
# Part I : obtain the dimension of Word Profile Matrix #
# ==================================================== #


########### ------------------------------------ #
########### obtain M by checking dictionary size #
########### ------------------------------------ #
##########
##########os.system('cp ../dictionary.np ./')
##########fileObject = open( 'dictionary.np' , 'r' )
##########dictLines  = fileObject.readlines()
##########fileObject.close()
##########WORDPROFILE_MATRIX_M = len( dictLines )
##########
##########
########### ------------------------------------------------------------ #
########### obtain N by checking number of articles in current directory #
########### ------------------------------------------------------------ #
##########
##########WORDPROFILE_MATRIX_N = DSP.READMATRIX( 'util_fileNum.cnt' )


# ====================================================================== #
# Part II : initialize A matrix and modelOrder , will fit S matrix first #
# ====================================================================== #

modelOrder = 20
A                          = np.random.ranf( [ WORDPROFILE_MATRIX_M , modelOrder ] ) * 6
S                          = np.zeros( [ modelOrder , WORKPROFILE_MATRIX_N ] )
WORKPROFILE_MATRIX_Jcolumn = np.zeros( [ WORKPROFILE_MATRIX_M , 1 ] )
#the below line requires a lot of memory usage
#WORDPROFILE_MATRIX = np.zeros( [ WORDPROFILE_MATRIX_M , WORDPROFILE_MATRIX_N ] )

for j in range( 0 , WORKPROFILE_MATRIX_N ) :
	# --------------------------- #
	# read the sparse vector info #
	# --------------------------- #
	
	if   j >= 1000000 and i < 10000000 :		sparsevec = DSP.READMATRIX(            str(i) + ".sparsevec" )
	elif j >= 100000  and i < 1000000  :		sparsevec = DSP.READMATRIX( "0"      + str(i) + ".sparsevec" )
	elif j >= 10000   and i < 100000   :		sparsevec = DSP.READMATRIX( "00"     + str(i) + ".sparsevec" )
	elif j >= 1000    and i < 10000    :		sparsevec = DSP.READMATRIX( "000"    + str(i) + ".sparsevec" )
	elif j >= 100     and i < 1000     :		sparsevec = DSP.READMATRIX( "0000"   + str(i) + ".sparsevec" )
	elif j >= 10      and i < 100      :		sparsevec = DSP.READMATRIX( "00000"  + str(i) + ".sparsevec" )
	elif j >= 0       and i < 10       :		sparsevec = DSP.READMATRIX( "000000" + str(i) + ".sparsevec" )
	
	# ---------------------------------------------------------- #
	# fill in the non-zero entry to the jth column of Big Matrix #
	# ---------------------------------------------------------- #
	
	sparsevec_M = sparsevec.shape[0]
	for i in range( 0 , sparsevec_M ) :
		WORDPROFILE_MATRIX_Jcolumn[ sparsevec[ i , 0] ] = sparsevec[ i , 1 ]

	# ------------------------------------------------------------ #
	# Part III(a) : perform NNLS clustering (update S Matrix part) #
	# ------------------------------------------------------------ #
	
	S_Jcolumn = DSP.NNLS( WORDPROFILE_MATRIX_Jcolumn , A )


# ================================ #
# change the model to Y' = S' * A' #
# ================================ #

# -------------------------------------------------- #
# read the sparse vector info (in transposed format) #
# -------------------------------------------------- #

for j in range( 0 , WORKPROFILE_MATRIX_A ) :

	

	# ------------------------------------------------------------ #
        # Part III(b) : perform NNLS clustering (update A Matrix part) #
        # ------------------------------------------------------------ #
        S_Jcolumn = DSP.NNLS( WORDPROFILE_MATRIX_Jcolumn , A )
        S[ : , j : j + 1 ] = S_Jcolumn



DSP.LOG( 'log matrix to file' , 'nmf_A.recov' , A , ' ' )
DSP.LOG( 'log matrix to file' , 'nmf_S.recov' , S , ' ' )
