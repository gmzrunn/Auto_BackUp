import os
import shutil
import datetime

#Kaynak klasörün yolu
kaynak_klasör = "C:\\Users\gmznu\desktop\kaynak_klasör"

#Hedef klasörün yolu
hedef_klasör = "C:\\Users\gmznu\desktop\hedef_klasör"

saklama_günü = 7  

def yedekle():
    try:
        if not os.path.exists(hedef_klasör):
            os.makedirs(hedef_klasör)
            print(f"Hedef klasör oluşturuldu: {hedef_klasör}")

            simdi = datetime.datetime.now()
            yedek_adi = simdi.strftime("%Y-%m-%d_%H-%M-%S")+ "_yedek"
            yedek_hedef = os.path.join(hedef_klasör, yedek_adi)

            print(f"Yedekleme işlemi başlatılıyor: {yedek_hedef}")
            shutil.copytree(kaynak_klasör, yedek_hedef) 
            print(f"Yedekleme işlemi tamamlandı: {yedek_hedef}")

    except Exception as e:
        print(f"Yedekleme sırasında hata oluştu: {e}")

def temizle():
    print("Eski yedekler kontrol ediliyor...")
    simdi = datetime.datetime.now()
    eski_yedek= simdi - datetime.timedelta(days=saklama_günü)   

    try:
        for yedek in os.listdir(hedef_klasör):
            yedek_yolu = os.path.join(hedef_klasör, yedek)
            if os.path.isdir(yedek_yolu):
                yedek_tarihi = datetime.datetime.strptime(yedek.split('_')[0], "%Y-%m-%d")
                if yedek_tarihi < eski_yedek:
                    shutil.rmtree(yedek_yolu)
                    print(f"Eski yedek silindi: {yedek_yolu}")

    except Exception as e:
        print(f"Temizleme sırasında hata oluştu: {e}")
    
if __name__ == "__main__":
    yedekle()
    temizle()
    print("Yedekleme ve temizlik işlemleri tamamlandı.")    
