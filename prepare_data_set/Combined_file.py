import pandas as pd
import os

def Combined_file( check_count, thai_path, english_path, combined_path ) :
    count = pd.read_csv(f'{check_count}/count.csv')
    combined_thai = pd.DataFrame()
    combined_english = pd.DataFrame()
    for i in range(0, int( count.columns[ 0 ])):
        thai_sentences = thai_path + f'/thai_sentences_{i}.csv'
        english_sentences = english_path + f'/english_sentences_{i}.csv'

        if not os.path.exists(thai_sentences):  # ตรวจสอบว่าไฟล์ input มีอยู่จริง
            print(f'File {thai_sentences} does not exist. Skipping...')
            continue

        if not os.path.exists(english_sentences):  # ตรวจสอบว่าไฟล์ input มีอยู่จริง
            print(f'File {english_sentences} does not exist. Skipping...')
            continue

        thai_df = pd.read_csv(thai_sentences)
        english_df = pd.read_csv(english_sentences)

        combined_thai = pd.concat([combined_thai, thai_df], ignore_index=True)
        combined_english = pd.concat([combined_english, english_df], ignore_index=True)
    
    combined_thai.to_csv(combined_path + "/thai_abstract.csv", index=False)
    combined_english.to_csv(combined_path + "/ennglish_abstract.csv", index=False)
    print( "Combined complete" )

Combined_file( "./Prepare_data_set/data", "./Prepare_data_set/thai_sentences", "./Prepare_data_set/english_sentences", "./Prepare_data_set/combined_sentences" )