"""
Database Enums Module
All enumeration types used across the database
"""
import enum


class MessageSource(enum.Enum):
    """Message source tracking"""
    AD = "Ad"  # من إعلان
    COMMENT = "Comment"  # من كومنت
    EXISTING_CUSTOMER = "Existing Customer"  # عميل قديم
    DIRECT_MESSAGE = "Direct Message"  # رسالة مباشرة
    REFERRAL = "Referral"  # إحالة


class PostType(enum.Enum):
    """Post type classification"""
    PRODUCT_POST = "Product Post"  # بوست منتج
    OFFER_POST = "Offer Post"  # بوست عرض
    PROMOTION_POST = "Promotion Post"  # بوست ترويجي
    GENERAL_POST = "General Post"  # بوست عام


class LeadStage(enum.Enum):
    """Lead progression stages"""
    INTAKE = "Intake"
    QUALIFIED = "Qualified"
    HOT = "Hot"
    IN_PROGRESS = "In-Progress"
    CONVERTED = "Converted"


class CustomerLabel(enum.Enum):
    """Customer classification labels"""
    JUMLA = "جمله"  # Wholesale
    QITAEI = "قطاعي"  # Retail
    NEW_CUSTOMER = "New Customer"
    AL_MUHAFAZA = "المحافظه"  # Governorate


class CustomerType(enum.Enum):
    """Customer behavioral types"""
    LEAD = "Lead"  # Lead/Prospect
    SCARCITY_BUYER = "عميل الندرة"  # The Scarcity Buyer
    EMOTIONAL_BUYER = "عميل العاطفة"  # The Emotional Buyer
    VALUE_SEEKER = "عميل القيمة"  # The Value Seeker
    LOYAL_BUYER = "عميل الولاء"  # The Loyal Buyer
    LOGICAL_BUYER = "عميل المنطق"  # The Logical Buyer
    BARGAIN_HUNTER = "عميل التوفير"  # The Bargain Hunter
    HESITANT_BUYER = "عميل التردد"  # The Hesitant Buyer


class Governorate(enum.Enum):
    """Egypt governorates"""
    CAIRO = "Cairo"
    ALEXANDRIA = "Alexandria"
    GIZA = "Giza"
    SHUBRA_EL_KHEIMA = "Shubra El Kheima"
    PORT_SAID = "Port Said"
    SUEZ = "Suez"
    LUXOR = "Luxor"
    MANSOURA = "Mansoura"
    EL_MAHALLA_EL_KUBRA = "El Mahalla El Kubra"
    TANTA = "Tanta"
    ASYUT = "Asyut"
    ISMAILIA = "Ismailia"
    FAYYUM = "Fayyum"
    ZAGAZIG = "Zagazig"
    ASWAN = "Aswan"
    DAMIETTA = "Damietta"
    MINYA = "Minya"
    BENI_SUEF = "Beni Suef"
    QENA = "Qena"
    SOHAAG = "Sohaag"
    HURGHADA = "Hurghada"
    SIXTH_OF_OCTOBER = "6th of October"
    SHEBIN_EL_KOM = "Shebin El Kom"
    SHIBIN_EL_QANATER = "Shibin El Qanater"
    BANHA = "Banha"
    KAFR_EL_SHEIKH = "Kafr El Sheikh"
    ARISH = "Arish"
    MALLAWI = "Mallawi"
    DESOUK = "Desouk"
    QALYUB = "Qalyub"
    ABU_KABIR = "Abu Kabir"
    GIRGA = "Girga"
    AKHMIM = "Akhmim"
    MATAREYA = "Matareya"


class MessageDirection(enum.Enum):
    """Message direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageStatus(enum.Enum):
    """Message delivery status"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
