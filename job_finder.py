import csv
import webbrowser
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus


CSV_FILE = Path("job_finds.csv")

HEADERS = [
    "role",
    "company",
    "lane",
    "site_found",
    "years_expected",
    "posted_date",
    "date_found",
    "url",
    "status",
    "notes",
]

LANES = {
    "1": (
        "GRC / Audit / Compliance",
        '"GRC Analyst" OR "IT Auditor" OR "Security Compliance Analyst" OR "Risk Analyst"'
    ),
    "2": (
        "Defense / RMF / NIST",
        'RMF OR CMMC OR "NIST 800-171" OR ISSO OR "Information Assurance"'
    ),
    "3": (
        "SOC / Security Analyst",
        '"SOC Analyst" OR "Security Analyst" OR "Cybersecurity Analyst"'
    ),
    "4": (
        "IT Support / Security Adjacent",
        '"IT Support Specialist" OR "Help Desk Technician" OR "Desktop Support" OR "Network Support Technician"'
    ),
    "5": (
        "Privacy / Vendor Risk",
        '"Vendor Risk Analyst" OR "Third Party Risk Analyst" OR "Privacy Analyst" OR "Compliance Specialist"'
    ),
}

EXPERIENCE = (
    '"0-2 years" OR "1-2 years" OR "2 years" OR '
    '"entry level" OR junior OR associate OR '
    '"master\'s degree with 0 years" OR '
    '"master\'s degree and 0 years" OR '
    '"bachelor\'s degree with 0 years" OR '
    '"bachelor\'s degree and 2 years" OR '
    '"equivalent combination of education and experience" OR '
    '"education may be substituted"'
)

LOCATION = '"San Diego" OR "San Diego County" OR Poway OR "Rancho Bernardo" OR remote OR "United States"'

STRICT_ATS_SITES = (
    "site:myworkdayjobs.com OR "
    "site:wd1.myworkdayjobs.com OR "
    "site:greenhouse.io OR "
    "site:jobs.lever.co OR "
    "site:icims.com OR "
    "site:taleo.net OR "
    "site:smartrecruiters.com"
)

BROAD_CAREER_SITES = (
    "site:myworkdayjobs.com OR "
    "site:wd1.myworkdayjobs.com OR "
    "site:greenhouse.io OR "
    "site:jobs.lever.co OR "
    "site:icims.com OR "
    "site:taleo.net OR "
    "site:smartrecruiters.com OR "
    "site:jobs.northropgrumman.com OR "
    "site:careers.leidos.com OR "
    "site:careers.* OR "
    "site:jobs.*"
)

EXCLUDE = "-senior -principal -director"


def setup_csv():
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(HEADERS)


def choose_lane():
    print("\nSearch lanes:")
    for number, lane in LANES.items():
        print(f"{number}. {lane[0]}")

    choice = input("\nPick lane number: ").strip()

    if choice not in LANES:
        print("Invalid lane.")
        return None, None

    return LANES[choice]


def choose_search_mode():
    print("\nSearch mode:")
    print("1. Strict ATS-only")
    print("2. Broad career sites")
    print("3. Exact low-years phrase search")

    choice = input("\nPick mode: ").strip()

    if choice == "1":
        return "Strict ATS-only", STRICT_ATS_SITES
    if choice == "2":
        return "Broad career sites", BROAD_CAREER_SITES
    if choice == "3":
        return "Exact low-years phrase", None

    print("Invalid mode.")
    return None, None


def build_query(company, lane_terms, mode_name, sites):
    if mode_name == "Exact low-years phrase":
        return (
            f'"{company}" '
            f'({lane_terms}) '
            f'("master\'s degree with 0 years" OR "master\'s degree and 0 years" OR '
            f'"bachelor\'s degree with 0 years" OR "bachelor\'s degree and 2 years") '
            f'({LOCATION}) '
            f'{EXCLUDE}'
        )

    return f'"{company}" ({lane_terms}) ({EXPERIENCE}) ({LOCATION}) ({sites}) {EXCLUDE}'


def open_dork_search(company):
    lane_name, lane_terms = choose_lane()
    if not lane_name:
        return

    mode_name, sites = choose_search_mode()
    if not mode_name:
        return

    query = build_query(company, lane_terms, mode_name, sites)
    url = "https://www.google.com/search?q=" + quote_plus(query)

    print(f"\nOpening search for: {company}")
    print(f"Lane: {lane_name}")
    print(f"Mode: {mode_name}")
    print(query)

    webbrowser.open_new_tab(url)


def save_good_find(company):
    lane_name, _ = choose_lane()
    if not lane_name:
        return

    print("\nSave good find")
    print("-" * 20)

    role = input("Role/title: ").strip()
    site_found = input("Site found on: ").strip()
    years_expected = input("Years expected: ").strip()
    posted_date = input("Posted date, if shown: ").strip()
    url = input("URL: ").strip()
    notes = input("Notes: ").strip()

    row = [
        role,
        company,
        lane_name,
        site_found,
        years_expected,
        posted_date,
        date.today().isoformat(),
        url,
        "found",
        notes,
    ]

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        csv.writer(file).writerow(row)

    print(f"\nSaved: {role} at {company}")


def main():
    setup_csv()

    while True:
        company = input("\nCompany to search, or q to quit: ").strip()

        if company.lower() == "q":
            break

        while True:
            print(f"\nCompany: {company}")
            print("1. Open Google dork search")
            print("2. Save good find to CSV")
            print("3. Search new company")
            print("4. Quit")

            choice = input("\nChoose: ").strip()

            if choice == "1":
                open_dork_search(company)
            elif choice == "2":
                save_good_find(company)
            elif choice == "3":
                break
            elif choice == "4":
                return
            else:
                print("Invalid choice.")

    print(f"\nDone. Your CSV is saved as: {CSV_FILE}")


if __name__ == "__main__":
    main()
