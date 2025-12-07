import os
import datetime
from sqlalchemy import create_engine, Column, String, Float, Date, Integer, UniqueConstraint, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    curr = Column(String)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String)
    sector = Column(String)
    asset_class = Column(String)

class PriceData(Base):
    __tablename__ = 'price_data'
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Integer)
    

    __table_args__ = (UniqueConstraint('ticker', 'date', name='uix_ticker_date'),)

class UserPreferences(Base):
    __tablename__ = 'user_preferences'
    key = Column(String, primary_key=True)
    value = Column(String)

class DataStore:
    def __init__(self, db_path='portfolio.db'):
        db_url = f'sqlite:///{db_path}'
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def get_session(self):
        return self.Session()
    
    def store_asset_details(self, ticker, name=None, sector=None, asset_class=None):
        session = self.Session()
        try:
            asset = session.query(Asset).filter_by(ticker=ticker).first()
            if not asset:
                asset = Asset(ticker=ticker, name=name, sector=sector, asset_class=asset_class)
                session.add(asset)
            else:
                if name: asset.name = name
                if sector: asset.sector = sector
                if asset_class: asset.asset_class = asset_class
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error storing asset details: {e}")
        finally:
            session.close()

    def store_prices(self, ticker, df):
        """
        Expects a pandas DataFrame with datetime index and columns: Open, High, Low, Close, Adj Close, Volume
        """
        session = self.Session()
        try:
            # Check existing dates to avoid constraint errors or excessive overwrites
            # For simplicity in bulk/df, we can use merge or "ignore" logic, 
            # but usually it's better to fetch only what we need. 
            # Here we will attempt to add new records.
            
            # A more robust way is to query existing max date.
            pass # Actually implemented in fetcher logic usually to filter, but here we insert.
            
            for index, row in df.iterrows():
                # Check exist
                # Optimization: For bulk, this is slow. Better to filter DF before loop or use bulk_insert_mappings
                # We will trust the fetcher to give us *new* data mostly, or handle Upsert.
                # SQLite INSERT OR IGNORE is easiest via raw sql or core, but via ORM:
                
                existing = session.query(PriceData).filter_by(ticker=ticker, date=index.date()).first()
                if not existing:
                    price = PriceData(
                        ticker=ticker,
                        date=index.date(),
                        open=row.get('Open'),
                        high=row.get('High'),
                        low=row.get('Low'),
                        close=row.get('Close'),
                        adj_close=row.get('Adj Close', row.get('Close')),
                        volume=int(float(row.get('Volume', 0)))
                    )
                    session.add(price)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error storing prices for {ticker}: {e}")
        finally:
            session.close()

    def get_latest_date(self, ticker):
        session = self.Session()
        try:
            last = session.query(PriceData.date).filter_by(ticker=ticker).order_by(PriceData.date.desc()).first()
            return last[0] if last else None
        finally:
            session.close()

    def load_prices(self, ticker):
        import pandas as pd
        session = self.Session()
        try:
            query = session.query(PriceData).filter_by(ticker=ticker).order_by(PriceData.date.asc())
            df = pd.read_sql(query.statement, session.bind)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
        finally:
            session.close()

    def set_preference(self, key, value):
        session = self.Session()
        try:
            pref = session.query(UserPreferences).filter_by(key=key).first()
            if not pref:
                pref = UserPreferences(key=key, value=str(value)) # Store as string
                session.add(pref)
            else:
                pref.value = str(value)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error setting preference {key}: {e}")
        finally:
            session.close()

    def get_preference(self, key, default=None):
        session = self.Session()
        try:
            pref = session.query(UserPreferences).filter_by(key=key).first()
            return pref.value if pref else default
        finally:
            session.close()

    def get_all_asset_names(self):
        session = self.Session()
        try:
            # Query all (ticker, name) pairs
            assets = session.query(Asset.ticker, Asset.name).all()
            return {ticker: name for ticker, name in assets}
        finally:
            session.close()


