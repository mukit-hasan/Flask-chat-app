from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "as2LJ93Hd7jlas45dj1#"
sio = SocketIO(app)

rooms = {}


def generate_uniue_code(l):
    while True:
        code = ''
        for _ in range(l):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code


@app.route('/', methods=["GET", "POST"])
def home():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)
        if not name:
            return render_template('home.html', errorN='Please Enter a Name!!!', code=code)

        if join != False and not code:
            return render_template('home.html', errorC='Please Enter a Room Code!!!', name=name)

        room = code
        if create != False:
            room = generate_uniue_code(4)
            rooms[room] = {'members': 0, 'messages': []}
        elif code not in rooms:
            return render_template('home.html', errorC='Romm dose not exist!!!', name=name, code=code)

        session['room'] = room
        session['name'] = name
        return redirect(url_for('room'))
    return render_template('home.html')


@app.route('/room')
def room():
    room = session.get('room')
    name = session.get('name')
    if room is None or name is None or room not in rooms:
        return redirect(url_for('home'))

    return render_template('room.html', room=room, name=name, messages=rooms[room]['messages'])


# Socket Io Codes
@sio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({'name': name, 'message': 'has enterd the cave'}, to=room)
    rooms[room]['members'] += 1
    print(f'{name} has enterd cave {room}')


@sio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)
    print(f'{name} leaved the cave {room}')
    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]
            print(f'cave {room} was Banned due to there was not enough memeber')
    send({'name': name, 'message': 'has left the cave'}, to=room)


@sio.on('message')
def message(data):
    print('message is recived')
    room = session.get('room')
    name = session.get('name')
    if room not in rooms:
        return
    content = {
        "name": name,
        "message": data['data']
    }
    send(content, to=room)
    rooms[room]['messages'].append(content)


if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=5000)
