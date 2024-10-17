import bs4
import requests
import csv
import pandas
from datetime import datetime
import time
import os

import pull_text

def open_articles( link_path, save_paths, back_year ) :
    line_one = True
    current_date = datetime.now()
    if back_year < 0 :
        back_year = 0
    if back_year >= 1000 :
        year = back_year
    else :
        year = current_date.year - back_year
    Text = ['', '', '', '', '', '']
    with open( link_path, 'r') as file:
        csv_reader = csv.reader(file) #ใช้ csv.reader() เพื่อสร้างอ็อบเจกต์ reader สำหรับอ่านข้อมูลจากไฟล์
        for row in csv_reader : #วนลูปอ่านข้อมูลในไฟล์ CSV แต่ละแถว
            if not( line_one ) :
                if row[ 1 ][ len( row[ 1 ] ) - 7 : len( row[ 1 ] ) ] != 'archive' :
                    if row[ 1 ].count("/") >= 5 :
                        url = row[ 1 ][ : row[ 1 ].rfind("/") ] + "/issue/archive"
                    else :
                        url = row[ 1 ] + "/issue/archive"
                else :
                    url = row[ 1 ]
                print( f"Journal : {url}" )
                pull_issue( link_path, url, save_paths, year, Text, 2, current_date.year )
            else :
                line_one = False

def pull_issue( link_path, url, save_paths, year, Text, page, year_now ) :
    soup = pull_web( url )
    if change_language( soup ) :
        issues, issue_years = find_issues( soup )
        Text[0] = url #=================
        last_year = 0
        for issue, temp_year1 in zip( issues, issue_years ) :
            temp_year2 = temp_year1.text.strip()
            try :
                issue_year = int( temp_year2[ temp_year2.rfind("(") + 1 : temp_year2.rfind(")")] )
                if issue_year - year_now >= 400 :
                    issue_year = issue_year - 543
                last_year = issue_year
                if issue_year >= year :
                    issue_link = issue.a["href"]
                    Text[1] = issue_link #=================
                    Text[2] = issue_year #=================
                    print( f'{ issue_year } : { issue_link }' )
                    pull_article( issue_link, save_paths, Text ) ########
                else :
                    print( f'Back to year {year} finish\n' )
                    break
            except :
                print( "Number can find from issue year may be error" )
        if ( last_year >= year ) and ( len( issues ) == 25 or len( issues ) == 10 ) :
            if url.count("/") >= 7 :
                pull_issue( url[ : url.rfind( '/' ) ] + '/' + str( page ), save_paths, year, Text, page + 1 )
            else :
                pull_issue( url + '/' + str( page ), save_paths, year, Text, page + 1 )
    else :
        save_non_pull( link_path, url )

def change_language( soup ) :
    change = soup.find( 'div', {'class' : 'pkp_block block_language'} )
    if change :
        print( "Have thai language" )
        return True
    else :
        print( "Not have thai language" )
        print( "---------------------------------------------" )
        return False
    

def pull_web( url ) :
    time.sleep( 2 )
    header1 = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'} # สร้าง Agent เพื่อให้เหมือนกับการที่มีคนใช้งาน
    cookies = dict(cookies='value') # กดยอมรับ cookie
    response = requests.get(url, headers = header1 ,cookies=cookies ).text #ดึงข้อมูลจาก URL
    soup = bs4.BeautifulSoup(response, 'html.parser') #สร้าง object
    return soup

def find_issues( soup ) :
    tags = [
        [ 'div', 'class', 'obj_issue_summary'],
        [ 'div', 'class', 'media-left' ],
        [ 'div', 'class', 'issue-summary media' ]
    ]
    year_tags =[
        [ 'div', 'class', 'series' ],
        [ 'div', 'class', 'issuse' ],
        [ 'div', 'class', 'series lead' ]
    ]
    for tag, year_tag in zip( tags, year_tags ) :
        issues = soup.find_all( tag[ 0 ], {tag[ 1 ] : tag[ 2 ]} )
        issue_years = soup.find_all( year_tag[ 0 ], { year_tag[ 1 ] : year_tag[2] } )
        if issues and issue_years :
            break
    if not( issues ) :
        print( "Can't find issue" )
    if not( issue_years ) :
        print( "Can't find issue years" )
    return issues, issue_years

#######################################################################
def pull_article( issue_link, save_paths, Text ) :
    soup = pull_web( issue_link )
    articles = find_articles( soup )
    try :
        with open( save_paths + 'count.csv', 'r') as file:
            csv_reader = csv.reader(file) #ใช้ csv.reader() เพื่อสร้างอ็อบเจกต์ reader สำหรับอ่านข้อมูลจากไฟล์
            for temp in csv_reader :
                count = int(temp[0])
            if count == None :
                count = 0
    except :
        count = 0
    for article in articles :
        article_link = article.a["href"]
        print( f"article_link : {article_link}" )
        Text[3] = article_link #=================
        count = pull_text.pull_abstract( article_link, save_paths, Text, count )
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

def save_non_pull( link_path, url ) :
    not_pull = link_path[ : link_path.rfind( '/' ) ] + '/not_pull.csv'
    if os.path.exists(not_pull) and os.stat(not_pull).st_size > 0:
        df = pandas.DataFrame( { 'journal' : [url] } )
        df.to_csv(not_pull, mode='a', header=False, index=False) # ถ้ามีข้อมูลอยู่ในไฟล์ CSV ให้เปิดไฟล์และเขียนข้อมูลใหม่โดยไม่เขียนชื่อคอลัมน์
    else:
        df = pandas.DataFrame( { 'journal' : [url] } )
        df.to_csv( not_pull, mode='w', header=True, index=False )

#open_articles( "./journal/journal.csv", "./data/", 1 )