from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    site_registrations = relationship('SiteRegistration', back_populates='user')

    def register(self, session):
        existing_user = session.query(User).filter((User.username == self.username) | (User.email == self.email)).first()
        if existing_user:
            if existing_user.username == self.username:
                print(f"Логін '{self.username}' вже існує.")
            if existing_user.email == self.email:
                print(f"Email '{self.email}' вже використовується.")
            return

        session.add(self)
        session.commit()
        print("Реєстрація пройшла успішно!")

    @staticmethod
    def login(session, username, password):
        user = session.query(User).filter_by(username=username, password=password).first()
        if user:
            print(f"Успішний вхід, користувач: {username}")
            return user
        else:
            print("Неправильні дані!")
            return None

class SiteRegistration(Base):
    __tablename__ = 'site_registrations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    site_name = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    login_method = Column(String(50), nullable=False)  # Google, Facebook, Apple, тощо

    user = relationship('User', back_populates='site_registrations')

    def register_site(self, session):
        existing_site = session.query(SiteRegistration).filter_by(user_id=self.user_id, site_name=self.site_name, login_method=self.login_method).first()
        if existing_site:
            print(f"Ви вже зареєстровані на сайті {self.site_name} через {self.login_method}.")
        else:
            session.add(self)
            session.commit()
            print(f"Інформація про реєстрацію на сайті {self.site_name} успішно додана.")

    @staticmethod
    def get_user_sites(session, user_id):
        sites = session.query(SiteRegistration).filter_by(user_id=user_id).all()
        if sites:
            print("Ви зареєстровані на наступних сайтах:")
            for site in sites:
                print(f"Сайт: {site.site_name}, Логін: {site.login}, Вид входу: {site.login_method}")
        else:
            print("Ви не зареєстровані на жодному сайті.")

DATABASE_URL = 'mysql+mysqlconnector://root:@localhost/project'
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    session = Session()

    while True:
        print("\nВиберіть опцію:")
        print("1 - Зареєструватися")
        print("2 - Увійти")
        print("3 - Додати сайт до реєстрацій")
        print("4 - Переглянути зареєстровані сайти")
        print("5 - Вийти")

        choice = input("Ваш вибір: ")

        if choice == "1":
            username = input("Введіть ім'я користувача: ")
            password = input("Введіть пароль: ")
            email = input("Введіть email: ")

            new_user = User(username=username, password=password, email=email)
            new_user.register(session)

        elif choice == "2":
            username = input("Введіть ім'я користувача: ")
            password = input("Введіть пароль: ")

            User.login(session, username, password)

        elif choice == "3":
            user_id = int(input("Введіть ваш ID користувача: "))
            site_name = input("Введіть назву сайту: ")
            login = input("Введіть логін на сайті: ")
            password = input("Введіть пароль на сайті: ")
            login_method = input("Введіть метод входу (Google, Facebook, Apple): ")

            site_registration = SiteRegistration(user_id=user_id, site_name=site_name, login=login, password=password, login_method=login_method)
            site_registration.register_site(session)

        elif choice == "4":
            user_id = int(input("Введіть ваш ID користувача: "))
            SiteRegistration.get_user_sites(session, user_id)

        elif choice == "5":
            print("Вихід з програми.")
            session.close()
            break

        else:
            print("Невірний вибір! Спробуйте ще раз.")