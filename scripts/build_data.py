"""Build the explicitly unreviewed pilot dataset. No network or paid API calls."""
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist' / 'data'
OUT.mkdir(parents=True, exist_ok=True)
DATE = '2026-10-23'
VERSION = 'pilot-0.1.0'

sources = [
    {'id': 'onet-bi', 'title': 'O*NET Business Intelligence Analysts', 'url': 'https://www.onetonline.org/link/summary/15-2051.01', 'kind': 'occupational_reference', 'region': 'US', 'source_occupation_code': '15-2051.01'},
    {'id': 'onet-dw', 'title': 'O*NET Data Warehousing Specialists', 'url': 'https://www.onetonline.org/link/summary/15-1243.01', 'kind': 'occupational_reference', 'region': 'US', 'source_occupation_code': '15-1243.01'},
    {'id': 'onet-mr', 'title': 'O*NET Market Research Analysts and Marketing Specialists', 'url': 'https://www.onetonline.org/link/summary/13-1161.00', 'kind': 'occupational_reference', 'region': 'US', 'source_occupation_code': '13-1161.00'},
]
for s in sources:
    s.update(retrieved_at=DATE, published_at=None, updated_year=2026,
             limitation='미국 직업 분류의 참고 자료입니다. 국내 직업과의 대응은 잠정적이며 국내 채용 수요나 보편적인 근무 조건을 입증하지 않습니다.',
             storage_policy='짧은 발췌와 자체 요약만 저장. 원문 전체를 재배포하지 않음.')

specs = [
    ('analyst', '데이터 분석가', '데이터로 문제를 해석하고 판단을 돕는 일', ['문제 해석', '결과 전달'], 'onet-bi', 'BI 분석가 업무의 일부를 데이터 분석가 탐색에 참고. 직업 전체의 일대일 대응은 아님.', [
        ('업무', '업무·재무·경제 데이터를 정리한 보고서를 작성한다.', 'Generate standard or custom reports summarizing business, financial, or economic data'),
        ('업무', 'BI 도구와 대시보드 등의 정보를 유지·갱신한다.', 'Maintain or update business intelligence tools, databases, dashboards, systems, or methods.')
    ], {
        'title': '주문은 늘었는데, 왜 매출은 줄었을까?',
        'context': '가상의 온라인 상점입니다. 지난주 주문은 100건, 매출은 500만 원입니다. 이번 주 주문은 120건, 매출은 480만 원입니다. 팀은 원인을 알고 싶어 합니다.',
        'steps': ['주문 수와 매출만으로 확인할 수 있는 사실을 적습니다.', '객단가를 계산하고, 원인으로 단정할 수 없는 부분을 구분합니다.', '추가로 필요한 데이터 두 가지와 팀에 설명할 문장 한 개를 씁니다.'],
        'deliverable': '관찰 사실·가설·추가 질문을 구분한 짧은 분석 메모',
        'reflection': '답이 정해지지 않은 문제를 정리하고, 설명하는 과정은 어땠나요?',
        'next_steps': ['공개 표 데이터로 관찰 사실과 가설을 나누는 메모 작성', '현직자에게 분석 결과가 실제 결정에 쓰인 사례 질문']
    }),
    ('engineer', '데이터 엔지니어', '데이터가 정확하게 흐를 수 있도록 만드는 일', ['데이터 흐름', '품질 확인'], 'onet-dw', '데이터웨어하우징 업무를 중심으로 한 참고. 데이터 엔지니어의 모든 역할을 포함하지 않음.', [
        ('업무', '데이터 수집·적재·변환·추출의 처리 모델을 설계한다.', 'Develop data warehouse process models, including sourcing, loading, transformation, and extraction.'),
        ('업무', '저장된 데이터의 구조·정확성·품질을 점검한다.', 'Verify the structure, accuracy, or quality of warehouse data.')
    ], {
        'title': '같은 주문이 두 번 들어온다면?',
        'context': '가상의 주문 자료입니다. A 파일에는 주문 101·102가, B 파일에는 주문 102·103이 있습니다. B 파일은 하루 늦게 도착했고 일부 날짜는 서로 다른 형식입니다.',
        'steps': ['주문을 중복 없이 합칠 기준을 정합니다.', '날짜가 다르거나 누락된 경우의 처리 규칙을 씁니다.', '새 파일이 내일 다시 도착했을 때 확인할 점을 적습니다.'],
        'deliverable': '데이터 통합 규칙과 품질 확인 목록',
        'reflection': '눈에 잘 보이지 않는 오류를 예방하고 규칙을 세우는 과정은 어땠나요?',
        'next_steps': ['두 개의 작은 표를 합치는 규칙을 문서화', '현직자에게 데이터 오류 발견과 대응 과정 질문']
    }),
    ('researcher', '시장조사 분석가', '고객과 시장을 조사해 선택의 근거를 만드는 일', ['시장 조사', '효과 확인'], 'onet-mr', '미국 시장조사·마케팅 전문직 분류의 일부 업무를 참고. 국내 산업별 범위 확인 필요.', [
        ('업무', '경쟁사와 가격·판매 관련 자료를 수집하고 분석한다.', 'Gather data on competitors and analyze their prices, sales'),
        ('업무', '마케팅·광고·커뮤니케이션 활동의 효과를 평가한다.', 'Measure the effectiveness of marketing, advertising, and communications programs and strategies.')
    ], {
        'title': '설문 응답만으로 신제품을 출시해도 될까?',
        'context': '가상의 동아리 상품입니다. 기존 구매자 20명에게 설문을 했고 16명이 신제품에 관심을 보였습니다. 운영팀은 전체 학생에게 판매할지 고민합니다.',
        'steps': ['이 설문이 설명하는 대상과 설명하지 못하는 대상을 구분합니다.', '출시 판단 전에 더 알아볼 질문 두 가지를 만듭니다.', '추가 조사 대상과 조사 방법을 제안합니다.'],
        'deliverable': '조사 범위의 한계와 추가 조사 계획',
        'reflection': '사람의 응답과 실제 행동의 차이를 생각해 보는 과정은 어땠나요?',
        'next_steps': ['서로 다른 응답자 집단을 고려한 설문 초안 작성', '현직자에게 조사 결과가 제품 결정에 쓰인 과정 질문']
    }),
]
claims, evidence, occupations = [], [], []
for oid, name, subtitle, tags, sid, mapping, items, scenario in specs:
    cids = []
    for n, (kind, statement, excerpt) in enumerate(items, 1):
        eid, cid = f'{oid}-e{n}', f'{oid}-c{n}'
        evidence.append({'id': eid, 'source_id': sid, 'locator': 'Tasks', 'excerpt': excerpt, 'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(), 'retrieved_at': DATE})
        claims.append({'id': cid, 'occupation_id': oid, 'category': kind, 'statement': statement, 'scope': '미국 참고 직업의 업무 설명', 'evidence_ids': [eid], 'review_status': 'pending', 'review_ids': [], 'confidence': None, 'frequency': None, 'version': VERSION})
        cids.append(cid)
    scenario.update(kind='authored_exercise', expert_review_status='pending', duration_minutes=15, measures_aptitude=False)
    occupations.append({'id': oid, 'name': name, 'subtitle': subtitle, 'tags': tags, 'mapping_note': mapping,
                        'source_id': sid, 'claim_ids': cids, 'version': VERSION, 'status': 'pilot_only',
                        'scenario': scenario, 'unknowns': ['국내 산업·경력별 업무 비중', '자율성·반복성·협업 방식', '만족 요인과 부담 요인의 대표성', '국내 도구·자격·채용 요구 수준']})

data = {'schema_version': '1.0', 'release': {'version': VERSION, 'created_at': DATE, 'status': 'prototype', 'expert_review_completed': False, 'public_information_release_allowed': False},
        'sources': sources, 'evidence': evidence, 'claims': claims, 'occupations': occupations, 'reviews': []}
(OUT / 'catalog.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

# Carry forward existing work without turning inherited counts into established market facts.
legacy_root = Path(r'C:\Users\user\AppData\Local\Temp\job-roadmap-analysis-20261023')
legacy_files = [p for p in legacy_root.rglob('공통요구역량.md') if p.stat().st_size > 1500]
legacy = {'status': 'quarantined', 'reason': '원문 URL·문서 집합과 집계 과정을 재검증하기 전에는 국내 채용 중요도나 비율로 표시하지 않음.', 'records': []}
for path in legacy_files:
    content = path.read_text(encoding='utf-8')
    relative = path.relative_to(legacy_root).as_posix()
    legacy['records'].append({'source_id': 'legacy-repo-competencies', 'url': 'https://github.com/seominse/job-roadmap-service/blob/e4e26b9802144d836c28b821573ad1efbba74402/' + quote(relative, safe='/'),
                              'commit': 'e4e26b9802144d836c28b821573ad1efbba74402', 'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                              'source_kind': 'derived_analysis', 'retrieved_at': DATE, 'original_document_ids': None,
                              'legacy_counts': [{'label': line.split('|')[1].strip(), 'reported_document_count': int(line.split('|')[2].strip()), 'verified_document_count': None}
                                                for line in content.splitlines() if line.startswith('|') and len(line.split('|')) > 3 and line.split('|')[2].strip().isdigit()]})
(OUT / 'legacy-audit.json').write_text(json.dumps(legacy, ensure_ascii=False, indent=2), encoding='utf-8')

with (OUT / 'expert-review.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['claim_id', '직업', '검토할 문장', '적용 범위', '근거 URL', '검토자 ID', '산업', '역할', '관련 경력 연수', '판정 정확 수정필요 범위제한 판단불가', '수정안', '수정 근거', '누락 내용', '검토일', '반영 여부', '반영 책임자'])
    for c in claims:
        o = next(o for o in occupations if o['id'] == c['occupation_id'])
        s = next(s for s in sources if s['id'] == o['source_id'])
        w.writerow([c['id'], o['name'], c['statement'], c['scope'], s['url']] + [''] * 11)
with (OUT / 'pilot-measurement.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['익명 참여 ID', '실시일', '조건 현재방식 서비스', '과제 ID', '직업 자료 버전', '상담 준비 분', '추가 조사 분', '업무 구분 0부터2', '근거와한계 0부터2', '다음행동구체성 0부터2', '오류 수정 건', '활동 완료 여부', '후속 행동 확인일', '후속 행동 여부', '평가자 ID', '비고'])
    w.writerow([''] * 16)
print(f'Built {len(occupations)} occupations, {len(claims)} claims, {len(legacy["records"])} quarantined source files.')
