from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active
        }


class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[Optional[str]] = mapped_column(String(20))
    mass: Mapped[Optional[str]] = mapped_column(String(20))
    hair_color: Mapped[Optional[str]] = mapped_column(String(50))
    eye_color: Mapped[Optional[str]] = mapped_column(String(50))

    favorited_by: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="character"
    )


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    diameter: Mapped[Optional[str]] = mapped_column(String(50))
    population: Mapped[Optional[str]] = mapped_column(String(50))
    climate: Mapped[Optional[str]] = mapped_column(String(50))

    favorited_by: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="planet"
    )


class Vehicle(db.Model):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(100))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    cost_in_credits: Mapped[Optional[str]] = mapped_column(String(50))
    passengers: Mapped[Optional[str]] = mapped_column(String(50))

    favorited_by: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="vehicle"
    )


class Favorite(db.Model):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    character_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE"),
        nullable=True
    )

    planet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("planet.id", ondelete="CASCADE"),
        nullable=True
    )

    vehicle_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vehicle.id", ondelete="CASCADE"),
        nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    character: Mapped[Optional["Character"]] = relationship("Character", back_populates="favorited_by")
    planet: Mapped[Optional["Planet"]] = relationship("Planet", back_populates="favorited_by")
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="favorited_by")

    def serialize(self):
        if self.character:
            return {
                "id": self.id,
                "type": "character",
                "name": self.character.name
            }
        if self.planet:
            return {
                "id": self.id,
                "type": "planet",
                "name": self.planet.name
            }
        if self.vehicle:
            return {
                "id": self.id,
                "type": "vehicle",
                "name": self.vehicle.name
            }
        return {
            "id": self.id,
            "type": "unknown"
        }