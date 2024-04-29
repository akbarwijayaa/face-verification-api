# Project Summary
Project Name : **Face Verification Approval - Face Recognition**
<br>
Environment : **`face-recognition-cpu --> include library`**
<br>
Algorithm : **[face-recognition]( https://github.com/ageitgey/face_recognition) from ageitgey**
<br>
Current Model : **dlib**
<br>
Folder for Development : /home/serverai/Project/face-recognition
<br>

# Quickstart
Clone repository ini, kemudian aktifkan environment yang akan menjalankan program tersebut.
```bash
$ git clone http://gitlab.quick.com/artificial-intelligence/face-verification-for-approval-kasie.git     #clone
$ cd face-verification-for-approval-kasie
$ conda activate face-recognition-cpu       #activate
```
<br>

# Dataset
Kami mengumpulkan beberapa foto karyawan yang akan didaftarkan wajahnya, mencoba untuk menjepret dari angel yang pas, dan mengekstrak fitur wajah dari setiap gambar yang ada.
Data wajah yang sudah diekstrak fiturnya, akan dimasukan kedalam file json, yang mana dalam kasus ini file json akan bertindak sebagai model.

<br>

# Training and Testing
Pada proses training terdapat pada file `train_piece.py`, selengkapnya akan dijelaskan [dibawah](##>face-encoding-module)

<br>

# Model Optimization
Pada proses optimasi model, kami hanya menyediakan fitur penggantian image baru yang lebih berkualitas secara kasat mata. Untuk itu silahkan merujuk pada file `update_data.py`. Penjelasan lengkap ada [dibawah](##>user's-data-manipulation-module)

<br>

# Source Code Documentation

## > Face Recognition Module
**File Location : `recognize.py`** <br> Dalam module ini mencakup proses untuk mengidentifikasi wajah-wajah dalam gambar yang diberikan. Jika ditemukan gambar wajah yang yang cocok dengan data, program akan memberikan informasi terkait wajah tersebut seperti nomor registrasi (nomor induk) dan nama, sesuai dengan data yang telah disimpan sebelumnya. Berikut penjelasan kode program recognize.py
#### class `Recognizer()`
Ini adalah sebuah kelas yang bertanggung jawab untuk mengenali wajah dalam gambar.

- `__init__` :  Pada tahap inisialisasi, beberapa variabel path disiapkan untuk menyimpan data dan model-model yang dibutuhkan.

    ```python 
    def __init__(self):
        self.base_path = dirname(abspath(__file__))
        self.data_path = join(self.base_path, 'data')
        self.models_path = join(self.base_path, 'models')
        self.weight_path = join(self.models_path, 'data.json')
        ...

    ```

- `load_model()` : Method ini memuat model yang telah dilatih sebelumnya untuk mengenali wajah. Data wajah yang telah diencode tersimpan dalam file JSON, kemudian method ini mengembalikan `face_encode` dan `list_face_encode`.

    ```python
    def load_model(self):
        data = open(self.weight_path)
        face_encode = json.load(data)
        list_face_encode = [data[0] for data in face_encode.values()]
        return face_encode, list_face_encode
    
    ```

- `predict()` : Method ini digunakan untuk melakukan prediksi terhadap gambar yang diberikan. 
    ```python
    def predict(self, img_nparr):
        img_rgb = cv2.cvtColor(img_nparr, cv2.COLOR_BGR2RGB)
        face_loc = face_recognition.face_locations(img_rgb)
        encode_images = face_recognition.face_encodings(img_rgb, face_loc)
        try:
            for encode_face, face_loc in zip(encode_images, face_loc):
                matches = face_recognition.compare_faces(self.list_face_encode, encode_face)
                ...

            return result, self.config['response']['success_code']

        except Exception as a:
            result = {
                'message': self.config['response']['fail_msg'],
                'data': None
            }
            return result, self.config['response']['fail_code']

    ```
Return value yang dikembalikan berupa hasil prediksi beserta kode yang menandakan apakah prediksi berhasil atau gagal.

<br>

## > Face Encoding Module
**File Location : `train_piece.py`** <br> Module ini menangani proses encoding wajah berdasarkan gambar. 
#### python class `Training()`

- `__init__` : Menginisialisasi path untuk gambar pelatihan, model, dan config
    ```python
    class Training:
        def __init__(self):
            self.base_path = os.path.dirname(os.path.realpath('__file__'))
            self.models_path = join(self.base_path, 'models')
            self.data_path = join(self.base_path, 'data')
            self.weight_path = join(self.models_path, 'data.json')
            
            self.config = ConfigParser()
            self.config.read(join(self.data_path,'config.ini'))
            self.url_server = self.config['train']['url_server']

    ```

- `find_class_name()`: Mengidentifikasi dan menyimpan gambar wajah yang baru didaftarkan ke dalam server. Dengan kondisi user yang sudah pernah didaftarkan nomor induknya tidak bisa mendaftar lagi. Mengembalikan file gambar dan nama kelas diambil dari splitting `no_ind`.
    ```python
        def find_class_name(self, image, img_name):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ...

            if res[0] not in no_ind:
                ...

            return images, class_name
    ```

- `find_encode()` : Memproses gambar untuk menghasilkan pengkodean wajah menggunakan library `face_recognition`. Resultnya disimpan kedalam list variabel `encode_list`. 
    ```python
        def find_encode(self, images):
            try:
                encode_list = []
                for img in images:
                    ...

                return encode_list
            except:
                encode_list = []
                return encode_list
    ```

- `append_json():` Memperbarui file JSON yang menyimpan data nomor, nama, dan face encoding dari user. 
    ```python
        def append_json(self, class_name, encode_list):
            if os.listdir(self.models_path) == []:
                result = {}
                ...
                
            else:
                data = open(self.weight_path)
                rs_json = json.load(data)
                for item in class_name:
                    rs_json[item]=encode_list

                ...

    ```

- `get_data_users():` Mengambil data pengguna yang sesuai.

    ```python
        def get_data_users(self):
            if os.listdir(self.models_path) == []:
                arr_users = []
            else:
                data = open(self.weight_path)
                rs_json = json.load(data)
                list_noind = []
                
                ...

            return arr_users
    ```

<br>

## > Retrieve Data Module
**File Location : `get_data_users.py`** <br> Modul ini bertanggung jawab atas pengambilan data dari file JSON dan pengurutan data berdasarkan nomor registrasi.
#### python class `DataUser()`

- `__init__` : Menginisialisasi path untuk gambar pelatihan, model, config, dll
    ```python
    class DataUser:
        def __init__(self):        
            base_path = os.path.dirname(os.path.realpath('__file__'))
            models_path = join(base_path, 'models')
            self.weight_path = join(models_path, 'data.json')
            self.data_path = join(base_path, 'data')
            
            self.config = ConfigParser()
            self.config.read(join(self.data_path,'config.ini'))
            self.url_img = self.config['api']['url_img']
        
    ```

- `get_data()`: membaca file JSON 'data.json' yang terletak pada `self.weight_path`. Kemudian, method ini melakukan pemrosesan terhadap isi JSON tersebutdan mengembalikan sebuah dictionary yang berisi data yang diekstrak yang telah terstruktur.
    ```python
        def get_data(self):
            data = open(self.weight_path)
            rs_json = json.load(data)
            result = {
                "data":[]
            }
            for key, value in rs_json.items():
                ...

            return result
    ```

- `get_sorted_data()` : menggunakan method `get_data()` untuk memperoleh data dalam format yang terstruktur. Kemudian mengekstrak nomor registrasi dari data yang diperoleh dan mengurutkannya. Hasilnya sama saja, namun dengan data yang telah diurutkan berdasarkan nomor induknya.
    ```python
        def get_sorted_data(self):
            data = self.get_data()
            no_induk = []
            for value in data.values():
                for id_pekerja in value:
                    idp = id_pekerja['registration_number']
                    no_induk.append(idp)

            ...

            return data_sorted
    ```

<br>

## > User's Data Manipulation Module
**File Location : `update_data.py`** <br> Module ini berfungsi untuk memanipulasi data hasil pengenalan wajah, mengubah informasi terkait, dan menghapus data.
#### python class `updateData()`

- `__init__` : Menginisialisasi path dan variabel yang diperlukan.
    ```python
    class updateData:
        def __init__(self):
            self.base_path = os.path.dirname(os.path.realpath('__file__'))
            self.models_path = join(self.base_path, 'models')
            self.weight_path = join(self.models_path, 'data.json')
            self.data_path = join(self.base_path, 'data')
            
            self.config = ConfigParser()
            self.config.read(join(self.data_path,'config.ini'))
            self.url_server = self.config['train']['url_server']
    ```

- `name()`: Mengubah nama file gambar dan entry data berdasarkan nomor induk dan nama baru yang diinputkan.
    ```python
        def name(self, no_ind, new_name):
            data = open(self.weight_path)
            rs_json = json.load(data)
            key_detected = []
            ...

            if key_detected != []:
                ...

                return 'Success', 200
            
            else:
                return 'No induk tidak terdaftar', 400
    ```

- `no_ind()`: Mengubah nomor induk pada file gambar dan entry data dengan nomor baru yang diinput.
    ```python
        def no_ind(self, no_ind, new_noind):
            data = open(self.weight_path)
            rs_json = json.load(data)
            key_detected = []

            for key in rs_json.keys():
                ...

            if key_detected != []:
                ...

                return 'Success', 200

            else:
                return 'No induk tidak terdaftar', 400
    ```

- `find_class_name()`: Memproses gambar di direktori 'update' dan menyimpannya di lokasi server tertentu. 
    ```python
        def find_class_name(self, name, image):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            images = []
            class_name = []
            ...

            if res[0] in no_ind:
                ...
                
            return images
    ```

- `find_encode()`: Mengambil fitur wajah dari gambar menggunakan library 'face_recognition'.
    ```python
        def find_encode(self, images):
            try:
                encode_list = []
                for img in images:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(img, num_jitters=100, model="large")[0]
                    encode_list.append(encode.tolist())
                return encode_list
            except:
                encode_list = []
                return encode_list
    ```

- `face_model()`: Memperbarui data pengenalan wajah dalam file JSON dengan encoding wajah baru berdasarkan nomor_induk tertentu.
    ```python
        def delete_data(self, no_ind):
            data = open(self.weight_path)
            rs_json = json.load(data)
            key_detected = []
            for key in rs_json.keys():
                ...

            if encode_list != []:
                if key_detected != []:
                    ...

                    return 'Success', 200
                else:
                    return 'No induk tidak terdaftar', 400
            else:
                return 'Wajah tidak terdeteksi', 400
    ```

- `delete_data()`: Menghapus data dalam JSON dan gambar yang sesuai dengan nomor induk yang diinput.
    ```python
        def delete_data(self, no_ind):
            data = open(self.weight_path)
            rs_json = json.load(data)
            key_to_delete = []
            for key in rs_json.keys():
                ...
            if key_to_delete != []:
                for key in key_to_delete:
                    del rs_json[key]

                ...

                return 'Success', 200
            else:
                return 'No induk tidak terdaftar', 400
    ```
- `get_data_user()`: untuk mengambil data yang sudah disesuaikan kebutuhanya.
    ```python
        def get_data_users(self):
            if os.listdir(self.models_path) == []:
                arr_users = []
            else:
                data = open(self.weight_path)
                rs_json = json.load(data)
                list_noind = []
                
                for key, value in rs_json.items():
                    res = re.findall(r'\w+', key)
                    list_noind.append(res[0])
                    
                arr_users = np.array(list_noind)
            return arr_users
    ```
<br>

## > Main API Program 
**File Location : `app.py`** <br> Aplikasi Flask python untuk membuat REST API yang berkaitan dengan verifikasi wajah. Rest API ini memeliki beberapa fungsi yang berbeda pada tiap endpointnya, seperti prediksi (*face recognition*), registrasi wajah baru, pembaruan data pengguna, dan penghapusan data pengguna.
- #### config file
    Mendefinisikan config file untuk dibaca diprogram selanjutnya.
    ```python
    base_path = dirname(abspath(__file__))
    data_path = join(base_path, 'data')
    config = ConfigParser()
    config.read(join(data_path,'config.ini'))
    ```
- #### error handler
    Mendefinisikan error handler standart httpExceptions. Maka ketika program error akan diberikan response standart dari flask.
    ```python
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """
        Handle exceptions and return JSON response.
        """
        response = e.get_response()
        response.data = json.dumps({"message": e.description})
        response.content_type = "application/json"
        return response, e.code
    ```

- #### endpoint `/face-recognition/predict`
    Endpoint ini bertujuan untuk melakukan pengenalan wajah pada gambar yang diterima sebagai masukan. Fungsi yang terdapat dalam endpoint ini adalah `predict()`. Setiap kali fungsi ini dijalankan, akan memberikan record baru didatabase, yang mana record tersebut sebagai historis program ini dijalankan.

    ```python
    @app.route(config['api']['url_login'], methods=["POST", "GET"])
    def predict():
        """
        Perform face recognition on the input image.
        """
        start_time = time.time()
        base_path = dirname(abspath(__file__))

        if request.method != "POST":
            response = {
                'status': 'running',
                'message': 'restapi run normally'
            }
            return response, 200

        if request.files.get("image"):
            ...
            
            rec = recognize.recognizer()
            result, code = rec.predict(image)
            result['time'] = round(time.time() - start_time, 2)
            ...

            return result, code

    ```

- #### endpoint `/face-recognition/registration`
    Endpoint ini bertujuan untuk mendaftarkan wajah baru beserta data terkait user yang mendaftar. Fungsi yang bertanggungjawab dalam endpoint ini adalah `register()`.

    ```python
    @app.route(url_registration, methods=["POST", "GET"])
    def register():
        """
        Register a new face with associated data.
        """
        base_path = dirname(abspath(__file__))
        train_path = join(base_path, 'train')

        if request.method != "POST":
            return "Register new face"

        ...

        if request.files.get("image"):
            ...

        train = Training()
        img, class_name = train.find_class_name(image, img_name)
        encode_list = train.find_encode(img)

        if encode_list != []:
            ...

            return response, 200
        else:
            ...

            return response, 200

    ```

- #### endpoint `/face-recognition/data-face`
    Endpoint ini bertujuan untuk Mengambil seluruh record data user terdaftar secara urut. Fungsi yang terdapat dalam endpoint ini adalah `get_data()`.

    ```python
    @app.route(url_data_user, methods=["POST", "GET"])
    def get_data():
        """
        Get sorted user data.
        """
        data = DataUser()
        data_result = data.get_sorted_data()
        response = data_result

        ...

        return response, 200
    
    ```

- #### endpoint `/face-recognition/update-name`
    Endpoint ini bertujuan untuk memperbarui data nama user dengan nomor induk tertentu. Fungsi yang terdapat dalam endpoint ini adalah `update_name()`.

    ```python
    @app.route(url_update_name, methods=["POST", "GET"])
    def update_name():
        """
        Update user's name.
        """
        no_ind = request.form.get("no_ind").upper()
        new_name = request.form.get("new_name").upper()
        upd = updateData()
        msg, code = upd.name(no_ind=no_ind, new_name=new_name)
        
        ...

        return response, code
    ```
- #### enpoint `/face-recognition/update-noind`
    Endpoint ini bertujuan untuk memperbarui nomor induk yang terdaftar. Fungsi yang terdapat dalam endpoint ini adalah `update_noind()`.
    ```python
    @app.route(url_update_noind, methods=["POST", "GET"])
    def update_noind():
        """
        Update user's registration number.
        """
        no_ind = request.form.get("no_ind").upper()
        new_noid = request.form.get("new_noid").upper()
        upd = updateData()

        msg, code = upd.no_ind(no_ind=no_ind, new_noind=new_noid)

        ...

        return response, code
    ```
- #### endpoint `/face-recognition/update-face`
    Endpoint ini bertujuan untuk memperbarui data enkoding wajah dari seorang user. Fungsi yang terdapat dalam endpoint ini adalah `update_face_encode()`.

    ```python
    @app.route(url_update_face, methods=["POST", "GET"])
    def update_face_encode():
        """
        Update user's face encoding.
        """
        ...

        upd = updateData()
        img = upd.find_class_name(name, image)
        encode_list = upd.find_encode(img)
        msg, code = upd.face_model(no_ind=no_ind, encode_list=encode_list)
        ...

        return response, code
    ```

- #### endpoint `/face-recognition/delete-data`
    Endpoint ini bertujuan untuk menghapus record data seorang user dengan nomor induk tertentu. Fungsi yang terdapat dalam endpoint ini adalah `delete_data()`.

    ```python
    @app.route(url_delete_data, methods=["POST", "GET"])
    def delete():
        """
        Delete user's data.
        """
        no_ind = request.form.get("no_ind").upper()
        upd = updateData()
        msg, code = upd.delete_data(no_ind=no_ind)

        ...

        return response, code
    ```

<br>
 
# Testing Program
Selalu lakukan testing program langsung menggunakans serverai. Lakukan ssh ke server ai dengan `serverai@192.168.168.195`. Gunakan environment yang sesuai dengan penjelasan diatas. Running program python seperti biasa, `python app.py`. Pastikan saat itu port tidak terpakai oleh aplikasi lain. Jika program sudah berjalan, lakukan pengujian dengan mengirimkan gambar sample delam api.

_Lihat dokumentasi api selengkapnya [disini](http://ai.quick.com/documentation/face-verification/)_
