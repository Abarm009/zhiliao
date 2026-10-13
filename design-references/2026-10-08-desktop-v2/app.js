/* Design fixtures only. No API, authentication, storage, or upload implementation. */
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const roles = {
  reporter1:{name:'报修人一', label:'报修人', project:'A', kind:'reporter'},
  tech1:{name:'维修员一', label:'维修人员', project:'A', kind:'tech', skills:['空调维修','给排水维修','照明维修','门禁维修','电气维修']},
  manager:{name:'项目管理员', label:'管理员', project:'A', kind:'manager'},
  reporter2:{name:'报修人二', label:'报修人', project:'B', kind:'reporter'}
};
const statuses = {DRAFT:'草稿',OPEN:'待接单',ACCEPTED:'待预约',SCHEDULED:'已预约',IN_PROGRESS:'维修中',AWAITING_ACCEPTANCE:'待验收',COMPLETED:'已完成',CANCELLED:'已取消'};
const fixtures = [
  {id:'R-0007',title:'东侧会议室空调不制冷',place:'办公楼 3F · 东侧会议室',desc:'空调已开启约半小时，室内温度仍然偏高，会议开始前需要安排检查。',status:'ACCEPTED',category:'空调维修',project:'A',reporter:'reporter1',assignee:'tech1',asset:'AC-001 · 会议室空调',appointment:'2026-10-09 14:00–15:00',proposed:true,updated:'10 分钟前',events:[['今天 09:10','报修人一提交报修'],['今天 09:18','维修员一接单并绑定设备'],['今天 09:25','维修员一提议预约：10 月 9 日 14:00–15:00']],notes:[],files:[]},
  {id:'R-0008',title:'茶水间水槽排水缓慢',place:'办公楼 2F · 茶水间',desc:'水槽排水速度变慢，请检查存水弯与排水管。',status:'IN_PROGRESS',category:'给排水维修',project:'A',reporter:'reporter1',assignee:'tech1',asset:'WS-002 · 茶水间水槽',appointment:'2026-10-08 10:00–11:00',updated:'25 分钟前',events:[['今天 09:00','维修员一开始处理'],['今天 09:20','发现排水管内有异物，正在清理']],notes:['已检查排水管，正在清理异物。'],files:[{name:'排水检查照片',ready:false,detail:'示例附件 · 等待真实证据接入'}]},
  {id:'R-0009',title:'西侧走廊照明闪烁',place:'办公楼 4F · 西侧走廊',desc:'西侧走廊第三盏照明灯持续闪烁，影响通行。',status:'AWAITING_ACCEPTANCE',category:'照明维修',project:'A',reporter:'reporter1',assignee:'tech1',asset:'LT-003 · 走廊照明',appointment:'2026-10-08 09:00–10:00',updated:'40 分钟前',events:[['今天 09:05','维修员一开始处理'],['今天 09:35','更换驱动器并完成通电检查'],['今天 09:40','提交第 1 轮完工，等待独立验收']],notes:['更换驱动器，连续通电检查 15 分钟，照明稳定。'],files:[{name:'更换后照明照片',ready:true,detail:'设计占位 · 无真实图片或上传回执'},{name:'通电检查记录',ready:true,detail:'设计占位 · 无真实文件或上传回执'}]},
  {id:'R-0010',title:'大厅自动门开合异响',place:'办公楼 1F · 南侧大厅',desc:'自动门开启时出现异响，请安排维修。',status:'OPEN',category:'门禁维修',project:'A',reporter:'reporter1',assignee:null,asset:null,updated:'1 小时前',events:[['今天 08:40','报修人一提交报修']],notes:[],files:[]},
  {id:'R-0006',title:'打印区插座松动',place:'办公楼 3F · 打印区',desc:'插座面板已重新固定。',status:'COMPLETED',category:'电气维修',project:'A',reporter:'reporter1',assignee:'tech1',asset:'PW-004 · 打印区插座',updated:'昨天',events:[['昨天 16:00','报修人一完成独立验收']],notes:['已重新紧固面板并检查供电。'],files:[]}
];
let tasks, actor='reporter1', selected='R-0007', nav='all', filter='all', tab='overview', favorites={}, modalDirty=false, modalTrigger;
const terminal = t => ['COMPLETED','CANCELLED'].includes(t.status);
const visible = t => t.project===roles[actor].project && (roles[actor].kind==='manager' || t.reporter===actor || roles[actor].kind==='tech' && (t.assignee===actor || t.status==='OPEN' && roles[actor].skills.includes(t.category)));
const canReview = t => ['reporter','manager'].includes(roles[actor].kind) && t.assignee!==actor && t.status==='AWAITING_ACCEPTANCE';
const mine = t => t.assignee===actor;
const todo = t => !terminal(t) && (canReview(t) || t.reporter===actor && (t.status==='DRAFT' || t.proposed) || roles[actor].kind==='tech' && (t.status==='OPEN' || mine(t) && ['ACCEPTED','SCHEDULED','IN_PROGRESS'].includes(t.status)));
const current = () => tasks.find(t => t.id===selected && visible(t));
function toast(msg) { $('#toast').textContent=msg; $('#toast').classList.add('show'); clearTimeout(toast.timer); toast.timer=setTimeout(()=>$('#toast').classList.remove('show'),3500); }
function badge(t) { return `<span class="badge ${terminal(t)?'gray':['ACCEPTED','AWAITING_ACCEPTANCE'].includes(t.status)?'amber':''}">${statuses[t.status]}</span>`; }
function nextLabel(t) {
  if (terminal(t)) return '协作记录已归档';
  if (canReview(t)) return '待你核对维修结果';
  if (t.status==='ACCEPTED' && t.proposed) return t.reporter===actor?'待你确认预约':'等待报修人确认';
  if (mine(t) && t.status==='IN_PROGRESS') return '记录进度，补齐完工证据';
  if (t.status==='SCHEDULED') return '按约到场处理';
  return t.status==='OPEN'?'等待维修人员接单':'查看任务安排';
}
function reset(scene='appointment') {
  clearTimeout(toast.timer); $('#toast').classList.remove('show'); $('#toast').textContent='';
  tasks=structuredClone(fixtures); favorites={}; nav='all'; filter='all'; tab='overview'; $('#search').value='';
  ({appointment:()=>{actor='reporter1';selected='R-0007';}, progress:()=>{actor='tech1';selected='R-0008';}, acceptance:()=>{actor='reporter1';selected='R-0009';}, empty:()=>{actor='reporter2';selected=null;}}[scene] || (()=>{}))();
  $('#scene').value=scene; render();
}
function render() {
  const role=roles[actor], list=tasks.filter(visible), query=$('#search').value.trim().toLowerCase();
  $('#profile-name').textContent=role.name; $('#profile-role').textContent=role.label; $('#avatar').textContent=role.name[0];
  $('.project-label').innerHTML=`项目 ${role.project} <span>/</span> 维修任务`;
  $('.project-note').innerHTML=`<span class="dot"></span> 项目 ${role.project}<small>任务协作工作空间</small>`;
  $('#count-all').textContent=list.length; $('#count-todo').textContent=list.filter(todo).length; $('#count-favorite').textContent=list.filter(t=>favorites[actor]?.includes(t.id)).length;
  $('#list-title').textContent={all:'我的任务',todo:'待我处理',favorite:'收藏任务'}[nav];
  document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('active',b.dataset.nav===nav));
  document.querySelectorAll('[data-filter]').forEach(b=>b.classList.toggle('active',b.dataset.filter===filter));
  const shown=list.filter(t => (nav!=='todo'||todo(t)) && (nav!=='favorite'||favorites[actor]?.includes(t.id)) && (filter==='all'||(filter==='done')===terminal(t)) && `${t.title} ${t.place} ${t.id} ${t.asset||''}`.toLowerCase().includes(query));
  $('#list-count').textContent=`${shown.length} 项任务`; $('#new-task').hidden=role.kind==='tech';
  if (!shown.some(t=>t.id===selected)) selected=shown[0]?.id;
  $('#tasks').innerHTML=shown.length?shown.map(t=>`<button class="task-card ${selected===t.id?'selected':''}" data-task="${t.id}" aria-pressed="${selected===t.id}"><span class="task-top">${badge(t)}<small>${esc(t.updated)}</small></span><h2>${esc(t.title)}</h2><p class="location">${esc(t.place)}</p><p class="next-label">${nextLabel(t)}</p><span class="task-foot"><span>${t.id}</span><span>${t.assignee?esc(roles[t.assignee].name):'尚未接单'}</span></span></button>`).join(''):`<div class="list-empty">${query?'没有匹配的任务':'这里暂无任务'}<small>${query?'尝试问题关键词或任务号':'任务会按当前身份显示'}</small></div>`;
  $('#scope-note').textContent=`项目 ${role.project} · 仅显示当前身份可见任务`;
  const t=current(); $('#action-panel').hidden=!t;
  if (!t) { $('#detail').innerHTML=`<div class="empty"><div class="empty-symbol">${icon('list')}</div><h2>${query?'没有找到匹配任务':'当前没有可见任务'}</h2><p>${query?'调整关键词，或清空搜索查看全部任务。':'你可以新建报修，或在设置中查看其他演示身份。项目之间的任务不会混合显示。'}</p><button class="secondary" data-action="${query?'clear-search':'new'}">${query?'清空搜索':'新建报修'}</button></div>`; return; }
  const stages=['OPEN','ACCEPTED','SCHEDULED','IN_PROGRESS','AWAITING_ACCEPTANCE','COMPLETED'];
  const step=stages.indexOf(t.status);
  $('#detail').innerHTML=`<div class="detail-top"><span>${t.id} <span class="separator">/</span> ${esc(t.category)}</span><div><button class="icon-btn" data-action="star" aria-label="${favorites[actor]?.includes(t.id)?'取消收藏':'收藏任务'}">${icon('star',favorites[actor]?.includes(t.id))}</button>${!terminal(t)&&['reporter','manager'].includes(role.kind)?'<button class="icon-btn" data-action="more" aria-label="更多任务操作">···</button>':''}</div></div><div class="title-row"><h1>${esc(t.title)}</h1>${badge(t)}</div><p class="detail-sub">${esc(t.place)} <span>·</span> ${t.assignee?esc(roles[t.assignee].name)+'负责':'等待安排维修人员'}</p><div class="stepper" aria-label="处理阶段">${['报修','接单','预约','处理','验收','完成'].map((s,i)=>`<div class="step ${i<step?'done':i===step?'current':''}"><span class="step-circle">${i<step?'✓':i+1}</span><p>${s}</p></div>`).join('')}</div><div class="detail-tabs" role="tablist" aria-label="详情视图">${[['overview','任务概览'],['activity','处理记录'],['files',`附件 ${t.files.length}`]].map(([key,name])=>`<button role="tab" data-tab="${key}" aria-selected="${tab===key}" class="${tab===key?'active':''}">${name}</button>`).join('')}</div><div class="tab-content" role="tabpanel">${tab==='overview'?overview(t):tab==='activity'?activity(t):files(t)}</div>`;
  $('#action-panel').innerHTML=actionPanel(t);
}
function dateLabel(value) { const d=new Date(value+'T12:00:00+08:00'); return value+'（'+['周日','周一','周二','周三','周四','周五','周六'][d.getUTCDay()]+'）'; }
function overview(t) {
  const result=t.status==='AWAITING_ACCEPTANCE'||t.status==='COMPLETED';
  const resultCard=result?`<section class="issue"><div class="section-heading"><h2>本轮维修结果</h2><span>设计示例</span></div><div class="quote">${esc(t.notes.at(-1)||'查看处理记录中的维修情况。')}</div><button class="plain" data-action="files">查看示例附件 ${t.files.length} 项 →</button></section>`:'';
  const issue=`<section class="issue"><div class="section-heading"><h2>报修问题</h2><span>${esc(roles[t.reporter].name)}</span></div><div class="quote">${esc(t.desc)}</div><div class="fact-grid"><div class="fact"><small>问题发生空间</small><b>${esc(t.place)}</b><span>维修服务的位置</span></div><div class="fact"><small>关联设备</small><b>${esc(t.asset||'尚未选择设备')}</b><span>${t.asset?'设备定位与问题空间分别记录':'接单后由维修人员确认'}</span></div></div></section>`;
  const progress=t.status==='IN_PROGRESS'?`<section class="issue"><div class="section-heading"><h2>最新处理进度</h2><button class="plain" data-action="activity">完整记录 →</button></div><div class="quote">${esc(t.notes.at(-1)||'尚未记录处理进度。')}</div></section>`:'';
  const appointment=!t.appointment?'':result||t.status==='IN_PROGRESS'?`<div class="appointment compact"><span class="badge">预约已确认</span><p>${esc(dateLabel(t.appointment.slice(0,10)))} ${esc(t.appointment.slice(11))} · 北京时间</p></div>`:`<section class="appointment"><div class="appointment-head"><span>维修预约</span><span class="badge ${t.proposed?'amber':''}">${t.proposed?'待报修人确认':'预约已确认'}</span></div><div class="appointment-date">${esc(dateLabel(t.appointment.slice(0,10)))}<b>${esc(t.appointment.slice(11))}</b></div><div class="appointment-bottom"><span>${esc(roles[t.assignee].name)}到场处理</span><span>北京时间</span></div></section>`;
  return resultCard+issue+progress+appointment+`<section class="recent"><div class="section-heading"><h2>最近动态</h2><button class="plain" data-action="activity">全部记录 →</button></div>${activity(t,3)}</section>`;
}
function activity(t,limit) { return `<ol class="timeline">${[...t.events].reverse().slice(0,limit||100).map(([date,msg])=>`<li><span>${esc(msg)}</span><small>${esc(date)} · 示例事件</small></li>`).join('')}</ol>`; }
function files(t) {
  return `<div class="section-heading"><h2>维修附件</h2><span>${t.files.length} 项</span></div><p class="meta-note">此原型只展示附件状态。验收场景的附件为设计占位，没有真实文件或上传回执。</p>${t.files.length?t.files.map(f=>`<div class="file-card"><div class="file-icon">${icon('file')}</div><div class="file-content"><b>${esc(f.name)}</b><small>${esc(f.detail)}</small></div><span class="badge ${f.ready?'':'amber'}">${f.ready?'就绪样式':'未就绪'}</span></div>`).join(''):'<div class="quiet-block">暂无附件。维修人员可在处理阶段补充维修证据。</div>'}${mine(t)&&t.status==='IN_PROGRESS'?'<button class="secondary" data-action="upload">添加维修证据</button>':''}`;
}
function actionPanel(t) {
  let title='等待下一位协作人',desc='任务状态会随协作进展更新。',primary='',secondary='',hint='';
  const button=(a,label,disabled=false)=>`<button class="primary" data-action="${a}" ${disabled?'disabled':''}>${label}</button>`;
  if(t.status==='DRAFT'&&t.reporter===actor) {title='确认并提交报修';desc='草稿仅保存在本页。确认问题与位置后，提交给维修人员。';primary=button('submit','提交报修');}
  else if(t.status==='OPEN'&&roles[actor].kind==='tech') {title='接下这项维修';desc='确认问题属于你的维修范围后接单，再核对关联设备。';primary=button('take','接下任务');}
  else if(t.status==='OPEN') {title='等待维修人员接单';desc='报修已提交，接单后会显示负责人和预约安排。';}
  else if(t.status==='ACCEPTED'&&t.proposed&&t.reporter===actor) {title='确认到场时间';desc='维修人员已提出预约。确认你可以配合到场；时间不合适可说明原因。';primary=button('confirm','确认维修预约');secondary='<button class="secondary" data-action="reject-time">时间不合适</button>';hint='确认后进入已预约状态；这不会直接开始维修。';}
  else if(t.status==='ACCEPTED'&&t.proposed) {title='等待报修人确认';desc='预约已提出，报修人确认后可按约到场。';}
  else if(t.status==='ACCEPTED'&&mine(t)) {title=t.asset?'安排到场时间':'确认维修设备';desc=t.asset?'与报修人确认到场时间，再按约开始维修。':'先确认实际维修设备，避免把问题空间当作设备安装位置。';primary=button(t.asset?'propose':'asset',t.asset?'提议维修预约':'选择维修设备');}
  else if(t.status==='SCHEDULED') {title='按约到场处理';desc=mine(t)?'到场后开始维修。真实版本必须检查预约时间与当前任务状态。':'预约已确认，等待维修人员按约到场。'; if(mine(t)) {primary=button('start','开始维修',new Date(t.appointment.slice(0,10)+'T'+t.appointment.slice(11,16)+':00+08:00')>new Date());hint='未到预约时间时保持禁用，不通过演示按钮跳过时间校验。';}}
  else if(t.status==='IN_PROGRESS'&&mine(t)) {title='记录处理进展';desc='记录已完成的检查与维修，再补齐可核验的证据。';primary=button('note','记录处理进度');secondary='<button class="secondary" data-action="upload">添加维修证据</button><button class="secondary" data-action="finish" disabled>提交完工</button>';hint='维修证据上传暂不可用，请先保留处理记录；证据可核验后再提交完工。';}
  else if(canReview(t)) {title='由你核对维修结果';desc='结合现场情况与维修证据独立验收。问题仍存在时退回维修人员处理。';primary=button('review','查看并验收');secondary='<button class="secondary" data-action="reject">退回重做</button>';hint='当前验收场景仅用于演示交互，附件是设计占位，点击不会生成真实验收记录。';}
  else if(t.status==='AWAITING_ACCEPTANCE') {title='等待独立验收';desc='维修人员不能验收自己的任务。等待报修人或合规的管理员核对维修结果。';}
  else if(terminal(t)) {title=t.status==='COMPLETED'?'维修已完成':'任务已取消';desc='查看完整协作记录。终态不提供继续处理或退回重做入口。';primary=button('activity','查看完整记录');}
  return `<p class="action-eyebrow">下一步</p><h2>${title}</h2><p class="lead">${desc}</p><div class="action-summary"><div class="summary-row"><span>当前阶段</span><b>${statuses[t.status]}</b></div><div class="summary-row"><span>维修负责人</span><b>${t.assignee?esc(roles[t.assignee].name):'待接单'}</b></div><div class="summary-row"><span>报修人</span><b>${esc(roles[t.reporter].name)}</b></div></div>${primary}${secondary}${hint?`<p class="action-hint">${hint}</p>`:''}${t.status==='IN_PROGRESS'&&mine(t)?'<div class="warning-note"><b>完工提交暂不可用</b><p>缺少可核验的维修证据，暂时不能提交完工。</p><button class="plain" data-action="files">查看附件状态 →</button></div>':''}<div class="quiet-block"><b>协作提示</b><p>预约变更说明原因；完工后由他人验收。处理记录随任务保留。</p></div><div class="quiet-block assistant"><b>AI 辅助</b><p>模型服务未连接，当前可按人工流程继续。接通后再展示真实建议。</p></div>`;
}
function icon(name,filled=false) {
  const paths={list:'<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',clock:'<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/>',star:'<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9Z"/>',settings:'<circle cx="12" cy="12" r="3"/><path d="M5 6h14M5 12h3m8 0h3M5 18h14"/>',file:'<path d="M6 3h8l4 4v14H6V3Z M14 3v5h4 M9 12h6 M9 16h6"/>'};
  return `<svg viewBox="0 0 24 24" width="20" height="20" fill="${filled?'currentColor':'none'}" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.list}</svg>`;
}
function closeModal(force=false) { if(!force&&modalDirty&&!confirm('有尚未保存的内容，确定放弃吗？'))return; $('#modal').close();modalDirty=false;modalTrigger?.focus(); }
function modal(title,body,foot='',submit) {
  modalTrigger=document.activeElement;modalDirty=false;
  $('#modal-content').innerHTML=`<form id="dialog-form" novalidate><div class="modal-head"><h2 id="dialog-title">${title}</h2><button type="button" class="icon-btn" data-close aria-label="关闭面板">×</button></div><div class="modal-body">${body}<p class="field-error" id="form-error" role="alert"></p></div>${foot?`<div class="modal-foot"><button type="button" class="secondary" data-close>返回</button><button class="primary" type="submit">${foot}</button></div>`:''}</form>`;
  if(!$('#modal').open) $('#modal').showModal();
  $('#dialog-form').oninput=()=>modalDirty=true;
  $('#dialog-form').onsubmit=e=>{e.preventDefault();if(submit)submit(new FormData(e.target));};
}
function error(text) { $('#form-error').textContent=text; const field=$('#dialog-form input[type=checkbox]:not(:checked)')||$('#dialog-form textarea')||$('#dialog-form input'); field?.focus(); $('#form-error').scrollIntoView({block:'nearest'}); }
function mutate(t,message,fn) { if(!visible(t)||terminal(t))return toast('当前任务已不可操作。');fn();t.events.push(['刚刚',message]);t.updated='刚刚';closeModal(true);render();toast('原型演示：'+message); }
function reasonDialog(t,title,label,fn) { modal(title,`<div class="review-box"><b>${esc(t.title)}</b><p>${t.id} · ${esc(t.place)}</p></div><label class="form-field"><span>原因 <em>必填</em></span><textarea name="reason" rows="4" placeholder="说明问题与期望调整，方便下一位协作人处理。"></textarea></label>`,label,data=>{const text=String(data.get('reason')).trim();if(!text)return error('请填写原因，内容已保留。');fn(text);}); }
function doAction(action) {
  const t=current();
  if(action==='clear-search') {$('#search').value='';render();return;}
  if(action==='new') {if(roles[actor].kind==='tech')return toast('当前维修身份不提供报修入口。');modal('新建报修',`<p class="meta-note">示例表单 · 保存为本页草稿，未提交到业务服务。</p><label class="form-field"><span>问题描述 <em>必填</em></span><textarea name="problem" rows="4" placeholder="例如：东侧会议室空调已开启，但仍不制冷。"></textarea></label><div class="field-row"><label class="form-field"><span>问题发生空间</span><select name="place"><option>办公楼 3F · 东侧会议室</option><option>办公楼 2F · 茶水间</option></select></label><label class="form-field"><span>维修类别</span><select name="category"><option>空调维修</option><option>给排水维修</option><option>电气维修</option></select></label></div>`,'保存草稿',data=>{const desc=String(data.get('problem')).trim();if(!desc)return error('请填写问题描述。');const item={id:'R-DEMO-'+(tasks.length+1),title:desc.length>22?desc.slice(0,22)+'…':desc,desc,place:data.get('place'),category:data.get('category'),project:roles[actor].project,reporter:actor,assignee:null,status:'DRAFT',updated:'刚刚',events:[['刚刚','创建本页设计草稿']],notes:[],files:[]};tasks.unshift(item);selected=item.id;nav='all';filter='all';$('#search').value='';closeModal(true);render();toast('设计草稿已保存到本页。');});return;}
  if(!t)return;
  if(action==='star') {favorites[actor]??=[];favorites[actor]=favorites[actor].includes(t.id)?favorites[actor].filter(id=>id!==t.id):[...favorites[actor],t.id];render();return;}
  if(action==='activity'||action==='files') {tab=action;render();return;}
  if(action==='submit'&&t.status==='DRAFT'&&t.reporter===actor) {mutate(t,'提交报修',()=>t.status='OPEN');return;}
  if(action==='take'&&t.status==='OPEN'&&roles[actor].kind==='tech'&&roles[actor].skills.includes(t.category)) {mutate(t,roles[actor].name+'接下任务',()=>{t.assignee=actor;t.status='ACCEPTED';});return;}
  if(action==='confirm'&&t.reporter===actor&&t.status==='ACCEPTED'&&t.proposed) {modal('确认维修预约',`<div class="review-box"><b>${esc(t.title)}</b><p>${esc(t.place)}</p></div><div class="appointment"><div class="appointment-head">预约时间 · 北京时间</div><div class="appointment-date">${esc(dateLabel(t.appointment.slice(0,10)))}<b>${esc(t.appointment.slice(11))}</b></div><p>维修负责人：${esc(roles[t.assignee].name)}</p></div><p class="meta-note">确认后，本页示例任务进入已预约；未发送通知或写入真实任务。</p>`,'确认这个时间',()=>mutate(t,'报修人一确认维修预约',()=>{t.status='SCHEDULED';t.proposed=false;}));return;}
  if(action==='reject-time'&&t.reporter===actor&&t.status==='ACCEPTED'&&t.proposed) {reasonDialog(t,'调整维修预约','提交调整原因',reason=>mutate(t,'预约未确认：'+reason,()=>{t.proposed=false;t.appointment=null;}));return;}
  if(action==='note'&&mine(t)&&t.status==='IN_PROGRESS') {modal('记录处理进度',`<div class="review-box"><b>${esc(t.title)}</b><p>记录检查结论、已做处理和剩余问题。</p></div><label class="form-field"><span>处理内容 <em>必填</em></span><textarea name="note" rows="5" placeholder="例如：已清理排水管内异物，正在进行排水测试。"></textarea></label>`,'保存进度',data=>{const note=String(data.get('note')).trim();if(!note)return error('请填写处理内容。');mutate(t,'新增维修进度：'+note,()=>t.notes.push(note));});return;}
  if(action==='upload') {modal('维修证据尚未接通','<div class="warning-note"><b>此原型不提供真实上传</b><p>原生版本需接入文件选择、附件保存、证据校验及回执后，才能显示就绪状态。</p></div><p>你可以继续记录处理进度。不要把示例占位附件当作上传成功。</p>');return;}
  if(action==='review'&&canReview(t)) {modal('独立验收维修结果',`<div class="review-box"><b>${esc(t.title)}</b><p>${esc(t.notes.at(-1))}</p></div><p class="meta-note">设计样例：附件没有真实文件。以下确认只演示表单与状态反馈。</p><label class="checkbox"><input type="checkbox" name="onsite">我已核对现场问题已解决（示例）</label><label class="checkbox"><input type="checkbox" name="evidence">我已核对维修证据与任务一致（示例）</label><label class="form-field"><span>${roles[actor].kind==='manager'?'代验收理由（必填）':'验收备注（选填）'}</span><textarea name="remark" rows="3" placeholder="记录验收情况。"></textarea></label>`,'演示验收通过',data=>{if(!data.has('onsite')||!data.has('evidence'))return error('请先核对现场与证据，两个确认项都需要勾选。');if(!canReview(t))return error('当前身份不具备独立验收权限。');if(roles[actor].kind==='manager'&&!String(data.get('remark')).trim())return error('请填写代验收理由。');mutate(t,'独立验收通过（设计样例）'+(data.get('remark')?'：'+data.get('remark'):''),()=>t.status='COMPLETED');});return;}
  if(action==='reject'&&canReview(t)) {reasonDialog(t,'退回维修人员重做','确认退回',reason=>mutate(t,'第 1 轮完工退回：'+reason,()=>{t.status='IN_PROGRESS';t.notes.push('验收退回：'+reason);}));return;}
  if(action==='more'&&!terminal(t)&&['reporter','manager'].includes(roles[actor].kind)) {reasonDialog(t,'取消这项任务','确认取消任务',reason=>mutate(t,'取消任务：'+reason,()=>t.status='CANCELLED'));return;}
  if(action==='asset'&&mine(t)&&t.status==='ACCEPTED') {modal('确认维修设备','<label class="form-field"><span>关联设备</span><select name="asset"><option>DR-001 · 大厅自动门</option><option>DR-002 · 北侧自动门</option></select><small>设备实际定位与问题发生空间分别记录。</small></label>','关联设备',data=>mutate(t,'维修人员关联设备',()=>t.asset=data.get('asset')));return;}
  if(action==='propose'&&mine(t)&&t.status==='ACCEPTED'&&!t.proposed) {modal('提议维修预约','<p class="meta-note">设计示例使用北京时间。正式版保留现有服务端预约约束。</p><label class="form-field"><span>到场日期</span><input type="date" name="date" value="2026-10-09"></label><div class="field-row"><label class="form-field"><span>开始时间</span><input type="time" name="start" value="14:00"></label><label class="form-field"><span>结束时间</span><input type="time" name="end" value="15:00"></label></div>','提交预约提议',data=>{const date=data.get('date'),start=data.get('start'),end=data.get('end');if(!date||!start||!end||end<=start)return error('请填写日期，并确保结束时间晚于开始时间。');mutate(t,'维修人员提出新的预约时间',()=>{t.appointment=`${date} ${start}–${end}`;t.proposed=true;});});return;}
  if(action==='start'&&mine(t)&&t.status==='SCHEDULED') {const time=new Date(t.appointment.slice(0,10)+'T'+t.appointment.slice(11,16)+':00+08:00');if(new Date()<time)return toast('尚未到预约时间。');mutate(t,'维修人员开始处理',()=>t.status='IN_PROGRESS');}
}
function settings() {modal('设置与演示身份',`<p class="meta-note">用于评审不同角色的界面。身份切换不是登录、认证或授权实现。</p>${Object.entries(roles).map(([key,r])=>`<button type="button" class="role-option ${actor===key?'current':''}" data-actor="${key}"><span><b>${r.name}</b><small>项目 ${r.project} · ${r.label}</small></span><span>${actor===key?'当前身份':'切换 →'}</span></button>`).join('')}<div class="capability"><b>当前原型能力</b><p>本页示例交互可用；业务服务、真实上传、模型和通知均未连接。</p></div>`);}
document.addEventListener('click',e=>{
  const button=e.target.closest('button');if(!button)return;
  if(button.hasAttribute('data-close'))return closeModal();
  if(button.dataset.actor){actor=button.dataset.actor;nav='all';filter='all';tab='overview';$('#search').value='';selected=null;closeModal(true);render();return;}
  if(button.dataset.task){selected=button.dataset.task;tab='overview';$('.workspace').classList.remove('mobile-open');render();return;}
  if(button.dataset.nav){nav=button.dataset.nav;render();return;}
  if(button.dataset.filter){filter=button.dataset.filter;render();return;}
  if(button.dataset.tab){tab=button.dataset.tab;render();return;}
  if(button.dataset.action)doAction(button.dataset.action);
});
$('#modal').addEventListener('cancel',e=>{e.preventDefault();closeModal();});
$('#search').oninput=render;
$('#scene').onchange=e=>reset(e.target.value);
$('#reset').onclick=()=>reset($('#scene').value);
$('#new-task').onclick=()=>doAction('new');
$('#settings').onclick=settings;$('#profile').onclick=settings;
$('#help').onclick=()=>modal('使用说明','<p>从左侧选任务，中间查看问题、预约和处理记录，右侧按当前身份完成下一步。</p><p>演示场景可切换预约确认、维修处置和独立验收。设置中的演示身份用于检查不同角色可见范围。</p><div class="warning-note"><b>这是设计原型</b><p>所有任务、事件与就绪样式都是示例，不构成真实业务、上传或验收证明。刷新或重置会清空示例修改。</p></div>');
$('#list-toggle').onclick=()=>$('.workspace').classList.toggle('mobile-open');
$('.brand').onclick=e=>{e.preventDefault();nav='all';filter='all';$('#search').value='';render();};
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'&&!$('#modal').open){e.preventDefault();$('.workspace').classList.add('mobile-open');$('#search').focus();}});
document.addEventListener('keydown',e=>{
  if(!e.target.matches('[data-tab]')||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
  const tabs=[...document.querySelectorAll('[data-tab]')],i=tabs.indexOf(e.target);
  const n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
  e.preventDefault();tab=tabs[n].dataset.tab;render();$(`[data-tab="${tab}"]`).focus();
});
document.querySelectorAll('.nav-icon').forEach((el,i)=>el.innerHTML=icon(['list','clock','star','settings'][i]));
reset();
