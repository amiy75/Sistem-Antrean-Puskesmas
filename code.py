import csv #membaca dan menulis file CSV, dan menyimpan data pasien
import os #membuat folder, mengecek file, menghapus file, melihat isi folder, dan menjalankan path/direktori, mengelola file sisem
import shutil #copy file dari data awal ke data pasien, pindah file, hapus folder beserta isi, dan backup data #menyalin file csv awal ke csv pasien
from collections import deque #mengatur que termasuk menambah pasien, menghapus pasien, dan dan mengatur jumlah max antrean

PRIORITAS = {
    "pendarahan": 1,
    "kejang": 2, 
    "demam tinggi": 3
}

def generate_nomor_antrean(poli):
    prefix = {
        "umum": "U",
        "gigi": "G",
        "anak": "A"
    }
    huruf = prefix[poli]
    nomor_terbesar = 0

    if os.path.exists(FILE_AKTIF):
        with open(FILE_AKTIF,
                  mode="r",
                  encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                nomor = row["Nomor Antrean"]

                if nomor.startswith(huruf):
                    angka = int(nomor[1:])
                    if angka > nomor_terbesar:
                        nomor_terbesar = angka

    nomor_baru = nomor_terbesar + 1
    return f"{huruf}{nomor_baru:03}"

FILE_AWAL = "data_awal.csv"
FILE_AKTIF = "data_pasien.csv"

class Pasien:
    def __init__(self, nomor, nama, umur,
                 gender, poli, keluhan,
                 status="Menunggu"):
        self.nomor = nomor
        self.nama = nama
        self.umur = umur
        self.gender = gender
        self.poli = poli.lower()
        self.keluhan = keluhan.lower()
        self.status = status
        self.prioritas = PRIORITAS.get(
            self.keluhan,
            999
        )
    def __str__(self):
        return (
            f"{self.nomor} | "
            f"{self.nama} | "
            f"{self.umur} tahun | "
            f"{self.gender} | "
            f"{self.keluhan}"
        )

antrian = {
    "umum": deque(maxlen=10),
    "gigi": deque(maxlen=10),
    "anak": deque(maxlen=10)
}
waiting_list = {
    "umum": deque(),
    "gigi": deque(),
    "anak": deque()
}
riwayat_selesai = []
def inisialisasi_file():
    if not os.path.exists(FILE_AKTIF):
        shutil.copy(FILE_AWAL, FILE_AKTIF)
        print("File data_pasien.csv berhasil dibuat.")

def load_csv():
    for poli in antrian:
        antrian[poli].clear()
        waiting_list[poli].clear()
    riwayat_selesai.clear()

    with open(FILE_AKTIF,
              mode="r",
              encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            status = row.get("Status", "").strip()
            if status == "Selesai":
                continue
            pasien = Pasien(
                row["Nomor Antrean"],
                row["Nama"],
                row["Umur"],
                row["Gender"],
                row["Poli"],
                row["Keluhan"]
            )
            poli = pasien.poli

            if len(antrian[poli]) < 10:
                antrian[poli].append(pasien)
            else:
                waiting_list[poli].append(pasien)

    for poli in antrian:
        sort_antrian(poli)
        sort_waiting_list(poli)

def sort_antrian(poli):
    queue = list(antrian[poli])
    queue.sort(
        key=lambda pasien: pasien.prioritas
    )
    antrian[poli].clear()
    for pasien in queue:
        antrian[poli].append(pasien)

def sort_waiting_list(poli):
    waiting = list(waiting_list[poli])
    waiting.sort(
        key=lambda pasien: pasien.prioritas
    )
    waiting_list[poli].clear()
    for pasien in waiting:
        waiting_list[poli].append(pasien)

def simpan_csv():
    data = []
    for poli in antrian:
        queue = list(antrian[poli])
        for i, pasien in enumerate(queue):
            if i == 0:
                pasien.status = "Diproses"
                estimasi = "Sedang Diproses"
            else:
                pasien.status = "Menunggu"
                estimasi = f"{i * 15} menit"
            data.append([
                pasien.nomor,
                pasien.nama,
                pasien.umur,
                pasien.gender,
                pasien.poli,
                pasien.keluhan,
                pasien.prioritas,
                pasien.status,
                estimasi
            ])
    for poli in waiting_list:
        for pasien in waiting_list[poli]:
            pasien.status = "Waiting List"
            data.append([
                pasien.nomor,
                pasien.nama,
                pasien.umur,
                pasien.gender,
                pasien.poli,
                pasien.keluhan,
                pasien.prioritas,
                pasien.status,
                "-"
            ])
    for pasien in riwayat_selesai:
        data.append([
            pasien.nomor,
            pasien.nama,
            pasien.umur,
            pasien.gender,
            pasien.poli,
            pasien.keluhan,
            pasien.prioritas,
            "Selesai",
            "-"
        ])
    with open(FILE_AKTIF,
              mode="w",
              newline="",
              encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Nomor Antrean",
            "Nama",
            "Umur",
            "Gender",
            "Poli",
            "Keluhan",
            "Prioritas",
            "Status",
            "Estimasi"
        ])
        writer.writerows(data)

def tambah_pasien():
    nama = input("Nama Pasien : ")
    umur = input("Umur : ")
    gender = input("Gender : ")
    poli = input(
        "Pilih Poli (umum/gigi/anak) : "
    ).lower()
    keluhan = input("Keluhan : ")

    if poli not in antrian:
        print("Poli tidak ditemukan!\n")
        return
    nomor = generate_nomor_antrean(poli)
    pasien = Pasien(
        nomor,
        nama,
        umur,
        gender,
        poli,
        keluhan
    )

    if len(antrian[poli]) < 10:
        antrian[poli].append(pasien)
        sort_antrian(poli)
        print(
            f"\nPasien masuk antrean aktif poli {poli}"
        )
    else:
        waiting_list[poli].append(pasien)
        sort_waiting_list(poli)
        print(
            "\nAntrean penuh!"
        )
        print(
            "Pasien masuk waiting list."
        )
    simpan_csv()

def tampilkan_antrian():
    for poli in antrian:
        print("\n================================")
        print(f"POLI {poli.upper()}")
        print("================================")
        queue = list(antrian[poli])
        if len(queue) == 0:
            print("Antrean kosong")
        else:
            for i, pasien in enumerate(queue):
                if i == 0:
                    status = "DIPROSES"
                    estimasi = "Sedang Diproses"
                else:
                    status = "MENUNGGU"
                    estimasi = f"{i * 15} menit"
                print(
                    f"[{pasien.nomor}] "
                    f"{pasien.nama} | "
                    f"{pasien.keluhan} | "
                    f"{status} | "
                    f"Estimasi: {estimasi}"
                )
        if len(waiting_list[poli]) > 0:
            print("\n--- WAITING LIST ---")
            for pasien in waiting_list[poli]:
                print(
                    f"[{pasien.nomor}] "
                    f"{pasien.nama} | "
                    f"{pasien.keluhan}"
                )

def selesaikan_pasien():
    poli = input(
        "Pilih poli (umum/gigi/anak) : "
    ).lower()
    if poli not in antrian:
        print("Poli tidak ditemukan!\n")
        return
    if len(antrian[poli]) == 0:
        print("Antrean kosong!\n")
        return
    pasien_selesai = antrian[poli].popleft()
    pasien_selesai.status = "Selesai"
    riwayat_selesai.append(
        pasien_selesai
    )
    print(
        f"\nPasien "
        f"{pasien_selesai.nama} "
        f"selesai diproses."
    )
    if len(waiting_list[poli]) > 0:
        pasien_baru = waiting_list[poli].popleft()
        antrian[poli].append(
            pasien_baru
        )

    sort_antrian(poli)
    sort_waiting_list(poli)
    simpan_csv()
    print("Antrean telah diperbarui.\n")

def tampilkan_riwayat():
    print("\n================================")
    print("RIWAYAT PASIEN SELESAI")
    print("================================")

    ada_riwayat = False
    with open(FILE_AKTIF,
              mode="r",
              encoding="utf-8") as file:
        reader = csv.DictReader(file)
        nomor = 1
        for row in reader:
            if row["Status"] == "Selesai":
                ada_riwayat = True
                print(
                    f"{nomor}. "
                    f"{row['Nama']} | "
                    f"{row['Poli']} | "
                    f"{row['Keluhan']}"
                )
                nomor += 1
    if not ada_riwayat:
        print("Belum ada pasien selesai.")

def reset_antrean():
    konfirmasi = input(
        "\nYakin reset semua antrean? (y/n): "
    ).lower()
    if konfirmasi == "y":
        if os.path.exists(FILE_AKTIF):
            os.remove(FILE_AKTIF)
        shutil.copy(FILE_AWAL, FILE_AKTIF)
        load_csv()
        simpan_csv()
        print(
            "\nAntrean berhasil direset!"
        )
    else:
        print("\nReset dibatalkan.")

inisialisasi_file()
load_csv()
simpan_csv()
while True:
    print("\n====================================")
    print(" SISTEM ANTREAN PUSKESMAS ")
    print("====================================")
    print("1. Lihat Antrean")
    print("2. Tambah Pasien")
    print("3. Selesaikan Pasien")
    print("4. Lihat Riwayat")
    print("5. Reset Antrean")
    print("6. Keluar")
    pilihan = input(
        "Pilih menu : "
    )
    if pilihan == "1":
        tampilkan_antrian()
    elif pilihan == "2":
        tambah_pasien()
    elif pilihan == "3":
        selesaikan_pasien()
    elif pilihan == "4":
        tampilkan_riwayat()
    elif pilihan == "5":
        reset_antrean()
    elif pilihan == "6":
        print("\nProgram selesai.")
        break
    else:
        print("\nPilihan tidak valid!")