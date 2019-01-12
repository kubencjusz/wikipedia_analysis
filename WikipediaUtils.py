class PrepareWikipedia(object):
    
    def __init__(self, path="./Desktop/SGH - magisterka/magisterka_60673/wikipedia/",
                 word=["ur."]):
        self.path = path
        self.word = word
    
    
    def extract_articles(self):
        
        '''
        A function to load all articles containing a given phrase
        path: path with json files containing Wikipedia articles
        word: word(s) to look for in articles
        '''
        all_articles = []
        
        path = os.path.join(self.path, "wikiextractor/text/")
        
        n_folders = len(os.listdir(path)); i=0
        
        for dirname, dirnames, filenames in os.walk(path):
            sys.stdout.write(f"\r Extracting... {str(round(100*i/n_folders,1))+'%'}")
            sys.stdout.flush()
            i += 1
            # reading files sequentially and parsing JSON
            for filename in filenames:
                file = os.path.join(dirname, filename)
                # loading a batch of articles
                batch = []
                for line in open(file, 'r', encoding='UTF-8'):
                    batch.append(json.loads(line))
                indexes = []
                # looking for articles with a given word(s) in a batch of articles
                # in order to speed things up, only first 500 characters are checked
                for idx, art in enumerate(batch):
                    if all(x in art['text'][:500] for x in self.word):
                        indexes.append(idx)
                # adding all found articles from batch
                all_articles.extend([batch[i] for i in indexes])
        return(all_articles)
    

    def get_stop_words(self):
        # create a list of stop words
        stop_words = open(os.path.join(self.path, "PL_stopwords.txt"),
                  encoding = 'utf-8').read()
        stop_words= stop_words.split('\n')
        stop_words.extend(['ur', 'zm']) # adding more words to list
        return stop_words
    
    
    def remove_stop_words(self, articles):
        # lowercasing and removing stop words
        n_art = len(articles)
        
        stop_words = self.get_stop_words()
        trans = str.maketrans({'.':'', '”':'', '„':'', ',':'', '-':' ', '–':' ',
                               '(':'', ')':'', '"':''})
        
        for idx, art in enumerate(articles):
            if idx % 1000 == 0:
                sys.stdout.write(f"\r Processing... {str(round(100*idx/n_art,1))+'%'}")
                sys.stdout.flush()
            
            
            art['text'] = art['text'].translate(trans).replace("\n\n", " ")
            
            articles[idx]['text'] = ' '.join([x.lower() for x in \
                    art['text'].split(" ") if x.lower() not in stop_words])
        
        return(articles)
    
    
    def stem_articles(self, articles):
        # stem the words using PyMorfologik
        parser = ListParser()
        stemmer = Morfologik()
            
        batch_num = len(articles) // 1000
        
        for batch in range(batch_num):
            batch_art = articles[(batch*1000):(1000*(batch+1))]
            full_text = ''
            for k in range(len(batch_art)):
                full_text += batch_art[k].get('text')
                # to split articles by some random token
                full_text += " BECARZYK "
            # stemming text from batch of articles
            bum = stemmer.stem([full_text], parser)
            tmp = []
            for wyraz in range(len(bum)):
                if len(bum[wyraz][1])>0:
                    lem = list(bum[wyraz][1].keys())[0]
                else:
                    lem = bum[wyraz][0]
                tmp.append(lem)
            final = ' '.join(tmp).split(' BECARZYK ')
            # overwriting stemmed text
            for j in range(len(final)):
                articles[batch*1000+j]['text'] = final[j]
    
            sys.stdout.write(f"\r Stemming... {str(round(100*batch/batch_num,1))+'%'}")
            sys.stdout.flush()
        
        return articles
    
    
    def extract_text(self, json_list):
        final = []
        for idx, art in enumerate(json_list):
            final.append(art['text'])
        return(final)
    
    
    def save_articles(self, obj,
                      save_path="./Desktop/SGH - magisterka/magisterka_60673/bio"):
        with open(save_path, 'w') as fout:
            json.dump(obj, fout)
    
    
    def load_articles(self, load_path):
        with open(load_path) as plik:
            articles = json.load(plik)
        return articles