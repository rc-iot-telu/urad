# Aplikasi Radar URad

Aplikasi GUI radar untuk urad yang sudah terintegrasi dengan sensor ultrasonic dan timer.
Digunakan untuk keperluan penelitian IS-IoT Telkom University.

## Cara Install

- Pastikan Python versi 3.7 keatas telah terinstall.
- Cek dengan membuka CMD (Command Prompt) dan ketik python, jika muncul tulisan: "Python 3.x.xx ..." (versi python) maka prosess instalasi berhasil.
- Buka lagi CMD (Command Prompt) di folder ini (URad) dengan cara: ```ctrl + shift + click``` kanan di dalam folder urad lalu pilih **Command Prompt** atau **Powershell** atau **Terminal**, lalu ketik ```pip install -r requirements.txt```
- Tunggu hingga selesai.
- Setelah prosess installasi library berhasil, double click file: main.py. Jika muncul UI maka prosess installasi berhasil

## Cara Menggunakan Aplikasi

1. Pastikan nomor **port** telah diatur dengan benar.
   - Buka Setting
     ![gambar setting](https://github.com/rc-iot-telu/urad/blob/master/screenshoot/open_setting.jpg?raw=true)
   - Setelah itu pastikan bahwa nomor port telah sesuai
     ![gambar setting](https://github.com/rc-iot-telu/urad/blob/master/screenshoot/setting_port.jpg?raw=true)
   - Piilh Juga tempat data di simpan dengan cara meng-click: "Pilih Folder"
   - Jika tidak akan menggunakan sensor ultrasonic, kosongkan saja nomor port nya
     
2. Setelah selesai mengatur **nomor port** dan **folder data**, aplikasi dapat langsung digunakan
3. Untuk mengatur waktu lamanya penggunaan aplikasi (fitur auto-stop) dapat input waktu lamanya radar akan digunakan di bawah tombol: "Simpan Data"
