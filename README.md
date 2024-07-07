# NLP_webscraping 
1. Extracting Articles from given urls present in input.xlsx 
2. Cleaning Articles and removing StopWords that are provided in the StopWord Folder
3. Calculating Various Scores for each Articles
4. Exporting Final Scores to output.xlsx   


## How To Run 
1. Install all dependencies using
   --> pip install -r requirements. txt
2. Now run following command
   -->  py run.py  

## How it Works 
1. when we run py run.py file
2. The obj of MyTask class is instantiated
3. it will call the start() methode
4. The Start Methode calls the following methods
   
   a) extract_articles()
      --> A article folder will be created in which all the extracted articles will be store with there UID as file name

   b) extract_stopwords()
      --> All the stopwords present in StopWord folder are extracted and store in a list (self.stopword_list) 

   c) clean_articles()
      -->A clean folder will be created in which all clean articles (Stopwords Removed) will be store 

   d) cal_score()
      --> All the scores will be calculated and store in a dataframe (self.scores)
     
   e) Finally the scores are exported to output.xlsx
   
