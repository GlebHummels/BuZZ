from flask import Flask, render_template, url_for, request, redirect, make_response, jsonify
import sqlite3
import time


con = sqlite3.connect("source/main.db")
cur = con.cursor()
result = cur.execute("""SELECT * FROM Users""").fetchall()
for i in result:
    print(i)
con.close()

def friends_of(user_id):
    res = []
    con = sqlite3.connect("source/main.db")
    cur = con.cursor()
    user_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users
    WHERE id={user_id}""").fetchall())
    user_subscribers = int_m(cur.execute(f"""SELECT SUBSCRIBERS FROM Users
    WHERE id={user_id}""").fetchall())   
    for i in user_subscriptions:
        if i in user_subscribers:
            res.append(i)
    con.close()
    return res

def subscribers_of(user_id):
    res = []
    con = sqlite3.connect("source/main.db")
    cur = con.cursor()
    user_subscribers = int_m(cur.execute(f"""SELECT SUBSCRIBERS FROM Users
    WHERE id={user_id}""").fetchall())
    friends = friends_of(user_id)
    for i in user_subscribers:
        if i not in friends:
            res.append(i)
    con.close()
    return res    

def user_in_base(a):
    con = sqlite3.connect("source/main.db")
    cur = con.cursor()
    result = [i[1].lower() for i in cur.execute("""SELECT * FROM Users""").fetchall()]
    if a.lower() in result:
        con.close()
        return True
    con.close()
    return False

def user_search(rec):
    res = []
    con = sqlite3.connect("source/main.db")
    cur = con.cursor()
    result = cur.execute("""SELECT * FROM Users""").fetchall()
    con.close()
    for i in result:
        i = list(i)
        if rec.lower() in i[1].lower():
            res.append([i[1], i[4], i[5], i[0]])
    return res

def check_password(user, pas):
    if user_in_base(user):
        con = sqlite3.connect("source/main.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT PASSWORD FROM Users
                    WHERE NAME = '{user}'""").fetchone()[0]
        if str(result) == str(pas):
            return True
        return False
    else:
        return False
    
def check_cookies(request):
    a, b = request.cookies.get('name'), request.cookies.get('password')
    if a and b:
        if check_password(a, b):
            return True
        return False
    return False
        
def int_m(a):
    b = a[0][0]
    if b == '':
        return []
    return [int(i) for i in b.split(',')]
        
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def main():
    if check_cookies(request):
        return redirect('/home')
    else:
        if request.method == 'GET':
            return render_template('page1.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'), err='')
        elif request.method == 'POST':
            button = request.form['butt']
            if button == 'login':
                return redirect('/login')
            if check_password(request.form['name'], request.form['password']):
                res = make_response(redirect('/home'))
                res.set_cookie('name', request.form['name'], max_age=6000)
                res.set_cookie('password', request.form['password'], max_age=6000)
                return res
            return render_template('page1.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'), err='Wrong password or login')
    
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login_page.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'), err='')
    elif request.method == 'POST':
        if not user_in_base(request.form['name']):
            if request.form['name'] != '' and request.form['password'] != '':
                if '@' in request.form['mail'] and '.' in request.form['mail']:
                    con = sqlite3.connect("source/main.db")
                    cur = con.cursor()
                    d = request.form['year'] + '.' + request.form['month'] + '.' + request.form['day']
                    result = cur.execute(f"""INSERT INTO Users(NAME, PASSWORD, MAIL, DATE, PHOTO, SUBSCRIPTIONS, SUBSCRIBERS) VALUES('{request.form['name']}', '{request.form['password']}', '{request.form['mail']}', '{d}', 'default.png', '', '')""")
                    con.commit()
                    con.close()
                    res = make_response(redirect('/home'))
                    res.set_cookie('name', request.form['name'], max_age=6000)
                    res.set_cookie('password', request.form['password'], max_age=6000)
                    return res
                else:
                    return render_template('login_page.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'), err='Wrong mail adress') #Неверный mail
            else:
                return render_template('login_page.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'), err='Wrong name or password')
        else:
            return render_template('login_page.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'), err='This login already exists.') #Если такой логин уже есть
        
    
@app.route('/home', methods=['POST', 'GET'])
def home():
    if check_cookies(request):
        con = sqlite3.connect("source/main.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT id FROM Users
                WHERE NAME='{request.cookies.get('name')}' and PASSWORD='{request.cookies.get('password')}'""").fetchall()
        con.close()    
        u_id = result[0][0]
        return make_response(redirect(f'/user/{u_id}'))
    else:
        return make_response(redirect('/'))


@app.route('/user/<int:u_id>', methods=['POST', 'GET'])
def user_page(u_id):
    if request.method == 'GET':
        if check_cookies(request):
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT * FROM Users
            WHERE id={u_id}""").fetchall()
            result = list(result[0])
            name, date, photo, friends = result[1], result[4], result[5], result[6]
            con.close()
            
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT id FROM Users
            WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()
            user_id = result[0][0]
            
            your_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users
            WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall())
            user_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users
            WHERE id={u_id}""").fetchall())
            your_subscribers = int_m(cur.execute(f"""SELECT SUBSCRIBERS FROM Users
            WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall())
            user_subscribers = int_m(cur.execute(f"""SELECT SUBSCRIBERS FROM Users
            WHERE id={u_id}""").fetchall())
            stories = cur.execute(f"""SELECT * FROM Stories
            WHERE USERID={u_id}""").fetchall()
            stories = [list(i) for i in stories]
            stories.reverse()
            for i in range(len(stories)):
                a = stories[i]
                a = a[1:]
                a.append(i)
                stories[i] = a
            con.close()
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['settings'] = url_for('static', filename='settings.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')
            param['user_photo'] = url_for('static', filename=f'user_photos/{photo}')
            param['add_friend'] = url_for('static', filename=f'add_friend.png')
            param['delete_friend'] = url_for('static', filename=f'delete_friend.png')
            param['subscribe'] = url_for('static', filename=f'subscribe.png')
            param['unsubscribe'] = url_for('static', filename=f'unsubscribe.png')
            param['send_story'] = url_for('static', filename='send_story.png')
            param['trash_bin'] = url_for('static', filename='trash_bin.png')
            param['write_message'] = url_for('static', filename='write_message.png')
            param['your_subscriptions'], param['user_subscriptions'] = your_subscriptions, user_subscriptions
            param['your_subscribers'], param['user_subscribers'] = your_subscribers, user_subscribers
            param['number_of_friends'] = len(friends_of(u_id))
            param['number_of_subscribers'] = len(subscribers_of(u_id))
            param['stories'] = stories
            param['name'] = name
            param['date'] = date
            param['u_id'] = u_id
            param['user_id'] = user_id
            return render_template('user_page.html', **param)
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        con = sqlite3.connect("source/main.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT id FROM Users
        WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()
        user_id = result[0][0]        
        your_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users
        WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall())
        user_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users
        WHERE id={u_id}""").fetchall())
        your_subscribers = int_m(cur.execute(f"""SELECT SUBSCRIBERS FROM Users
        WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall())
        user_subscribers = int_m(cur.execute(f"""SELECT SUBSCRIBERS FROM Users
        WHERE id={u_id}""").fetchall())
        a = request.form['butt']
        if a in ['subscribe', 'delete_friend', 'add_friend', 'unsubscribe']:
            if a == 'subscribe':
                user_subscribers.append(user_id)
                your_subscriptions.append(u_id)
            elif a == 'delete_friend': #удаление из друзей
                user_subscribers.remove(user_id)
                your_subscriptions.remove(u_id)
            elif a == 'add_friend':
                your_subscriptions.append(u_id)
                user_subscribers.append(user_id)
            elif a == 'unsubscribe':
                user_subscribers.remove(user_id)
                your_subscriptions.remove(u_id)
            result = cur.execute(f"""UPDATE Users
            SET SUBSCRIBERS = '{','.join([str(i) for i in user_subscribers])}'
            WHERE id = {u_id}""")
            con.commit()
            result = cur.execute(f"""UPDATE Users
            SET SUBSCRIPTIONS = '{','.join([str(i) for i in your_subscriptions])}'
            WHERE id = {user_id}""")
            con.commit()
            con.close() 
            return make_response(redirect(f'/user/{u_id}'))
        elif a in ['u_subscribers', 'u_friends']:
            con.close()
            return make_response(redirect(f'/{a[2:]}/{u_id}'))
        elif a == 'send_story':
            t = ' '.join(time.ctime(time.time()).split()[1:-1])
            cont = request.form['story']
            cont = "/'".join(cont.split("'"))
            if cont != '':
                con = sqlite3.connect("source/main.db")
                cur = con.cursor()
                #result = cur.executemany(f"""INSERT INTO Stories(id, CONTENT, DATE) VALUES(?, ?, ?)""", [(u_id, str(cont), str(t))])
                result = cur.execute(f"""INSERT INTO Stories(USERID, CONTENT, DATE) VALUES({u_id}, '{cont}', '{t}')""")
                con.commit()
                con.close() 
            return make_response(redirect(f'/user/{u_id}'))
        elif 'throw_out' in a:
            a = int(a[10:])
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT id FROM Stories""").fetchall()
            post_id = result[-1][0] - a
            result = cur.execute(f"""DELETE from Stories where id={post_id}""")
            con.commit()
            con.close()
            return make_response(redirect(f'/user/{u_id}'))
        elif a == 'write_message':
            return make_response(redirect(f'/chat/{user_id}/{u_id}'))
        con.close()
        return make_response(redirect(f'/{a}'))
    
    
@app.route('/friends/<int:u_id>', methods=['POST', 'GET'])
def user_friends(u_id):
    if request.method == 'GET':
        if check_cookies(request):
            friends = friends_of(u_id)
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = [list(i) for i in cur.execute(f"""SELECT * FROM Users WHERE id IN ({','.join(tuple([str(i) for i in friends]))})""").fetchall()]
            con.close()
            result = [[i[1], i[4], i[5], i[0]] for i in result]
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')
            param['arrow'] = url_for('static', filename='arrow.png')            
            param['friends_of_user'] = result
            return render_template('user_friends.html', **param)
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        if request.form['butt'] == 'arrow':
            return make_response(redirect(f'/user/{u_id}'))
        elif 'redirect' in request.form['butt']:
            a = request.form['butt'][9:]
            return make_response(redirect(f'/user/{a}'))
        else:
            a = request.form['butt']
            return make_response(redirect(f'/{a}'))



@app.route('/subscribers/<int:u_id>', methods=['POST', 'GET'])
def user_subscribers(u_id):
    if request.method == 'GET':
        if check_cookies(request):
            subscribers = subscribers_of(u_id)
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = [list(i) for i in cur.execute(f"""SELECT * FROM Users WHERE id IN ({','.join(tuple([str(i) for i in subscribers]))})""").fetchall()]
            con.close()
            result = [[i[1], i[4], i[5], i[0]] for i in result]
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')
            param['arrow'] = url_for('static', filename='arrow.png')            
            param['subscribers_of_user'] = result
            return render_template('user_subscribers.html', **param)
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        if request.form['butt'] == 'arrow':
            return make_response(redirect(f'/user/{u_id}'))
        elif 'redirect' in request.form['butt']:
            a = request.form['butt'][9:]
            return make_response(redirect(f'/user/{a}'))
        else:
            a = request.form['butt']
            return make_response(redirect(f'/{a}'))    
  
    
@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if request.method == 'GET':
        if check_cookies(request):
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT * FROM Users
            WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()
            result = list(result[0])
            name, password, mail, date = result[1], result[2], result[3], result[4]
            con.close()
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['save'] = url_for('static', filename='save.png')
            param['style'] = url_for('static', filename='doc.css')
            param['name'] = name
            param['password'] = password
            param['mail'] = mail
            param['err'] = ''
            return render_template('settings.html', **param)
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        a = request.form['butt']
        if a == 'save':
            if (not user_in_base(request.form['name'])) or request.form['name'] == request.cookies.get('name'):
                if request.form['name'] != '' and request.form['password'] != '':
                    if '@' in request.form['mail'] and '.' in request.form['mail']:
                        con = sqlite3.connect("source/main.db")
                        cur = con.cursor()
                        d = request.form['year'] + '.' + request.form['month'] + '.' + request.form['day']
                        result = cur.execute(f"""UPDATE Users
                        SET (NAME, PASSWORD, MAIL, DATE, PHOTO) = ('{request.form['name']}', '{request.form['password']}', '{request.form['mail']}', '{d}', 'default.png')
                        WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""")
                        user_id = cur.execute(f"""SELECT id from Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()[0][0]
                        res = make_response(redirect('/home'))
                        res.set_cookie('name', request.form['name'], max_age=6000)
                        res.set_cookie('password', request.form['password'], max_age=6000)
                        file = request.files['file']
                        file.save("static\\user_photos\\" + str(user_id) + '.png')
                        result = cur.execute(f"""UPDATE Users
                        SET (PHOTO) = ('{str(user_id) + '.png'}')
                        WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""")
                        con.commit()
                        con.close()                        
                        return res
                    else:
                        return render_template('settings.html', buzz_png=url_for('static', filename='buzz.png'), style=url_for('static', filename='doc.css'), err='Wrong mail adress') #Неверный mail
                else:
                    return render_template('settings.html', buzz_png=url_for('static', filename='buzz.png'), style=url_for('static', filename='doc.css'), err='Wrong name or password')
            else:
                return render_template('settings.html', buzz_png=url_for('static', filename='buzz.png'), style=url_for('static', filename='doc.css'), err='This login already exists.') #Если такой логин уже есть
        else:
            return make_response(redirect(f'/{a}'))
    

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    if request.method == 'GET':
        if check_cookies(request):
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')
            param['send_rec'] = url_for('static', filename='send_story.png')
            param['user_list'] = []
            return render_template('friends.html', **param)
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        a = request.form['butt']
        if a == 'send_rec':
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')
            param['send_rec'] = url_for('static', filename='send_story.png')          
            param['user_list'] = user_search(request.form['friend_name'])
            param['len_user_list'] = len(user_search(request.form['friend_name']))
            return render_template('friends.html', **param)
        return make_response(redirect(f'/{a}'))


@app.route('/chat/<string:my_id>/<int:u_id>', methods=['POST', 'GET'])
def chat(my_id, u_id):
    my_id = int(my_id)
    if request.method == 'GET':
        if check_cookies(request):
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT id FROM Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()[0][0]
            user_inf = cur.execute(f"""SELECT * FROM Users WHERE id={u_id}""").fetchall()[0]
            con.close()
            if my_id == result:
                con = sqlite3.connect("source/main.db")
                cur = con.cursor()
                result = [list(i)[1:] for i in cur.execute(f"""SELECT * FROM Messages WHERE (FIRSTID={my_id} AND SECONDID={u_id}) OR  (FIRSTID={u_id} AND SECONDID={my_id})""").fetchall()]
                con.commit()
                con.close()
                param = {}
                param['friends'] = url_for('static', filename='friends.png')
                param['messages'] = url_for('static', filename='messages.png')
                param['home'] = url_for('static', filename='home.png')
                param['news'] = url_for('static', filename='news.png')
                param['style'] = url_for('static', filename='doc.css')
                param['user_inf'] = [user_inf[0], user_inf[1], url_for('static', filename=f'user_photos/{user_inf[5]}'), user_inf[4]]
                param['send_message'] = url_for('static', filename='send_story.png')
                param['chat_messages'] = result
                return render_template('chat.html', **param)
            else:
                return 'ВАМ БАН'
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        a = request.form['butt']
        if a == 'send_message':
            message = request.form['message']
            t = time.ctime(time.time()).split()
            m = str(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(t[1]) + 1)
            m = '0' + m if len(m) == 1 else m
            t = t[2] + '.' + m + ' ' + t[3]
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            user_inf = cur.execute(f"""SELECT * FROM Users WHERE id={u_id}""").fetchall()[0]
            result = cur.execute(f"""INSERT INTO Messages(FIRSTID, SECONDID, CONTENT, DATE) VALUES({my_id}, '{u_id}', '{message}', '{t}')""")
            result = [list(i)[1:] for i in cur.execute(f"""SELECT * FROM Messages WHERE (FIRSTID={my_id} AND SECONDID={u_id}) OR  (FIRSTID={u_id} AND SECONDID={my_id})""").fetchall()]
            con.commit()
            con.close()
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')
            param['user_inf'] = [user_inf[0], user_inf[1], url_for('static', filename=f'user_photos/{user_inf[5]}'), user_inf[4]]
            param['send_message'] = url_for('static', filename='send_story.png')
            param['chat_messages'] = result
            return render_template('chat.html', **param)            
        return make_response(redirect(f'/{a}'))    
    
    
@app.route('/messages', methods=['POST', 'GET'])
def chats():
    if request.method == 'GET':
        if check_cookies(request):
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            my_id = cur.execute(f"""SELECT id FROM Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()[0][0]
            result = list(set([i[0] for i in cur.execute(f"""SELECT SECONDID FROM Messages WHERE FIRSTID={my_id}""").fetchall()]))
            result2 = list(set([i[0] for i in cur.execute(f"""SELECT FIRSTID FROM Messages WHERE SECONDID={my_id}""").fetchall()]))
            result2 = [i for i in result2 if i not in result]
            result = [list(i) for i in cur.execute(f"""SELECT * FROM Users WHERE id IN ({','.join(tuple([str(i) for i in result]))})""").fetchall()]
            result2 = [list(i) for i in cur.execute(f"""SELECT * FROM Users WHERE id IN ({','.join(tuple([str(i) for i in result2]))})""").fetchall()]
            result = [[i[1], url_for('static', filename=f'user_photos/{i[5]}'), i[4], i[0]] for i in result]
            result2 = [[i[1], url_for('static', filename=f'user_photos/{i[5]}'), i[4], i[0]] for i in result2]
            con.commit()
            con.close()
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')            
            param['users'] = result
            param['new_users'] = result2
            param['len_new_users'] = len(result2)
            param['my_id'] = my_id
            return render_template('chats.html', **param) 
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        a = request.form['butt']
        return make_response(redirect(f'/{a}'))
    
    
@app.route('/news', methods=['POST', 'GET'])
def news():
    if request.method == 'GET':
        if check_cookies(request):
            news_list = []
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            my_id = cur.execute(f"""SELECT id FROM Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()[0][0]
            my_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall())
            result = [[i[0], i[1], url_for('static', filename=f'user_photos/{i[5]}')] for i in cur.execute(f"""SELECT * FROM Users WHERE id IN ({','.join(tuple([str(i) for i in my_subscriptions]))})""").fetchall()]
            result2 = [list(i) for i in cur.execute(f"""SELECT * FROM Stories WHERE USERID IN ({','.join(tuple([str(i[0]) for i in result]))})""").fetchall()]
            for i in result2:
                i = list(i)
                a = list(filter(lambda x: x[0] == i[1], result))
                i.extend(a[0])
                news_list.append(i[2:])
            con.close()
            print(news_list)
            news_list.reverse()
            param = {}
            param['friends'] = url_for('static', filename='friends.png')
            param['messages'] = url_for('static', filename='messages.png')
            param['home'] = url_for('static', filename='home.png')
            param['news'] = url_for('static', filename='news.png')
            param['style'] = url_for('static', filename='doc.css')            
            param['news_list'] = news_list
            return render_template('news.html', **param) 
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        a = request.form['butt']
        return make_response(redirect(f'/{a}'))
    

@app.route('/json_news', methods=['POST', 'GET'])
def json_news():
    if request.method == 'GET':
        if check_cookies(request):
            news_list = []
            con = sqlite3.connect("source/main.db")
            cur = con.cursor()
            my_id = cur.execute(f"""SELECT id FROM Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall()[0][0]
            my_subscriptions = int_m(cur.execute(f"""SELECT SUBSCRIPTIONS FROM Users WHERE NAME='{request.cookies.get('name')}' AND PASSWORD='{request.cookies.get('password')}'""").fetchall())
            result = [[i[0], i[1], url_for('static', filename=f'user_photos/{i[5]}')] for i in cur.execute(f"""SELECT * FROM Users WHERE id IN ({','.join(tuple([str(i) for i in my_subscriptions]))})""").fetchall()]
            result2 = [list(i) for i in cur.execute(f"""SELECT * FROM Stories WHERE USERID IN ({','.join(tuple([str(i[0]) for i in result]))})""").fetchall()]
            for i in result2:
                i = list(i)
                a = list(filter(lambda x: x[0] == i[1], result))
                i.extend(a[0])
                news_list.append(i[2:])
            con.close()
            news = []
            for i in news_list:
                news.append({'User': i[3], 'Date': i[1], 'Content': i[0]})
            return jsonify({'news': news})
        else:
            return make_response(redirect('/'))

@app.route('/none_page')
def none_page():
    return render_template('none_page.html', buzz_png=url_for('static', filename='buzz.png'), a=url_for('static', filename='doc.css'))
    
    
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')