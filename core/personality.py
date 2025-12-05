from typing import Optional, List
import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import Session

from .database import Base, engine, get_db


class PersonalityProfile(Base):
    __tablename__ = "personality_profile"

    id = Column(Integer, primary_key=True, index=True)

    display_name = Column(String(100), nullable=False, default="Aziz AI")
    short_bio = Column(Text, nullable=False, default="Azizning raqamli super kloni.")

    speaking_style = Column(String(50), nullable=False, default="friendly-expert")
    main_languages = Column(String(100), nullable=False, default="uz,ru,en")

    style_rules = Column(Text, nullable=False, default="""
    {
        "tone": "do'stona, tushuntiruvchi, texnik joylarda juda aniq",
        "avoid": ["ortiqcha maqtov", "keraksiz rasmiylik"],
        "always_do": [
            "loyihalar bilan bog'lab misollar keltir",
            "kerak bo'lsa qisqa reja va ketma-ketlik ber",
            "Azizning vaqtini qadrlab, ortiqcha gapni kamaytir"
        ]
    }
    """)

    strengths = Column(Text, nullable=False, default="python,fastapi,flask,telegram-bot,data-analysis,ai,ux-ui,freelance,upwork")

    default_mode = Column(String(50), nullable=False, default="developer")
    is_active = Column(Boolean, nullable=False, default=True)


class PersonaPreset(Base):
    __tablename__ = "persona_preset"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    style_rules = Column(Text, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)


class PersonalityProfileBase(BaseModel):
    display_name: str = Field(default="Aziz AI", max_length=100)
    short_bio: str = Field(default="Azizning raqamli super kloni.")

    speaking_style: str = Field(default="friendly-expert")
    main_languages: str = Field(default="uz,ru,en")

    style_rules: str = Field(
        default="""{
    "tone": "do'stona, tushuntiruvchi, texnik joylarda juda aniq",
    "avoid": ["ortiqcha maqtov", "keraksiz rasmiylik"],
    "always_do": [
        "loyihalar bilan bog'lab misollar keltir",
        "kerak bo'lsa qisqa reja va ketma-ketlik ber",
        "Azizning vaqtini qadrlab, ortiqcha gapni kamaytir"
    ]
}"""
    )

    strengths: str = Field(default="python,fastapi,flask,telegram-bot,data-analysis,ai,ux-ui,freelance,upwork")
    default_mode: str = Field(default="developer")
    is_active: bool = Field(default=True)


class PersonalityProfileCreate(PersonalityProfileBase):
    pass


class PersonalityProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    short_bio: Optional[str] = None
    speaking_style: Optional[str] = None
    main_languages: Optional[str] = None
    style_rules: Optional[str] = None
    strengths: Optional[str] = None
    default_mode: Optional[str] = None
    is_active: Optional[bool] = None


class PersonalityProfileOut(PersonalityProfileBase):
    id: int

    class Config:
        from_attributes = True


class PersonaPresetBase(BaseModel):
    code: str = Field(max_length=50)
    title: str = Field(max_length=100)
    description: str
    style_rules: str
    is_default: bool = False


class PersonaPresetCreate(PersonaPresetBase):
    pass


class PersonaPresetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    style_rules: Optional[str] = None
    is_default: Optional[bool] = None


class PersonaPresetOut(PersonaPresetBase):
    id: int

    class Config:
        from_attributes = True


class StyleConfigOut(BaseModel):
    profile_id: int
    display_name: str
    short_bio: str
    speaking_style: str
    languages: List[str]
    strengths: List[str]
    default_mode: str
    style_rules_json: dict
    active_preset_code: Optional[str] = None


def _ensure_profile_exists(db: Session) -> PersonalityProfile:
    profile = db.query(PersonalityProfile).first()
    if profile is None:
        profile = PersonalityProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_profile(db: Session) -> PersonalityProfile:
    return _ensure_profile_exists(db)


def update_profile(db: Session, data: PersonalityProfileUpdate) -> PersonalityProfile:
    profile = _ensure_profile_exists(db)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_presets(db: Session):
    return db.query(PersonaPreset).all()


def create_preset(db: Session, data: PersonaPresetCreate) -> PersonaPreset:
    if data.is_default:
        db.query(PersonaPreset).update({"is_default": False})

    preset = PersonaPreset(
        code=data.code,
        title=data.title,
        description=data.description,
        style_rules=data.style_rules,
        is_default=data.is_default
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


def update_preset(db: Session, preset_id: int, data: PersonaPresetUpdate) -> Optional[PersonaPreset]:
    preset = db.query(PersonaPreset).filter(PersonaPreset.id == preset_id).first()
    if not preset:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "is_default" in update_data and update_data["is_default"]:
        db.query(PersonaPreset).update({"is_default": False})

    for field, value in update_data.items():
        setattr(preset, field, value)

    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


def delete_preset(db: Session, preset_id: int) -> bool:
    preset = db.query(PersonaPreset).filter(PersonaPreset.id == preset_id).first()
    if not preset:
        return False
    db.delete(preset)
    db.commit()
    return True


def get_style_config(db: Session) -> StyleConfigOut:
    profile = _ensure_profile_exists(db)

    preset = db.query(PersonaPreset).filter(PersonaPreset.is_default == True).first()

    raw_rules = preset.style_rules if preset else profile.style_rules

    try:
        style_rules_json = json.loads(raw_rules)
    except Exception:
        style_rules_json = {"raw": raw_rules}

    languages = [x.strip() for x in profile.main_languages.split(",") if x.strip()]
    strengths = [x.strip() for x in profile.strengths.split(",") if x.strip()]

    return StyleConfigOut(
        profile_id=profile.id,
        display_name=profile.display_name,
        short_bio=profile.short_bio,
        speaking_style=profile.speaking_style,
        languages=languages,
        strengths=strengths,
        default_mode=profile.default_mode,
        style_rules_json=style_rules_json,
        active_preset_code=preset.code if preset else None
    )


router = APIRouter(prefix="/personality", tags=["Personality Engine"])


@router.get("/profile", response_model=PersonalityProfileOut)
def api_get_profile(db: Session = Depends(get_db)):
    profile = get_profile(db)
    return profile


@router.put("/profile", response_model=PersonalityProfileOut)
def api_update_profile(
    payload: PersonalityProfileUpdate,
    db: Session = Depends(get_db)
):
    profile = update_profile(db, payload)
    return profile


@router.get("/presets", response_model=list[PersonaPresetOut])
def api_list_presets(db: Session = Depends(get_db)):
    presets = list_presets(db)
    return presets


@router.post(
    "/presets",
    response_model=PersonaPresetOut,
    status_code=status.HTTP_201_CREATED,
)
def api_create_preset(
    payload: PersonaPresetCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(PersonaPreset).filter(PersonaPreset.code == payload.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu code bilan preset allaqachon mavjud."
        )
    preset = create_preset(db, payload)
    return preset


@router.put("/presets/{preset_id}", response_model=PersonaPresetOut)
def api_update_preset(
    preset_id: int,
    payload: PersonaPresetUpdate,
    db: Session = Depends(get_db)
):
    preset = update_preset(db, preset_id, payload)
    if not preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset topilmadi.")
    return preset


@router.delete("/presets/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_preset(
    preset_id: int,
    db: Session = Depends(get_db)
):
    ok = delete_preset(db, preset_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset topilmadi.")
    return


@router.get("/style-config", response_model=StyleConfigOut)
def api_get_style_config(db: Session = Depends(get_db)):
    cfg = get_style_config(db)
    return cfg
