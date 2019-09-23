import regex as re
import argparse
import os
import json
from pythainlp import word_tokenize
import random
from rules import RULEs
from stop_words import STOP_WORDS

def parse_arguments():
    """
        Parse the command line arguments of the program.
    """

    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')
    parser.add_argument(
        "-r",
        "--report_dir",
        type=str,
        nargs="?",
        help="The report directory in .txt extension",
        default="report.txt",
    )
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        nargs="?",
        help="The raw data directory in .json extension",
        default=""
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        nargs="?",
        help="'squard' or 'iapp'",
        default=""
    )
    parser.add_argument(
        "-en",
        "--engine",
        type=str,
        nargs="?",
        help="Tokenizer to use ==> from pythainlp, for example: 'deepcut' or 'mm'",
        default="mm"
    )
    parser.add_argument(
        "-d",
        "--dictionary_dir",
        type=str,
        nargs="?",
        help="The dictionary directory in .txt extension",
        default='dictionary.txt'
    )
    parser.add_argument(
        "-tr",
        "--output_train_dir",
        type=str,
        nargs="?",
        help="The training set directory in .json extension ==> convert into SQUARD format",
        default="train.json"
    )
    parser.add_argument(
        "-te",
        "--output_test_dir",
        type=str,
        nargs="?",
        help="The test set directory in .json extension ==> convert into SQUARD format",
        default="test.json"
    )
    parser.add_argument(
        "-p",
        "--train_percent",
        type=int,
        nargs="?",
        help="Percentage of train-test spliting",
        default="80"
    )
    return parser.parse_args()

def cut_and_clean_blank(string_in,engine,stop_words,rules):
    regex = re.compile(r'[\n\r\t]')#clear special characters
    string_in = string_in.lower()
    string_in = regex.sub("  ", string_in)
    string_in = re.sub(r'[^A-Za-z0-9ก-๙\.-]', r'  ', string_in)#clear all other languages out
    for string_to_be_replaced, string_to_replace in rules:#clear all special charaters according to RULEs 
        string_in = re.sub(string_to_be_replaced, string_to_replace, string_in)
    string_in = " ".join(string_in.split())
    string_out = word_tokenize(string_in,engine = engine)
    string_out = [x.strip().lower() for x in string_out if x != ' ' and x != '' and x != '  ' and x!= '    ']#get blanks off
#   Kobkrit
#     current_stop_words = set(string_out) & stop_words
#     for i in current_stop_words:
#         string_out.remove(i)
    string_out = [x for x in string_out if x != ' ' and x != '' and x != '  ' and x!= '    ']
    return ' '.join(string_out)

def gen_question_id(count, data_format):
    ID = '0'*(23-len(str(count))) + str(count)
    if data_format == 'iapp':
        return '0' + ID
    else:#can be extended to '2' + ID, '3' + ID, ..... if more than 2 formats are used
        return '1' + ID
    

def gen_dictoinary(word_set, dictionary_dir):
    word_set = list(word_set)
    t_index = 0
    with open(dictionary_dir,"w",encoding='utf-8') as file:
        for i in range(len(word_set)+2):
            if i == 0:
                file.write("[PAD]" + "\n") 
            elif i == 101:
                file.write("[CLS]" + "\n")
            elif i == 102:
                file.write("[SEP]" + "\n")
            else:
                file.write(word_set[t_index] + "\n")
                t_index = t_index + 1
        file.write(word_set[t_index])

def write_report_for_iapp_format(cnt_tr_sample, cnt_te_sample, cnt_tr_paragraph, cnt_te_paragraph, report_dir):
    with open(report_dir,"w",encoding='utf-8') as file:
        file.write("#######summary for iapp format#######\n")
        file.write('total_train_paragraphs: '+str(cnt_tr_paragraph)+'\n')
        file.write('total_test_paragraphs: '+str(cnt_te_paragraph)+'\n')
        file.write('total_train_samples: '+str(cnt_tr_sample)+'\n')
        file.write('total_test_samples: '+str(cnt_te_sample)+'\n')
        file.write('Note: There might be some overlapping paragraphs due to randomly train-test separating')
        
def write_report_for_squard_format(cnt_sample, cnt_broken_sample, report_dir):
    with open(report_dir,"w",encoding='utf-8') as file:
        file.write("#######summary for SQUARD format#######\n")
        file.write('total_usable_samples: '+str(cnt_sample)+'\n')
        file.write('total_broken_samples: '+str(cnt_broken_sample)+'\n')

def main():
    dictionary = set()#define dictionary
    
    args = parse_arguments()
    
    if args.input_dir == "":
        raise TypeError("Wrong input directory")
    
    ##############################
    #######count for report ######
    ##############################
    cnt_broken_sample = 0
    cnt_sample = 0
    cnt_train_sample = 0
    cnt_test_sample = 0
    cnt_train_paragraph = 0
    cnt_test_paragraph = 0
    
    with open(args.input_dir, 'r', encoding="utf8") as fp:
        obj1 = json.load(fp)
    if args.format == 'squard':
        ################################
        for story in range(len(obj1['data'])):
            obj1['data'][story]['title'] = cut_and_clean_blank(obj1['data'][story]['title']\
                                                                   , args.engine, STOP_WORDS, RULEs)
            dictionary = dictionary | set(obj1['data'][story]['title'].split())
            for paragraph in range(len(obj1['data'][story]['paragraphs'])):
                obj1['data'][story]['paragraphs'][paragraph]['context'] = \
                cut_and_clean_blank(obj1['data'][story]['paragraphs'][paragraph]['context'],\
                                    args.engine, STOP_WORDS, RULEs)
                dictionary = dictionary | set(obj1['data'][story]['paragraphs'][paragraph]['context'].split())
                broken_sample = []
                for qa in range(len(obj1['data'][story]['paragraphs'][paragraph]['qas'])):
                    obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['question'] = \
                    cut_and_clean_blank(obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['question'],\
                                        args.engine, STOP_WORDS, RULEs)
                    dictionary = dictionary | set(obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['question'].split())
                    if len(obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['answers']) > 1:
                        obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['answers'] = \
                        [{"text": cut_and_clean_blank(obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['answers'][0]['text'],\
                                                      'mm', STOP_WORDS, RULEs)
                         }]
                        dictionary = dictionary | set(obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['answers'][0]['text'].split())
                        cnt_sample = cnt_sample + 1
                    else:
                        broken_sample.append(qa)
                        continue
                    obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['answers'][0]['answer_start'] = \
                    obj1['data'][story]['paragraphs'][paragraph]['context'].index(obj1['data'][story]['paragraphs'][paragraph]['qas'][qa]['answers'][0]['text'])
                broken_sample.sort(reverse = True)
                cnt_broken_sample = cnt_broken_sample + len(broken_sample)
                for sample in broken_sample:
                    del obj1['data'][story]['paragraphs'][paragraph]['qas'][sample]
        
        with open(args.output_train_dir, 'w',encoding="utf8") as json_file:
            json.dump(obj1, json_file,ensure_ascii=False)
        gen_dictoinary(dictionary, args.dictionary_dir)
        write_report_for_squard_format(cnt_sample, cnt_broken_sample, args.report_dir)
    
    
    elif args.format == 'iapp':
        data_train = []
        data_test = []
        for U_id in obj1['db']:
            if 'detail' in obj1['db'][U_id]:
                tmp_paragraph = cut_and_clean_blank(obj1['db'][U_id]['detail'], args.engine, STOP_WORDS, RULEs)
                dictionary = dictionary | set(tmp_paragraph.split())
                qa_list_train = []
                qa_list_test = []
                for QA in obj1['db'][U_id]['QA']:
                    tmp_question = cut_and_clean_blank(QA['q'], args.engine, STOP_WORDS, RULEs)
                    dictionary = dictionary | set(tmp_question.split())
                    cnt_sample = cnt_sample + 1
                    if len(QA['a']) > 0:
                        tmp_answer = {'text': cut_and_clean_blank(' '.join(QA['a'])\
                                                                  , args.engine, STOP_WORDS, RULEs)}

                        try:
                            tmp_answer['answer_start'] = tmp_paragraph.index(tmp_answer['text'])
                        except:
                            cnt_broken_sample = cnt_broken_sample + 1
                            continue
                        dictionary = dictionary | set(tmp_answer['text'].split())
                    else:
                        cnt_broken_sample = cnt_broken_sample + 1
                        continue
                    if random.uniform(0,1) < (args.train_percent)/100:
                        cnt_train_sample = cnt_train_sample + 1
                        qa_list_train.append({'question': tmp_question, 'is_impossible': False,\
                                              'id': gen_question_id(cnt_sample, args.format), 'answers': [tmp_answer]})
                    else:
                        cnt_test_sample = cnt_test_sample + 1
                        qa_list_test.append({'question': tmp_question, 'is_impossible': False,\
                                              'id': gen_question_id(cnt_sample, args.format), 'answers': [tmp_answer]})
                if len(qa_list_train) > 0:
                    cnt_train_paragraph = cnt_train_paragraph + 1
                    data_train.append({'title': obj1['db'][U_id]['title'], 'paragraphs':\
                                       [{'context': tmp_paragraph, 'qas': qa_list_train}]})
                if len(qa_list_test) > 0:
                    cnt_test_paragraph = cnt_test_paragraph + 1
                    data_test.append({'title': obj1['db'][U_id]['title'], 'paragraphs':\
                                       [{'context': tmp_paragraph, 'qas': qa_list_test}]})
                    
        
        with open(args.output_train_dir, 'w',encoding="utf8") as json_file:  
            json.dump({'version': 'v2.0', 'data': data_train}, json_file,ensure_ascii=False)
        with open(args.output_test_dir, 'w',encoding="utf8") as json_file:  
            json.dump({'version': 'v2.0', 'data': data_test}, json_file,ensure_ascii=False)
        gen_dictoinary(dictionary, args.dictionary_dir)
        write_report_for_iapp_format(cnt_train_sample, cnt_test_sample, cnt_train_paragraph,\
                                     cnt_test_paragraph, args.report_dir)
    else:
        raise TypeError("Wrong input format")

if __name__ == '__main__':
    main()