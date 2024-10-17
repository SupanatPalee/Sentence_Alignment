import os
import thai_sentences as th
import pandas as pd
import time

for i in range( 1693 ) :
    if not(os.path.exists( f'./thai_sentences/thai_sentences_{i}.csv' ) ) :
        print( f'thai_sentences_{i}.csv' )
        df = pd.read_csv(f'./data/sort/{i}.csv', usecols=[ 'Journal_link', 'Archives_link' ,'Archives_year' ,'Article_link', 'Thai_sentence' ])
        sentences = df.iloc[ 0 ,4 ]
        print( f"{i}) {sentences}" )
        print( "-----------------------------------------" )
        th.send_curl( f"/app/thai_sentence/thai_sentences_{i}.csv", "sen_cut", sentences )
        # time.sleep( 1 )