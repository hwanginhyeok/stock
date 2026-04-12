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
    const depthFilter = document.getElementById('graph-depth-filter').value || '2';
    const [graphRes, timelineRes] = await Promise.all([
      fetch(`/api/issues/${issueId}/graph?top=${topFilter}&depth=${depthFilter}`),
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

let lwChartInitialized = false;
let lwMainChart = null;
let lwCandleSeries = null;
let lwVolumeSeries = null;
let lwSmaSeries = {};   // key: "5","10",... value: LineSeries
let lwVwmaSeries = null;
let lwVpvrSeries = [];  // histogram series for volume profile
let lwTrendlineSeries = [];  // 추세선 시리즈
let lwRsiChart = null;
let lwRsiSeries = null;
let lwMacdChart = null;
let lwMacdSeries = null;
let lwSignalSeries = null;
let lwHistSeries = null;
let currentChartPeriod = '6mo';
let currentChartInterval = '1d';
let allEventMarkers = [];
let allChartData = null;

function switchView(view) {
  currentView = view;
  document.getElementById('btn-graph').classList.toggle('active', view === 'graph');
  document.getElementById('btn-timeline').classList.toggle('active', view === 'timeline');
  document.getElementById('btn-chart').classList.toggle('active', view === 'chart');
  document.getElementById('graph-container').style.display = view === 'graph' ? '' : 'none';
  document.getElementById('timeline-container').style.display = view === 'timeline' ? '' : 'none';
  document.getElementById('chart-container').style.display = view === 'chart' ? '' : 'none';

  if (view === 'chart' && !lwChartInitialized) {
    initLightweightChart();
    lwChartInitialized = true;
  }
}

function initLightweightChart() {
  const LWC = LightweightCharts;
  const mainEl = document.getElementById('lw-main-chart');
  const rsiEl = document.getElementById('lw-rsi-chart');
  const macdEl = document.getElementById('lw-macd-chart');

  const darkOpts = {
    layout: { background: { color: '#0d1117' }, textColor: '#d1d5db' },
    grid: { vertLines: { color: '#1e2329' }, horzLines: { color: '#1e2329' } },
    crosshair: {
      vertLine: { color: '#4b5563', labelBackgroundColor: '#374151' },
      horzLine: { color: '#4b5563', labelBackgroundColor: '#374151' },
    },
    rightPriceScale: { borderColor: '#2a2d3a' },
    timeScale: { borderColor: '#2a2d3a', timeVisible: false },
  };

  // 메인 차트
  lwMainChart = LWC.createChart(mainEl, { ...darkOpts, height: mainEl.clientHeight || 400 });
  lwCandleSeries = lwMainChart.addCandlestickSeries({
    upColor: '#26a69a', downColor: '#ef5350',
    borderUpColor: '#26a69a', borderDownColor: '#ef5350',
    wickUpColor: '#26a69a', wickDownColor: '#ef5350',
  });
  lwVolumeSeries = lwMainChart.addHistogramSeries({
    priceFormat: { type: 'volume' },
    priceScaleId: 'volume',
  });
  lwMainChart.priceScale('volume').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });

  // RSI 서브차트
  lwRsiChart = LWC.createChart(rsiEl, { ...darkOpts, height: 100 });
  lwRsiChart.timeScale().applyOptions({ visible: false });
  lwRsiSeries = lwRsiChart.addLineSeries({ color: '#a78bfa', lineWidth: 1.5, priceScaleId: 'right' });
  // RSI 기준선
  lwRsiSeries.createPriceLine({ price: 70, color: '#f8514988', lineWidth: 1, lineStyle: 2 });
  lwRsiSeries.createPriceLine({ price: 30, color: '#3fb95088', lineWidth: 1, lineStyle: 2 });

  // MACD 서브차트
  lwMacdChart = LWC.createChart(macdEl, { ...darkOpts, height: 100 });
  lwMacdChart.timeScale().applyOptions({ visible: true });
  lwMacdSeries = lwMacdChart.addLineSeries({ color: '#58a6ff', lineWidth: 1.5 });
  lwSignalSeries = lwMacdChart.addLineSeries({ color: '#f85149', lineWidth: 1 });
  lwHistSeries = lwMacdChart.addHistogramSeries({ color: '#3fb95066' });

  // 크로스헤어 동기화
  function syncCrosshair(source, targets) {
    source.subscribeCrosshairMove((param) => {
      if (!param.time) {
        targets.forEach(t => t.chart.clearCrosshairPosition());
        return;
      }
      targets.forEach(t => {
        t.chart.setCrosshairPosition(NaN, param.time, t.series);
      });
    });
  }
  syncCrosshair(lwMainChart, [
    { chart: lwRsiChart, series: lwRsiSeries },
    { chart: lwMacdChart, series: lwMacdSeries },
  ]);
  syncCrosshair(lwRsiChart, [
    { chart: lwMainChart, series: lwCandleSeries },
    { chart: lwMacdChart, series: lwMacdSeries },
  ]);
  syncCrosshair(lwMacdChart, [
    { chart: lwMainChart, series: lwCandleSeries },
    { chart: lwRsiChart, series: lwRsiSeries },
  ]);

  // 타임스케일 동기화 (피드백 루프 방지)
  let _isSyncingTimeScale = false;
  function syncTimeScale(source, targets) {
    source.timeScale().subscribeVisibleLogicalRangeChange((range) => {
      if (!range || _isSyncingTimeScale) return;
      _isSyncingTimeScale = true;
      targets.forEach(t => t.timeScale().setVisibleLogicalRange(range));
      _isSyncingTimeScale = false;
    });
  }
  syncTimeScale(lwMainChart, [lwRsiChart, lwMacdChart]);
  syncTimeScale(lwRsiChart, [lwMainChart, lwMacdChart]);
  syncTimeScale(lwMacdChart, [lwMainChart, lwRsiChart]);

  // SMA 시리즈 미리 생성 (한 번만, loadChartData에서 setData만 호출)
  const smaStyles = {
    '5':   { color: '#ef5350', lineWidth: 1, lineStyle: 0 },
    '10':  { color: '#f59e0b', lineWidth: 1, lineStyle: 0 },
    '20':  { color: '#3fb950', lineWidth: 1, lineStyle: 0 },
    '50':  { color: '#58a6ff', lineWidth: 1.5, lineStyle: 0 },
    '100': { color: '#a78bfa', lineWidth: 1.5, lineStyle: 0 },
    '200': { color: '#e6edf3', lineWidth: 2, lineStyle: 0 },
  };
  for (const [len, style] of Object.entries(smaStyles)) {
    lwSmaSeries[len] = lwMainChart.addLineSeries({
      color: style.color, lineWidth: style.lineWidth, lineStyle: style.lineStyle,
      lastValueVisible: false, priceLineVisible: false, crosshairMarkerVisible: false,
      title: `MA${len}`,
    });
  }
  // VWMA 시리즈 미리 생성
  lwVwmaSeries = lwMainChart.addLineSeries({
    color: '#ff6b6b', lineWidth: 2.5, lineStyle: 2,
    lastValueVisible: true, priceLineVisible: false,
    title: 'VWMA100',
  });

  // SMA 토글
  document.getElementById('show-sma').addEventListener('change', (e) => {
    Object.values(lwSmaSeries).forEach(s => s.applyOptions({ visible: e.target.checked }));
  });
  // VWMA 토글
  document.getElementById('show-vwma').addEventListener('change', (e) => {
    if (lwVwmaSeries) lwVwmaSeries.applyOptions({ visible: e.target.checked });
  });
  // VPVR 토글
  document.getElementById('show-vpvr').addEventListener('change', (e) => {
    const canvas = document.getElementById('lw-main-chart').querySelector('.vpvr-canvas');
    if (canvas) canvas.style.display = e.target.checked ? 'block' : 'none';
    if (e.target.checked && lwCandleSeries && allChartData) {
      renderVPVR(lwMainChart, lwCandleSeries, allChartData, document.getElementById('lw-main-chart'));
    }
  });

  // interval 버튼
  document.querySelectorAll('.interval-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.interval-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentChartInterval = btn.dataset.interval;
      loadChartData(currentChartPeriod);
    });
  });

  // visible range 변경 시 VPVR 업데이트 (debounce)
  let vpvrDebounce;
  lwMainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
    if (!document.getElementById('show-vpvr')?.checked) return;
    clearTimeout(vpvrDebounce);
    vpvrDebounce = setTimeout(() => {
      if (lwCandleSeries && allChartData) {
        renderVPVR(lwMainChart, lwCandleSeries, allChartData, mainEl);
      }
    }, 200);
  });

  // 마커 호버 툴팁
  const tooltip = document.getElementById('chart-tooltip');
  lwMainChart.subscribeCrosshairMove((param) => {
    if (!param.point || !param.time) { tooltip.style.display = 'none'; return; }
    const timeStr = typeof param.time === 'string' ? param.time
      : `${param.time.year}-${String(param.time.month).padStart(2,'0')}-${String(param.time.day).padStart(2,'0')}`;
    const ev = allEventMarkers.find(m => m.time === timeStr);
    if (!ev) { tooltip.style.display = 'none'; return; }
    tooltip.innerHTML = `
      <div class="tt-date">${ev.time}</div>
      <div class="tt-title"><span class="tt-cat" style="background:${ev.color}22;color:${ev.color}">${ev.category_label}</span>${ev.title}</div>
      <div class="tt-desc">${ev.severity} · ${ev.story_thread || ''}</div>
    `;
    tooltip.style.display = 'block';
    const x = param.point.x;
    const tw = tooltip.offsetWidth || 260;
    const cw = mainEl.clientWidth;
    tooltip.style.left = `${x + tw + 16 > cw ? x - tw - 8 : x + 12}px`;
    tooltip.style.top = `${Math.max(0, param.point.y - 50)}px`;
  });

  // 기간 버튼
  document.querySelectorAll('.period-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentChartPeriod = btn.dataset.period;
      loadChartData(currentChartPeriod);
    });
  });

  // 이벤트 토글
  document.getElementById('show-events').addEventListener('change', (e) => {
    renderEventMarkers(e.target.checked);
  });
  document.getElementById('show-all-events').addEventListener('change', () => {
    loadChartData(currentChartPeriod);
  });

  // 리사이즈 대응
  const ro = new ResizeObserver(() => {
    lwMainChart.applyOptions({ width: mainEl.clientWidth });
    lwRsiChart.applyOptions({ width: rsiEl.clientWidth });
    lwMacdChart.applyOptions({ width: macdEl.clientWidth });
  });
  ro.observe(mainEl);

  // 초기 데이터 로드
  loadChartData('6mo');
}

async function loadChartData(period) {
  const showAll = document.getElementById('show-all-events')?.checked;
  const sevMin = showAll ? 'moderate' : 'major';

  try {
    const [ohlcvResp, eventsResp, signalsResp, trendResp] = await Promise.all([
      fetch(`/api/chart/ohlcv?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
      fetch(`/api/chart/events?symbol=TSLA&period=${period}&severity_min=${sevMin}`),
      fetch(`/api/chart/signals?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
      fetch(`/api/chart/trendlines?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
    ]);
    const ohlcvData = await ohlcvResp.json();
    const eventsData = await eventsResp.json();
    const signalsData = await signalsResp.json();
    const trendData = await trendResp.json();

    // VPVR 계산용 + timeScale 설정
    allChartData = ohlcvData.ohlcv;
    lwMainChart.timeScale().applyOptions({ timeVisible: ['1h','4h'].includes(currentChartInterval) });

    // 동기화 리스너 비활성화 (setData 중 range 변경 방지)
    _isSyncingTimeScale = true;

    // 캔들 + 볼륨
    lwCandleSeries.setData(ohlcvData.ohlcv);
    lwVolumeSeries.setData(ohlcvData.ohlcv.map(d => ({
      time: d.time,
      value: d.volume,
      color: d.close >= d.open ? '#26a69a33' : '#ef535033',
    })));

    // SMA 이평선 — 기존 시리즈에 데이터만 업데이트 (시리즈 재생성 안 함)
    const smaData = ohlcvData.indicators.sma || {};
    for (const [len, series] of Object.entries(lwSmaSeries)) {
      if (smaData[len]?.series?.length) {
        series.setData(smaData[len].series);
      } else {
        series.setData([]);
      }
    }

    // VWMA 100 — 기존 시리즈에 데이터만 업데이트
    const vwmaData = ohlcvData.indicators.vwma100;
    if (lwVwmaSeries) {
      lwVwmaSeries.setData(vwmaData?.series?.length ? vwmaData.series : []);
    }

    // Volume Profile (VPVR) — Canvas 오버레이로 visible range 기반 렌더링
    // (서버 volume_profile 무시, 클라이언트에서 실시간 계산)

    // RSI
    if (ohlcvData.indicators.rsi_series) {
      lwRsiSeries.setData(ohlcvData.indicators.rsi_series);
    }

    // MACD
    if (ohlcvData.indicators.macd_series) lwMacdSeries.setData(ohlcvData.indicators.macd_series);
    if (ohlcvData.indicators.signal_series) lwSignalSeries.setData(ohlcvData.indicators.signal_series);
    if (ohlcvData.indicators.histogram_series) {
      lwHistSeries.setData(ohlcvData.indicators.histogram_series.map(d => ({
        time: d.time, value: d.value,
        color: d.value >= 0 ? '#26a69a66' : '#ef535066',
      })));
    }

    // 지표 요약
    const ind = ohlcvData.indicators;
    const summaryEl = document.getElementById('chart-indicator-summary');
    if (summaryEl && ind.last_price) {
      const changeColor = ind.change >= 0 ? 'var(--green)' : 'var(--red)';
      const stDir = ind.supertrend_direction === 1 ? '▲' : '▼';
      summaryEl.innerHTML = `
        <span style="color:var(--white);font-weight:600">$${ind.last_price}</span>
        <span style="color:${changeColor}">${ind.change >= 0 ? '+' : ''}${ind.change} (${ind.change_pct}%)</span>
        · RSI <span style="color:${ind.rsi < 30 ? 'var(--green)' : ind.rsi > 70 ? 'var(--red)' : 'var(--dim)'}">${ind.rsi}</span>
        · ADX ${ind.adx || '-'}
        · ST ${stDir}
      `;
    }

    // 평행 채널 렌더링 (빗각 + 같은 기울기 평행선)
    lwTrendlineSeries.forEach(s => { try { lwMainChart.removeSeries(s); } catch(e){} });
    lwTrendlineSeries = [];
    if (trendData.channel) {
      const ch = trendData.channel;
      const isPrimSupport = ch.primary.type === 'support';

      // 핵심 빗각 (굵은 실선)
      const primaryS = lwMainChart.addLineSeries({
        color: isPrimSupport ? '#26a69a' : '#ef5350',
        lineWidth: 2, lineStyle: 0,
        lastValueVisible: true, priceLineVisible: false, crosshairMarkerVisible: false,
        title: isPrimSupport ? '지지 빗각' : '저항 빗각',
      });
      primaryS.setData(ch.primary.line);
      lwTrendlineSeries.push(primaryS);

      // 채널 반대편 (굵은 실선, 같은 기울기)
      const oppositeS = lwMainChart.addLineSeries({
        color: isPrimSupport ? '#ef5350' : '#26a69a',
        lineWidth: 2, lineStyle: 0,
        lastValueVisible: true, priceLineVisible: false, crosshairMarkerVisible: false,
        title: isPrimSupport ? '채널 상단' : '채널 하단',
      });
      oppositeS.setData(ch.opposite.line);
      lwTrendlineSeries.push(oppositeS);

      // 채널 중심선 (얇은 점선)
      const centerS = lwMainChart.addLineSeries({
        color: '#f59e0b88', lineWidth: 1, lineStyle: 2,
        lastValueVisible: false, priceLineVisible: false, crosshairMarkerVisible: false,
        title: '',
      });
      centerS.setData(ch.center.line);
      lwTrendlineSeries.push(centerS);
    }

    // 시그널 마커 (BUY/SELL) + 이벤트 마커 통합
    const signalMarkers = (signalsData.signals || []).map(s => ({
      time: s.time,
      position: s.type.includes('BUY') ? 'belowBar' : 'aboveBar',
      color: s.type.includes('BUY') ? '#26a69a' : '#ef5350',
      shape: s.type === 'STRONG_BUY' ? 'arrowUp' : s.type.includes('BUY') ? 'arrowUp' : 'arrowDown',
      text: s.type === 'STRONG_BUY' ? 'B+' : s.type === 'BUY' ? 'B' : 'S',
      size: s.type === 'STRONG_BUY' ? 3 : 2,
    }));
    // 시그널은 항상 표시 (이벤트와 합치되 시그널 우선)
    allEventMarkers = eventsData.markers;
    const combinedMarkers = [...signalMarkers];
    if (document.getElementById('show-events')?.checked !== false) {
      // 이벤트 마커 추가 (시그널과 같은 날짜면 시그널 우선)
      const signalDates = new Set(signalMarkers.map(m => m.time));
      allEventMarkers.forEach(m => {
        if (!signalDates.has(m.time)) {
          combinedMarkers.push({
            time: m.time,
            position: m.position || 'aboveBar',
            color: m.color,
            shape: 'circle',
            text: m.category_label?.charAt(0) || '·',
            size: 1,
          });
        }
      });
    }
    // 시간순 정렬 + 같은 날짜 중복 처리
    const byDate = {};
    combinedMarkers.forEach(m => {
      if (!byDate[m.time] || m.size > byDate[m.time].size) byDate[m.time] = m;
    });
    const sortedMarkers = Object.values(byDate).sort((a, b) => a.time > b.time ? 1 : -1);
    lwCandleSeries.setMarkers(sortedMarkers);
    renderEventList(eventsData.markers);

    // 추세 상태 표시 업데이트
    const trendEl = document.getElementById('chart-indicator-summary');
    if (trendEl && signalsData.current_trend) {
      const trendColors = { TREND_UP: 'var(--green)', TREND_DOWN: 'var(--red)', NEUTRAL: 'var(--dim)' };
      const trendLabels = { TREND_UP: '추세 ▲', TREND_DOWN: '추세 ▼', NEUTRAL: '중립', INSUFFICIENT_DATA: '—' };
      const trendHtml = `<span style="color:${trendColors[signalsData.current_trend] || 'var(--dim)'};font-weight:600">${trendLabels[signalsData.current_trend] || '—'}</span>`;
      trendEl.innerHTML = trendEl.innerHTML.replace(/· ST [▲▼]/, `· ${trendHtml}`);
    }

    // fitContent: 2단계 지연 — chart 내부 렌더 완전 종료 후 range 설정
    // _isSyncingTimeScale는 true 상태 유지 (setData 위에서 켰음)
    setTimeout(() => {
      lwMainChart.timeScale().fitContent();
      setTimeout(() => {
        const range = lwMainChart.timeScale().getVisibleLogicalRange();
        if (range) {
          lwRsiChart.timeScale().setVisibleLogicalRange(range);
          lwMacdChart.timeScale().setVisibleLogicalRange(range);
        }
        _isSyncingTimeScale = false;
        // VPVR 렌더링
        if (document.getElementById('show-vpvr')?.checked) {
          renderVPVR(lwMainChart, lwCandleSeries, allChartData, document.getElementById('lw-main-chart'));
        }
      }, 100);
    }, 100);

  } catch (err) {
    console.error('차트 데이터 로드 실패:', err);
  }
}

function renderEventMarkers(show) {
  if (!lwCandleSeries) return;
  if (!show) { lwCandleSeries.setMarkers([]); return; }

  // lightweight-charts 마커 포맷
  const markers = allEventMarkers.map(m => ({
    time: m.time,
    position: m.position || 'aboveBar',
    color: m.color,
    shape: m.severity === 'critical' ? 'arrowDown' : 'circle',
    text: m.category_label?.charAt(0) || '·',
    size: m.severity === 'critical' ? 2 : m.is_tesla ? 2 : 1,
  }));

  // 같은 날짜 중복 처리 — 가장 중요한 것만
  const byDate = {};
  markers.forEach(m => {
    if (!byDate[m.time] || m.size > byDate[m.time].size) byDate[m.time] = m;
  });

  const deduplicated = Object.values(byDate).sort((a, b) => a.time > b.time ? 1 : -1);
  lwCandleSeries.setMarkers(deduplicated);
}

function renderEventList(markers) {
  const list = document.getElementById('chart-event-list');
  if (!list) return;

  if (!markers.length) {
    list.innerHTML = '<div class="empty-state" style="height:100px;">이벤트 없음</div>';
    return;
  }

  // 최신순 정렬
  const sorted = [...markers].sort((a, b) => b.time > a.time ? 1 : -1);

  list.innerHTML = sorted.map(m => `
    <div class="chart-event-item">
      <div class="ev-date">
        <span class="ev-severity" style="background:${m.color}"></span>
        ${m.time} · ${m.severity}${m.is_tesla ? ' · TSLA' : ''}
      </div>
      <div class="ev-title">
        <span class="ev-badge" style="background:${m.color}22;color:${m.color}">${m.category_label}</span>
        ${m.title.length > 50 ? m.title.slice(0, 50) + '...' : m.title}
      </div>
    </div>
  `).join('');
}

// ============================================================
// Volume Profile (VPVR) — Visible Range 기반
// ============================================================

function computeVPVR(ohlcvData, fromTime, toTime, numBins = 30) {
  const visible = ohlcvData.filter(d => d.time >= fromTime && d.time <= toTime);
  if (!visible.length) return [];

  const prices = visible.flatMap(d => [d.high, d.low]);
  const minP = Math.min(...prices);
  const maxP = Math.max(...prices);
  const binSize = (maxP - minP) / numBins || 1;

  const bins = new Array(numBins).fill(0);
  visible.forEach(d => {
    const mid = (d.high + d.low) / 2;
    const idx = Math.min(Math.floor((mid - minP) / binSize), numBins - 1);
    bins[idx] += d.volume;
  });

  const maxVol = Math.max(...bins);
  return bins.map((vol, i) => ({
    price: minP + (i + 0.5) * binSize,
    volume: vol,
    pct: maxVol > 0 ? vol / maxVol * 100 : 0,
  }));
}

function renderVPVR(chart, series, ohlcvData, container) {
  const old = container.querySelector('.vpvr-canvas');
  if (old) old.remove();

  const range = chart.timeScale().getVisibleRange();
  if (!range) return;

  const vpData = computeVPVR(ohlcvData, range.from, range.to);
  if (!vpData.length) return;

  const canvas = document.createElement('canvas');
  canvas.className = 'vpvr-canvas';
  canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:5;';
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  container.style.position = 'relative';
  container.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  const maxBarWidth = canvas.width * 0.15;
  const lastClose = ohlcvData[ohlcvData.length - 1]?.close || 0;

  vpData.forEach(bin => {
    const y = series.priceToCoordinate(bin.price);
    if (y === null || y === undefined) return;

    const barWidth = (bin.pct / 100) * maxBarWidth;
    const barHeight = Math.max(2, canvas.height / vpData.length * 0.8);

    if (bin.pct >= 95) ctx.fillStyle = '#f59e0b88';
    else if (bin.price > lastClose) ctx.fillStyle = '#ef535044';
    else ctx.fillStyle = '#26a69a44';

    ctx.fillRect(canvas.width - barWidth - 60, y - barHeight / 2, barWidth, barHeight);
  });
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

function renderTimeline(data) {
  const container = document.getElementById('timeline-scroll');
  // 하위호환: 배열이면 기존 포맷, 객체면 새 포맷
  const threads = data.threads || {};
  const ungrouped = data.ungrouped || (Array.isArray(data) ? data : []);
  const total = data.total || ungrouped.length;

  if (total === 0) {
    container.innerHTML = '<div class="empty-state">이벤트 없음</div>';
    return;
  }

  const SEV_COLORS = {
    critical: 'var(--red)', major: 'var(--orange)',
    moderate: 'var(--blue)', minor: 'var(--dim)',
  };

  function renderEvent(ev) {
    const date = ev.started_at ? new Date(ev.started_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }) : '?';
    const cat = ev.event_type || ev.category || 'macro';
    const icon = CATEGORY_ICONS[cat] || '📌';
    const label = CATEGORY_LABELS[cat] || cat;
    const sevColor = SEV_COLORS[ev.severity] || 'var(--dim)';
    return `<div class="tl-item" style="cursor:pointer;" onclick="selectEvent('${ev.id}')">
      <div class="tl-date">
        <span class="tl-severity" style="background:${sevColor};"></span>
        ${date}
        <span class="tl-category">${icon} ${label}</span>
      </div>
      <div class="tl-title">${ev.title}</div>
    </div>`;
  }

  let html = `<div class="tl-header">이벤트 ${total}개</div>`;

  // story_thread별 그룹 렌더링
  const threadKeys = Object.keys(threads).sort((a, b) => {
    const aFirst = threads[a][0]?.started_at || '';
    const bFirst = threads[b][0]?.started_at || '';
    return bFirst.localeCompare(aFirst);
  });

  for (const key of threadKeys) {
    const evts = threads[key];
    const threadLabel = key.replace(/_/g, ' ');
    html += `<div class="tl-thread">
      <div class="tl-thread-title">${threadLabel} <span class="tl-thread-count">${evts.length}</span></div>
      <div class="timeline-line">`;
    evts.forEach(ev => { html += renderEvent(ev); });
    html += `</div></div>`;
  }

  // 미분류 이벤트
  if (ungrouped.length > 0) {
    html += `<div class="tl-thread">
      <div class="tl-thread-title">기타 <span class="tl-thread-count">${ungrouped.length}</span></div>
      <div class="timeline-line">`;
    ungrouped.forEach(ev => { html += renderEvent(ev); });
    html += `</div></div>`;
  }

  container.innerHTML = html;
}

// ============================================================
// Event Detail (타임라인 클릭)
// ============================================================

async function selectEvent(eventId) {
  // 타임라인 아이템 하이라이트
  document.querySelectorAll('.tl-item').forEach(el => el.style.borderLeft = 'none');
  const items = document.querySelectorAll('.tl-item');
  items.forEach(el => {
    if (el.getAttribute('onclick')?.includes(eventId)) {
      el.style.borderLeft = '3px solid var(--blue)';
    }
  });

  try {
    const res = await fetch(`/api/events/${eventId}/detail`);
    if (!res.ok) return;
    const data = await res.json();
    renderEventBriefing(data);
  } catch (e) { console.error('이벤트 상세 로딩 실패:', e); }
}

function renderEventBriefing(data) {
  const container = document.getElementById('briefing-content');
  const ev = data.event;
  const SEV_KR = { critical: '긴급', major: '중요', moderate: '보통', minor: '경미' };
  const sevLabel = SEV_KR[ev.severity] || ev.severity;
  const date = ev.started_at ? new Date(ev.started_at).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }) : '?';

  let html = `<div class="briefing-header"><div>
    <div class="briefing-title">${ev.title}</div>
    <div class="briefing-subtitle">${date} · ${sevLabel} · ${ev.event_type}</div>
  </div></div>`;

  // 요약
  if (ev.summary) {
    html += `<div class="briefing-section"><h3>요약</h3><div style="font-size:12px;line-height:1.6;color:var(--fg);">${ev.summary}</div></div>`;
  }

  // 관련 엔티티
  if (data.entities && data.entities.length > 0) {
    html += `<div class="briefing-section"><h3>관련 엔티티 (${data.entities.length})</h3><ul>`;
    data.entities.forEach(e => {
      html += `<li><strong>${e.name}</strong> <span class="rel-tag ${e.entity_type}">${e.entity_type}</span> <span style="color:var(--dim);font-size:10px;">${e.link_type}</span></li>`;
    });
    html += `</ul></div>`;
  }

  // 관련 뉴스
  if (data.news && data.news.length > 0) {
    html += `<div class="briefing-section"><h3>관련 뉴스 (${data.news.length})</h3><ul>`;
    data.news.forEach(n => {
      const pubDate = n.published_at ? new Date(n.published_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }) : '';
      html += `<li style="margin-bottom:6px;"><span style="color:var(--dim);font-size:10px;">${pubDate} [${n.source}]</span><br>${n.title}</li>`;
    });
    html += `</ul></div>`;
  } else {
    html += `<div class="briefing-section"><div style="color:var(--dim);font-size:11px;">연결된 뉴스 없음</div></div>`;
  }

  container.innerHTML = html;
}

// ============================================================
// Entity Briefing
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

  // Relationships — 중요도 순 요약
  if (rels.length > 0) {
    html += `<div class="briefing-section"><h3>주요 관계 (${rels.length})</h3><ul>`;
    rels.forEach(r => {
      const tags = r.types.map(t =>
        `<span class="rel-tag ${t.type}">${t.label}${t.count > 1 ? ' ×' + t.count : ''}</span>`
      ).join(' ');
      html += `<li style="margin-bottom:6px;"><strong>${r.name}</strong> ${tags}</li>`;
    });
    html += `</ul></div>`;
  }
  container.innerHTML = html;
}

// ============================================================
// News Ticker
// ============================================================

async function loadNewsTicker() {
  try {
    const res = await fetch('/api/news/latest?per_category=2');
    const news = await res.json();
    const track = document.getElementById('ticker-track');
    if (news.length === 0) { track.innerHTML = '<span class="ticker-text">뉴스가 없습니다</span>'; return; }

    const CAT_LABELS = { geo: 'GEO', stock_us: 'US', stock_kr: 'KR' };
    const CAT_COLORS = { geo: '#f85149', stock_us: '#58a6ff', stock_kr: '#3fb950' };
    const items = news.map(n => {
      const cat = n.category || 'geo';
      const catTag = `<span style="background:${CAT_COLORS[cat]}22;color:${CAT_COLORS[cat]};border:1px solid ${CAT_COLORS[cat]}44;padding:1px 5px;border-radius:3px;font-size:9px;margin-right:4px;font-weight:600;">${CAT_LABELS[cat]}</span>`;
      const issueTag = n.top_issue
        ? `<span style="color:#8b949e;font-size:9px;margin-right:4px;">${n.top_issue}</span>`
        : '';
      return `<span class="news-item">${catTag}${issueTag}${n.title}</span>`;
    }).join('<span class="news-dot">·</span>');

    track.innerHTML = `<span class="ticker-text">${items}<span class="news-dot">·</span>${items}</span>`;
    const text = track.querySelector('.ticker-text');
    text.style.animationDuration = `${Math.max(60, news.length * 15)}s`;
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
