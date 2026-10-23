// Run against an owned, headless browser with a dedicated profile and CDP port 9227.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const targets=await fetch('http://127.0.0.1:9227/json/list').then(r=>r.json());
const target=targets.find(t=>t.type==='page');
const ws=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true});});
let sequence=0;const pending=new Map();const errors=[];
ws.addEventListener('message',event=>{const message=JSON.parse(event.data);if(message.id){const p=pending.get(message.id);pending.delete(message.id);message.error?p?.reject(message.error):p?.resolve(message.result);}else if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text);});
function send(method,params={}) {return new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(JSON.stringify(result.exceptionDetails));return result.result.value;}
async function until(expression){for(let i=0;i<60;i++){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,100));}throw new Error('Timed out: '+expression);}
async function route(hash){await evaluate(`location.hash=${JSON.stringify(hash)}`);await new Promise(r=>setTimeout(r,100));}
async function fill(selector,value){await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});if(!el)throw Error('Missing field');el.value=${JSON.stringify(value)};el.dispatchEvent(new Event('input',{bubbles:true}));})()`);}
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);}
try {
  await send('Runtime.enable');await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:'http://127.0.0.1:8765/'});
  await until("document.querySelectorAll('.card').length===3");
  await evaluate('localStorage.clear()');
  await fs.mkdir('artifacts',{recursive:true});
  const home=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});await fs.writeFile('artifacts/desktop.png',Buffer.from(home.data,'base64'));
  await fill('#search','시장');assert.equal(await evaluate("document.querySelectorAll('.card').length"),1);
  await fill('#search','');assert.equal(await evaluate("document.querySelectorAll('.card').length"),3);
  await route('job/analyst');assert.equal(await evaluate("document.querySelectorAll('.evidence').length"),2);
  await route('compare');assert.equal(await evaluate("document.querySelectorAll('thead th').length"),3);
  await route('notebook/analyst');await click('#create-report');assert.equal(await evaluate('location.hash'),'#notebook/analyst');
  await fill('[data-field="notes.analyst.work"]','주문당 매출이 감소했다. 원인은 추가 확인이 필요하다. <script>window.bad=true</script>');
  await fill('[data-field="notes.analyst.interest"]','관찰과 가설을 나누는 일이 흥미롭다.');
  await route('notebook/engineer');await fill('[data-field="notes.engineer.work"]','주문 번호로 중복을 확인하고 날짜 형식을 통일한다.');
  await fill('[data-field="comparison"]','결과를 해석하는 일과 데이터가 모이는 규칙을 만드는 일의 차이를 보았다.');
  await fill('[data-field="questions"]','산업마다 반복 업무와 협업 비중은 어떻게 달라지는가?');
  await fill('[data-field="action"]','현직자에게 실제 협업 사례를 질문한다.');
  await click('#persist');await click('#create-report');await until("location.hash==='#report'");
  assert.ok(await evaluate("document.body.innerText.includes('주문당 매출이 감소했다')"));
  assert.equal(await evaluate('window.bad===true'),false);
  await fill('[data-field="feedback"]','조건별 차이를 확인하는 질문을 추가해 보세요.');await click('#save-feedback');
  assert.ok(await evaluate("document.querySelector('#feedback-display').innerText.includes('조건별')"));
  await send('Page.reload');await until("document.querySelector('#feedback-display')!==null");
  assert.ok(await evaluate("document.querySelector('#feedback-display').innerText.includes('조건별')"));
  await route('notebook/analyst');await fill('[data-field="notes.analyst.work"]','수정한 활동 기록');await route('report');
  assert.ok(await evaluate("document.body.innerText.includes('주문당 매출이 감소했다')"));
  assert.equal(await evaluate("document.body.innerText.includes('수정한 활동 기록')"),false);
  await send('Page.printToPDF',{printBackground:true,preferCSSPageSize:true}).then(r=>fs.writeFile('artifacts/report.pdf',Buffer.from(r.data,'base64')));
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await route('explore');assert.equal(await evaluate('document.documentElement.scrollWidth<=window.innerWidth'),true);
  const mobile=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});await fs.writeFile('artifacts/mobile.png',Buffer.from(mobile.data,'base64'));
  await route('compare');assert.equal(await evaluate('document.documentElement.scrollWidth<=window.innerWidth'),true);
  await send('Page.navigate',{url:'http://127.0.0.1:8765/kit.html'});await until("document.querySelector('#delivery')!==null");
  assert.equal(await evaluate('document.documentElement.scrollWidth<=window.innerWidth'),true);
  for(const path of ['data/expert-review.csv','data/pilot-measurement.csv','data/catalog.json','data/catalog.schema.json'])assert.equal((await fetch('http://127.0.0.1:8765/'+path)).status,200);
  assert.deepEqual(errors,[]);
  await evaluate('localStorage.clear()');
  console.log('PASS: desktop/mobile, search, comparison, required fields, notes, snapshot, persistence, feedback, safe text, PDF, downloads, no browser exceptions.');
} finally {await send('Browser.close').catch(()=>{});ws.close();}
