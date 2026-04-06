/* GeoInvest — C 레이아웃: 좌측 이슈+엔티티 / 가운데 그래프·타임라인 / 우측 브리핑 */

const COLOR_MAP = {
  country: '#58a6ff', proxy: '#f85149', commodity: '#d29922',
  company: '#3fb950', asset: '#bc8cff', institution: '#56d4dd',
  person: '#db6d28', event: '#8b949e',
};
const LINK_COLORS = {
  ally: '#58a6ff', hostile: '#f85149', proxy: '#db6d28',
  trade: '#d29922', supply: '#3fb950', attack: '#f85149',
  blockade: '#bc8cff', base: '#56d4dd', impacts: '#8b949e',
  mentions: '#8b949e', triggers: '#8b949e', involves: '#8b949e',
  reacts_to: '#8b949e', supports: '#3fb950', sanctions: '#f85149',
};
const CATEGORY_ICONS = {
  diplomatic: '🕊️', military: '⚔️', legal: '⚖️', event: '📌',
  sanctions: '🚫', energy: '⚡', trade: '📦', territorial: '🗺️',
  earnings: '💰', analyst: '📊', product: '🚀', regulatory: '📋',
  sector: '🏭', deal: '🤝', macro: '🌐', war: '💥', policy: '📜',
};
const CATEGORY_LABELS = {
  diplomatic: '외교', military: '군사', legal: '법적', event: '기타',
  sanctions: '제재', energy: '에너지', trade: '무역', territorial: '영토',
  earnings: '실적', analyst: '애널리스트', product: '제품', regulatory: '규제',
  sector: '섹터', deal: '딜', macro: '매크로', war: '전쟁', policy: '정책',
};

let currentIssueId = null;
let currentView = 'graph';
let currentCategory = 'geo';
let simulation = null;
let allIssues = [];

const ANALYSIS_LABELS = {
  fundamental: 'FUNDAMENTAL', technical: 'TECHNICAL', market: 'MARKET',
};
const ANALYSIS_COLORS = {
  fundamental: 'var(--green)', technical: 'var(--purple)', market: 'var(--orange)',
};

// ============================================================
// Category tabs
// ============================================================

function switchCategory(category) {
  currentCategory = category;
  document.querySelectorAll('.nav-tab').forEach(el => {
    el.classList.toggle('active', el.dataset.category === category);
  });
  currentIssueId = null;
  document.getElementById('briefing-content').innerHTML = '<div class="empty-state">노드를 클릭하면 브리핑이 표시됩니다</div>';
  loadIssues();
}

// ============================================================
// Issue list (left panel)
// ============================================================

async function loadIssues() {
  try {
    const res = await fetch(`/api/issues?category=${currentCategory}`);
    allIssues = await res.json();
    renderIssueList(allIssues);
    if (allIssues.length > 0) selectIssue(allIssues[0].id);
  } catch (e) { console.error('이슈 로딩 실패:', e); }
}

function renderIssueList(issues) {
  const container = document.getElementById('issue-list');

  // 주식 탭: 분석유형별 그룹핑
  if (currentCategory !== 'geo' && issues.some(i => i.analysis_type)) {
    const groups = { market: [], fundamental: [], technical: [] };
    issues.forEach(i => {
      const t = i.analysis_type || 'market';
      if (groups[t]) groups[t].push(i);
    });
    let html = '';
    for (const [type, items] of Object.entries(groups)) {
      if (items.length === 0) continue;
      const label = ANALYSIS_LABELS[type] || type;
      const color = ANALYSIS_COLORS[type] || 'var(--dim)';
      html += `<div class="analysis-group-title" style="color:${color}">${label}</div>`;
      html += items.map(issue => renderIssueItem(issue)).join('');
    }
    container.innerHTML = html;
    return;
  }

  container.innerHTML = issues.map(issue => renderIssueItem(issue)).join('');
}

function renderIssueItem(issue) {
  const sevClass = issue.severity || 'moderate';
  const trend = issue.trend || '→';
  const trendCls = trend === '↑' ? 'trend-up' : trend === '↓' ? 'trend-down' : 'trend-flat';
  return `<div class="issue-item${issue.id === currentIssueId ? ' selected' : ''}" data-id="${issue.id}" onclick="selectIssue('${issue.id}')">
    <span class="issue-rank">${issue.rank}</span>
    <span class="severity-dot ${sevClass}"></span>
    <div class="issue-info">
      <div class="issue-name">${issue.title}</div>
      <div class="issue-meta">${issue.news_24h || 0}건 뉴스 · ${issue.event_count} events</div>
    </div>
    <span class="issue-trend ${trendCls}">${trend}</span>
  </div>`;
}

async function selectIssue(issueId) {
  currentIssueId = issueId;
  // 이슈 리스트 하이라이트
  document.querySelectorAll('.issue-item').forEach(el => {
    el.classList.toggle('selected', el.dataset.id === issueId);
  });
  // 그래프 + 타임라인 로드
  try {
    const topFilter = document.getElementById('graph-top-filter').value || '10';
    const [graphRes, timelineRes] = await Promise.all([
      fetch(`/api/issues/${issueId}/graph?top=${topFilter}`),
      fetch(`/api/issues/${issueId}/timeline`),
    ]);
    const graphData = await graphRes.json();
    const timelineData = await timelineRes.json();
    renderEntityList(graphData.nodes);
    // 필터 정보 표시
    const toolbar = document.getElementById('graph-toolbar');
    const countLabel = document.getElementById('graph-count-label');
    if (graphData.total_entities) {
      toolbar.style.display = 'flex';
      countLabel.textContent = `${graphData.filtered}/${graphData.total_entities}개 표시`;
    }
    if (graphData.nodes.length > 0) {
      renderGraph(graphData.nodes, graphData.edges);
    } else {
      // 빈 그래프 — 이슈 설명 표시
      const issue = allIssues.find(i => i.id === issueId);
      const svg = document.getElementById('graph-svg');
      svg.style.display = 'none';
      document.getElementById('graph-legend').style.display = 'none';
      document.getElementById('graph-empty').style.display = 'block';
      document.getElementById('graph-empty').innerHTML = `<div style="text-align:center;padding:40px;">
        <div style="font-size:18px;font-weight:700;margin-bottom:8px;">${issue ? issue.title : ''}</div>
        <div style="color:var(--dim);font-size:12px;">${issue ? issue.description : ''}</div>
        <div style="color:var(--dim);font-size:11px;margin-top:16px;">뉴스 ${issue ? issue.news_24h : 0}건 수집 중 — 엔티티 추출 대기</div>
      </div>`;
    }
    renderTimeline(timelineData);
    document.getElementById('updated-at').textContent = `갱신: ${new Date().toLocaleString('ko-KR')}`;
  } catch (e) { console.error('데이터 로딩 실패:', e); }
}

// ============================================================
// View toggle
// ============================================================

function switchView(view) {
  currentView = view;
  document.getElementById('btn-graph').classList.toggle('active', view === 'graph');
  document.getElementById('btn-timeline').classList.toggle('active', view === 'timeline');
  document.getElementById('graph-container').style.display = view === 'graph' ? '' : 'none';
  document.getElementById('timeline-container').style.display = view === 'timeline' ? '' : 'none';
}

// ============================================================
// Entity list
// ============================================================

function renderEntityList(nodes) {
  const container = document.getElementById('entity-list');
  const entities = nodes.filter(n => n.type === 'entity');
  const typeLabels = {
    country: '국가', proxy: '프록시/비국가', commodity: '원자재',
    company: '기업', asset: '전략자산', institution: '기관', person: '인물',
  };
  const groups = {};
  entities.forEach(e => {
    const t = e.entity_type || 'country';
    if (!groups[t]) groups[t] = [];
    groups[t].push(e);
  });
  let html = '';
  for (const [type, items] of Object.entries(groups)) {
    html += `<div class="entity-group">
      <div class="entity-group-title">${typeLabels[type] || type} (${items.length})</div>
      ${items.map(e => `
        <div class="entity-item" data-id="${e.id}" onclick="selectEntity('${e.id}', this)">
          <span class="entity-dot ${type}"></span>${e.name}
        </div>
      `).join('')}
    </div>`;
  }
  container.innerHTML = html || '<div class="empty-state">엔티티 없음</div>';
}

// ============================================================
// Search
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  const searchBox = document.getElementById('search-box');
  searchBox.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    // 이슈 필터
    document.querySelectorAll('.issue-item').forEach(el => {
      const name = el.querySelector('.issue-name').textContent.toLowerCase();
      el.style.display = name.includes(q) ? '' : 'none';
    });
    // 엔티티 필터
    document.querySelectorAll('.entity-item').forEach(el => {
      el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
});

// ============================================================
// D3.js Graph
// ============================================================

function renderGraph(nodes, edges) {
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();
  svg.style('display', 'block');
  document.getElementById('graph-empty').style.display = 'none';
  document.getElementById('graph-legend').style.display = 'block';

  const container = document.getElementById('graph-container');
  const width = container.clientWidth;
  const height = container.clientHeight - 40;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  if (simulation) simulation.stop();

  const linkCount = {};
  edges.forEach(e => {
    linkCount[e.source] = (linkCount[e.source] || 0) + 1;
    linkCount[e.target] = (linkCount[e.target] || 0) + 1;
  });
  nodes.forEach(n => { n.radius = Math.max(8, Math.min(25, 6 + (linkCount[n.id] || 0) * 2)); });

  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => d.radius + 5));

  const g = svg.append('g');
  svg.call(d3.zoom().scaleExtent([0.3, 3]).on('zoom', e => g.attr('transform', e.transform)));

  const link = g.selectAll('.link-line').data(edges).join('line')
    .attr('class', d => `link-line ${d.link_type}`)
    .attr('stroke', d => LINK_COLORS[d.link_type] || '#8b949e')
    .attr('stroke-width', d => ['hostile','blockade'].includes(d.link_type) ? 2.5 : 1.5);

  const node = g.selectAll('.node-group').data(nodes).join('g').attr('class', 'node-group')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
    );

  node.append('circle').attr('class', 'node-circle')
    .attr('r', d => d.radius)
    .attr('fill', d => COLOR_MAP[d.type === 'entity' ? d.entity_type : 'event'] || '#8b949e')
    .attr('fill-opacity', 0.8)
    .attr('stroke', d => COLOR_MAP[d.type === 'entity' ? d.entity_type : 'event'] || '#8b949e')
    .attr('stroke-width', 2)
    .on('click', (e, d) => { if (d.type === 'entity') selectEntity(d.id); });

  node.append('text').attr('class', 'node-label').attr('dy', d => d.radius + 14).text(d => d.name);

  simulation.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });
}

// ============================================================
// Timeline
// ============================================================

function renderTimeline(events) {
  const container = document.getElementById('timeline-scroll');
  if (!events || events.length === 0) {
    container.innerHTML = '<div class="empty-state">이벤트 없음</div>';
    return;
  }

  let html = `<div class="tl-legend">
    <div class="tl-legend-item"><div class="tl-legend-dot" style="background:var(--blue);"></div> 외교</div>
    <div class="tl-legend-item"><div class="tl-legend-dot" style="background:var(--red);"></div> 군사</div>
    <div class="tl-legend-item"><div class="tl-legend-dot" style="background:var(--purple);"></div> 법적</div>
    <div class="tl-legend-item"><div class="tl-legend-dot" style="background:var(--dim);"></div> 기타</div>
  </div>`;

  html += '<div class="timeline-line">';
  events.forEach(ev => {
    const date = ev.started_at ? new Date(ev.started_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', year: 'numeric' }) : '?';
    const cat = ev.category || 'event';
    const icon = CATEGORY_ICONS[cat] || '📌';
    const label = CATEGORY_LABELS[cat] || '기타';
    const sevColor = ev.severity === 'critical' ? 'var(--red)' : 'var(--yellow)';

    html += `<div class="tl-item ${cat}">
      <div class="tl-date ${cat}">
        <span class="tl-severity" style="background:${sevColor};"></span>
        ${date}
        <span class="tl-category ${cat}">${icon} ${label}</span>
      </div>
      <div class="tl-title">${ev.title}</div>
      ${ev.summary ? `<div class="tl-summary">${ev.summary}</div>` : ''}
    </div>`;
  });
  html += '</div>';

  container.innerHTML = html;
}

// ============================================================
// Briefing
// ============================================================

async function selectEntity(entityId, listEl) {
  document.querySelectorAll('.entity-item').forEach(e => e.classList.remove('selected'));
  if (listEl) { listEl.classList.add('selected'); }
  else { const el = document.querySelector(`.entity-item[data-id="${entityId}"]`); if (el) el.classList.add('selected'); }

  try {
    const res = await fetch(`/api/entities/${entityId}/briefing`);
    if (!res.ok) return;
    renderBriefing(await res.json());
  } catch (e) { console.error('브리핑 로딩 실패:', e); }
}

function renderBriefing(data) {
  const container = document.getElementById('briefing-content');
  const entity = data.entity;
  const rels = data.relationships;

  let html = `<div class="briefing-header"><div>
    <div class="briefing-title">${entity.name}</div>
    <div class="briefing-subtitle">${entity.entity_type}${entity.ticker ? ' · ' + entity.ticker : ''}</div>
  </div></div>`;

  if (entity.aliases && entity.aliases.length > 0) {
    html += `<div class="briefing-section"><h3>별칭</h3><div style="font-size:11px;color:var(--dim);">${entity.aliases.join(', ')}</div></div>`;
  }

  // Structured properties
  if (entity.properties) {
    const p = entity.properties;
    const sections = [
      { key: 'objectives', title: '🎯 목표', color: 'var(--blue)' },
      { key: 'strategy', title: '⚡ 전략', color: 'var(--cyan)' },
      { key: 'achievements', title: '✅ 달성', color: 'var(--green)' },
      { key: 'failures', title: '❌ 미달성', color: 'var(--red)' },
    ];
    for (const { key, title, color } of sections) {
      const items = p[key];
      if (items && items.length > 0) {
        html += `<div class="briefing-section"><h3 style="color:${color}">${title}</h3><ul>`;
        items.forEach(item => { html += `<li>${item}</li>`; });
        html += `</ul></div>`;
      }
    }
    // 한줄평
    if (p['한줄평']) {
      html += `<div class="briefing-section"><h3>한줄평</h3><div style="font-size:11px;color:var(--yellow);font-style:italic;padding:6px 0;">"${p['한줄평']}"</div></div>`;
    }
    // 나머지 속성
    const skipKeys = new Set(['objectives', 'strategy', 'achievements', 'failures', '한줄평']);
    const otherProps = Object.entries(p).filter(([k]) => !skipKeys.has(k));
    if (otherProps.length > 0) {
      html += `<div class="briefing-section"><h3>상세</h3><ul>`;
      for (const [k, v] of otherProps) {
        html += `<li><strong>${k}:</strong> ${Array.isArray(v) ? v.join(', ') : v}</li>`;
      }
      html += `</ul></div>`;
    }
  }

  // Relationships
  if (rels.length > 0) {
    const outgoing = rels.filter(r => r.direction === 'outgoing');
    const incoming = rels.filter(r => r.direction === 'incoming');
    if (outgoing.length > 0) {
      html += `<div class="briefing-section"><h3>관계 →</h3><ul>`;
      outgoing.forEach(r => { html += `<li><span class="rel-tag ${r.link_type}">${r.link_type}</span> → ${r.target}${r.evidence ? ' — ' + r.evidence : ''}</li>`; });
      html += `</ul></div>`;
    }
    if (incoming.length > 0) {
      html += `<div class="briefing-section"><h3>관계 ←</h3><ul>`;
      incoming.forEach(r => { html += `<li>${r.source} → <span class="rel-tag ${r.link_type}">${r.link_type}</span>${r.evidence ? ' — ' + r.evidence : ''}</li>`; });
      html += `</ul></div>`;
    }
  }
  container.innerHTML = html;
}

// ============================================================
// News Ticker
// ============================================================

async function loadNewsTicker() {
  try {
    const res = await fetch('/api/news/latest?limit=30');
    const news = await res.json();
    const track = document.getElementById('ticker-track');
    if (news.length === 0) { track.innerHTML = '<span class="ticker-text">뉴스가 없습니다</span>'; return; }

    const ISSUE_COLORS = {
      '이란 전쟁': '#f85149', '비트코인 지정학': '#d29922', 'IMEC 회랑': '#bc8cff',
      '트럼프 관세전쟁 2.0': '#db6d28', 'AI/반도체 패권전쟁': '#3fb950',
      '러시아-우크라이나 전쟁': '#f85149', '대만 해협 위기': '#58a6ff',
      '유럽 정치 위기': '#bc8cff', '글로벌 AI 규제 경쟁': '#56d4dd',
      '일본 금리 전환 (BOJ)': '#d29922',
    };
    const items = news.map(n => {
      const tag = n.top_issue
        ? `<span style="background:${ISSUE_COLORS[n.top_issue] || '#8b949e'}22;color:${ISSUE_COLORS[n.top_issue] || '#8b949e'};border:1px solid ${ISSUE_COLORS[n.top_issue] || '#8b949e'}44;padding:1px 5px;border-radius:3px;font-size:9px;margin-right:5px;">${n.top_issue}</span>`
        : '';
      return `<span class="news-item">${tag}<span class="news-src">[${n.source}]</span>${n.title}</span>`;
    }).join('<span class="news-dot">·</span>');

    track.innerHTML = `<span class="ticker-text">${items}<span class="news-dot">·</span>${items}</span>`;
    const text = track.querySelector('.ticker-text');
    text.style.animationDuration = `${Math.max(300, news.length * 20)}s`;
  } catch (e) { console.error('뉴스 티커 실패:', e); }
}

setInterval(loadNewsTicker, 5 * 60 * 1000);

// Top N 필터 변경 시 그래프만 다시 로드
function reloadGraph() {
  if (currentIssueId) selectIssue(currentIssueId);
}

// ============================================================
// Init
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  // 탭 클릭 이벤트 바인딩
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      switchCategory(btn.dataset.category);
    });
  });
  loadIssues();
  loadNewsTicker();
});
