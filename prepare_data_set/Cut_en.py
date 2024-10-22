import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
import os

# ตรวจสอบว่ามีโฟลเดอร์ nltk_data ถ้ายังไม่มี ให้สร้างขึ้นมา
nltk_data_folder = os.path.join(os.path.expanduser('~'), 'nltk_data')
if not os.path.exists(nltk_data_folder):
    os.makedirs(nltk_data_folder)

# ดาวน์โหลดตัวตัดประโยคของ NLTK
nltk.download('punkt', download_dir=nltk_data_folder)

# ฟังก์ชันสำหรับตัดประโยค
def tokenize_sentences(text):
    return sent_tokenize(text)

def nltk_cut( check_count, data_path, save_path ) :
    count = pd.read_csv(f'{check_count}/count.csv') #ใช้ csv.reader() เพื่อสร้างอ็อบเจกต์ reader สำหรับอ่านข้อมูลจากไฟล์

    for i in range(0, int( count.columns[ 0 ])):
        input_file_path = data_path + f'/{i}.csv'
        output_file_path = save_path + f'/english_sentences_{i}.csv'
        
        if not os.path.exists(input_file_path):  # ตรวจสอบว่าไฟล์ input มีอยู่จริง
            print(f'File {input_file_path} does not exist. Skipping...')
            continue
 
        abstract = pd.read_csv(input_file_path)['English_sentence']# อ่านไฟล์ CSV

        sentences = tokenize_sentences( abstract[0] ) #ตัดประโยค
        print( sentences )

        df = pd.DataFrame({'sentences': sentences})
        df.to_csv(output_file_path, index=False)# บันทึกผลลัพธ์ลงไฟล์ CSV ใหม่

        print(f'Processed and saved: {output_file_path}')
    print('Completed processing all files.')

nltk_cut( "./Prepare_data_set/data", "./Prepare_data_set/data", "./Prepare_data_set/english_sentences" )
