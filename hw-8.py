import pickle
from collections import UserDict
from datetime import datetime, timedelta

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            pass

class Record:
    def __init__(self, name):
        self.name = name
        self.phones = []
        self.birthday = None
    def add_phone(self, phone):
        self.phones.append(phone)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            index = self.phones.index(old_phone)
            self.phones[index] = new_phone

    def find_phone(self, phone):
        return phone in self.phones

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def get_birthday(self):
        return self.birthday

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}"

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.users = {}

    def add_record(self, record):
        self.data[record.name] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return None

    @staticmethod
    def find_next_weekday(d, weekday: int):
        """
         Ф-ція для знаходження наступного заданого дня тижня після заданої дати
        :param d: datetime.date - початкова дата
        :param weekday: int - день тижня від 0 (понеділок) до 6 (неділя)
        :return:
        """
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days=days_ahead)

    @staticmethod
    def prepare_users(users):
        prepared_users = []
        for user in users:
            try:
                birthday = datetime.strptime(user['birthday'], '%Y.%m.%d').date()
                prepared_users.append({"name": user['name'], 'birthday': birthday})
            except ValueError:
                print(f'Некоректна дата народження для користувача {user["name"]}')
        return prepared_users

    @staticmethod
    def get_upcoming_birthday(prepared_users, days=7):
        today = datetime.today().date()

        upcoming_birthdays = []
        for user in prepared_users:
            birthday_this_year = user["birthday"].replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year = AddressBook.find_next_weekday(birthday_this_year, 0)

                congratulation_date_str = birthday_this_year.strftime('%Y.%m.%d')
                upcoming_birthdays.append({
                    "name": user["name"],
                    "congratulation_date": congratulation_date_str
                })
        return upcoming_birthdays

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for contact '{name}' has been updated"
    else:
        return f"Contact '{name}' does not exist."

@input_error
def show_phones(book: AddressBook):
    if book:
        return "\n".join(f"{name}: {phone}" for name, phone in book.items())
    else:
        return "No contacts found."

@input_error
def show_all(book: AddressBook):
    all_contacts_data = []
    for record in book.data.values():
        phones = record.phones if record.phones else None
        birthday = record.birthday.value if record.birthday else None
        contact_data = {
            "name": record.name,
            "phones": phones,
            "birthday": birthday
        }
        all_contacts_data.append(contact_data)
    return all_contacts_data

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Birthday added."
    if birthday:
        record.add_birthday(birthday)
        book.users[name] = birthday
    return message

@input_error
def show_birthday(name, book):
    record = book.find(name)
    if record:
        birthday = record.get_birthday()
        if birthday:
            return f"Birthday for contact '{name}': {birthday}"
        else:
            return f"Birthday for contact '{name}' does not exist."
    else:
        return f"Contact '{name}' does not exist."

@input_error
def birthdays(book):
    upcoming = []
    for name in book.users:
        birthday = book.users[name]
        upcoming.append({"name": name, "congratulation_date": birthday})
    return upcoming

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args
    pass

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))


        elif command == "phone":
            print(show_phones(book))


        elif command == "all":
            print(show_all(book))


        elif command == "add-birthday":
            print(add_birthday(args, book))


        elif command == "show-birthday":
            print(show_birthday(args[0], book))


        elif command == "birthdays":
            print(birthdays(book))


        else:
            print("Invalid command.")

        save_data(book)

if __name__ == "__main__":
    main()