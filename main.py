from flask import (
	Flask,
	render_template,
	redirect,
	url_for,
	request,
	session
)
from flask_socketio import SocketIO, send, emit

from bs4 import BeautifulSoup
import math
import pymysql
import lxml
import requests
import datetime
import base64
#from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname, realpath
import json
import random
#from gevent import monkey
#monkey.patch_all()

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException


app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = '4jklhkujkn'
socketio = SocketIO(app)


#app.config['UPLOAD_FOLDER'] = './static/images/'
#현재 날짜, 시간 
current_time = datetime.datetime.now()
year = current_time.year
month = current_time.month
day = current_time.day
time = current_time.strftime('%H:%M:%S')



@app.route('/logout')
def logout():
	session['user_id'] = None
	session['name'] = None

	return "<script>alert('로그아웃 되었습니다.');window.location.href='/'</script>"
	
@app.route('/')
def index():
	global month
	
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		sql = f"select * from pay_board order by num desc limit 4"
		curs.execute(sql)
		new_product = []
		pro = curs.fetchall()
		#for i in range(0, 4):
		#	new_product.append(list(pro[i]))
		#print(new_product)
		return render_template('main.html',user_id=user_id, name=name, month=month, new_product=new_product)
		
	return render_template('main.html',user_id='-1', name='-1', month=month)
	
	
@app.route('/mypage')
def mypage():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"
		
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']	
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		#현재 로그인 되어있는 사람 정보 select
		sql = "select * from user_info where id='%s'"%user_id
		curs.execute(sql)
		detail = curs.fetchall()
		
		#현재 로그인 되어어있는 사람이 구매한 목록 select   
		sql2 = "select * from pay_info where buyer='%s' order by id desc"%name
		curs.execute(sql2)
		buy_list = curs.fetchall()
        
		sql3 = "select * from pay_info where seller='%s' order by id desc"%user_id
		curs.execute(sql3)
		sell_list = curs.fetchall() 

		b_list=[]        
		print(buy_list)        
		for i in range(0,len(buy_list)):
			sql5="select * from pay_info where id = '%s'" %buy_list[i][0] #buy_list[i][8]
			curs.execute(sql5)

			b_list.append(list(curs.fetchall()))
		
		
		s_list=[]
		for i in range(0,len(sell_list)):
			sql5="select * from pay_board where userid = '%s'"%sell_list[i][2] #buy_list[i][8]
			curs.execute(sql5)

			s_list.append(curs.fetchall())
			
		sql4 = "select * from user_info where name = '%s'"%name
		curs.execute(sql4)
		
		user_info = curs.fetchall()

		return render_template('mypage.html',user_id=user_id, name=name,detail=detail ,buy_list=buy_list,sell_list=sell_list, user_info=user_info, b_list=b_list, s_list=s_list)  
	return render_template('main.html',user_id='-1', name='-1')

@app.route('/fruitmarket')
def fruitmarket():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"
		
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql2 = f"select * from pay_board where kind='과일'"
		curs.execute(sql2)
		
		product_list = curs.fetchall()
		
		print(product_list)
		
		return render_template('fruitmarket.html',user_id=user_id, name=name, product_list=product_list)
		
	return render_template('fruitmarket.html',user_id='-1', name='-1')

#추천 마당	
@app.route('/recommend')
def recommend():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"

	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']	
		
		return render_template('recommend.html',user_id=user_id, name=name, month=month)
		
	return render_template('recommend.html',user_id='-1', name='-1')

#장 마당
@app.route('/cropmarket')
def cropmarket():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"

	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql2 = f"select * from pay_board where kind='작물'"
		curs.execute(sql2)
		
		product_list = curs.fetchall()
		
		print(product_list)
		
		return render_template('fruitmarket.html',user_id=user_id, name=name, product_list=product_list)
		
	return render_template('fruitmarket.html',user_id='-1', name='-1')
	
#작물 정보
@app.route('/fruitinform')
def fruitinform():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"
		
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		return render_template('fruitinform.html',user_id=user_id, name=name)
		
	return render_template('fruitinform.html',user_id='-1', name='-1')

#작물 검색 정보
@app.route('/inform_view', methods=["GET", "POST"])
def inform_view():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"

	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		if request.method == "POST":
			keyword = request.form['keyword']
			
			#driver_url = 'C:\\chromedriver.exe' #윈도우 환경

			driver_url = './chromedriver' #우분투 환경

			chrome_options = webdriver.ChromeOptions()
			chrome_options.add_argument('--headless') #우분투
			chrome_options.add_argument('--no-sandbox')
			chrome_options.add_argument('--privileged')
			chrome_options.add_argument('--incognito')
			chrome_options.add_argument('--disable-dev-shm-usage')
			chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
			
			chrome_options = chrome_options

			driver = webdriver.Chrome(driver_url, chrome_options=chrome_options)
			
			url = f'https://ko.wikipedia.org/wiki/{keyword}'.format(keyword)
			
			driver.get(url)
			contents = driver.page_source

			soup = BeautifulSoup(contents, "html.parser")
		
			# 큰제목 크롤링
			big_title = soup.find_all('h1', class_='firstHeading')
			# 소제목 들 크롤링
			small_title = soup.find_all('span', class_='mw-headline')
			
			#내용들 크롤링
			content = soup.find_all('p')
			
			#이미지 크롤링
			img = soup.find_all('img', class_='thumbimage')
			
			content_list = []
			s_title_list = []
			
			print(img)
			#print(content)
			#소제목들 for문 돌려 리스트에 저장
			for i in small_title:
				s_title_list.append(i.get_text())
			
			#내용들 for문 돌려 리스트에 저장
			for j in content:
				content_list.append(j.get_text())

			
			print("검색어 : " +keyword)
			print("큰 제목 : " +big_title[0].get_text())
			#print(s_title_list)
			#print(content_list)
				
			
			
			#return "<script>alert('삭제가 완료되었습니다!');window.location.href='/borad'</script>"
			
			return render_template('inform_view.html', user_id=user_id, name=name, keyword=keyword, s_title_list=s_title_list, content_list=content_list)
			
		return render_template('inform_view.html',user_id='-1', name='-1')

#동영상 검색 페이지
@app.route('/searchvideo')
def searchvideo():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		return render_template('searchvideo.html',user_id=user_id, name=name)
			
	return render_template('searchvideo.html',user_id='-1', name='-1')


#동영상 검색시 보여주는 페이지
@app.route('/video_view', methods=["GET", "POST"])
def video_view():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"
	
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		if request.method == "POST":
			keyword = request.form['keyword']
			
			#driver_url = 'C:\\chromedriver.exe'

			driver_url = './chromedriver' #우분투 환경' #우분투 환경
			
			chrome_options = webdriver.ChromeOptions()
			chrome_options.add_argument('--headless') #우분투
			chrome_options.add_argument('--no-sandbox')
			chrome_options.add_argument('--privileged')
			chrome_options.add_argument('--incognito')
			chrome_options.add_argument('--disable-dev-shm-usage')
			chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
			
			chrome_options = chrome_options

			driver = webdriver.Chrome(driver_url, chrome_options=chrome_options)

			url = f'https://www.youtube.com/results?search_query={keyword}'

			driver.get(url)
			contents = driver.page_source

			soup = BeautifulSoup(contents, "html.parser")

			lis = soup.find_all('a', class_='yt-simple-endpoint style-scope ytd-video-renderer')			

			#조회수 리스트
			view_list = []

			#제목 리스트
			title_list = []

			#링크 리스트
			src_list = []
		
			for h in lis:
				view_list.append(h.get('aria-label').split()[-1])
				title_list.append(h["title"])
				v_id = h["href"].split("v=")[1]
				src_list.append( f"""<iframe width="400" height=400" src="https://www.youtube.com/embed/{v_id}" frameborder="0" allowfullscreen=""></iframe>""" )
	

			print(f'src_list:{len(src_list)}')

			src_list_html = "<br><br><br>".join(src_list)

			
			return render_template('video_view.html', user_id=user_id, name=name, src_list=src_list, title_list=title_list, view_list=view_list, keyword=keyword)
			
		return render_template('video_view.html',user_id='-1', name='-1')
		
#게시판 
@app.route('/borad')
def borad():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
	
		#페이지 값 1
		page = request.args.get("page", 1, type=int)
		#한 페이지 당 게시물 출력 갯수
		limit = 10
	
		# 페이지 블럭을 5개씩 표기
		block_size = 5
		block_num = int((page - 1) / block_size)   
		block_start = (block_size * block_num) + 1	
		block_end = block_start + (block_size - 1)
  
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
	
		sql = "select count(*) from board"
		curs.execute(sql)
   
	
		#게시물 총 개수
		count_num = curs.fetchall()[0][0]
		#페이지 갯수
		last_page_num = math.ceil(count_num / limit)
	
		# 2페이지 이상
		if page > 1: 
			item_count = count_num % ((page-1)*limit)
			if item_count == 0: item_count = limit
		# 1페이지
		else:
			item_count = count_num % (limit)
			if item_count == 0: item_count = limit
	
	
		if "user_id" in session:
			user_id = session['user_id']
			name = session['user_name']
		
			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()
		
			sql2 = f"select num, title, writer, date, count from board order by num desc limit {limit} offset {(page-1)*limit}"
			curs.execute(sql2)
  
			board_list = curs.fetchall()
			print(board_list)
			return render_template('borad.html',board_list=board_list, name=name, count_num=count_num,limit=limit,page=page,block_start=block_start,block_end=block_end,last_page_num=last_page_num)
		
		return render_template('borad.html',user_id='-1', name='-1')

		
# 게시판 검색
@app.route('/board_search', methods=["GET", "POST"])
def board_search():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		

		keyword = request.form['keyword123']

		print("키워드 : " +keyword)

		if keyword == "":
			return "<script>alert('검색을 하세요');window.location.href='/borad'</script>"
		else:
		
			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()	

		
			sql = "select num, title, writer, date, count from board where title like '%{}%'".format(keyword)
			curs.execute(sql)
		
			search_keyword = curs.fetchall()
	
			print(search_keyword)
		
			return render_template('board_search.html', user_id=user_id, name=name, search_keyword=search_keyword)
	
	return render_template('board_search.html', user_id='-1', name='-1')
	
# 게시글 하나 보기
@app.route('/board_view<int:id>')
def board_view(id):   
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
	 
	   #print(id)
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		#특정 번호인 board 데이터 출력
		sql = "select title, writer, content, date from board where num=%d"%id
		curs.execute(sql)
		
		view = curs.fetchall()
		
		# 작성자 데이터 추출
		sql2 = "select writer from board where num=%d"%id
		curs.execute(sql2)
		
		writer = curs.fetchone()[0]
		
		#작성 번호 출력
		sql3 = "select num from board where num=%d"%id
		curs.execute(sql3)
		
		num = curs.fetchone()[0]
		
		#조회수 증가
		sql4 = "update board set count = count + 1 where num=%d"%id
		curs.execute(sql4)
		
		#댓글
		sql5 = "select writer,content, date from comment where board_num=%d"%id
		curs.execute(sql5)
		comm_list=curs.fetchall()
		
		con.commit()
		print(comm_list)
		
		return render_template('board_view.html', view=view,name=name,writer=writer,user_id=user_id,num=num, id=id, comm_list=comm_list)
	return render_template('write.html',user_id='-1', name='-1') 

# 덧글 작성
@app.route('/comment_write<int:number>', methods=["GET", "POST"])
def comment_write(number):
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor() 
		
		if request.method == "POST":
			comment = request.form['comment'] 
			print(comment)
			if comment is not None:					   
					sql = "insert into comment (`board_num`, `writer`, `content`, `date`) values ('%s', '%s','%s','%s')" %(number, name, comment,current_time)
					curs.execute(sql)
					con.commit()
					con.close()
					curs.close()
					print("comment : "+comment)
					return "<script>alert('글 작성이 완료 되었습니다.');window.location.href='/board_view%d'</script>"%number 
			else:
				
				if comment is None:
					return "<script>alert('내용을 작성해주세요');window.location.href='/write'</script>"

	return render_template('main.html',user_id='-1', name='-1')

# 덧글 작성
@app.route('/proComment_write<int:number>', methods=["GET", "POST"])
def proComment_write(number):
	global current_time
	global month,year,day,time
	
	print(123)
	
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']	

		if request.method == "POST":
			content = request.form['content'] #사진 내용
			f = request.files['img_name']
			img = f.filename #이미지 이름
			print(img)
			
			farm_load = "static/comment/"

		#저장할 경로 + 파일명
			f.save(farm_load+secure_filename(f.filename)) #사진 파일 이름

			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()

			sql = "insert into pro_comment (`name`,`content`, `img_name`, `date`,`proNum`) values ('%s','%s','%s','%s','%d')" %(name, content, img, current_time,number)
			curs.execute(sql)
			con.commit()

			return "<script>alert('후기가 작성되었습니다!');window.location.href='/product_view%d'</script>"%number
	
# 게시글 삭제
@app.route('/board_delete/<int:number>')
def board_delete(number):
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
			  
		sql = "delete from board where num=%d"%number	   
		curs.execute(sql)
		con.commit()
			  
		return "<script>alert('삭제가 완료되었습니다!');window.location.href='/borad'</script>"
	
	return render_template('borad.html')
	

#게시글 수정 보여주는 거
@app.route('/board_modify/<int:number>')
def board_modify(number):
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = "select writer, title, content, date from board where num=%d"%number
		curs.execute(sql)
		
		modify = curs.fetchall()
		
		print(modify)
		return render_template('board_modify.html',user_id=user_id, name=name, modify=modify, number=number)
		
	return render_template('board_modify.html',user_id='-1', name='-1')



#게시글 수정 완료
@app.route('/modify_success/<int:number>', methods=["GET", "POST"])
def modify_success(number):
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		if request.method == "POST":
			title = request.form['title']
			content = request.form['content']
		
			print(title)
			print(content)
			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()
		
			sql = "update board set title = '%s', content = '%s' where num=%d"%(title,content,number)
			curs.execute(sql)
			con.commit()
			
			return "<script>alert('글 수정이 완료되었습니다!');window.location.href='/borad'</script>"
	
	
	return render_template('board_view',user_id='-1', name='-1')
#게시글 작성
@app.route('/write', methods=["GET", "POST"])
def write():
	global current_time
	global month,year,day,time
 
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		return render_template('write.html',user_id=user_id, name=name, year=year, month=month, day=day, time=time)
	   
	else:
		return "<script>alert('로그인을 먼저 해주세요!');window.location.href='/login'</script>"
		
	return render_template('write.html',user_id='-1', name='-1')


@app.route('/write_success', methods=["GET", "POST"])
def write_success():
	global current_time
	global month,year,day,time  
	
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		if request.method == "POST":
			title = request.form['title']
			content = request.form['content']
			
			if title is not None and content is not None:
				con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
				curs = con.cursor()
						 
				sql = "insert into board (`writer`, `title`, `content`, `date`) values ('%s','%s','%s','%s')" %(user_id, title, content,current_time)
				curs.execute(sql)
				con.commit()
				con.close()
				curs.close()
				print("title : " +title)
				print("content : "+content)
				return "<script>alert('글 작성이 완료 되었습니다.');window.location.href='/borad'</script>" 
			else:
				if title is None:
					return "<script>alert('제목을 작성해주세요');window.location.href='/write'</script>"
				elif content is None:
					return "<script>alert('내용을 작성해주세요');window.location.href='/write'</script>"
			

	
@app.route('/login', methods=["GET", "POST"])
def login():
	if "uesr_id" in session:
		user_id = session['user_id']
		name = session['user_name']
	if request.method=="GET":
		if "user_id" in session:
			user_id = session['user_id']
			name = session['user_name']
			return render_template('login.html',user_id=user_id, name=name)
		return render_template('login.html',user_id='-1', name='-1')

	elif request.method=="POST":
		user_id = request.form["user_id"]
		pw = request.form["password"]
		if user_id == "":
			return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"
		else:
			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			cur = con.cursor()
			sql = f'select EXISTS (select * from user_info where id="{user_id}" and password="{pw}") as success'

			cur.execute(sql)
	
			login_check=cur.fetchone()[0]
			sql2 = f'select name from user_info where id = "{user_id}"'
			cur.execute(sql2)
		
			name=cur.fetchone()
			if name:
				name = name[0]
			# if logout:
				# session['user_id'] = None

			#로그인성공
			if login_check == 1:
				session['user_id'] = user_id
				session['user_name'] = name
				pass
		
			else:
				return "<script>alert('존재하지 않습니다');window.location.href='/login'</script>"
		
			print(login_check)
			print(f'user_id={user_id}\tpw={pw}')
		
			return render_template('main.html',user_id=user_id,name=name)
	
@app.route('/test', methods=['GET', 'POST'])

def test(): #회원가입 함수
   
   #입력된 값 id 값 통해 전송
	if request.method == 'POST':
		name = request.form['name']
		userid = request.form['userid']
		password = request.form['password']
		passCheck = request.form['pass_check']
		email = request.form['email']
		phoneNum = request.form['phoneNum']
		job = request.form['job']
	  
		

   # mysql db 연결
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
	  
		sql2 = f'select EXISTS (select * from user_info where id="{userid}") as success'
		curs.execute(sql2)
		result = curs.fetchone()[0]
	  
		if result==1:
			return "<script>alert('이미 존재하는 아이디입니다.');window.location.href ='/signup'</script>"
		else:
			if 4 <= len(userid) < 20:		
				if userid not in password:
					
					sql = "insert into user_info (`name`,`id`,`password`,`email`,`phoneNum`, `job`) values ('%s','%s','%s','%s','%s','%s')" %(name,userid,password,email,phoneNum,job)
					curs.execute(sql)
					con.commit()
				elif userid in password:
					return "<script>alert('개인정보관련은 사용불가입니다!');window.location.href='/signup'</script>"
			else:
				return "<script>alert('4~20자리 이내 영문 소문자, 숫자만 가능합니다.');window.location.href='/signup'</script>"			
		
		
		return "<script>alert('회원가입이 완료되었습니다..');window.location.href ='/login'</script>"
		con.close()
		curs.close()



	return render_template('login.html')	
@app.route('/signup')
def signup():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		return render_template('signup.html',user_id=user_id, name=name)
		
	return render_template('signup.html',user_id='-1', name='-1')

	
@app.route('/product_regist')
def product_regist():
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 해주세요!');window.location.href='/login'</script>"

	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']   
		
		return render_template('product_regist.html',user_ids=user_id, name=name)
			
	return render_template('product_regist.html', user_id='-1', name='-1')

# 작물 등록
@app.route('/product_success', methods=["GET", "POST"])
def product_success():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		ranNum = str(random.randint(1, 10000))
			
		if request.method == "POST":
			f = request.files['img_name']
			#저장할 경로 + 파일명
			f.save('static/uploads/'+secure_filename(ranNum+f.filename))
			
			kind = request.form['kind'] #과일, 작물
			name = request.form['name'] #이름
			content = request.form['content'] #내용
			price = request.form['price'] #가격
			count = request.form['count'] #수량
			img = ranNum+f.filename #이미지 이름
			
			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()
						
			sql = "insert into pay_board (`userid`, `proname`, `price`, `content`, `count`, `kind`, `image`,`state`,`invo_num`) values ('%s', '%s','%s','%s','%s', '%s','%s','%s','%s')"%(user_id, name, price, content, count, kind, img,'준비중','준비중')
			curs.execute(sql)
			con.commit()
			
			if kind == "과일":
				return "<script>alert('작물 등록이 완료되었습니다');window.location.href ='/fruitmarket'</script>"
			elif kind == "작물":
				return "<script>alert('작물 등록이 완료되었습니다');window.location.href='/cropmarket'</script>"
			
@app.route('/product_view<int:pro_num>')
def product_view(pro_num):
	if "user_id" not in session:
		return "<script>alert('로그인을 먼저 하세요!');window.location.href='/login'</script>"

	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = "select * from pay_board where num=%d"%pro_num
		curs.execute(sql)
		product = curs.fetchall()
		
		sql2 = "select * from pro_comment where proNum=%d"%pro_num
		curs.execute(sql2)
		comment = curs.fetchall()
		print(comment)
		print(product)
		return render_template('product_view.html', user_id=user_id, name=name, product=product,pro_num=pro_num,comment=comment)
	
	return render_template('product_view.html', user_id='-1', name='-1')
	
	
@app.route('/purchase<int:pro_num>', methods=["GET", "POST"])
def purchase(pro_num):
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
			
		if request.method == "POST":
			count = int(request.form["count"])
		
		print(count)
    
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = "select * from pay_board where num=%d"%pro_num
		curs.execute(sql)
		
		detail = curs.fetchall()
		
		sql2 = f"select phoneNum from user_info where id='%s'"%user_id
		curs.execute(sql2)
		phone = curs.fetchone()[0]
		
		sql3 = f"select point from user_info where id='%s'"%user_id
		curs.execute(sql3)
		point = curs.fetchone()[0]
		
		print(detail)		
		print(phone)		
		
		return render_template('purchase.html', user_id=user_id, name=name, detail=detail, count=count, phone=phone, point=point)
	
	return render_template('purchase.html', user_id='-1', name='-1')

@app.route('/test2', methods=["POST"])
def test2():
	if "user_id" in session:
		a =  request.form['postcode']
		b =  request.form['roadAddress']
		c =  request.form['jibunAddress']
		d =  request.form['detailAddress']
		e =  request.form['extraAddress']
		productNum = int(request.form['productNum'])
		seller =request.form['seller_id']
		buyer=request.form['buyer']
		price=int(request.form['price'])
		count=int(request.form['count'])

		
		user_id = session['user_id']
		name = session['user_name']   
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		print(buyer)
		print(a+b+c+d+e)
		print(seller)
		print(productNum)
		print(price)
		print(count)
		
		sql = "insert into pay_info values ('%s','%s','%s','%d','%d','%s','%s','%s','%d')"%(user_id, buyer, seller, count, price,'준비중','준비중',a+b+c+d+e,productNum)
		curs.execute(sql)
		con.commit()
		
		# sql2 = "select * from pay_board"
		# curs.execute(sql2)
		# test = curs.fetchone()
		#print(curs.rowcount)		        

		return render_template('main.html', user_id=user_id, name=name)
	
	return render_template('main.html', user_id='-1', name='-1')
@app.route('/test3', methods=["POST"])
def test3():
	print(123)
	if "user_id" in session:
		user_id = session['user_id']
		price=int(request.form['price'])
	 
		print(price)
		user_id = session['user_id']
		name = session['user_name']   
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = "update user_info set point = point - '%d' where id = '%s'" %(price,user_id)
		curs.execute(sql)
		con.commit()
		
		return render_template('main.html', user_id=user_id, name=name)
	
	return render_template('main.html', user_id='-1', name='-1')	
	
@app.route('/test4', methods=["POST"])
def test4():
	if "user_id" in session:
		user_id = session['user_id']
		point=int(request.form['point'])
	 
		print(point)
		user_id = session['user_id']
		name = session['user_name']   
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = "update user_info set point = point + '%d' where id = '%s'" %(point,user_id)
		curs.execute(sql)
		con.commit()
		
		return render_template('main.html', user_id=user_id, name=name)
	
	return render_template('main.html', user_id='-1', name='-1')		

@app.route('/test5', methods=["POST"])
def test5():
	if "user_id" in session:
		user_id = session['user_id']
		invoNum=request.form['invoNum']
		pNum =int(request.form['pNum'])
		print(pNum)
		user_id = session['user_id']
		name = session['user_name']   
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = "update pay_info set invo_num = '%s',status='%s' where product_num = '%d'" %(invoNum,'배송중',pNum)
		curs.execute(sql)
		con.commit()

        
		return render_template('main.html', user_id=user_id, name=name)
	
	return render_template('main.html', user_id='-1', name='-1')		 
	
@app.route('/detail_purchase', methods=["GET", "POST"])
def detail_purchase():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

	
		return render_template('main.html', user_id=user_id, name=name)
	
	return render_template('main.html', user_id='-1', name='-1')
	


#들어가기 전에 소개글 작성
@app.route('/meeting_intro', methods=["GET", "POST"])
def meeting_intro():
	if "user_id" not in session:
		return "<script>alert('로그인 후 이용가능합니다!');window.location.href='/login'</script>"
		
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		if request.method == "POST":
			intro = request.form['intro']

			
			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()

			sql = "insert into user_intro (`name`, `intro`) values ('%s','%s')" %(name, intro)
			curs.execute(sql)
			con.commit()


		return redirect(url_for('meeting'))
		
#채팅 
@app.route('/meeting', methods=["GET", "POST"])
def meeting():	
	
	if "user_id" not in session:
		return "<script>alert('로그인 후 이용가능합니다!');window.location.href='/login'</script>"
		
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
				
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
	
		#만남의 광장, 특정 유저 가입, 존재 여부 확인 쿼리
		sql = "select exists (select * from user_intro where name = '%s') as success"%name
		curs.execute(sql)
		
		result = curs.fetchone()[0]

		#데이터가 존재할때
		if result == 1:
			
			sql = f"select * from user_images where name = '%s'"%name
			curs.execute(sql)

			u_images = curs.fetchall()


			sql2 = f"select * from user_intro where name = '%s'"%name
			curs.execute(sql2)
		
			f_intro = curs.fetchone()

			#만남의 광장에 등록된 유저들
			sql3 = f"select name from user_intro"
			curs.execute(sql3)
		
			users = curs.fetchall()
			
			
			return render_template('meeting.html', user_id=user_id, name=name, f_intro=f_intro, u_images=u_images,users=users)

		#데이터가 존재하지 않을 떄
		elif result == 0:
			
			return render_template('meeting_intro.html', user_id=user_id, name=name)

def messageReceived(methods=['GET', 'POST']):
	print('message was received!!!')
	

@socketio.on('my event')
def handle_my_custom_event(json):
	print('received my event: ' + str(json))
	socketio.emit('my response', json, callback=messageReceived)	
	


@app.route('/chatting_test')
def chatting_test():
        
	return render_template('chatting_test.html')
	
#자기 농장 사진관 등록
@app.route('/regist_farm')
def regist_farm():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		return render_template('regist_farm.html', user_id=user_id, name=name)

	return render_template('regist_farm.html', user_id='-1', name='-1')

	

#사진 등록 완료
@app.route('/farm_success', methods=["GET", "POST"])
def farm_success():
	global current_time
	global month,year,day,time

	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		if request.method == "POST":
			title = request.form['title'] #사진 제목
			content = request.form['content'] #사진 내용
			f = request.files['file']

			img = f.filename #이미지 이름

			farm_load = "C:/Users/ehdrm/Desktop/졸작/static/farm/"

		#저장할 경로 + 파일명
			f.save(farm_load+secure_filename(f.filename)) #사진 파일 이름

			con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
			curs = con.cursor()

			sql = "insert into user_images (`name`, `title`, `content`, `img_name`, `date`) values ('%s','%s','%s','%s','%s')" %(name, title, content, img, current_time)
			curs.execute(sql)
			con.commit()

			return redirect(url_for('meeting'))
	
#농장 사진 볼 수 있는 곳
@app.route('/image_view<int:num>')
def image_view(num):
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()

		sql = f"select * from user_images where num = %d"%num
		curs.execute(sql)

		detail_farm = curs.fetchall()

		return render_template('image_view.html', user_id=user_id, name=name, detail_farm=detail_farm)

	return render_template('image_view.html', user_id='-1', name='-1')

	
#유저의 개인 농장 입장
@app.route('/user_farm')
def user_farm():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		user_name = request.args.get('visit')
		
		con = pymysql.connect(host='15.164.103.25', user='ehdrms523', password='1234', db='farmdiary', charset='utf8', port=3306)
		curs = con.cursor()
		
		sql = f"select * from user_intro where name = '%s'"%user_name
		curs.execute(sql)
		
		visit_intro = curs.fetchone()
		
		sql2 = f"select * from user_images where name = '%s'"%user_name
		curs.execute(sql2)
		
		visit_images = curs.fetchall()
		
		sql3 = f"select name from user_intro"
		curs.execute(sql3)
		
		users = curs.fetchall()
				
		if name == user_name:
			return redirect(url_for('meeting'))
		
		else:
			return render_template('user_farm.html', user_id=user_id, name=name, visit_intro=visit_intro,visit_images=visit_images,users=users)
	
	return render_template('user_farm.html', user_id='-1', name='-1')


	   
@app.route('/kakaomap')
def kakaomap():
	if "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']

		return render_template('kakaomap.html', user_id=user_id, name=name)
	 
	return render_template('kakaomap.html', user_id='-1', name='-1')


	
@app.route('/weathertest', methods=["GET", "POST"])
def weathertest():
	if "user_id" not in session:
		return "<script>alert('로그인 후 이용가능합니다!');window.location.href='/login'</script>"
		
	elif "user_id" in session:
		user_id = session['user_id']
		name = session['user_name']
		
		if request.method == "POST":
			local = request.form['local']
			
			#driver_url = 'C:\\chromedriver.exe'
			
			driver_url = './chromedriver' #우분투 환경' #우분투 환경
			
			chrome_options = webdriver.ChromeOptions()
			chrome_options.add_argument('--headless') #우분투
			chrome_options.add_argument('--no-sandbox')
			chrome_options.add_argument('--privileged')
			chrome_options.add_argument('--incognito')
			chrome_options.add_argument('--disable-dev-shm-usage')
			chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
			
			chrome_options = chrome_options

			driver = webdriver.Chrome(driver_url, chrome_options=chrome_options)

			contents = driver.page_source
		
			#서울 지역 날씨 
			if local == "seoul":
				
		
				url = f'https://www.weather.go.kr/weather/observation/currentweather.jsp?auto_man=m&stn=0&type=t99&reg=109&x=21&y=6&tm=2021.05.19.08%3A00'
				driver.get(url)
				contents = driver.page_source

				soup = BeautifulSoup(contents, "html.parser")
		
		
				table = soup.find('table', class_='table_develop3')
		
				w_list = []		
		
				print(w_list)
		
				for tr in table.find_all('tr'):
					tds = list(tr.find_all('td'))
					for td in tds:
						if td.find('a'):
							point = td.find('a').text
							temp = tds[5].text
							humidity = tds[9].text
							print("{0:<7} {1:<7} {2:<7}".format(point,temp,humidity))
							w_list.append([point,temp,humidity])
				
		
			
		
		
			#부산 지역 날씨
			elif local == "busan":
				url = f'https://www.weather.go.kr/weather/observation/currentweather.jsp?auto_man=m&stn=0&type=t99&reg=159&x=18&y=12&tm=2021.05.19.08%3A00'
				driver.get(url)
				contents = driver.page_source

				soup = BeautifulSoup(contents, "html.parser")
		
		
				table = soup.find('table', class_='table_develop3')
		
				w_list = []		
		
		
		
				for tr in table.find_all('tr'):
					tds = list(tr.find_all('td'))
					for td in tds:
						if td.find('a'):
							point = td.find('a').text
							temp = tds[5].text
							humidity = tds[9].text
							print("{0:<7} {1:<7} {2:<7}".format(point,temp,humidity))
							w_list.append([point,temp,humidity])
				
		
		
			
			
				
			#광주 지역 날씨
			elif local == "gwangju":
				url = f'https://www.weather.go.kr/weather/observation/currentweather.jsp?auto_man=m&stn=0&type=t99&reg=156&x=24&y=14&tm=2021.05.19.08%3A00'
				driver.get(url)
				contents = driver.page_source

				soup = BeautifulSoup(contents, "html.parser")
		
		
				table = soup.find('table', class_='table_develop3')
		
				w_list = []		
		
		
		
				for tr in table.find_all('tr'):
					tds = list(tr.find_all('td'))
					for td in tds:
						if td.find('a'):
							point = td.find('a').text
							temp = tds[5].text
							humidity = tds[9].text
							print("{0:<7} {1:<7} {2:<7}".format(point,temp,humidity))
							w_list.append([point,temp,humidity])
				
		
			
			
			
			#대전 지역 날씨
			elif local == "daejun":
				url = f'https://www.weather.go.kr/weather/observation/currentweather.jsp?auto_man=m&stn=0&type=t99&reg=133&x=25&y=11&tm=2021.05.19.08%3A00'
				driver.get(url)
				contents = driver.page_source

				soup = BeautifulSoup(contents, "html.parser")
		
		
				table = soup.find('table', class_='table_develop3')
		
				w_list = []		
		
		
		
				for tr in table.find_all('tr'):
					tds = list(tr.find_all('td'))
					for td in tds:
						if td.find('a'):
							point = td.find('a').text
							temp = tds[5].text
							humidity = tds[9].text
							print("{0:<7} {1:<7} {2:<7}".format(point,temp,humidity))
							w_list.append([point,temp,humidity])
				
		
			
			
			#강원 지역 날씨
			elif local == "gwanone":
				url = f'https://www.weather.go.kr/weather/observation/currentweather.jsp?auto_man=m&stn=0&type=t99&reg=105&x=28&y=10&tm=2021.05.19.08%3A00'
				driver.get(url)
				contents = driver.page_source

				soup = BeautifulSoup(contents, "html.parser")
		
		
				table = soup.find('table', class_='table_develop3')
		
				w_list = []		
		
		
		
				for tr in table.find_all('tr'):
					tds = list(tr.find_all('td'))
					for td in tds:
						if td.find('a'):
							point = td.find('a').text
							temp = tds[5].text
							humidity = tds[9].text
							print("{0:<7} {1:<7} {2:<7}".format(point,temp,humidity))
							w_list.append([point,temp,humidity])
				
		
				
			

			#제주도 날씨
			elif local == "jeju":
				url = f'https://www.weather.go.kr/weather/observation/currentweather.jsp?auto_man=m&stn=0&type=t99&reg=184&x=22&y=0&tm=2021.05.19.08%3A00'
				driver.get(url)
				contents = driver.page_source

				soup = BeautifulSoup(contents, "html.parser")
		
		
				table = soup.find('table', class_='table_develop3')
		
				w_list = []		
		
		
		
				for tr in table.find_all('tr'):
					tds = list(tr.find_all('td'))
					for td in tds:
						if td.find('a'):
							point = td.find('a').text
							temp = tds[5].text
							humidity = tds[9].text
							print("{0:<7} {1:<7} {2:<7}".format(point,temp,humidity))
							w_list.append([point,temp,humidity])
				
		

			return render_template('weathertest.html', user_id=user_id, name=name, w_list=w_list)
		
		return render_template('weathertest.html', user_id='-1', name='-1')
 

#Socket 가동

if __name__ == '__main__':
	#app.run(debug=True)
	#socketio.run(app, debug=True, host = '0.0.0.0')
		
	socketio.run(app,port=5000, host='0.0.0.0', debug=True)
	#app.run(host='0.0.0.0', debug=True, port=5000)