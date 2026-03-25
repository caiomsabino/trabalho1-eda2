# scraper.py
import time
import json
import subprocess
from selenium import webdriver
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.adidas.com.br/tenis-homem"

SEL_PRODUCT = "article[data-testid='plp-product-card']"
SEL_NAME    = "[data-testid='product-card-upper-label'], [class*='product-card__title'], h3, .product-card_product-card-content__name"
SEL_PRICE   = "[class*='product-card__price'], [data-testid*='price'], [class*='gl-price']"


def init_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")  # ← ESSENCIAL
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    # Remove o flag webdriver do JS
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def parse_price(raw: str) -> Optional[float]:
    if not raw:
        return None
    # Remove espaços inquebráveis (\xa0) e limpa o R$
    clean_raw = raw.replace("\xa0", " ").replace("R$", "").strip()
    
    # Se houver preço antigo e novo, pega o último (valor atual)
    parts = clean_raw.split()
    if not parts:
        return None
    
    # Pega o último pedaço (ex: "1.199,99")
    price_str = parts[-1].replace(".", "").replace(",", ".")
    try:
        return float(price_str)
    except ValueError:
        return None

def scrape_first_page() -> list[dict]:
    driver = init_driver()
    wait = WebDriverWait(driver, 20)
    products = []

    try:
        driver.get(URL)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-testid='plp-product-card']")))

        # Scroll para garantir que o JS renderize os textos
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 800)")
            time.sleep(0.7)

        cards = driver.find_elements(By.CSS_SELECTOR, "article[data-testid='plp-product-card']")
        print(f"  {len(cards)} cards encontrados. Extraindo dados...")

        for idx, card in enumerate(cards, start=1):
            try:
                # USANDO innerText EM VEZ DE .text
                name = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-title']").get_attribute("innerText").strip()
                price_raw = card.find_element(By.CSS_SELECTOR, "[data-testid='main-price']").get_attribute("innerText").strip()
                price = parse_price(price_raw)

                if name and price:
                    products.append({"id": idx, "name": name, "price": price})
                else:
                    # Log de erro para você ver no terminal por que pulou
                    print(f"  [Card {idx}] Falha no parse: Nome='{name}', Preço='{price_raw}'")
            except Exception as e:
                print(f" [Card {idx}] Erro: {e}")
                continue

    finally:
        driver.quit()

    return products


def ask_user() -> tuple[float, Optional[float]]:
    print("\n=== Busca de Tênis Adidas ===")
    print("Digite um valor exato  → ex: 299.90")
    print("Digite um range        → ex: 100 500")
    raw = input("\nPreço: ").strip()

    parts = raw.split()
    if len(parts) == 1:
        return float(parts[0]), None
    elif len(parts) == 2:
        return float(parts[0]), float(parts[1])
    else:
        raise ValueError("Entrada inválida. Use '299.90' ou '100 500'.")


def call_ruby(products: list[dict], price_min: float, price_max: Optional[float]) -> str:
    payload = json.dumps({
        "products":  products,
        "price_min": price_min,
        "price_max": price_max if price_max is not None else price_min
    })
    result = subprocess.run(
        ["ruby", "search.rb"],
        input=payload,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


if __name__ == "__main__":
    print("Carregando primeira página...")
    products = scrape_first_page()
    print(f"  {len(products)} produtos carregados.\n")

    price_min, price_max = ask_user()
    output = call_ruby(products, price_min, price_max)
    print("\n" + output)