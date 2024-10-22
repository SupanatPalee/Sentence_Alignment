import bs4
import requests
import csv
import pandas
from datetime import datetime
import os

import Pull_text

def open_articles( path, save_paths, start_year, back_year ) :
    current_date = datetime.now() #ดึงข้อมูลเวลาปัจจุบัน
    year_now = current_date.year #เลือกเฉพาะข้อมูลปี

    start_year = cal_year( start_year, year_now ) #คำนวณให้ศักราชอยู่ในรูปของ คริสต์ศักราช
    back_year = cal_year( back_year, year_now )
    print( f"{start_year},{back_year}" )

    Text = ['', '', '', '', '', ''] #สร้างตัวแปรในการเก็บข้อมูล
    csv_reader = pandas.read_csv( path )['journal'] #อ่านข้อมูลไฟล์ที่เก็บลิงค์วารสาร
    for row in csv_reader : #วนลูปอ่านข้อมูลในไฟล์ CSV แต่ละแถว
        
        if row[ len( row ) - 1 ] == "/" : #แก้ไขลิงค์ของวารสารให้เป็นลิงค์ของบทความย้อนหลังในแต่ละวารสาร
            row = row[ : len( row ) - 1 ]
        if row[ len( row ) - 7 : ] != 'archive' :
            if row.count("/") >= 5 :
                url = row[ : row.rfind("/") ] + "/issue/archive"
            else :
                url = row + "/issue/archive"
        else :
            url = row
        print( f"Journal : {url}" )

        pull_issue( path, url, save_paths, start_year, back_year, Text, 2, year_now ) #ดึงข้อมูลวารสาร

def cal_year( year, year_now ) : #ฟังก์ชั่นแปลงให้เป็น คริสต์ศักราช
    if year < 0 : #ศักราชไม่ติดลบ
        year = year_now
    if year > year_now : #ถ้าศักราชมากกว่าปัจจุบัน(ค.ศ.) แสดงว่าเป็น พ.ศ.
        year -= 543
        if year > year_now :
            year = year_now
    if year < 1000 : #หากไม่ใช่การป้อนศักราชให้เอาไปลบแทน
        year = year_now - year
    return year

def pull_issue( path, url, save_paths, start_year, back_year, Text, page, year_now ) :
    soup = pull_web( url ) #ดึงหน้าเว็บไซต์
    if change_language( soup ) : #ตรวจสอบว่ามีปุ่มเปลี่ยนภาษาไหม
        issues, issue_years = find_issues( soup ) #ค้นหา tag ที่มีลิงค์ของวารสารแต่ละฉบับ และปีของวารสาร
        
        Text[0] = url #บันทึก URL ของวารสาร
        last_year = 0
        for issue, temp_year1 in zip( issues, issue_years ) : # loop เพื่อดูวารสารแต่ละฉบับในหน้านั้น
            temp_year2 = temp_year1.text.strip()
            try :
                issue_year = int( temp_year2[ temp_year2.rfind("(") + 1 : temp_year2.rfind(")")] ) #แปลงข้อความที่อยู่ภายใต้ลงเล็บซึ่งเป็น เลข
                if issue_year - year_now >= 400 : # หากไม่ใช่ พุทธศักราช ให้แปลงเป็น คริสต์ศักราช
                    issue_year = issue_year - 543
                last_year = issue_year #กำหนด ปีล่าสุดที่ดึงวารสารมา
                if issue_year >= back_year :
                    print( f"issue_year = {issue_year} start_year = {start_year} back_year = {back_year}" )
                    if issue_year <= start_year : #ตรวจสอบว่าดึงข้อมูลถึง คริสต์ศักราช ที่กำหนดหรือยัง
                        issue_link = issue.a["href"] #เลือกลิงค์ของ วารสารฉบับนั้นมา
                        Text[1] = issue_link #=================
                        Text[2] = issue_year #=================
                        print( f'{ issue_year } : { issue_link }' )
                        pull_article( issue_link, save_paths, Text ) #ดึงบทความ
                else :
                    break #หยุดดึงข้อมูลเมื่อถึงช่วงปีที่กำหนด
            except :
                print( "Number can find from issue year may be error" )
        if ( last_year >= back_year ) and ( len( issues ) == 25 or len( issues ) == 10 ) : #หน้าเพจจะต้องมีจำนวน 10 หรือ 25 วารสาร และปีล่าสุดต้องไม่น้อยกว่าที่กำหนด หากตรงเงื่อนไขให้ recursive
            if url.count("/") >= 7 : #แก้ลิงค์ของ
                pull_issue( path, url[ : url.rfind( '/' ) ] + '/' + str( page ), save_paths, start_year, back_year, Text, page + 1, year_now ) #ดึงข้อมูลหน้าเว็บต่อ
            else :
                pull_issue( path, url + '/' + str( page ), save_paths, start_year, back_year, Text, page + 1, year_now ) #ดึงข้อมูลหน้าเว็บต่อ
        else :
            print( f'Back to year {last_year} finish\n' )
    else :
        save_non_pull( path, url ) #บันทึกลิงค์ที่ไม่มีการดึงเลยเพื่อตรวจสอบว่ามีความผิดพลาดเพิ่มเติมไหม

def change_language( soup ) :
    change = soup.find( 'div', {'class' : 'pkp_block block_language'} )
    if change :
        print( "Have two language" )
        return True
    else :
        print( "Not have two language" )
        print( "---------------------------------------------" )
        return False

def pull_web( url ) : #ฟังก์ชั่นดึงหน้าเว็บ
    header1 = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'} # สร้าง Agent เพื่อให้เหมือนกับการที่มีคนใช้งาน
    cookies = dict(cookies='value') #กดยอมรับ cookie
    response = requests.get(url, headers = header1 ,cookies=cookies ).text #ดึงข้อมูลจาก URL
    soup = bs4.BeautifulSoup(response, 'html.parser') #สร้าง object
    return soup

def find_issues( soup ) : #ฟังก์ชั่นหาวารสาร
    tags = [
        [ 'div', 'class', 'obj_issue_summary'],
        [ 'div', 'class', 'media-left' ],
        [ 'div', 'class', 'issue-summary media' ]
    ]
    year_tags = [
        [ 'div', 'class', 'series' ],
        [ 'div', 'class', 'issuse' ],
        [ 'div', 'class', 'series lead' ]
    ]
    for tag, year_tag in zip( tags, year_tags ) : #วน loop เพื่อหาทุก tag ที่เป็นไปได้
        issues = soup.find_all( tag[ 0 ], {tag[ 1 ] : tag[ 2 ]} )
        issue_years = soup.find_all( year_tag[ 0 ], { year_tag[ 1 ] : year_tag[2] } )
        if issues and issue_years : #ให้หยุดเมื่อพบ วารสาร และ ปี แล้ว
            break
    if not( issues ) :
        print( "Can't find issue" )
    if not( issue_years ) :
        print( "Can't find issue years" )
    return issues, issue_years

def pull_article( issue_link, save_paths, Text ) :
    soup = pull_web( issue_link ) #ดึงข้อมูลหน้าเว็บ
    articles = find_articles( soup ) #ค้นหาพบคัดย่อแต่ละบทคัดย่อ
    try :
        with open( save_paths + 'count.csv', 'r') as file: #เปิดไฟล์ count เพื่อสร้างชื่่อไฟล์ต่อจากเดิม
            csv_reader = csv.reader(file) #ใช้ csv.reader() เพื่อสร้างอ็อบเจกต์ reader สำหรับอ่านข้อมูลจากไฟล์
            for temp in csv_reader :
                count = int(temp[0])
            if count == None :
                count = 0
    except :
        count = 0
    for article in articles :
        article_link = article.a["href"] #ดึงเฉพาะลิงค์บทคัดย่อมา
        print( f"article_link : {article_link}" )
        Text[3] = article_link #=================
        count = Pull_text.pull_abstract( article_link, save_paths, Text, count )
    df = pandas.DataFrame( [count] )
    df.to_csv( save_paths + 'count.csv', mode='w', header=False, index=False )

def find_articles( soup ) :
    tags = [
        [ 'div', 'class', 'obj_article_summary'],
        [ 'h3', 'class', 'media-heading' ]
    ]
    for tag in tags :
        articles = soup.find_all( tag[ 0 ], { tag[ 1 ] : tag[ 2 ] } )
        if articles :
            break
    if not( articles ) :
        print( "Can't find article" )
    return articles

def save_non_pull( path, url ) :
    not_pull = path[ : path.rfind( '/' ) ] + '/not_pull.csv'
    if os.path.exists(not_pull) and os.stat(not_pull).st_size > 0:
        df = pandas.DataFrame( { 'journal' : [url] } )
        df.to_csv(not_pull, mode='a', header=False, index=False) # ถ้ามีข้อมูลอยู่ในไฟล์ CSV ให้เปิดไฟล์และเขียนข้อมูลใหม่โดยไม่เขียนชื่อคอลัมน์
    else:
        df = pandas.DataFrame( { 'journal' : [url] } )
        df.to_csv( not_pull, mode='w', header=True, index=False )

open_articles( "./Prepare_data_set/journal/journal.csv", "./Prepare_data_set/data/", 0, 6 )