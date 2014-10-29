wiki_learning
=============

Background:

Text learning is to classify a sea of texts into certain categories.
This project, namely wiki_learning, self-states the purpose that Wikipedia texts are aimed to be clustered into some group such that the texts within a single group has their content mutually related.

How To Do:

For each file, all punctuations are removed and the remaining words are sorted.
The frequency of occurance of the existing words in each file are calculated and is presented as a column vector.
When these column vectors, each representing the word profile of a text file, are gathered together form a big matrix, Non-Negative Matrix Factorization (NMF) can be employed to help classify the texts.

Mathematical model:

Y = A * S , with model order takens as K

Y (MxN):= big matrix with cN olumn vectors representing the word profile of N files

A (MxK):= 'pure text' matrix, where each column vector represents the word profile of a 'pure text' corresponding to the column subject.  There are M words exist in the entire considered text assembly.  

S (KxN):= abundance (proportion) of the 'pure text' that contributes to those N files
