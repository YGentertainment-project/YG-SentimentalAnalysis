import re
import os
import json
import torch
import langid
import pymongo
import unicodedata
import numpy as np

from jamo import j2h
from tqdm import tqdm
from shutil import copyfile
from konlpy.tag import Mecab
from datetime import datetime
from hanspell import spell_checker
from soyspacing.countbase import CountSpace
from transformers import PreTrainedTokenizer
from pymongo.errors import DuplicateKeyError
from transformers import AutoModelForTokenClassification
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler

MONGO_ADDR='150.230.34.147'
MONGO_PORT=27017
MONGO_DB='crawling_tuto'
MONGO_USER='ygenter'
MONGO_PSWD='ygenter'

VOCAB_FILES_NAMES = {"vocab_file": "tokenizer_78b3253a26.model",
                     "vocab_txt": "vocab.txt"}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "monologg/kobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert/tokenizer_78b3253a26.model",
        "monologg/kobert-lm": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert-lm/tokenizer_78b3253a26.model",
        "monologg/distilkobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/distilkobert/tokenizer_78b3253a26.model"
    },
    "vocab_txt": {
        "monologg/kobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert/vocab.txt",
        "monologg/kobert-lm": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert-lm/vocab.txt",
        "monologg/distilkobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/distilkobert/vocab.txt"
    }
}

PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "monologg/kobert": 512,
    "monologg/kobert-lm": 512,
    "monologg/distilkobert": 512
}

PRETRAINED_INIT_CONFIGURATION = {
    "monologg/kobert": {"do_lower_case": False},
    "monologg/kobert-lm": {"do_lower_case": False},
    "monologg/distilkobert": {"do_lower_case": False}
}

SPIECE_UNDERLINE = u'▁'


class TextCleaner():
    '''
    Text Cleaner
    
    Remove Noise by regular expression and extract special tokens
    Check language and Correct spelling and spacing
    
    Attributes:
        cfg (List[Dict[str: str]]): Cleaning Rule List
        spacing_model (soyspacing.countbase.CountSpace): Spacing correction model
    
    methods
     * load_spacing_model: load soyspacing model
     * get_lang: get language code of sentence
     * remove_stopwords: 
     * cleaning_data: 
    '''
    def __init__(
                 self, 
                 path="./crawler/NLP_engine/CleaningRule.cfg", 
                 verbose=False):
        '''
        Text Cleaner initilizer
        
        Args:
            path (str, default: './crawler/NLP_engine/CleaningRule.cfg'): 
                Cleaning rule cfg file path
                Cleaning Rule File: JSON format
                List[Dict('name': str, 'type': str, 'regex': str, 'target': str)]
                * name (str): rule name
                * type (str): 
                    * "sub": replace "regex" to "target"
                    * "extract": extract "regex" to ret_dict[target]
                * regex (str): Regular expression of step
                * target (str): Target of cleaning Rule
                
                ex) Cleaning 'Very Funny, 😀😀😀'
                    {
                        'name': 'Remove Emoji',
                        'type': 'extract',
                        'regex': '[\\u2700-\\u27BF]|[\\u2011-\\u26FF]|[\\u2900-\\u2b59]'
                        'target': 'emoji'
                    }
                    
                    Method cleaning_data returns
                    ('True', 'Very Funny,', {'emoji': ['😀']}
            verbose (boolean, default: True): Enable debug mode
                print debug log to stdout
        '''
        with open(path, encoding='utf-8') as jsonfile:
            self.cfg = json.load(jsonfile)
        if verbose:
            for rule in self.cfg:
                print(rule)
        self.spacing_model = None

    def load_spacing_model(self, model_path):
        '''
        Load soyspacing Countspace model
        
        Args:
            model_path (str): model path
        '''
        self.spacing_model = CountSpace()
        self.spacing_model.load_model(model_path)

    def get_lang(self, sentence):
        '''
        Get language id from sentence
        
        Args:
            sentence (str): Input sentence
        
        Returns:
            language_id (str): ISO Language id 
                ex)'ko', 'en'
        '''
        lang = langid.classify(sentence)
        return lang[0]
    
    def cleaning_data(self, sent: str, spacing=False, verbose=False):
        '''
        Cleaning Sentence
        
        Args:
            sent (str): target sentence
            spacing (bool, default: False): Enable spacing check mode
            verbose (bool, default: False): Enable debug log print to stdout
        
        Returns: 
            It has two different return type
                True , sentence , ret_dict : 
                    if cleaning success and not filtered by sum options,
                    sentence (str): clean sentence 
                    ret_dict (Dict[str: List[str]]): Extracted strings
                False, reason: 
                    reason (str): Filtered reason
        '''
        
        # If Spacing 
        if spacing and not self.spacing_model:
            return False, 'Load Spacing Model First'

        # Merge splitted ja, mo
        # ex) ㅇㅖㅅㅣ -> 예시
        splited_word = re.findall(r'[ㄱ-ㅎ][ㅏ-ㅣ]', sent)
        for k in range(len(splited_word)):
            if verbose:
                print(f'Merge Jamo: {splited_word[k]} -> {j2h(splited_word[k][0], splited_word[k][1])}')
            sent = re.sub(splited_word[k], j2h(splited_word[k][0], splited_word[k][1]), sent)

        ret_dict = {}
        # Cleaning Step
        for idx, step in enumerate(self.cfg):
            if verbose:
                print(f'Step #{idx + 1}: {step["name"]}')
            # mode 'sub' replace regex to target
            if step['type'] == 'sub':
                sent = re.sub(step['regex'], step['target'], sent)
            # mode 'extract' extract regex to ret_dict[target]
            if step['type'] == 'extract':
                if step['target'] not in ret_dict:
                    ret_dict[step['target']] = []
                ret_dict[step['target']] += re.findall(step['regex'], sent)
                if verbose:
                    print(f'Extract: {re.findall(step["regex"], sent)}')
                sent = re.sub(step['regex'], '', sent)
            if verbose:
                print('->{}'.format(sent))

        # Languages Detection
        # Split sentence and Detect language for each part
        # Only "ko", "ko" pair can pass
        sentence_len = len(sent)
        pivot = sentence_len // 2
        lang1 = self.get_lang(sent[:pivot])
        lang2 = self.get_lang(sent[pivot:])
        if verbose:
            print('Language Detection')
            print(f'Part 1\'s Language: {lang1}')
            print(f'Part 2\'s Language: {lang2}')
        ret_dict['lang'] = [lang1, lang2]
        if ret_dict['lang'][0] != 'ko' or ret_dict['lang'][1] != 'ko':
            return False, f'Filter by Language: {lang1} {lang2} | {sent}'

        # Spacing and Spell check
        if spacing:
            if verbose:
                print('Spell Check')
            # 띄어쓰기 필터링
            sent_nospace_before = re.sub(' ', '', sent)
            # While loop for hanspell's error
            while True:
                try:
                    sent_spell_checked = spell_checker.check(sent).checked
                    break
                except:
                    pass
            sent_nospace_after = re.sub(' ', '', sent_spell_checked)
            if verbose:
                print(f'->{sent_spell_checked}')
            # Compare Spell changed, We ignore when spelling is changed 
            # for ignore hanspell correct the proper noun
            if sent_nospace_before == sent_nospace_after:
                sent = sent_spell_checked
                if verbose:
                    print(f'->{sent}')
            elif verbose:
                print(f'Spell Changed -> Revert')
            # SoySpacing 사용
            if verbose:
                print('Soyspacing')
            # Spacing check with soyspacing
            sent, tags = self.spacing_model.correct(
                doc=sent,
                force_abs_threshold=0.5,
                nonspace_threshold=-0.1,
                space_threshold=0.1,
                min_count=3
            )

            if verbose:
                print(f'->{sent}')
        return True, sent, ret_dict


class BertTokenizer(PreTrainedTokenizer):
    """
        SentencePiece based tokenizer. Peculiarities:
            - requires `SentencePiece <https://github.com/google/sentencepiece>`_
    """
    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    pretrained_init_configuration = PRETRAINED_INIT_CONFIGURATION
    max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES

    def __init__(
            self,
            vocab_file,
            vocab_txt,
            do_lower_case=False,
            remove_space=True,
            keep_accents=False,
            unk_token="[UNK]",
            sep_token="[SEP]",
            pad_token="[PAD]",
            cls_token="[CLS]",
            mask_token="[MASK]",
            **kwargs):
        super().__init__(
            unk_token=unk_token,
            sep_token=sep_token,
            pad_token=pad_token,
            cls_token=cls_token,
            mask_token=mask_token,
            **kwargs
        )

        # Build vocab
        self.token2idx = dict()
        self.idx2token = []
        with open(vocab_txt, 'r', encoding='utf-8') as f:
            for idx, token in enumerate(f):
                token = token.strip()
                self.token2idx[token] = idx
                self.idx2token.append(token)

        try:
            import sentencepiece as spm
        except ImportError:
            pass

        self.do_lower_case = do_lower_case
        self.remove_space = remove_space
        self.keep_accents = keep_accents
        self.vocab_file = vocab_file
        self.vocab_txt = vocab_txt

        self.sp_model = spm.SentencePieceProcessor()
        self.sp_model.Load(vocab_file)

    @property
    def vocab_size(self):
        return len(self.idx2token)

    def get_vocab(self):
        return dict(self.token2idx, **self.added_tokens_encoder)

    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        return state

    def __setstate__(self, d):
        self.__dict__ = d
        try:
            import sentencepiece as spm
        except ImportError:
            pass
        self.sp_model = spm.SentencePieceProcessor()
        self.sp_model.Load(self.vocab_file)

    def preprocess_text(self, inputs):
        if self.remove_space:
            outputs = " ".join(inputs.strip().split())
        else:
            outputs = inputs
        outputs = outputs.replace("``", '"').replace("''", '"')

        if not self.keep_accents:
            outputs = unicodedata.normalize('NFKD', outputs)
            outputs = "".join([c for c in outputs if not unicodedata.combining(c)])
        if self.do_lower_case:
            outputs = outputs.lower()

        return outputs

    def _tokenize(self, text, return_unicode=True, sample=False):
        """ Tokenize a string. """
        text = self.preprocess_text(text)

        if not sample:
            pieces = self.sp_model.EncodeAsPieces(text)
        else:
            pieces = self.sp_model.SampleEncodeAsPieces(text, 64, 0.1)
        new_pieces = []
        for piece in pieces:
            if len(piece) > 1 and piece[-1] == str(",") and piece[-2].isdigit():
                cur_pieces = self.sp_model.EncodeAsPieces(piece[:-1].replace(SPIECE_UNDERLINE, ""))
                if piece[0] != SPIECE_UNDERLINE and cur_pieces[0][0] == SPIECE_UNDERLINE:
                    if len(cur_pieces[0]) == 1:
                        cur_pieces = cur_pieces[1:]
                    else:
                        cur_pieces[0] = cur_pieces[0][1:]
                cur_pieces.append(piece[-1])
                new_pieces.extend(cur_pieces)
            else:
                new_pieces.append(piece)

        return new_pieces

    def _convert_token_to_id(self, token):
        """ Converts a token (str/unicode) in an id using the vocab. """
        return self.token2idx.get(token, self.token2idx[self.unk_token])

    def _convert_id_to_token(self, index, return_unicode=True):
        """Converts an index (integer) in a token (string/unicode) using the vocab."""
        return self.idx2token[index]

    def convert_tokens_to_string(self, tokens):
        """Converts a sequence of tokens (strings for sub-words) in a single string."""
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string

    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification tasks
        by concatenating and adding special tokens.
        A KoBERT sequence has the following format:
            single sequence: [CLS] X [SEP]
            pair of sequences: [CLS] A [SEP] B [SEP]
        """
        if token_ids_1 is None:
            return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + token_ids_1 + sep

    def get_special_tokens_mask(self, token_ids_0, token_ids_1=None, already_has_special_tokens=False):
        """
        Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
        special tokens using the tokenizer ``prepare_for_model`` or ``encode_plus`` methods.
        Args:
            token_ids_0: list of ids (must not contain special tokens)
            token_ids_1: Optional list of ids (must not contain special tokens), necessary when fetching sequence ids
                for sequence pairs
            already_has_special_tokens: (default False) Set to True if the token list is already formated with
                special tokens for the model
        Returns:
            A list of integers in the range [0, 1]: 0 for a special token, 1 for a sequence token.
        """

        if already_has_special_tokens:
            if token_ids_1 is not None:
                raise ValueError(
                    "You should not supply a second sequence if the provided sequence of "
                    "ids is already formated with special tokens for the model."
                )
            return list(map(lambda x: 1 if x in [self.sep_token_id, self.cls_token_id] else 0, token_ids_0))

        if token_ids_1 is not None:
            return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]

    def create_token_type_ids_from_sequences(self, token_ids_0, token_ids_1=None):
        """
        Creates a mask from the two sequences passed to be used in a sequence-pair classification task.
        A KoBERT sequence pair mask has the following format:
        0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1
        | first sequence    | second sequence
        if token_ids_1 is None, only returns the first portion of the mask (0's).
        """
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None:
            return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]

    def save_vocabulary(self, save_directory):
        """ Save the sentencepiece vocabulary (copy original file) and special tokens file
            to a directory.
        """
        if not os.path.isdir(save_directory):
            pass
            return

        # 1. Save sentencepiece model
        out_vocab_model = os.path.join(save_directory, VOCAB_FILES_NAMES["vocab_file"])

        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_model):
            copyfile(self.vocab_file, out_vocab_model)

        # 2. Save vocab.txt
        index = 0
        out_vocab_txt = os.path.join(save_directory, VOCAB_FILES_NAMES["vocab_txt"])
        with open(out_vocab_txt, "w", encoding="utf-8") as writer:
            for token, token_index in sorted(self.token2idx.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    pass
                    index = token_index
                writer.write(token + "\n")
                index += 1

        return out_vocab_model, out_vocab_txt


class NLP_Engine:
    '''
    NLP Engine 
    
    Attributes:
        ner_model_path (str): Named Entity Recognition Model's path
        absa_model_path (str): Aspect Based Sentimental Analysis Model's path
        ner_model (AutoModelForTokenClassification): Named Entity Recognition Model
        absa_model (AutoModelForTokenClassification): Aspect Based Sentimental Analysis Model
        pos_model (Mecab): Part Of Speech Model, Mecab
        device (str): Model Device
        tokenizer (BertTokenizer): Bert Tokenizer for ner, absa model
    '''
    def __init__(self,
                 ner_model_path='crawler/NLP_engine/ner_model',
                 absa_model_path='crawler/NLP_engine/absa_model',
                 device="cuda" if torch.cuda.is_available() else "cpu"
                ) -> None:
        '''
        NLP Engine Initializer
        
        Args:
            ner_model_path (str, default: ./ner_model): ner model's path
            absa_model_path (str, default: ./absa_model): ner model's path
            device (str, default: 'cuda' or 'cpu'): model's device
                If gpu is available 'cuda', else 'cpu'
        '''
        self.ner_model_path = ner_model_path
        self.absa_model_path = absa_model_path
        self.pos_model = Mecab()
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained('monologg/kobert')
        self.load_ner_model()
        self.load_absa_model()

    def load_ner_model(self):
        '''
        Load Named Entity Recongnition Model
        
        load model to devicde from ner_model_path
        '''
        # Check whether model exists
        if not os.path.exists(self.ner_model_path):
            raise Exception("Model Path Error")

        try:
            self.ner_model = AutoModelForTokenClassification.from_pretrained(self.ner_model_path)
            self.ner_model.to(self.device)
            self.ner_model.eval()
        except:
            raise Exception("Some model files might be missing...")
    
    def load_absa_model(self):
        '''
        Load Aspect Based Sentimental Analysis Model
        
        load model to devicde from absa_model_path
        '''
        # Check whether model exists
        if not os.path.exists(self.absa_model_path):
            raise Exception("Model Path Error")

        try:
            self.absa_model = AutoModelForTokenClassification.from_pretrained(self.absa_model_path)
            self.absa_model.to(self.device)
            self.absa_model.eval()
        except:
            raise Exception("Some model files might be missing...")
    
    def sent_to_dataset(self, sents, max_seq_len=50):
        '''
        Transform Sentences to Tensor and Dataset
        
        Args: 
            sents (List[str]): Input Sentences
            max_seq_len (int, default: 50): max token length
        '''
        cls_token = self.tokenizer.cls_token
        sep_token = self.tokenizer.sep_token
        unk_token = self.tokenizer.unk_token
        pad_token_id = self.tokenizer.pad_token_id
        pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index

        all_input_ids = []
        all_attention_mask = []
        all_token_type_ids = []
        all_slot_label_mask = []

        for sent in sents:
            tokens = []
            slot_label_mask = []
            for word in sent.split():
                word_tokens = self.tokenizer.tokenize(word)
                # For handling the bad-encoded word
                if not word_tokens:
                    word_tokens = [unk_token]  
                tokens.extend(word_tokens)
                # Use the real label id for the first token of the word,
                # and padding ids for the remaining tokens
                slot_label_mask.extend([0] + [pad_token_label_id] * (len(word_tokens) - 1))

            # Account for [CLS] and [SEP]
            special_tokens_count = 2
            if len(tokens) > max_seq_len - special_tokens_count:
                tokens = tokens[: (max_seq_len - special_tokens_count)]
                slot_label_mask = slot_label_mask[:(max_seq_len - special_tokens_count)]

            # Add [SEP] token
            tokens += [sep_token]
            token_type_ids = [0] * len(tokens)
            slot_label_mask += [pad_token_label_id]

            # Add [CLS] token
            tokens = [cls_token] + tokens
            token_type_ids = [0] + token_type_ids
            slot_label_mask = [pad_token_label_id] + slot_label_mask

            input_ids = self.tokenizer.convert_tokens_to_ids(tokens)

            # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
            attention_mask = [1] * len(input_ids)

            # Zero-pad up to the sequence length.
            padding_length = max_seq_len - len(input_ids)
            input_ids = input_ids + ([pad_token_id] * padding_length)
            attention_mask = attention_mask + ([0] * padding_length)
            token_type_ids = token_type_ids + ([0] * padding_length)
            slot_label_mask = slot_label_mask + ([pad_token_label_id] * padding_length)

            all_input_ids.append(input_ids)
            all_attention_mask.append(attention_mask)
            all_token_type_ids.append(token_type_ids)
            all_slot_label_mask.append(slot_label_mask)
        
        all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
        all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
        all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)
        all_slot_label_mask = torch.tensor(all_slot_label_mask, dtype=torch.long)
        
        dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_slot_label_mask)

        return dataset
    
    def ner_postprocessing(self, dataset, preds, id2label):
        '''
        NER predict data postprocessing
        
        Args:
            dataset (torch.utils.data.TensorDataset): Dataset
            preds (np.array): NER model output
            id2label (Dict[str: str]): Dict for id to label transform
        
        Returns:
            tag_list (List[List[Tuple(str, str)]]): return Sentences NER Tag
                ex) [[('블랙핑크', 'PER'), ('R', 'AFW')], [], ['팝', 'FLD]]
        '''
        return_list = []
        for i in range(len(dataset)):
            data = dataset[i]
            token_ids = data[0][data[1] == 1][1:-1]
            tokens = self.tokenizer.convert_ids_to_tokens(token_ids)
            pred = preds[i]
            eojeol_range = []
            for j, token in enumerate(tokens):
                if token[0] == SPIECE_UNDERLINE:
                    eojeol_range.append(j)
            eojeol_range.append(len(tokens))
            eojeol_range = [(eojeol_range[idx], eojeol_range[idx+1]) \
                            for idx in range(len(eojeol_range) - 1)]
            tag_list = []
            prev_tag = False
            for s, e in eojeol_range:
                tag_str = ''
                for j in range(s, e):
                    if id2label[str(pred[j + 1])] != 'O':
                        tag_str += tokens[j].replace(SPIECE_UNDERLINE, '')
                if id2label[str(pred[s + 1])] != 'O':
                    if id2label[str(pred[s + 1])][-1] == 'B':
                        tag_list.append([tag_str.strip(), id2label[str(pred[s + 1])][:-2]])
                        if id2label[str(pred[e + 1])] !=' O':
                            prev_tag = True
                        else:
                            prev_tag = False
                    if id2label[str(pred[s + 1])][-1] == 'I':
                        if prev_tag:
                            tag_list[-1][0] += ' '
                        else:
                            tag_list.append(['', id2label[str(pred[s + 1])]])
                        tag_list[-1][0] += tag_str
            return_list.append(tag_list)
        return return_list
    
    def ner_predict(self, sents, batch_size=32):
        '''
        NER predict
        
        Tokenize input sentences and Get Model Output
        
        Args:
            sents (List[str]): input sentences
            batch_size (int, default=32): batch size
        
        Returns:
            output_tensor: Output tensor of model
        '''
        if len(sents) == 0 :
            return []
        id2label = json.load(open(os.path.join(self.ner_model_path, 'config.json'), 'r', encoding='utf-8'))['id2label']
        dataset = self.sent_to_dataset(sents)
        sampler = SequentialSampler(dataset)
        data_loader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

        all_slot_label_mask = None
        preds = None

        for batch in data_loader:
            batch = tuple(t.to(self.device) for t in batch)
            with torch.no_grad():
                inputs = {"input_ids": batch[0],
                        "attention_mask": batch[1],
                        "labels": None}
                outputs = self.ner_model(**inputs)
                logits = outputs[0]

                if preds is None:
                    preds = logits.detach().cpu().numpy()
                    all_slot_label_mask = batch[3].detach().cpu().numpy()
                else:
                    preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)
                    all_slot_label_mask = np.append(all_slot_label_mask, batch[3].detach().cpu().numpy(), axis=0)

        preds = np.argmax(preds, axis=2)
        
        return self.ner_postprocessing(dataset, preds, id2label)
    
    def absa_postprocessing(self, dataset, preds, dp_preds, id2label):
        '''
        ABSA predict
        
        Args:
            dataset (torch.utils.data.TensorDataset): Dataset
            preds (np.array): ABSA model output
            dp_preds (List[List[Tuple(int, str, int, str)]]): Dependency Parsing Result
            id2label (Dict[str: str]): Dict for id to label transform
        
        Returns:
            tag_list (List[List[Tuple(str, str)]]): return Sentences ABSA Tag
        '''
        
        asp_opn_list = []
        for i in range(len(dataset)):
            data = dataset[i]
            token_ids = data[0][data[1] == 1][1:-1]
            tokens = self.tokenizer.convert_ids_to_tokens(token_ids)
            pred = preds[i]
            eojeol_range = []
            for j, token in enumerate(tokens):
                if token[0] == SPIECE_UNDERLINE:
                    eojeol_range.append(j)
            eojeol_range.append(len(tokens))
            eojeol_range = [(eojeol_range[idx], eojeol_range[idx+1]) for idx in range(len(eojeol_range) - 1)]
            tag_list = []
            prev_tag = False
            for eojeol_id, (s, e) in enumerate(eojeol_range):
                tag_str = ''
                for j in range(s, e):
                    if id2label[str(pred[j + 1])] != 'O':
                        tag_str += tokens[j].replace(SPIECE_UNDERLINE, '')
                if id2label[str(pred[s + 1])] != 'O':
                    if id2label[str(pred[s + 1])][-1] == 'B':
                        tag_list.append([tag_str.strip(), id2label[str(pred[s + 1])][:-2], eojeol_id + 1])
                        if id2label[str(pred[e + 1])] !=' O':
                            prev_tag = True
                        else:
                            prev_tag = False
                    if id2label[str(pred[s + 1])][-1] == 'I':
                        if prev_tag:
                            tag_list[-1][0] += ' '
                        else:
                            tag_list.append(['', id2label[str(pred[s + 1])], eojeol_id + 1])
                        tag_list[-1][0] += tag_str
            asp_opn_list.append(tag_list)
        return_list = []
        for asp_opn, dp in zip(asp_opn_list, dp_preds):
            if len(dp) == 0 :
                return_list.append([])
                continue
            asp_opn_pair = []
            asp_dict = {asp[2]:asp for asp in asp_opn if asp[1][:3] == 'ASP'}
            for opn_tag in asp_opn:
                if opn_tag[1][:3] == 'OPN':
                    asp_tag_eojeol_id = dp[opn_tag[2] - 1][2]
                    if asp_tag_eojeol_id in asp_dict:
                        asp_tag = asp_dict[asp_tag_eojeol_id][1]
                        asp_text = asp_dict[asp_tag_eojeol_id][0]
                        asp_opn_pair.append((asp_tag, asp_text, opn_tag[0]))
            return_list.append(asp_opn_pair)
        return return_list
    
    def absa_predict(self, sents, batch_size=32):
        if len(sents) == 0 :
            return []
        id2label = json.load(open(os.path.join(self.absa_model_path, 'config.json'), 'r', encoding='utf-8'))['id2label']
        dataset = self.sent_to_dataset(sents)
        sampler = SequentialSampler(dataset)
        data_loader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

        all_slot_label_mask = None
        preds = None

        for batch in data_loader:
            batch = tuple(t.to(self.device) for t in batch)
            with torch.no_grad():
                inputs = {"input_ids": batch[0],
                        "attention_mask": batch[1],
                        "labels": None}
                outputs = self.absa_model(**inputs)
                logits = outputs[0]

                if preds is None:
                    preds = logits.detach().cpu().numpy()
                    all_slot_label_mask = batch[3].detach().cpu().numpy()
                else:
                    preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)
                    all_slot_label_mask = np.append(all_slot_label_mask, batch[3].detach().cpu().numpy(), axis=0)

        preds = np.argmax(preds, axis=2)
        dp_preds = []
        for sent in sents:
            try:
                dp_preds.append(self.dp_model(sent))
            except RuntimeError:
                dp_preds.append([])
        
        return self.absa_postprocessing(dataset, preds, dp_preds, id2label)

    def pos_predict(self, sents):
        results = [self.pos_model.pos(sent) for sent in sents]
        return results


def NLP_update(from_date, to_date):
    '''
    NLP Update
    Perform NLP analysis and
    Insert it into the database
    
    Args:
        from_date (str): start date (format: YYYYMMDD)
        to_date (str): end date (format: YYYYMMDD)
    '''
    from_date = datetime.strptime(from_date, '%Y%m%d')
    to_date = datetime.strptime(to_date, '%Y%m%d')
    to_date = to_date.replace(hour=23, minute=59, second=59)
    engine = NLP_Engine()
    cleaner = TextCleaner()
    connection = pymongo.MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
    # Raw Data Collection
    raw_data_collection = connection[MONGO_DB]['News']
    # NLP Data Collection
    nlp_data_collection = connection[MONGO_DB]['NewsNLP']
    cursor = raw_data_collection.find({
        'create_dt': {'$gte': from_date, '$lte': to_date, }
    })
    # Get Data from MongoDB
    for item in cursor:
        sents = [
            cleaner.cleaning_data(sent)[1]
            for sent in item['body'].split('. ')
            if cleaner.cleaning_data(sent)[0]
        ]
        ner = engine.ner_predict(sents)
        pos = engine.pos_predict(sents)
        absa = engine.absa_predict(sents)
        # Save to MongoDB NLP Data Collection
        try:
            nlp_data_collection.insert_one(
                {
                    '_id': item['_id'],
                    'data_id': item['data_id'],
                    'create_dt': item['create_dt'],
                    'keyword': item['keyword'],
                    'NER': json.dumps(ner, ensure_ascii=False),
                    'POS': json.dumps(pos, ensure_ascii=False),
                    'ABSA': json.dumps(absa, ensure_ascii=False)
                }
            )
        except DuplicateKeyError:
            pass
