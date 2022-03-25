# AEOP태킹
# 딕셔너리 리스트 전달
def compare_init_vp(vp, morph):
    flag_all = True
    vp_split = vp.split(" ")
    morph_split = morph.split(" ")
    #띄어쓰기 개수 다르면 false
    if len(morph_split) != len(vp_split):
      flag_all = False
    elif len(morph_split) > 1:
      #  두 어절 이상이면 처음 부분이 같으면 
      for i in range(len(morph_split)-1):
        if(morph_split[i] != vp_split[i]):
          flag_all = False
    return flag_all
def tag_aeop(dp, vp_word_list, np_word_list):
  cnt1=0
  cnt2=0
  cnt3=0
  cnt = 0
  VP_NP_list1 = list()
  VP_NP_list2 = list()
  aeop_list = list()
  RawSentence = dp['RawSentence']
  data = dp['data']
  lendata = len(data)
  print(lendata,"건의 문장에 대한 AEOP 태깅 시작...")
  for morph_list in data:

    if cnt % 20000 == 1:
      print(cnt,"개 문장 태깅...",round(cnt*100/lendata,1),"%")
      print(aeop_list[-1])

    # 태깅 준비
    sentence_list = list()
    for i in range(len(morph_list)):
      word_dict = {
          'e_id': 0, 
          'm_id': 0, 
          'morph': '', 
          'pos': '', 
          'ner': '', 
          'dp': 0, 
          'gr': '',
          'aeop':''
      }
      sentence_list.append(word_dict)
    
    O_num = 0
    idx=0
    for morph_dict in morph_list:
      for key in morph_dict.keys():
          sentence_list[idx][key] = morph_dict[key]
      # print("after:", sentence_list[idx])
      #vp 전체에 대해 순회하면서 문장에서 vp가 포함되는 경우를 찾을 것임
      for vp in vp_word_list:
        
        morph = morph_dict['morph']
        # 단순 in 사용하지 말고 처음부터 포함되어야한다.
        vp_size = len(vp)
        # 오피니언 후보 중 vp 사이즈가 현재 어절의 길이보다 크면 스킵
        if vp_size > len(morph):
          continue
        
        flag_compare = compare_init_vp(vp, morph)
        
        if vp == morph[:vp_size] and flag_compare:
          cnt2 += 1
          sentence_list[idx]['aeop'] = 'O_'+ str(O_num)
          sentence_list[idx]['morph'] = morph
          A_num = O_num
          O_num += 1
          # 1. 앞에서 수식해주는 VP_MOD를 찾는다.
          # 2. 뒤에서 수식해주는 NP 나 VP를 찾는다.
          for temp_morph in morph_list:
            # 두 어절의 e_id 가 같으면 수식관계로 보지 않는다
            if temp_morph['e_id'] == morph_dict['e_id']:
              continue
            index = temp_morph['m_id'] - 1
            compare_morph = temp_morph['morph']
            # (1) 현재 vp가 수식하는 어절(지배소), (2) NP(피지배소) (3,4) 숫자 기호(S-), 조사(J-) 제외
            if ((morph_dict['dp'] in temp_morph['e_id']) 
                and temp_morph['gr'][:2] == 'NP' 
                and (temp_morph['pos'][0] not in ['S','J'] 
                and morph_dict['pos'][0] not in ['S','J'])) :
              for np in np_word_list:
                np_size = len(np)
                if np_size >len(compare_morph):
                  continue
                if np == compare_morph[:np_size] and temp_morph['ner'][0] in ["O", "F"] and temp_morph['ner'] not in ['ORG-B', 'ORG-I']:
                  # print("np: ",np, 'A_'+ str(A_num))
                  VP_NP_list1.append([vp, np])
                  sentence_list[index]['aeop'] = 'A_'+ str(A_num)
                  sentence_list[index]['morph'] = compare_morph
                  # print(sentence_list[index]['aeop'], sentence_list[index]['morph'])
                  # print(index, sentence_list)
                  break
            elif (temp_morph['dp'] in morph_dict['e_id']) and temp_morph['gr'][:2] == 'NP' and (temp_morph['pos'][0] not in ['S','J'] and morph_dict['pos'][0] not in ['S','J']):
              for np in np_word_list:
                np_size = len(np)
                if np_size >len(compare_morph):
                  continue
                # ner이 O나 FLD인 경우에만 aspect가 될 수 있다
                if np == compare_morph[:np_size] and temp_morph['ner'][0] in ["O","F"] and temp_morph['ner'] not in ['ORG-B', 'ORG-I']:
                  VP_NP_list2.append([np, vp])
                  sentence_list[index]['aeop'] = 'A_'+ str(A_num)
                  sentence_list[index]['morph'] = compare_morph
                  break
          break # 카운트만 하고 NP로 찾은 쌍이랑 차이를 보면 될듯 하다
      
      idx += 1
    result_dict=dict()
    result_dict['RawSentence'] = RawSentence[cnt]
    result_dict['data'] = sentence_list
    aeop_list.append(result_dict)
    cnt += 1
  print(cnt1, " ", cnt2, " ", cnt3)
  return aeop_list, VP_NP_list1, VP_NP_list2