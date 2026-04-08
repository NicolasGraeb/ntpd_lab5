from db import init_db


def main() -> None:
    created = init_db()
    if created:
        print("Tabela predictions zostala utworzona lub juz istnieje.")
    else:
        print(
            "Brak konfiguracji bazy. Ustaw DATABASE_URL albo DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD."
        )


if __name__ == "__main__":
    main()
