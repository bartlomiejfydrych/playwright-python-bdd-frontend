import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# ==========================================================================================================
# PATHS
# ==========================================================================================================

# NOTE FOR ME: Katalog "src" (2 poziomy wyżej niż ten plik: src/configuration/config.py -> src)
_SRC_DIR = Path(__file__).resolve().parent.parent

# NOTE FOR ME: Root repozytorium (1 poziom wyżej niż "src")
_PROJECT_ROOT_DIR = _SRC_DIR.parent

_ENV_PATH = _PROJECT_ROOT_DIR / ".env"

# ==========================================================================================================
# LOAD ENVIRONMENT FILE (.env)
# ==========================================================================================================

# NOTE FOR ME:
# Wczytanie .env od razu (brak pliku nie powoduje błędu). load_dotenv() NIE nadpisuje istniejących
# zmiennych systemowych (override=False), więc zmienne systemowe mają automatycznie wyższy priorytet niż .env.
load_dotenv(dotenv_path=_ENV_PATH)


# ==========================================================================================================
# PROPERTY READER
# ==========================================================================================================

# ------
# STRING
# ------

def _get_property(key: str, default_value: Optional[str] = None) -> str:
    # 1. {system} / {.env} – Get environment variables (.env is already loaded into os.environ)
    value = os.environ.get(key)
    if value is not None:
        return value.strip()

    # 2. {default} – Get default property (if was provided)
    if default_value is not None:
        print(f"[WARNING] (CONFIG) Using default value for missing configuration key '{key}': {default_value}")
        return default_value

    # 3. {missing} – Get error if property is missing
    raise RuntimeError(
        f"(CONFIG) Missing required configuration key: '{key}'. "
        f"Checked {{system environment}} and {{.env}} ({_ENV_PATH})."
    )


# -----------------
# STRING (OPTIONAL)
# -----------------

# NOTE FOR ME: Dla pól opcjonalnych (np. fax, company) brak wartości to normalna sytuacja,
# więc zwracamy pusty string bez ostrzeżenia.
def _get_optional_property(key: str) -> str:
    return os.environ.get(key, "").strip()


# -------
# BOOLEAN
# -------

def _get_property_bool(key: str, default_value: Optional[bool] = None) -> bool:
    raw = _get_property(key, None if default_value is None else str(default_value)).lower()

    if raw in ("true", "yes", "1"):
        return True
    if raw in ("false", "no", "0"):
        return False

    raise RuntimeError(f"(CONFIG) Invalid boolean value for key '{key}': {raw}. Allowed: true/false, yes/no, 1/0")


# ==========================================================================================================
# PUBLIC CONFIG GETTERS
# ==========================================================================================================

# ----
# .env
# ----

# ACCOUNT DATA

# Get account {first name}
def get_account_first_name() -> str:
    return _get_property("ACCOUNT_FIRST_NAME")


# Get account {last name}
def get_account_last_name() -> str:
    return _get_property("ACCOUNT_LAST_NAME")


# Get account {e-mail}
def get_account_e_mail() -> str:
    return _get_property("ACCOUNT_E_MAIL")


# Get account {telephone}
def get_account_telephone() -> str:
    return _get_property("ACCOUNT_TELEPHONE")


# Get account {fax} (optional)
def get_account_fax() -> str:
    return _get_optional_property("ACCOUNT_FAX")


# Get account {company} (optional)
def get_account_company() -> str:
    return _get_optional_property("ACCOUNT_COMPANY")


# Get account {address 1}
def get_account_address_1() -> str:
    return _get_property("ACCOUNT_ADDRESS_1")


# Get account {address 2} (optional)
def get_account_address_2() -> str:
    return _get_optional_property("ACCOUNT_ADDRESS_2")


# Get account {city}
def get_account_city() -> str:
    return _get_property("ACCOUNT_CITY")


# Get account {region / state}
def get_account_region_state() -> str:
    return _get_property("ACCOUNT_REGION_STATE")


# Get account {zip code}
def get_account_zip_code() -> str:
    return _get_property("ACCOUNT_ZIP_CODE")


# Get account {country}
def get_account_country() -> str:
    return _get_property("ACCOUNT_COUNTRY")


# Get account {login name}
def get_account_login_name() -> str:
    return _get_property("ACCOUNT_LOGIN_NAME")


# Get account {password}
def get_account_password() -> str:
    return _get_property("ACCOUNT_PASSWORD")


# Get account {subscribe}
def get_account_subscribe() -> bool:
    return _get_property_bool("ACCOUNT_SUBSCRIBE")
