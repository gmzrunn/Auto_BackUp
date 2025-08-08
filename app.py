import os
import shutil
import datetime
import logging
import json
import fnmatch
from plyer import notification

CONFIG_FILE = 'config.json'

try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Hata: {CONFIG_FILE} dosyası bulunamadı. Lütfen bir konfigürasyon dosyası oluşturun.")
    exit()
except json.JSONDecodeError:
    print(f"Hata: {CONFIG_FILE} dosyası bozuk veya yanlış formatta.")
    exit()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("yedekleme.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])

class BackupManager:
    #Yedekleme ve temizleme işlemlerini yöneten ana sınıf

    def __init__(self, config):
        self.kaynak_klasor = config.get("kaynak_klasor")
        self.hedef_klasor = config.get("hedef_klasor")
        self.saklama_gunu = config.get("saklama_gunu", 5)
        self.dislama_listesi = config.get("dislama_listesi", [])

        if not self.kaynak_klasor or not self.hedef_klasor:
            logging.error("Konfigürasyon dosyasında kaynak veya hedef klasör belirtilmemiş.")
            exit()
    
    def _send_notification(self, title, message):
        #Masaüstü bildirimi gönderir
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Yedekleme Yöneticisi",
                timeout=5 
            )
        except Exception as e:
            logging.error(f"Bildirim gönderilirken hata oluştu: {e}")

    def yedekle(self):
        #Kaynak klasörün içeriğini hedef klasöre yedekler
        logging.info("--- Yedekleme İşlemi Başlatılıyor ---")
        try:
            if not os.path.exists(self.hedef_klasor):
                os.makedirs(self.hedef_klasor)
                logging.info(f"Hedef klasör oluşturuldu: {self.hedef_klasor}")

            if not os.path.exists(self.kaynak_klasor):
                logging.error(f"Yedeklenecek kaynak klasör bulunamadı: {self.kaynak_klasor}. Lütfen kontrol edin.")
                self._send_notification("Yedekleme Başarısız", "Kaynak klasör bulunamadı!")
                return

            simdi = datetime.datetime.now()
            yedek_klasor_adi = simdi.strftime("%Y-%m-%d_%H-%M-%S") + "_yedek"
            yedek_yolu = os.path.join(self.hedef_klasor, yedek_klasor_adi)
            
            logging.info(f"Yedekleme işlemi başlatılıyor: {self.kaynak_klasor} -> {yedek_yolu}")
            
            def ignore_patterns(path, names):
                ignored_names = set()
                for pattern in self.dislama_listesi:
                    for name in names:
                        if fnmatch.fnmatch(name, pattern):
                            ignored_names.add(name)
                
                for name in names:
                    source_path = os.path.join(path, name)
                    if os.path.isdir(source_path):
                        if any(fnmatch.fnmatch(name, pattern) for pattern in self.dislama_listesi):
                            ignored_names.add(name)
                            logging.info(f"Klasör dışlandı: {source_path}")
                            continue

                    if name not in ignored_names:
                        try:
                            os.stat(source_path)
                        except OSError as e:
                            if e.errno == 13:
                                logging.warning(f"Erişim hatası nedeniyle dosya/klasör atlandı: {source_path}. Hata: {e}")
                                ignored_names.add(name)
                            else:
                                raise

                return ignored_names

            shutil.copytree(self.kaynak_klasor, yedek_yolu, ignore=ignore_patterns, dirs_exist_ok=True)
            
            logging.info(f"Yedekleme işlemi tamamlandı: {yedek_yolu}")
            self._send_notification("Yedekleme Tamamlandı", f"{yedek_yolu} klasörü başarıyla yedeklendi.")

        except Exception as e:
            logging.error(f"Yedekleme sırasında beklenmedik bir hata oluştu: {e}")
            self._send_notification("Yedekleme Başarısız", f"Yedekleme sırasında bir hata oluştu: {e}")

    def temizle(self):
        #Belirtilen günden eski yedek klasörlerini siler
        logging.info("--- Eski Yedekler Kontrol Ediliyor ---")
        simdi = datetime.datetime.now()
        eski_yedek_limiti = simdi - datetime.timedelta(days=self.saklama_gunu)
        silinen_sayisi = 0

        try:
            if not os.path.exists(self.hedef_klasor):
                logging.warning("Hedef klasör bulunamadığı için temizlik yapılamadı.")
                return

            for yedek in os.listdir(self.hedef_klasor):
                yedek_yolu = os.path.join(self.hedef_klasor, yedek)
                
                if os.path.isdir(yedek_yolu) and yedek.endswith("_yedek"):
                    try:
                        yedek_tarihi_str = yedek.split('_')[0]
                        yedek_tarihi = datetime.datetime.strptime(yedek_tarihi_str, "%Y-%m-%d")

                        if yedek_tarihi < eski_yedek_limiti:
                            shutil.rmtree(yedek_yolu)
                            logging.info(f"Eski yedek silindi: {yedek_yolu}")
                            silinen_sayisi += 1
                    except (ValueError, IndexError):
                        logging.warning(f"Klasör adı formatı okunamadı, atlanıyor: {yedek}")
                        continue
            
            if silinen_sayisi > 0:
                self._send_notification("Temizlik Tamamlandı", f"{silinen_sayisi} adet eski yedek başarıyla silindi.")
            else:
                logging.info("Silinecek eski yedek bulunamadı.")
        
        except Exception as e:
            logging.error(f"Temizleme sırasında beklenmedik bir hata oluştu: {e}")
            self._send_notification("Temizlik Başarısız", f"Temizlik sırasında bir hata oluştu: {e}")
    
if __name__ == "__main__":
    manager = BackupManager(config)
    manager.yedekle()
    manager.temizle()
    logging.info("--- Tüm işlemler tamamlandı. ---")