"""Module for handling cases in eFlyt"""
from dataclasses import dataclass
from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@dataclass
class Case:
    """A dataclass representing an Eflyt case."""
    case_number: str
    deadline: date | None
    case_types: list[str]
    status: str
    cpr: str
    name: str
    case_worker: str


@dataclass
class Inhabitant:
    """A dataclass representing an inhabitant."""
    cpr: str
    name: str
    move_in_date: date
    relations: list[str]


@dataclass
class Applicant:
    """A dataclass representing an applicant."""
    cpr: str
    name: str


def get_beboere(browser: webdriver.Chrome) -> list[Inhabitant]:
    """Get a list of current inhabitants on the case currently open.

    Args:
        browser: The webdriver browser object.

    Returns:
        A list of Inhabitants.
    """
    # Go to the correct tab and scrape data
    change_tab(browser, 1)
    beboer_table = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_becPersonTab_GridViewBeboere")
    rows = beboer_table.find_elements(By.TAG_NAME, "tr")

    # Remove header
    rows.pop(0)

    inhabitants = []
    for inhabitant in rows:
        # Get date for moving in, CPR and name
        moving_in = datetime.strptime(inhabitant.find_element(By.XPATH, "td[1]/span | td[1]/a").text, "%d-%m-%Y").date()
        cpr = inhabitant.find_element(By.XPATH, "td[2]").text.replace("-", "")
        name = inhabitant.find_element(By.XPATH, "td[3]").text

        # Check for a list of relations
        relations = []
        elements = inhabitant.find_elements(By.XPATH, "td[4]/span")
        if elements:
            relations = elements[0].text.replace("<br>", ";").replace("\n", ";").split(";")

        # Create an Inhabitant and add to list
        new_inhabitant = Inhabitant(cpr, name, moving_in, relations)
        inhabitants.append(new_inhabitant)

    return inhabitants


def get_room_count(browser: webdriver.Chrome) -> int:
    """Get the number of rooms on the address.

    Args:
        browser: The webdriver browser object.

    Returns:
        The number of rooms on the address.
    """
    change_tab(browser, 1)
    area_room_text = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_stcPersonTab6_lblAreaText").text
    room_text = area_room_text.split("/")[1]
    return int(room_text)


def get_applicants(browser: webdriver.Chrome) -> list[Applicant]:
    """Get a list of applicants' cpr numbers from the applicant table.

    Args:
        browser: The webdriver browser object.

    Returns:
        A list of cpr numbers.
    """
    table = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_GridViewMovingPersons")
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Remove header row
    rows.pop(0)

    applicants = []

    for row in rows:
        cpr = row.find_element(By.XPATH, "td[2]/a[2]").text.replace("-", "")
        name = row.find_element(By.XPATH, "td[3]/a").text
        applicant = Applicant(cpr, name)
        applicants.append(applicant)

    return applicants


def change_tab(browser: webdriver.Chrome, tab_index: int):
    """Change the tab in the case view e.g. 'Sagslog', 'Breve'.

    Args:
        browser: The webdriver browser object.
        tab_index: The zero-based index of the tab to select.
    """
    # Use the src of the tab image to determine if the tab needs to be changed
    tab_image = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ImgJournalMap")
    image_src = tab_image.get_attribute("src")
    current_index = int(image_src[-5]) - 1

    if current_index != tab_index:
        browser.execute_script(f"__doPostBack('ctl00$ContentPlaceHolder2$ptFanePerson$ImgJournalMap','{tab_index}')")


def approve_case(browser: webdriver.Chrome):
    """Approve a case.
    If any person on the case is blocking approval, approve each person individually.
    """
    change_tab(browser, 0)

    deadline_field = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_txtDeadline")
    deadline_field.clear()
    note_field = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_txtDeadlineNote")
    note_field.clear()

    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_stcPersonTab1_btnGodkend").click()
    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_stcPersonTab1_btnApproveYes").click()

    approve_persons_button = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_stcPersonTab1_btnGodkendAlle")
    if approve_persons_button.is_enabled():
        approve_persons_button.click()
    else:
        # Approve each person individually
        person_count = len(browser.find_elements(By.XPATH, '//table[@id="ctl00_ContentPlaceHolder2_GridViewMovingPersons"]//tr')) - 1

        for i in range(person_count):
            browser.find_element(By.XPATH, f'//table[@id="ctl00_ContentPlaceHolder2_GridViewMovingPersons"]//tr[{i+2}]//td[2]').click()

            browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_stcPersonTab1_btnGodkend").click()
            approve_button = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_stcPersonTab1_btnApproveYes")
            if approve_button.is_displayed():
                approve_button.click()

        # Go back to the case
        browser.find_element(By.XPATH, '//table[@id="ctl00_ContentPlaceHolder2_GridViewMovingPersons"]//tr[1]//td[2]').click()


def check_all_approved(browser: webdriver.Chrome) -> bool:
    """Check all inhabiatants in table have a status 'Godkendt'.
    """
    person_table = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_GridViewMovingPersons")
    rows = person_table.find_elements(By.TAG_NAME, "tr")
    rows.pop(0)

    for row in rows:
        row_status = row.find_element(By.XPATH, "td[6]").text
        if row_status not in ("Godkendt", "Afsluttet"):
            return False
    return True


def add_note(browser: webdriver.Chrome, message: str):
    """Add a note to a case."""
    change_tab(browser, 0)
    message = f"{date.today().strftime('%Y-%m-%d')} Besked fra Robot: {message}"
    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_ButtonVisOpdater").click()

    existing_note = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_txtVisOpdaterNote").text
    if len(existing_note) > 0:
        message = "\n\n" + message
        browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_txtVisOpdaterNote").send_keys(Keys.CONTROL+Keys.END)

    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_txtVisOpdaterNote").send_keys(message)
    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_btnLongNoteUpdater").click()


def get_note_text(browser: webdriver.Chrome) -> str:
    """Read note text and close the window, returning the value.
    """
    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_ButtonVisOpdater").click()
    text = browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_txtVisOpdaterNote").text
    browser.find_element(By.ID, "ctl00_ContentPlaceHolder2_ptFanePerson_ncPersonTab_btnLuk").click()
    return text
