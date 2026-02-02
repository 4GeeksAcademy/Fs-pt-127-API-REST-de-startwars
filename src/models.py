from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

db = SQLAlchemy()

class User(db.Model): 
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    
    favorites = relationship("Favorite", back_populates="user")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Character(db.Model):
 __tablename__ = "character"
 id: Mapped[int] = mapped_column(primary_key=True)
 name: Mapped[str] = mapped_column(String(100), nullable=False)
 height: Mapped[str] = mapped_column(String(20))
 mass: Mapped[str] = mapped_column(String(20))
hair_color: Mapped[str] = mapped_column(String(50))
eye_color: Mapped[str] = mapped_column(String(50))
    
favorited_by = relationship("Favorite", back_populates="character")

def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "eye_color": self.eye_color
        }

class Planet(db.Model):
    __tablename__ = "planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    diameter: Mapped[str] = mapped_column(String(50))
    population: Mapped[str] = mapped_column(String(50))
    climate: Mapped[str] = mapped_column(String(50))

    favorited_by = relationship("Favorite", back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate
        }

class Vehicle(db.Model):
    __tablename__ = "vehicle"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100))
    manufacturer: Mapped[str] = mapped_column(String(100))
    cost_in_credits: Mapped[str] = mapped_column(String(50))
    passengers: Mapped[str] = mapped_column(String(50))

    favorited_by = relationship("Favorite", back_populates="vehicle")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer
        }
class Favorite(db.Model):
    __tablename__ = "favorite"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicle.id"), nullable=True)

    user = relationship("User", back_populates="favorites")
    character = relationship("Character", back_populates="favorited_by")
    planet = relationship("Planet", back_populates="favorited_by")
    vehicle = relationship("Vehicle", back_populates="favorited_by")

    def serialize(self):

        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_name": (
                self.character.name if self.character else 
                self.planet.name if self.planet else 
                self.vehicle.name if self.vehicle else "Unknown"
            ),
            "type": (
                "character" if self.character else 
                "planet" if self.planet else 
                "vehicle" if self.vehicle else "unknown"
            )
        }

