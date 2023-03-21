from sqlalchemy import create_engine, Column, Integer, String, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dateparser

# create the database engine and session
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
session = Session()

# create the declarative base
Base = declarative_base()

# define the user class
class User(Base):
    __tablename__ = "users"

    session_id = Column(Integer, primary_key=True)
    username = Column(String)
    origin = Column(String)
    destination = Column(String)
    departure_date = Column(Date)
    return_date = Column(Date)
    num_adults = Column(Integer, default=1)
    num_children = Column(Integer, default=0)
    child_ages = Column(JSON)

    def _init_(
        self,
        session_id,
        origin,
        destination,
        departure_date,
        return_date,
        num_adults=1,
        num_children=0,
        child_ages=None,
    ):
        self.session_id = session_id
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date

        self.return_date = return_date
        self.num_adults = num_adults
        self.num_children = num_children
        self.child_ages = child_ages or []


# create the table
Base.metadata.create_all(engine)


# # create a user
current_user = User(
    session_id=1,
    origin=None,
    destination=None,
    departure_date=None,
    return_date=None,
    num_adults=1,
    num_children=0,
    child_ages=[],
)

# # add the user to the database
# session.add(user)
# session.commit()

# # # update the user's number of adults
# # user.num_adults = 3
# # session.commit()

# # # get all users
# # users = session.query(User).all()

# # # delete the user
# # session.delete(user)
# # session.commit()
