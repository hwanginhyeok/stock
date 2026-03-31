/* GeoInvest — D3.js force-directed graph + interactions */

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

let currentIssueId = null;
let simulation = null;

// ============================================================
// Issue tabs
// ============================================================

async function loadIssues() {
  try {
    const res = await fetch('/api/issues');
    const issues = await res.json();
    const tabs = document.getElementById('issue-tabs');

    if (issues.length === 0) {
      tabs.innerHTML = '<div class="issue-tab" style="color:var(--dim);">등록된 이슈가 없습니다</div>';
      return;
    }

    tabs.innerHTML = issues.map(issue => {
      const sevClass = issue.severity || 'moderate';
      return `<div class="issue-tab" data-id="${issue.id}" onclick="selectIssue('${issue.id}', this)">
        <span class="severity-dot ${sevClass}"></span>${issue.title}
      </div>`;
    }).join('');

    // 첫 번째 이슈 자동 선택
    const firstTab = tabs.querySelector('.issue-tab');
    if (firstTab) {
      firstTab.click();
    }
  } catch (e) {
    console.error('이슈 로딩 실패:', e);
  }
}

async function selectIssue(issueId, tabEl) {
  // 탭 활성화
  document.querySelectorAll('.issue-tab').forEach(t => t.classList.remove('active'));
  if (tabEl) tabEl.classList.add('active');

  currentIssueId = issueId;

  // 그래프 로딩
  try {
    const res = await fetch(`/api/issues/${issueId}/graph`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderEntityList(data.nodes);
    renderGraph(data.nodes, data.edges);
    document.getElementById('updated-at').textContent = `갱신: ${new Date().toLocaleString('ko-KR')}`;
  } catch (e) {
    console.error('그래프 로딩 실패:', e);
  }
}

// ============================================================
// Entity list (left panel)
// ============================================================

function renderEntityList(nodes) {
  const container = document.getElementById('entity-list');
  const entities = nodes.filter(n => n.type === 'entity');

  // 타입별 그룹핑
  const groups = {};
  const typeLabels = {
    country: '국가', proxy: '프록시/비국가', commodity: '원자재',
    company: '기업', asset: '전략자산', institution: '기관', person: '인물',
  };

  entities.forEach(e => {
    const t = e.entity_type || 'country';
    if (!groups[t]) groups[t] = [];
    groups[t].push(e);
  });

  let html = '';
  for (const [type, items] of Object.entries(groups)) {
    html += `<div class="entity-group">
      <div class="entity-group-title">${typeLabels[type] || type}</div>
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
// D3.js Graph (center panel)
// ============================================================

function renderGraph(nodes, edges) {
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();
  svg.style('display', 'block');
  document.getElementById('graph-empty').style.display = 'none';
  document.getElementById('graph-legend').style.display = 'block';

  const container = document.getElementById('graph-container');
  const width = container.clientWidth;
  const height = container.clientHeight;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  // 시뮬레이션 중지
  if (simulation) simulation.stop();

  // 노드 크기 계산 (연결 수 기반)
  const linkCount = {};
  edges.forEach(e => {
    linkCount[e.source] = (linkCount[e.source] || 0) + 1;
    linkCount[e.target] = (linkCount[e.target] || 0) + 1;
  });
  nodes.forEach(n => { n.radius = Math.max(8, Math.min(25, 6 + (linkCount[n.id] || 0) * 2)); });

  // 시뮬레이션
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => d.radius + 5));

  // Zoom
  const g = svg.append('g');
  svg.call(d3.zoom().scaleExtent([0.3, 3]).on('zoom', e => g.attr('transform', e.transform)));

  // Links
  const link = g.selectAll('.link-line')
    .data(edges)
    .join('line')
    .attr('class', d => `link-line ${d.link_type}`)
    .attr('stroke', d => LINK_COLORS[d.link_type] || '#8b949e')
    .attr('stroke-width', d => d.link_type === 'hostile' || d.link_type === 'blockade' ? 2.5 : 1.5);

  // Nodes
  const node = g.selectAll('.node-group')
    .data(nodes)
    .join('g')
    .attr('class', 'node-group')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
    );

  node.append('circle')
    .attr('class', 'node-circle')
    .attr('r', d => d.radius)
    .attr('fill', d => {
      const t = d.type === 'entity' ? d.entity_type : 'event';
      return COLOR_MAP[t] || '#8b949e';
    })
    .attr('fill-opacity', 0.8)
    .attr('stroke', d => {
      const t = d.type === 'entity' ? d.entity_type : 'event';
      return COLOR_MAP[t] || '#8b949e';
    })
    .attr('stroke-width', 2)
    .on('click', (e, d) => {
      if (d.type === 'entity') selectEntity(d.id);
    });

  node.append('text')
    .attr('class', 'node-label')
    .attr('dy', d => d.radius + 14)
    .text(d => d.name);

  // Tick
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });
}

// ============================================================
// Briefing (right panel)
// ============================================================

async function selectEntity(entityId, listEl) {
  // 리스트 하이라이트
  document.querySelectorAll('.entity-item').forEach(e => e.classList.remove('selected'));
  if (listEl) {
    listEl.classList.add('selected');
  } else {
    const el = document.querySelector(`.entity-item[data-id="${entityId}"]`);
    if (el) el.classList.add('selected');
  }

  try {
    const res = await fetch(`/api/entities/${entityId}/briefing`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderBriefing(data);
  } catch (e) {
    console.error('브리핑 로딩 실패:', e);
  }
}

function renderBriefing(data) {
  const container = document.getElementById('briefing-content');
  const entity = data.entity;
  const rels = data.relationships;

  let html = `
    <div class="briefing-header">
      <div>
        <div class="briefing-title">${entity.name}</div>
        <div class="briefing-subtitle">${entity.entity_type}${entity.ticker ? ' · ' + entity.ticker : ''}</div>
      </div>
    </div>
  `;

  // Aliases
  if (entity.aliases && entity.aliases.length > 0) {
    html += `<div class="briefing-section">
      <h3>별칭</h3>
      <div style="font-size:12px;color:var(--dim);">${entity.aliases.join(', ')}</div>
    </div>`;
  }

  // Properties
  if (entity.properties && Object.keys(entity.properties).length > 0) {
    html += `<div class="briefing-section"><h3>상세</h3><ul>`;
    for (const [k, v] of Object.entries(entity.properties)) {
      html += `<li><strong>${k}:</strong> ${v}</li>`;
    }
    html += `</ul></div>`;
  }

  // Relationships
  if (rels.length > 0) {
    const outgoing = rels.filter(r => r.direction === 'outgoing');
    const incoming = rels.filter(r => r.direction === 'incoming');

    if (outgoing.length > 0) {
      html += `<div class="briefing-section"><h3>관계 (발신)</h3><ul>`;
      outgoing.forEach(r => {
        html += `<li><span class="rel-tag ${r.link_type}">${r.link_type}</span> → ${r.target}${r.evidence ? ' — ' + r.evidence : ''}</li>`;
      });
      html += `</ul></div>`;
    }

    if (incoming.length > 0) {
      html += `<div class="briefing-section"><h3>관계 (수신)</h3><ul>`;
      incoming.forEach(r => {
        html += `<li>${r.source} → <span class="rel-tag ${r.link_type}">${r.link_type}</span>${r.evidence ? ' — ' + r.evidence : ''}</li>`;
      });
      html += `</ul></div>`;
    }
  }

  container.innerHTML = html;
}

// ============================================================
// Init
// ============================================================

document.addEventListener('DOMContentLoaded', loadIssues);
