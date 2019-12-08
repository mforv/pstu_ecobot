#!/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import flask
# from msg import parser
# from cv import command_wrapper
import fractal_path_finder as fpf
# from cv import roto
import hw_wrapper as hw

app = flask.Flask('Ecobot')
messages = []
# objects = [
#     {'name': "Ель", 'loc': [31, 613], 'size': [276, 427]}, 
#     {'name': "Оранжевый дом", 'loc': [709, 789], 'size': [271, 301]}, 
#     {'name': "Фиолетовый дом", 'loc': [69, 104], 'size': [202, 249]}, 
#     {'name': "Желтый дом", 'loc': [1476, 237], 'size': [237, 294]}, 
#     {'name': "Камень на дороге", 'loc': [1539, 743], 'size': [30, 50]},
#     {'name': "Какая-то шина", 'loc': [650, 60], 'size': [30, 50]}
#     ]
objects = [
    {'name': "Парковка корпуса А", 'loc': [503, 297], 'size': [171, 316]}, 
    {'name': "Корпус А", 'loc': [310, 276], 'size': [110, 712]}, 
    {'name': "Корпус Б", 'loc': [707, 287], 'size': [115, 694]}, 
    {'name': "Корпус В", 'loc': [1108, 284], 'size': [108, 706]}, 
    {'name': "Корпус Г", 'loc': [1500, 294], 'size': [108, 699]},
    {'name': "Парковка корпуса Г", 'loc': [1342, 343], 'size': [115, 164]}, 
    {'name': "Шина", 'loc': [779, 147], 'size': [25, 20]},
    {'name': "Камень", 'loc': [230, 140], 'size': [25, 20]}
    ]
path = []
# r = roto.Roto()

def send_message(author, message):
    messages.append(f"{str(author)} [" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]: " + str(message))

'''Основные адреса'''
@app.route('/')
def index():
    return flask.render_template("start.html")

@app.route('/msg')
def show_msg():
    # send_message('Bot', 'Привет!')
    return flask.render_template("msg.html", messages=messages)

@app.route('/cam')
def show_cam():
    return flask.render_template("cam.html")

@app.route('/map')
def show_map():
    return flask.render_template("map.html", map_objects=objects)

@app.route('/auto')
def show_auto():
    # return flask.render_template("auto.html")
    return flask.redirect('/')

@app.route('/prefs')
def show_prefs():
    # return flask.render_template("prefs.html")
    return flask.redirect('/')

'''Сбор данных с разного рода форм'''
@app.route('/send_msg', methods=['POST'])
def process_message():
    message = flask.request.form['command']
    send_message('Usr', message)
    if 'привет' in str(message).lower():
        send_message('Bot', 'Привет!')
    elif 'пока' in str(message).lower():
        send_message('Bot', 'Пока!')
    elif 'связаны' in str(message).lower():
        send_message('Bot', 'Связаны.')
    # answer = parser.get_answer(message)
    # send_message('Bot', answer)
    return flask.redirect('/msg')

@app.route('/setroute', methods=['GET'])
def process_route():
    # route_to = flask.request.args.get['route_to']
    route_to = flask.request.args.get('name')
    # route_from = flask.request.form['route_from']
    # route_to = flask.request.form['route_to']
    route_from = ''
    # route_what = flask.request.form['route_what']
    start_point = (0, 0)
    end_point = (0, 0)
    for obj in objects:
        if obj['name'].lower() in route_from.lower():
            start_point = tuple(obj['loc'])
        elif obj['name'].lower() in route_to.lower():
            end_point = tuple(obj['loc'])
    # TODO Remove, for testing only
    start_point = (475, 455)
    # start_point = (350, 500)
    #end_point = (1539, 743)
    # fpf.passable_color = (77, 73, 41, 255)
    fpf.passable_color = (255, 255, 255, 255)
    global path
    path = fpf.calc_path('./static/img/map1.png', start_point, end_point)
    print(len(path))
    # print(route_from, route_to, route_what)  # TODO Обрабатывать это FractalPathFinder
    return flask.jsonify(path)
    # return flask.redirect('/map')

@app.route('/path')
def send_next_point():
    global path
    current_point = flask.request.args.get('cpt', default = 0, type = int)
    if len(path) > 0:
        if current_point < len(path):
            return str(path[current_point+1])
        else:
            return str(path[-1])
    else:
        return (0,0)

@app.route('/movecam', methods=['POST'])
def move_cam():
    direction = int(flask.request.form['mcdir'])
    resp = -1
    if direction == 0:   # вверх
        # r.move(150, 180)
        resp = 0
    elif direction == 1: # вниз
        # r.move(100, 180)
        resp = 1
    elif direction == 2: # влево
        # r.moveZ(40)
        resp = 2
    elif direction == 3: # вправо
        # r.moveZ(-40)
        resp = 3
    return 'Moved in ' + str(resp)

@app.route('/controls')
def show_controls():
    return flask.render_template('controls.html')

@app.route('/initialize', methods=['POST'])
def init_controls():
    hw_data = hw.initialize()
    with open('hw_list.txt', 'r', encoding='utf-8') as f:
        hw_list = f.readlines()
    hw_init = []
    for i in range(len(hw_list)):
        try:
            hw_init.append((hw_list[i].strip(), hw_data[i]))
        except IndexError:
            hw_init.append((hw_list[i].strip(), None))
    return flask.jsonify(hw_init)

@app.route('/ask', methods=['POST'])
def ask_hardware():
    command_code = int(flask.request.args.get('code'))
    raw_message = str(flask.request.args.get('message'))
    message = raw_message.split(',') if raw_message.lower() != 'nan' and raw_message.lower() !='' else None
    message = list(map(float, message)) if message is not None else None
    return flask.jsonify(hw.ask(command_code, message))

if __name__ == "__main__":
    hw.assign_port()
    # TODO Сюда запихать загрузку списка объектов из JSON'а
    app.run(host='0.0.0.0', port=8008, debug=True)
