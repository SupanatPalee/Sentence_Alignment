import bs4
import requests
import pandas
import os
from lxml import etree

def pull_journal( save_path, search_key, tear ) :
    url = "https://tci-thailand.org/list%20journal.php"
    soup = web_pull( url )
    journals = soup.find_all('tr')
    for journal in journals :
        html_string = str( journal )
        parser = etree.HTMLParser()
        tree = etree.fromstring(html_string, parser)
        journal_link = tree.xpath('//a[starts-with(@href, "http")]/@href') # ใช้ XPath เพื่อค้นหาแท็ก a ที่ href ขึ้นต้นด้วย "http"
        journal_tear = tree.xpath('//td[5]/font//text()')
        journal_tear = [text.replace(u'\xa0', '') for text in journal_tear]
        if ( check_tears( journal_tear ) <= tear ) and check_link( journal_link ) and ( search_key.lower() in str( journal ).lower() ) :
            print( f"{journal_tear[ 0 ]} {journal_link[0]}" )
            if check_journal( save_path, journal_link ) :
                save_text( save_path, journal_tear[0], journal_link[0] )
            else :
                print( "ลิงค์ซ้ำกัน" )
    print("end................")

def check_tears( journals_tears ) :
    try :
        return int( journals_tears[0] )
    except :
        return 99
    
def check_link( journal ) :
    try :
        if journal[0].find( "thaijo.org" ) != -1 :
            return True
        else :
            return False
    except :
        return False

def save_text( save_path, journals_tear, journal ) :
    if os.path.exists(save_path) and os.stat(save_path).st_size > 0:
        df = pandas.DataFrame( { 'tear' : [journals_tear], 'journal' : [journal] } )
        df.to_csv(save_path, mode='a', header=False, index=False) # ถ้ามีข้อมูลอยู่ในไฟล์ CSV ให้เปิดไฟล์และเขียนข้อมูลใหม่โดยไม่เขียนชื่อคอลัมน์
    else:
        df = pandas.DataFrame( { 'tear' : [journals_tear], 'journal' : [journal] } )
        df.to_csv( save_path, mode='w', header=True, index=False )

def web_pull( url ) :
    try :
        header1 = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'} # สร้าง Agent เพื่อให้เหมือนกับการที่มีคนใช้งาน
        cookies = dict(cookies='value') # กดยอมรัย cookie
        response = requests.put(url, headers = header1 ,cookies =cookies).text #ดึงข้อมูลจาก URL
        soup = bs4.BeautifulSoup(response, 'html.parser') #สร้าง object
        return soup
    except requests.exceptions.RequestException as e :
        print(f"An error occurred: {e}")
        return None
    
def check_journal( path, journal_link ) :
    check = True
    journals = pandas.read_csv( path )[ 'journal' ]
    for i in range( len( journals ) ) :
        if journals[ i ] == journal_link[ 0 ] :
            check = False
    return check

pull_journal( './journal/journal.csv', 'engineering', 2 )