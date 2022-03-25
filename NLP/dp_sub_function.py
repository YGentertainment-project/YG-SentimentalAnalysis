# 보조 함수
# gr에 대해 카운트하는 함수
def count_dict(Obj_count_dict, word):
    if word in Obj_count_dict:
        Obj_count_dict[word] += 1
    else:
        Obj_count_dict[word] = 1
    return Obj_count_dict
# 새로운 dp 구조를 만들어주는 함수
def make_dp_dict_num(e_id, m_id, morph, pos, ner, dp, gr):
    ret_dict = dict()
    ret_dict['e_id'] = e_id
    ret_dict['m_id'] = m_id
    ret_dict['morph'] = morph
    ret_dict['pos'] = pos
    ret_dict['ner'] = ner
    ret_dict['dp'] = dp
    ret_dict['gr'] = gr
    return ret_dict

def make_dp_dict(e_id, m_id, morph, pos, ner, dp, gr):
    new_e_id = list()
    for id in e_id:
        if id not in new_e_id:
            new_e_id.append(id)
    ret_dict = dict()
    ret_dict['e_id'] = new_e_id
    ret_dict['m_id'] = m_id
    ret_dict['morph'] = morph
    ret_dict['pos'] = pos
    ret_dict['ner'] = ner
    ret_dict['dp'] = dp
    ret_dict['gr'] = gr
    return ret_dict

# 같은 어절이면 붙여서 리턴, 다른 어절이면 띄어서 리턴
def join_morph(id1, id2, word1, word2):
    result = word1+word2
    if id1 != id2:
        result = word1 +" "+ word2 
    if len(word1) == 0:
        result = word2
    elif len(word2) == 0:
        result = word1
    return result

#Aspect 조건 확인 함수
import regex as re
def isAspect(word, pos, ner):
    flag = True
    other_char = re.findall(r'[^가-힣 ]', word)
    if len(word) <2:
        flag = False
    elif ('NNG' not in pos and 'XR' not in pos): 
        flag = False
    elif ner != 'O':
        flag = False
    elif len(other_char) > 0:
        flag = False
    if "FLD" in ner:
        flag = True
    return flag

#Opinion 조건 확인 함수
def isOpinion(word, pos, gr=''):
    #VCP는 살리는 형태
    flag = True
    if len(word) <2:
        flag = False
    elif pos[:2] in ['EC','EF']:
        flag = False
    elif 'SC' == pos:
        flag = False
    elif 'J' == pos[0]:
        flag = False  
    return flag

# ner이 Other 또는 FLD-B인지 확인하는 함수
def check_ner(ner_list):
    flag = False
    for ner in ner_list:
        if ner != 'O':
            flag = True
            break
    return flag

# NP word의 자격을 검사하는 함수
def get_NP_word(morph_list, gr_list, pos_list=[], exclude_gr=["NP_SBJ","NP_OBJ"]):
    ret_word = ""
    flag = False
    cnt = 0
    idx = -1
    if morph_list[0] in  ['의','가','이','은','들','는','좀','잘','걍','과','도','를','을','로','으로','자','에','와','한','하다', '던', '든','에서','요','랑', '라던', '고', '듯', '쯤']:
        flag = True
        return ret_word, flag
    if len(pos_list) > 0:
        for pos in pos_list:
            if pos[0] == "J" or pos == "NNB":
                idx = cnt
                flag = True
                break
            cnt+=1
    if idx != -1:
        ret_word = "".join(morph_list[:idx])
        flag = True   
    elif gr_list[-1] in exclude_gr:
        ret_word = "".join(morph_list[:-1])
        flag = True
    else:
        ret_word = "".join(morph_list)
    return ret_word, flag

# VP word의 자격을 검사하는 함수
def get_VP_word(morph_list, pos_list, gr_list, exclude_gr=["VP_SBJ","VP_OBJ"]):
    ret_word = ""
    flag = False
    if gr_list[-1] in exclude_gr:
        ret_word = "".join(morph_list[:-1])
        flag = True
    elif "EC" in pos_list[-1]:
        ret_word = "".join(morph_list[:-1])
    elif "EP" in pos_list[-1]:
        original_morph = morph_list[-1]
        change_morph=""
        sample_dict = {"였":"이","했":"하", "올랐":"오르","몄":"미","났":"나","냈":"내","왔":"오","됐":"되","켰":"키"}
        for key in sample_dict.keys():
            if key in change_morph:
                change_morph = key
                break
        if change_morph != "":
            ret_word = "".join(morph_list[:-1])
            ret_word += original_morph.replace(change_morph,sample_dict[change_morph])
        else:
            ret_word = "".join(morph_list)
    else:
        ret_word = "".join(morph_list)
    return ret_word, flag