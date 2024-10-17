#import pull_journal
import pull_article
#import thai_sentences

#pull_journal.pull_journal( './journal/journal.csv', 'วิศวกรรมศาสตร์', 1 )
pull_article.open_articles( "./journal/journal1.csv", "./data/", 3 )
#thai_sentences.docker_ctrl( "./data/", "/thai_sentences/", "some-name" ) # /thai_sentences/ ไม่ต้องมี . (จุด)