def get_element(driver, selector):
    from selenium.webdriver.common.by import By

    return driver.find_element(By.CSS_SELECTOR, selector)


def get_elements(driver, selector):
    from selenium.webdriver.common.by import By

    return driver.find_elements(By.CSS_SELECTOR, selector)


def click_button(driver, selector):
    # just using element.click() can fail if the element is not in view
    element = get_element(driver, selector)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)
