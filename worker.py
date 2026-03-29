import uuid
import random
import string
import time
from DrissionPage import ChromiumPage, ChromiumOptions
import json
import os
import shutil
import logging

# Worker için logging yapılandırması
logging.basicConfig(filename="worker.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_secure_password():
    prefix = "Xelesxeles"
    random_numbers = "".join(random.choices(string.digits, k=4))
    extra_symbol = random.choice("!@#$")
    return f"{prefix}{random_numbers}.{extra_symbol}"

def generate_custom_username():
    random_digits = "".join(random.choices(string.digits, k=6))
    return f"xeles{random_digits}"

def create_riot_account(task_id, user_data_dir):
    logging.info(f"Starting task {task_id} - Max 2 retry")
    
    result = {"task_id": task_id, "status": "failed", "account_info": {}, "error": None}
    max_retries = 2   # ← 2'ye düşürüldü

    for attempt in range(max_retries):
        attempt_dir = f"{user_data_dir}_attempt_{attempt}"
        os.makedirs(attempt_dir, exist_ok=True)
        
        account_info = {}
        logging.info(f"Attempt {attempt + 1}/{max_retries} for task {task_id}")
        
        try:
            # Tarayıcı Ayarları
            options = ChromiumOptions()
            options.incognito(True)
            options.set_user_data_path(attempt_dir)
            options.set_argument('--disable-gpu')
            options.set_argument('--disable-setuid-sandbox')
            options.set_argument('--disable-dev-shm-usage')
            options.set_argument('--no-zygote')
            page = ChromiumPage(options)

            # 1. Giriş Sayfası
            page.get("https://account.riotgames.com/")
            time.sleep(4)
           
            # Kayıt ol butonuna tıkla
            page.ele('xpath:/html/body/div[2]/div/main/div/form/div/div/div[3]/span[2]').click()
            time.sleep(1)
           
            # 2. E-POSTA
            account_info['email'] = "xeleshop@atomicmail.io"
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div[1]/div/input').input(account_info['email'])
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div').click()
            time.sleep(1)
           
            # 3. DOĞUM TARİHİ
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[1]/input').input("12")
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[2]/input').input("12")
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[3]/input').input("2002")
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div').click()
            time.sleep(1)
           
            # 4. KULLANICI ADI
            account_info['username'] = generate_custom_username()
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div/input').input(account_info['username'])
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div').click()
            time.sleep(1)
           
            # 5. ŞİFRE
            secure_pw = generate_secure_password()
            account_info['password'] = secure_pw
           
            def safe_input_with_trigger(input_element, password_text):
                input_element.input(password_text)
                time.sleep(0.5)
                input_element.click()
                page.actions.key_down('\ue003').key_up('\ue003')
                time.sleep(0.3)
                input_element.input(password_text[-1])
           
            p1 = page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[1]/div/input')
            safe_input_with_trigger(p1, secure_pw)
           
            p2 = page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[4]/div[1]/input')
            safe_input_with_trigger(p2, secure_pw)
           
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button/div').click()
            time.sleep(2)
           
            # 6. TOS
            element = page.ele('xpath://*[@id="tos-scrollable-area"]')
            page.run_js("arguments[0].scrollTop = arguments[0].scrollHeight", element)
            time.sleep(1)
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[2]/div/div[3]/div/div/div/input').click()
           
            # 7. FİNAL
            page.ele('xpath:/html/body/div[2]/div/main/div[3]/div/div[2]/div/div[3]/button').click()
           
            time.sleep(15)

            # Hata kontrolü (yeni hata mesajını da yakalıyor)
            page_text = page.run_js("return document.body.innerText || ''").lower()
            
            if any(phrase in page_text for phrase in [
                "kullanıcı adın veya şifren yanlış olabilir",
                "birkaç aydır oynamıyorsan",
                "giriş yapamıyorum bağlantısına göz at",
                "username already taken"
            ]):
                raise Exception("Username already taken - retrying with new username")

            # Başarılı
            result["status"] = "success"
            result["account_info"] = account_info
            logging.info(f"Task {task_id} SUCCESS on attempt {attempt + 1}")
            break

        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
            result["error"] = str(e)
        
        finally:
            try: page.quit()
            except: pass
            try: shutil.rmtree(attempt_dir, ignore_errors=True)
            except: pass

    # Sonuçları kaydet
    os.makedirs("results", exist_ok=True)
    with open(f"results/{task_id}.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    import sys
    task_id = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())
    user_data_dir = f"user_data_{task_id}"
    create_riot_account(task_id, user_data_dir)
