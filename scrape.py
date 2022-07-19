from sgselenium import SgChrome

if __name__ == "__main__":    
    url = "https://www.greasemonkeyauto.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=5ca57c5aba&load_all=1&layout=1&category=87%2C86%2C85%2C84%2C83%2C82%2C81%2C80%2C79%2C78%2C77%2C76%2C75%2C74%2C73%2C72%2C71%2C70%2C69%2C68%2C67%2C66%2C65%2C64%2C63%2C62%2C61%2C60%2C58%2C57%2C56%2C55%2C53%2C132%2C140%2C143%2C144"
    with SgChrome() as driver:
        driver.get(url)
        response = driver.page_source
        
    print(response)