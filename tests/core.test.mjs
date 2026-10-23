import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { emptyState, cleanState, escapeHTML, reportErrors, makeReport, canPublishClaim } from '../dist/core.js';
const catalog=JSON.parse(fs.readFileSync(new URL('../dist/data/catalog.json',import.meta.url),'utf8'));
test('unreviewed catalog cannot pass publication gate',()=>{
  for(const c of catalog.claims)assert.equal(canPublishClaim(c,catalog.evidence,catalog.reviews),false);
});
test('stale approval cannot approve a changed claim',()=>{
  const c={...catalog.claims[0],review_status:'approved',review_ids:['r1']};
  const review={id:'r1',claim_id:c.id,claim_version:'old',decision:'approve',reviewer_id:'reviewer-1',reviewed_at:'2026-10-23'};
  assert.equal(canPublishClaim(c,catalog.evidence,[review]),false);
  review.claim_version=c.version;
  assert.equal(canPublishClaim(c,catalog.evidence,[review]),true);
  assert.equal(canPublishClaim(c,[],[review]),false);
});
test('report requires two completed activities and explicit comparison, questions, action',()=>{
  const state=emptyState();assert.ok(reportErrors(state).length>0);
  assert.throws(()=>makeReport(state,catalog));
  state.selected=['analyst'];state.notes.analyst={work:'done'};state.comparison='difference';state.questions='question';state.action='next';
  assert.ok(reportErrors(state).some(e=>e.includes('두 개')));
});
test('report snapshots preserve evidence and notes when draft or catalog changes',()=>{
  const state=emptyState();for(const id of state.selected)state.notes[id]={work:'my work',interest:'interest',burden:'unknown'};
  state.comparison='difference';state.questions='question';state.action='interview';
  const copy=structuredClone(catalog);const report=makeReport(state,copy,'2026-10-23T00:00:00Z');
  state.notes.analyst.work='changed';copy.claims[0].statement='edited';copy.sources[0].title='edited source';
  assert.equal(report.occupations[0].notes.work,'my work');
  assert.notEqual(report.occupations[0].claims[0].statement,'edited');
  assert.notEqual(report.occupations[0].claims[0].evidence[0].source.title,'edited source');
});
test('invalid persisted inputs are filtered and HTML is escaped',()=>{
  const state=cleanState({selected:['bad','analyst','analyst'],notes:{analyst:{work:'<script>attack</script>'}},comparison:45,report:{occupations:null}},catalog);
  assert.deepEqual(state.selected,['analyst']);assert.equal(state.comparison,'');assert.equal(state.report,null);
  assert.equal(escapeHTML(state.notes.analyst.work),'&lt;script&gt;attack&lt;/script&gt;');
  assert.equal(escapeHTML('"&\''),'&quot;&amp;&#39;');
});
