export const STORE_KEY = 'job-roadmap-pilot-v1';
export const emptyState = () => ({ selected: ['analyst', 'engineer'], notes: {}, comparison: '', questions: '', action: '', due: '', feedback: '', report: null });
export function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
export function cleanState(raw, catalog) {
  const state = emptyState();
  const ids = new Set(catalog.occupations.map(x => x.id));
  if (!raw || typeof raw !== 'object') return state;
  if (Array.isArray(raw.selected)) state.selected = [...new Set(raw.selected.filter(id => ids.has(id)))].slice(0, 3);
  for (const key of ['comparison', 'questions', 'action', 'due', 'feedback']) if (typeof raw[key] === 'string') state[key] = raw[key].slice(0, 10000);
  for (const id of ids) {
    const n = raw.notes?.[id];
    if (n && typeof n === 'object') state.notes[id] = Object.fromEntries(['work', 'interest', 'burden'].map(k => [k, typeof n[k] === 'string' ? n[k].slice(0, 10000) : '']));
  }
  // Rebuild source links from the trusted catalog for this release, never from local storage.
  if (raw.report && raw.report.catalog_version === catalog.release.version && Array.isArray(raw.report.occupations)
      && raw.report.occupations.every(o => ids.has(o.id) && typeof o.name === 'string' && typeof o.version === 'string' && o.notes && ['work','interest','burden'].every(k => typeof o.notes[k] === 'string'))
      && ['created_at','comparison','questions','action','due','feedback'].every(k => typeof raw.report[k] === 'string')) {
    const snapshotState = cleanState({
      selected: raw.report.occupations.map(o => o.id),
      notes: Object.fromEntries(raw.report.occupations.map(o => [o.id, o.notes])),
      comparison: raw.report.comparison, questions: raw.report.questions,
      action: raw.report.action, due: raw.report.due, feedback: raw.report.feedback
    }, catalog);
    if (reportErrors(snapshotState).length === 0 && !Number.isNaN(Date.parse(raw.report.created_at))) {
      state.report = makeReport(snapshotState, catalog, raw.report.created_at);
    }
  }
  return state;
}
export function reportErrors(state) {
  const errors = [];
  if (state.selected.length < 2) errors.push('비교할 직업을 두 개 이상 선택해 주세요.');
  for (const id of state.selected) if (!state.notes[id]?.work?.trim()) errors.push('선택한 직업마다 탐색 활동 기록을 작성해 주세요.');
  if (!state.comparison.trim()) errors.push('직업을 비교하며 알게 된 차이를 작성해 주세요.');
  if (!state.questions.trim()) errors.push('상담에서 확인하고 싶은 질문을 작성해 주세요.');
  if (!state.action.trim()) errors.push('다음에 실행할 행동을 작성해 주세요.');
  return [...new Set(errors)];
}
export function makeReport(state, catalog, now = new Date().toISOString()) {
  const errors = reportErrors(state);
  if (errors.length) throw new Error(errors.join(' '));
  return structuredClone({ created_at: now, catalog_version: catalog.release.version, status: 'student_draft',
    content_review_status: 'pending', occupations: state.selected.map(id => {
      const o = catalog.occupations.find(o => o.id === id);
      return {id, name: o.name, version: o.version, notes: {work: state.notes[id]?.work || '', interest: state.notes[id]?.interest || '', burden: state.notes[id]?.burden || ''},
        claims: catalog.claims.filter(c => o.claim_ids.includes(c.id)).map(c => ({id:c.id, statement:c.statement, scope:c.scope, version:c.version, review_status:c.review_status,
          evidence: c.evidence_ids.map(eid => {const e=catalog.evidence.find(e=>e.id===eid);return {...e,source:catalog.sources.find(s=>s.id===e.source_id)};})}))};
    }), comparison: state.comparison, questions: state.questions, action: state.action, due: state.due, feedback: state.feedback });
}
export function canPublishClaim(claim, evidence, reviews) {
  return claim.review_status === 'approved' && claim.evidence_ids.length > 0
    && claim.evidence_ids.every(id => evidence.some(e => e.id === id && e.source_id && e.excerpt))
    && claim.review_ids.some(id => reviews.some(r => r.id === id && r.claim_id === claim.id && r.claim_version === claim.version && r.decision === 'approve' && r.reviewer_id && r.reviewed_at));
}
