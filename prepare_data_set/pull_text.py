import bs4
import requests
import time
import langdetect
import pandas
import os

def pull_abstract( url, save_paths, Text, count ) :
    class_title = [
        [ 'div', 'class', 'article-abstract'],
        [ 'section', 'class', 'item abstract']
    ] #ชื่อ class title ที่มี atribute อยู่

    thai_urls = [
        [ 'li', 'class', 'locale_th_TH current' ],
        [ 'li', 'class', 'locale_th_TH' ],
    ]

    eng_urls = [
        [ 'li', 'class', 'locale_en_US current' ],
        [ 'li', 'class', 'locale_en_US' ],
    ]
    
    soup = web_pull( url )
    for title in class_title :
        abstract = soup.find(title[0],{title[1]:title[2]}) #ค้นหาแท็ก class ในตัวแปร soup แล้วนำมาไว้ใน abstract
        Thai = ''
        English = ''
        if abstract : #ดูว่า abstract นั้นดึงข้อมูลมาได้ไหม
            paragraphs = abstract.find_all('p') #('p', string=lambda text: text and len(text) > 10) #ค้นหาแท็ก <p> ในตัวแปร abstract ที่มีข้อความมากกว่า 10 ตัวอักษร เพื่อตัดหัวข้อที่ไม่จำเป็น
            if paragraphs :
                for temp in paragraphs :
                    if temp.text.strip() != '' : #ป้องกันกรณีที่มีข้อความว่างเปล่าใน array
                        if check_language( temp.text.strip() ) == 'th' : #เช็คว่าเป็นภาษาอะไร
                            if Thai == '' :
                                Thai += temp.text.strip()
                            else :
                                Thai += ' ' + temp.text.strip()
                        else :
                            if English == '' :
                                English += temp.text.strip()
                            else :
                                English += ' ' + temp.text.strip() #แบบไม่ตัดการเว้นวรรคหัวท้ายออก
            else :
                if check_language( abstract.text.strip() ) == 'th' : #เช็คว่าเป็นภาษาอะไร
                    Thai = abstract.text.strip()
                else :
                    English = abstract.text.strip() #แบบไม่ตัดการเว้นวรรคหัวท้ายออก
            if Thai == '' :
                for thai_url in thai_urls :
                    second = soup.find(thai_url[ 0 ],{thai_url[ 1 ]:thai_url[ 2 ]})
                    if second :
                        second_url = second.a['href']
                        Thai = second_pull( class_title, second_url )
                        break
            if English == '' :
                for eng_url in eng_urls :
                    second = soup.find(eng_url[ 0 ],{eng_url[ 1 ]:eng_url[ 2 ]})
                    if second :
                        second_url = second.a['href']
                        English = second_pull( class_title, second_url )
                        break
            if English[ 0 : 20 ] != Thai[ 0 : 20 ] and ( len( English ) > 15  and len( Thai ) > 15 ) :
                Text[4] = English #=================
                Text[5] = Thai #=================
                save_path = save_paths + str( count ) + '.csv'
                save_text( save_path, Text )
                print( f'English : {English}' )
                print( f'Thai : {Thai}' )
                count += 1
            elif len( English ) == 0 and len( Thai ) == 0 :
                print( 'ไม่สามารถดึงประโยคได้' )
            elif len( English ) == 0 or len( Thai ) == 0 :
                print( 'ไม่มีคู่ประโยค' )
            elif len( English ) <= 15 or len( Thai ) <= 15 :
                print( 'บทคัดย่อน้อยเกินไป' )
            else :
                print( 'ประโยคซ้ำกัน' )
            print( "--------------------------------------------------------------------------------------\n" )
            break #ถ้าหาเจอแล้วก็หยุด
    return ( count )

def check_language( text ) :
    language = langdetect.detect( text[:20] ) # เลือก String เฉพาะตัวที่ 0 - 20 มาตรวจสอบ
    return( language )

def second_pull( class_title, second_url ) :
    print( f'Second_URL : {second_url}' )
    soup = web_pull( second_url )
    for title in class_title :
        abstract = soup.find( title[0], { title[1] : title[2] }) #ค้นหาแท็ก class ในตัวแปร soup แล้วนำมาไว้ใน abstract
        Text = ''
        if abstract : #ดูว่า abstract นั้นดึงข้อมูลมาได้ไหม
            paragraphs = abstract.find_all('p')
            if paragraphs :
                for temp in paragraphs :
                    if temp.text.strip() != '' : #ป้องกันกรณีที่มีข้อความว่างเปล่าใน array
                        if( Text == '' ) :
                            Text += temp.text.strip()
                        else :
                            Text += ' ' + temp.text.strip()
            else :
                Text = abstract.text.strip()
            break
    if not( Text ) :
        print( "Can't pull second abstract" )
    return Text

def web_pull( url ) :
    time.sleep( 2 )
    header1 = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'} # สร้าง Agent เพื่อให้เหมือนกับการที่มีคนใช้งาน
    cookies = dict(cookies='value') # กดยอมรัย cookie
    response = requests.get(url, headers = header1 ,cookies=cookies ).text #ดึงข้อมูลจาก URL
    soup = bs4.BeautifulSoup(response, 'html.parser') #สร้าง object
    return soup

def save_text( path, Text ) :
    if os.path.exists(path) and os.stat(path).st_size > 0:
        df = pandas.DataFrame( [ Text ] )
        df.to_csv(path, mode='a', header=False, index=False) # ถ้ามีข้อมูลอยู่ในไฟล์ CSV ให้เปิดไฟล์และเขียนข้อมูลใหม่โดยไม่เขียนชื่อคอลัมน์
    else:
        df = pandas.DataFrame( { 'Journal_link' : [ Text[ 0 ] ], 'Archives_link' : [ Text[ 1 ] ], 'Archives_year' : [ Text[ 2 ] ], 'Article_link' : [ Text[ 3 ] ], 'English_sentence' : [ Text[ 4 ] ], 'Thai_sentence' : [ Text[ 5 ] ] } )
        df.to_csv(path, mode='a', header=True, index=False) # ถ้าไม่มีข้อมูลในไฟล์ CSV ให้เขียนข้อมูลใหม่โดยเขียนชื่อคอลัมน์ด้วย