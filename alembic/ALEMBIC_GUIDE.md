# 🔧 Alembic 마이그레이션 가이드

## 📝 Alembic이란?
Alembic은 SQLAlchemy용 데이터베이스 마이그레이션 도구입니다.
데이터베이스 스키마 변경 이력을 관리하고, 버전 관리를 할 수 있습니다.

---

## 🚀 기본 사용법

### 1️⃣ 첫 마이그레이션 생성 (최초 1회)

```bash
# 현재 모델 기반으로 마이그레이션 파일 생성
alembic revision --autogenerate -m "Initial migration: create all tables"
```

**생성되는 파일**: `alembic/versions/XXXX_initial_migration_create_all_tables.py`

이 파일에는 다음 테이블들이 자동으로 생성됩니다:
- cattle (소 기본 정보)
- breeding_records (수정 기록)
- cattle_notes (특이사항)
- event_logs (이벤트 로그)
- statistics (통계)

---

### 2️⃣ 마이그레이션 실행

```bash
# 데이터베이스에 마이그레이션 적용
alembic upgrade head
```

✅ 성공 시: `INFO  [alembic.runtime.migration] Running upgrade -> xxxxx, Initial migration`

---

### 3️⃣ 마이그레이션 확인

```bash
# 현재 마이그레이션 상태 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history

# 대기 중인 마이그레이션 확인
alembic history --verbose
```

---

## 🔄 모델 변경 시 워크플로우

### 시나리오: Cattle 모델에 새 컬럼 추가

**1단계: 모델 수정**
```python
# app/models/cattle.py
class Cattle(Base, TimestampMixin):
    # ... 기존 코드 ...
    weight = Column(Float, nullable=True)  # 새 컬럼 추가!
```

**2단계: 마이그레이션 파일 생성**
```bash
alembic revision --autogenerate -m "Add weight column to cattle"
```

**3단계: 마이그레이션 파일 확인**
`alembic/versions/XXXX_add_weight_column_to_cattle.py` 파일을 열어서 내용 확인:

```python
def upgrade() -> None:
    op.add_column('cattle', sa.Column('weight', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('cattle', 'weight')
```

**4단계: 마이그레이션 적용**
```bash
alembic upgrade head
```

---

## ⏪ 롤백 (되돌리기)

### 한 단계 롤백
```bash
alembic downgrade -1
```

### 특정 버전으로 롤백
```bash
alembic downgrade <revision_id>
```

### 처음으로 롤백 (모든 테이블 삭제)
```bash
alembic downgrade base
```

---

## 🔍 주요 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `alembic revision --autogenerate -m "메시지"` | 자동으로 마이그레이션 파일 생성 |
| `alembic upgrade head` | 최신 버전으로 업그레이드 |
| `alembic downgrade -1` | 한 단계 롤백 |
| `alembic current` | 현재 버전 확인 |
| `alembic history` | 마이그레이션 히스토리 |
| `alembic downgrade base` | 모든 마이그레이션 롤백 |

---

## 🎯 실습: 지금 바로 해보기!

### Step 1: 첫 마이그레이션 생성
```bash
alembic revision --autogenerate -m "Initial migration: create all tables"
```

### Step 2: 생성된 파일 확인
`alembic/versions/` 폴더에 파일이 생성되었는지 확인

### Step 3: 데이터베이스에 적용
```bash
alembic upgrade head
```

### Step 4: PostgreSQL에서 확인
```sql
-- PostgreSQL에 접속해서 확인
\dt  -- 테이블 목록 확인

-- 테이블 구조 확인
\d cattle
\d breeding_records
```

---

## ⚠️ 주의사항

### 1. 모델 변경 후 반드시 마이그레이션 생성!
```bash
# 모델 수정 → 마이그레이션 생성 → 적용
alembic revision --autogenerate -m "변경 내용"
alembic upgrade head
```

### 2. 프로덕션에서는 조심히!
- 마이그레이션 파일을 항상 먼저 확인
- 백업 후 적용
- 롤백 계획 준비

### 3. autogenerate 한계
자동 감지 못 하는 것들:
- 테이블명 변경
- 컬럼명 변경
- 제약조건 일부 변경

이런 경우 수동으로 마이그레이션 파일 수정 필요!

---

## 🆘 트러블슈팅

### 문제 1: "Target database is not up to date"
```bash
# 해결: 최신 버전으로 업그레이드
alembic upgrade head
```

### 문제 2: 마이그레이션 충돌
```bash
# 해결: 현재 상태 확인 후 수동 조정
alembic current
alembic history
```

### 문제 3: 처음부터 다시 시작하고 싶을 때
```bash
# 1. 모든 마이그레이션 롤백
alembic downgrade base

# 2. versions 폴더의 파일 모두 삭제
rm alembic/versions/*.py

# 3. 처음부터 다시 시작
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## 📚 더 알아보기

공식 문서: https://alembic.sqlalchemy.org/

---

## ✅ 체크리스트

- [ ] Alembic 설치 확인 (`pip install alembic`)
- [ ] `.env` 파일에 DATABASE_URL 설정 확인
- [ ] 모든 모델이 `app/models/__init__.py`에 import 되어 있는지 확인
- [ ] `alembic revision --autogenerate` 실행
- [ ] 생성된 마이그레이션 파일 확인
- [ ] `alembic upgrade head` 실행
- [ ] PostgreSQL에서 테이블 생성 확인

---

🎉 **이제 Phase 2 완료!** 다음은 Repository와 Service 계층 구현입니다!
