# Preprocessing_for_THAI_BERT

## What is it for?
These codes convert raw Q&A data into the SQUARD format because in order to finetune BERT model from https://github.com/google-research/bert. 

## Processing step
1.Clear \n, \r, \t.  
2.In case of English, we convert into lowercase.  
3.Clear all other languages, for example, hindi, chinese.  
4.Clear all special characters according to "rules.py", for example, (".", " . ") means substitude "." by " . ". You can add others if needed.  
5.Apply a word tokenizer to sentences, questions and answers. You can choose a tokenizer from https://github.com/PyThaiNLP/pythainlp.  
6.Clear all stop words. See "stop_words.py"

## Outputs
1.A reporting file tells about the details of output data in SQUARD format. (in .txt)  
2.A dictionary file in .txt. (for every words found in raw data input)  
3.A training file in .json. (in SQUARD format)  
4.A test file in .json and SQUARD format. (only for iapp format)  

## input arguments
1.-r => The report directory in .txt extension => default: .\report.txt  
2.-i => The raw data directory in .json extension **required  
3.-f => The input format (squard or iapp) **required  
4.-en => Tokenizer to use ==> from pythainlp, for example: deepcut or mm => default: mm  
5.-d => The dictionary directory in .txt extension => default: .\dictionary.txt  
6.-tr => The training set directory in .json extension ==> convert into SQUARD format => default: train.json  
7.-te => The test set directory in .json extension ==> convert into SQUARD format => default: test.json  
8.-p => Percentage of train-test spliting (only for iapp format) for training set => default: 80

## Example of input
python run.py -i squard.json -f squard -en deepcut  
python run.py -i iapp.json -f iapp -en newmm -p 90