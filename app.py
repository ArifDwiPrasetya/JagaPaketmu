import os
from os.path import join, dirname
from dotenv import load_dotenv

from pymongo import MongoClient
import jwt #pip install pyjwt 
from datetime import datetime, timedelta, timezone 
import hashlib #untuk enkripsi, sudah bawaan
from flask import (
    Flask, 
    render_template, 
    jsonify, 
    request,
    redirect, 
    url_for )
from werkzeug.utils import secure_filename
from bson import ObjectId

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN_KEY = os.environ.get("TOKEN_KEY")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)

# app.config['TEMPLATES_AUTO_RELOAD']=True
app.config['UPLOAD_FOLDER']='./static/bukti_img'

@app.route('/', methods=['GET']) #UNTUK HALAMAN INDEX
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'useremail' :payload.get('useremail')})
        
        keyword = request.args.get('keyword')
        showAll = request.args.get('all')
        if keyword:
            list_paket = list(db.paket.find({"nama_paket" : {'$regex' : keyword, '$options': 'i'}}))
            if list_paket : 
                for paket in list_paket:
                    paket['add_date'] = paket['add_date'].replace('-',' -> ')
                    if paket['received_date'] != 'none':
                        paket['received_date'] = paket['received_date'].replace('-',' -> ')
                    paket['_id'] = str(paket['_id'])
                return render_template('index.html', list_paket = list_paket)
            else : return render_template('index.html', notFound = "True")
        elif showAll:
            list_paket = list(db.paket.find({}).sort('add_date', -1))
            for paket in list_paket:
                paket['add_date'] = paket['add_date'].replace('-',' -> ')
                if paket['received_date'] != 'none':
                    paket['received_date'] = paket['received_date'].replace('-',' -> ')
                paket['_id'] = str(paket['_id'])
            return render_template('index.html', list_paket = list_paket)
        else :
            list_paket = list(db.paket.find({}).sort('add_date', -1).limit(5))
            for paket in list_paket:
                paket['add_date'] = paket['add_date'].replace('-',' -> ')
                if paket['received_date'] != 'none':
                    paket['received_date'] = paket['received_date'].replace('-',' -> ')
                paket['_id'] = str(paket['_id'])
            return render_template('index.html', list_paket = list_paket, limit = "True")

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('halaman_login',msg = msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('halaman_login',msg = msg))

@app.route('/halaman_login', methods=['GET']) #UNTUK HALAMAN LOGIN
def halaman_login():
    msg = request.args.get('msg')
    return render_template('login.html', msg =msg)
    
@app.route("/sign_in", methods=["POST"]) #UNTUK HALAMAN LOGIN
def sign_in():
    useremail_receive = request.form["useremail_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "useremail": useremail_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "useremail": useremail_receive,
            # the token will be valid for 24 hours
            "exp": datetime.now(timezone.utc) + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"result": "success","token": token})
    else:
        return jsonify(
            {"result": "fail", "msg": "Email atau Password anda tidak sesuai"})

@app.route('/tambahPaket', methods=['POST']) #UNTUK HALAMAN TAMBAH
def posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        #di browser client, buat kondisi input tidak boleh kosong, termasuk input choose file
        name_receive = request.form.get('name_give').strip()
        resi_receive = request.form.get('resi_give').strip()

        doc = {
            'nama_paket' : name_receive,
            'no_resi' : resi_receive,
            'add_date': datetime.now().strftime('%d/%m/%Y-%H:%M:%S'),
            'status' : "Dalam Pengiriman",
            'received_date' : "none",
            'file_foto' : 'none'
        }
        db.paket.insert_one(doc)
        return jsonify({'result' : 'success','msg' : 'Paket baru telah ditambahkan!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/editPaket', methods=['POST'])  #UNTUK HALAMAN EDIT
def edit():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        id_paket = request.form.get('id_give')
        id_paket = ObjectId(id_paket)

        name_receive = request.form.get('name_give')
        resi_receive = request.form.get('resi_give')
        doc = {
            'nama_paket' : name_receive,
            'no_resi' : resi_receive
        }
        db.paket.update_one({'_id' : id_paket},{'$set': doc})
        return jsonify({'result' : 'success','msg' : 'Data paket berhasil diedit'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route('/deletePaket', methods=['POST'])  #UNTUK HALAMAN DELETE
def delete():
    token_receive = request.cookies.get(TOKEN_KEY)

    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        id_paket = request.form.get('id_give')
        id_paket = ObjectId(id_paket)
        info_paket = db.paket.find_one({'_id' : id_paket})
        foto_paket = info_paket['file_foto']
        print(foto_paket)
        if  foto_paket != "default.png" and foto_paket != "none":
            os.remove(f'./static/bukti_img/{foto_paket}') #hapus gambar lama di server biar ga jadi sampah
        db.paket.delete_one({'_id' : id_paket})
        return jsonify({'result' : 'success'})

    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route("/validasi/<id>")
def validasi(id):
    id_paket = id
    if id_paket == 'default':
        return render_template("validasi_kurir.html")
    elif id_paket == "sukses_upload":
        return render_template("validasi_kurir.html", sukses_upload = "True")
    else : 
        return render_template('validasi_kurir.html', id_paket = id_paket)

@app.route("/cekResi", methods=["POST"])
def cekResi():
    resi_receive = request.form.get("resi_give").strip()
    valid = db.paket.find_one({"no_resi" : resi_receive})
    if valid : 
        print('resi valid')
        valid['_id'] = str(valid['_id'])
        id = valid['_id'] 
        doc = {
            'status' : 'Telah Sampai',
            'received_date':  datetime.now().strftime('%d/%m/%Y-%H:%M:%S'),
            'file_foto' : 'default.png'
        }
        param_id = ObjectId(id)
        id_paket = str(param_id)
        db.paket.update_one({'_id' : param_id}, {'$set' : doc})
        db.box_status.update_one({}, {'$set' : {'open_status' : 'True'}})
        return jsonify({'result' : 'success', 'id' : id_paket })
        # return render_template("validasi_kurir.html", id_paket = id)
        # return redirect(url_for('validasi', id_paket = id))
    else : 
        print('resi tidak valid')
        return jsonify({'result' : "Tidak Valid"})

@app.route("/upload", methods=["POST"])
def upload():
    id_receive = request.form.get('id_give')
    print(id_receive)
    id_paket = ObjectId(id_receive)
    waktu = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    if 'file_give' in request.files:
        file = request.files.get('file_give')
        file_name = secure_filename(file.filename)
        picture_name= file_name.split(".")[0]
        ekstensi = file_name.split(".")[1]
        picture_name = f"{picture_name}[{waktu}].{ekstensi}"
        file_path = f'./static/bukti_img/{picture_name}'
        print(file_path)
        file.save(file_path)
    
        db.paket.update_one({'_id' : id_paket}, {'$set' : {'file_foto' : picture_name}})
        return jsonify({'result' : 'success'})
    else: return jsonify({'result' : 'Gagal mengupload Foto'})

@app.route("/openBox", methods = ['POST'])
def openBox():
    status_receive = request.form.get('status')
    db.box_status.update_one({}, {'$set' : {'open_status' : status_receive}})
    return jsonify ({'result' : 'success'})

@app.route("/statusBox")
def statusBox():
    reset = request.args.get('reset')
    if reset:
        db.box_status.update_one({},{'$set' : {'open_status' : 'False'}})
        return jsonify({'message' : 'Status open box telah di reset'})
    else :
        status = str(bool(db.box_status.find_one({'open_status' : 'True'})))
        print(status)
        print(type(status))
        return jsonify({'status' : status})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)