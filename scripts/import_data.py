import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
import pandas as pd
from datetime import datetime

from app.database import SessionLocal
from app.models.cattle import Cattle
from app.models.cattle_note import CattleNote
from app.models.cattle import GenderEnum, StatusEnum


EXCEL_PATH = "cattle.xls"


def clean_id(v):
    if pd.isna(v):
        return None
    return str(v).strip()


def parse_date(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    # yy.mm.dd 형식 (예: 25.11.24)
    try:
        return datetime.strptime(s, "%y.%m.%d").date()
    except ValueError:
        pass
    # 그 외 형식은 pandas에 위임
    return pd.to_datetime(s).date()


def parse_gender(v):
    if not v:
        return None

    v = str(v).strip()

    if v in ["수", "수컷", "MALE"]:
        return GenderEnum.MALE

    if v in ["암", "암컷", "FEMALE"]:
        return GenderEnum.FEMALE

    if "프리마틴" in v:
        return GenderEnum.FREEMARTIN

    print("Unknown gender:", v)
    return None


def parse_status(v):
    if not v:
        return StatusEnum.ACTIVE

    v = str(v).strip()

    if "사육" in v:
        return StatusEnum.ACTIVE

    if "출하" in v:
        return StatusEnum.SOLD

    if "폐사" in v:
        return StatusEnum.DECEASED

    print("Unknown status:", v)
    return StatusEnum.ACTIVE


def main():
    db = SessionLocal()

    print("=== 기존 데이터 삭제 ===")
    deleted = db.query(CattleNote).delete()
    deleted = db.query(Cattle).delete()
    db.commit()
    print(f"cattle {deleted}건 삭제 완료")

    df = pd.read_excel(EXCEL_PATH)

    # 엑셀 컬럼 이름 확인용
    print("Columns:", df.columns)

    cattle_map = {}
    rows = df.to_dict("records")

    print("=== 1단계: cattle 생성 ===")

    for row in rows:

        identification_number = clean_id(row["개체식별번호"])

        cattle = Cattle(
            identification_number=identification_number,
            gender=parse_gender(row["성별"]),
            birth_date=parse_date(row["출생일자"]),
            status=parse_status(row["상태"]),
            father_kpn=clean_id(row.get("KPN")),
            mother_id=None
        )

        db.add(cattle)
        cattle_map[identification_number] = cattle

    db.commit()

    print("cattle insert 완료")

    print("=== 2단계: mother 연결 ===")

    for row in rows:

        child_number = clean_id(row["개체식별번호"])
        mother_number = clean_id(row.get("모개체"))

        if not mother_number:
            continue

        child = db.query(Cattle).filter(
            Cattle.identification_number == child_number
        ).first()

        mother = db.query(Cattle).filter(
            Cattle.identification_number == mother_number
        ).first()

        if mother:
            child.mother_id = mother.id
        else:
            print(f"mother not found: {mother_number}")

    db.commit()

    print("mother 연결 완료")
    print("Import finished!")

    db.close()


if __name__ == "__main__":
    main()