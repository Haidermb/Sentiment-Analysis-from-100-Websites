import os , re
import requests
from bs4 import BeautifulSoup
import pandas as pd


import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')



class MyTask:

    def __init__(self) -> None:
        self.c = 1
        self.folder_stopword = 'StopWords'
        self.input_file_path = 'Input.xlsx'
        self.output_folder_articles = 'articles'
        self.output_folder_clean = 'clean'
        #self.output_stopword_json = 'stopwords.json'

        os.makedirs(self.output_folder_articles, exist_ok=True)
        os.makedirs(self.output_folder_clean, exist_ok=True)

        with open('MasterDictionary\\negative-words.txt', 'r', encoding='utf-8',errors='ignore') as file:
            text = file.read()
        self.n_words = word_tokenize(text)

        with open('MasterDictionary\\positive-words.txt', 'r', encoding='utf-8',errors='ignore') as file:
            text = file.read()
        self.p_words = word_tokenize(text)


    def __get_article(self,url):
        try:
            response = requests.get(url)

            if response.status_code == 200:
                  
                soup = BeautifulSoup(response.text, 'html.parser')

                try : 
                    article_text = soup.find('div', class_='td-post-content tagdiv-type').get_text()
                except: 
                    article_text = soup.find('div', class_='tdb-block-inner td-fix-index').get_text() 

                return article_text

        except Exception as e:
            print(f"Error extracting article from {url}: {e}")

        return None


    def __extract_articles(self):
        
        '''
        Input : Input.xlsx path
        Output : extracted articles with fname as ids in articles folder
        Description : It extract articles from each urls and store them in article folder with filename as id.txt   
                      It uses get_article func to get data from urls  
        '''    
        try : 
            
            df = pd.read_excel(self.input_file_path)
        except Exception as e:
            
            return print(f'error in loading df : {e}')
        
        #os.makedirs(self.output_folder_articles, exist_ok=True)
        #r = []
        for index, row in df.iterrows():
            url_id = row['URL_ID']
            url = row['URL']
            #r.append({'URL_ID': url_id,'URL':url})

            article_text = self.__get_article(url)

        
            if article_text:
                file_name = f"{url_id}.txt"
                file_path = os.path.join(self.output_folder_articles, file_name)
            
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(article_text)
                print(f"Article extracted from {url} and saved to {file_path}")

        #self.df_url = pd.DataFrame(r)

    def __extract_stopwords(self):
       
        final_list = []
        for filename in os.listdir(self.folder_stopword):
            file_path = os.path.join(self.folder_stopword, filename)

            if os.path.isfile(file_path) and file_path.endswith(".txt"):
                
                with open(file_path, 'r', encoding='utf-8',errors='ignore') as file:
                    
                    stopwords_text = file.read()
                    
                    if stopwords_text:
                        # getting clean stopwords from a txt 
                        ex = ['|','(',')']
                        tokens = word_tokenize(stopwords_text)
                        filtered_words = [word for word in tokens if word not in ex]

                        
                        # appending all stopwords from all files in one list (2d)
                        final_list.append(filtered_words)

        # converting 2d list to 1d
        flat_list = [item for sublist in final_list for item in sublist]
        self.stopword_list = flat_list

    def __clean_articles(self):

        for filename in os.listdir(self.output_folder_articles):
            file_path = os.path.join(self.output_folder_articles, filename)

            if os.path.isfile(file_path) and file_path.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as file:
                    article_text = file.read()
                
                # Remove stopwords
                    if article_text:

                        tokens = word_tokenize(article_text)
            
                        # Remove stopwords
                        filtered_words = []

                        filtered_words = [word for word in tokens if word.lower() not in  self.stopword_list]

                        # Join the filtered words back into a string
                        filtered_text = ' '.join(filtered_words)



                # Save the processed article in a text file within the output folder
                new_filename =str(filename)
                new_filename = new_filename.split('.')[0]
                file_name = f"{new_filename}clean.txt"
                file_path = os.path.join(self.output_folder_clean, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(filtered_text)
                print(f"Processed article {new_filename} saved to {file_path}")

    def __syllable_count(self,word):
        # Count the number of vowels in the word
        vowels = "aeiouAEIOU"
        count = sum(1 for char in word if char in vowels)

        # Adjust for common exceptions
        if word.endswith(('es', 'ed')) and count > 1:
            count -= 1

        return count

    def __cal_clean_score (self,text,new_filename):
    
        words = word_tokenize(text)

        pronoun_count = self.__personal_pronouns(text)
        
        Total_clean_words =len(words)

        #Positive Score Calculating
        positive_score = sum(1 for word in words if word.lower() in self.p_words)

        #Negative Score Calculating
        negative_score = sum(-1 for word in words if word.lower() in self.n_words)
        negative_score = negative_score*-1

        # Polarity
        # range -1 to 1 
        # (Positive Score – Negative Score) / ((Positive Score + Negative Score) + 0.000001)
        nu_p = positive_score - negative_score
        de_p = positive_score + negative_score + 0.000001
        polarity_Score = nu_p / de_p 

        # subjectivity_score
        # range 0 to 1
        # (Positive Score + Negative Score)/ ((Total Words after cleaning) + 0.000001)
        nu_s = positive_score + negative_score
        de_s = Total_clean_words + 0.000001
        subjectivity_score = nu_s / de_s
        
        # sylabus score for each words in a clean article
        Total_sycount = 0

        for word in words : 
            count = self.__syllable_count(word)
            Total_sycount =Total_sycount  +  count

        # No of complex words in a clean article
        complex_word_count = sum(1 for word in words if self.__syllable_count(word) > 2)



        final_score = {'URL_ID':new_filename,'POSITIVE_SCORE':positive_score,'NEGATIVE_SCORE':negative_score,'POLARITY_SCORE':polarity_Score,'SUBJECTIVITY_SCORE':subjectivity_score,'WORD_COUNT' :Total_clean_words,'COMPLEX_WORD_COUNT' :complex_word_count,'SYLLABLE_PER_WORD':Total_sycount,'PERSONAL_PRONOUNS': pronoun_count} 
        
        return final_score

    def __personal_pronouns(self,text):
        
        pronoun_pattern = re.compile(r'\b(?:I|we|my|ours|us)\b', flags=re.IGNORECASE)

        # Find all matches in the text


        matches = pronoun_pattern.findall(text)


        filter_match = [match for match in matches if match != 'US']

        # Count the number of matches
        pronoun_count = len(filter_match)
        return pronoun_count

    def __clean_score(self):

        result = []

        for filename in os.listdir(self.output_folder_clean):
            file_path = os.path.join(self.output_folder_clean, filename)    
            
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

                
                suffix = 'clean'
                new_filename =str(filename)
                new_filename = new_filename.split('.')[0]

                if new_filename.endswith(suffix):
                    new_filename = new_filename[:-len(suffix)]


                s = self.__cal_clean_score(text,new_filename)
                #s = {'id':new_filename , 'No_Words' :len(words)}
                result.append(s)
        
        self.df_clean =pd.DataFrame(result)

    def __count_sentences(self):
        # no of sentences of txt file in articles folder 
        result = []
        
        for filename in os.listdir(self.output_folder_articles):
            file_path = os.path.join(self.output_folder_articles, filename)    
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                # Split the text into sentences using a simple regex pattern
                sentences = re.split(r'[.!?]', text)
                # Remove empty strings from the list (resulting from consecutive sentence-ending punctuation)
                sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
                new_filename =str(filename)
                new_filename = new_filename.split('.')[0]

                s = {'URL_ID':new_filename , 'No_sentences' :len(sentences)}
                result.append(s)
        
        self.df_no_sentence =pd.DataFrame(result)

    def __cal_score(self):
        self.__count_sentences()
        self.__clean_score()

        df = pd.merge(self.df_clean,self.df_no_sentence,on='URL_ID')
        
        df['Avg_Sen_Leng'] = df['WORD_COUNT']/df['No_sentences']
        df['Percentage_complex_word'] = df['COMPLEX_WORD_COUNT']/df['WORD_COUNT']
        df['FOG_INDEX'] = (df['Avg_Sen_Leng']+df['Percentage_complex_word'])*0.4
        
        df_i = pd.read_excel(self.input_file_path)
        df1 = pd.merge(df_i,df,on='URL_ID')    
        
        self.scores = df1.copy()

    def start(self):
        # Extract articles from urls
        #self.__extract_articles()
        
        # Extract stopwords from Stopword folder
        #self.__extract_stopwords()

        # Removing stopwords from articles
        #self.__clean_articles()

        # Cal scores 
        self.__cal_score()

        try: 
            self.scores.to_excel('output.xlsx', index=False)
        except:
            import random
            num = random.random()   
            self.scores.to_excel(f'output{num}.xlsx', index=False)

if __name__ == '__main__':
    obj = MyTask()
    obj.start()

