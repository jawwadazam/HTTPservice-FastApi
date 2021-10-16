import sqlalchemy as db
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm



SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
engine = db.create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative.declarative_base()


class CustomerModel(Base):
    __tablename__ = 'customers'
    id= db.Column(db.Integer, primary_key = True)
    name= db.Column(db.String, nullable=False)
    is_active= db.Column(db.Boolean, nullable=False)

    logs = orm.relationship("LoggerModel", backref="customers")
    hourly_stat = orm.relationship("HourlyStatsModel", backref="customers")
    
class RequestsModel(Base):
    __tablename__ = 'requests'
    id= db.Column(db.Integer, primary_key = True)
    request_body = db.Column(db.String)  
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    logs = orm.relationship("LoggerModel", backref="requests")

class InvalidCodesModel(Base):
    __tablename__ = 'invalidCodes'
    id= db.Column(db.Integer, primary_key = True)
    info = db.Column(db.String)

    logs = orm.relationship("LoggerModel", backref="invalidCodes")

class LoggerModel(Base):
    __tablename__ = 'logger'
    id= db.Column(db.Integer, primary_key = True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False)
    invalid_code_id = db.Column(db.Integer, db.ForeignKey("invalidCodes.id"))
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

class IPBlacklistModel(Base):
    __tablename__ = 'ipBlacklist'
    id= db.Column(db.Integer, primary_key = True)
    ip= db.Column(db.String, nullable=False)

class UserAgentBlacklistModel(Base):
    __tablename__ = 'userAgentBlacklist'
    id= db.Column(db.Integer, primary_key = True)
    user_agent= db.Column(db.String(36), nullable=False)

class HourlyStatsModel(Base):
    __tablename__ = 'hourlyStats'
    id= db.Column(db.Integer, primary_key = True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    total_requests_count = db.Column(db.Integer, nullable=False)
    valid_requests_count = db.Column(db.Integer, nullable=False)
    invalid_requests_count = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)