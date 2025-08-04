import os
import shutil
import datetime

#kaynak klasör ve hedef klasör yolları.
kaynak_klasör = r"C:\Users\gmznu\desktop\kaynak_klasör"
hedef_klasör = r"C:\Users\gmznu\desktop\hedef_klasör"

saklama_günü = 7 

def yedekle():
    try:
        # Hedef klasör mevcut değilse oluştur.
        if not os.path.exists(hedef_klasör):
            os.makedirs(hedef_klasör)
            print(f"Hedef klasör oluşturuldu: {hedef_klasör}")

        # Yeni yedek için klasör adı oluştur.
        simdi = datetime.datetime.now()
        yedek_adi = simdi.strftime("%Y-%m-%d_%H-%M-%S")+ "_yedek"
        yedek_hedef = os.path.join(hedef_klasör, yedek_adi)

        print(f"Yedekleme işlemi başlatılıyor: {kaynak_klasör} -> {yedek_hedef}")
        
        shutil.copytree(kaynak_klasör, yedek_hedef) 
        print(f"Yedekleme işlemi tamamlandı: {yedek_hedef}")

    except Exception as e:
        print(f"Yedekleme sırasında hata oluştu: {e}")

def temizle():
    print("Eski yedekler kontrol ediliyor...")
    simdi = datetime.datetime.now()
    eski_yedek_limiti = simdi - datetime.timedelta(days=saklama_günü) 

    try:
        for yedek in os.listdir(hedef_klasör):
            yedek_yolu = os.path.join(hedef_klasör, yedek)
            
            if os.path.isdir(yedek_yolu):
                try:
                    yedek_tarihi_str = yedek.split('_')[0]
                    yedek_tarihi = datetime.datetime.strptime(yedek_tarihi_str, "%Y-%m-%d")

                    if yedek_tarihi < eski_yedek_limiti:
                        shutil.rmtree(yedek_yolu)
                        print(f"Eski yedek silindi: {yedek_yolu}")
                except (ValueError, IndexError):
                    continue

    except Exception as e:
        print(f"Temizleme sırasında hata oluştu: {e}")
    
if __name__ == "__main__":
    yedekle()
    temizle()
    print("Yedekleme ve temizlik işlemleri tamamlandı.")