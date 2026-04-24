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
let futureEvents = [];  // 미래/예정 이벤트 저장

function switchView(view) {
  currentView = view;
  document.getElementById('btn-graph').classList.toggle('active', view === 'graph');
  document.getElementById('btn-timeline').classList.toggle('active', view === 'timeline');
  document.getElementById('btn-chart').classList.toggle('active', view === 'chart');
  document.getElementById('btn-essence').classList.toggle('active', view === 'essence');
  document.getElementById('graph-container').style.display = view === 'graph' ? '' : 'none';
  document.getElementById('timeline-container').style.display = view === 'timeline' ? '' : 'none';
  document.getElementById('chart-container').style.display = view === 'chart' ? '' : 'none';
  document.getElementById('essence-container').style.display = view === 'essence' ? '' : 'none';

  if (view === 'chart' && !lwChartInitialized) {
    initLightweightChart();
    lwChartInitialized = true;
  }

  // Essence 탭 선택 시 데이터 로드
  if (view === 'essence') {
    loadEssenceDashboard();
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
    handleScroll: { mouseWheel: false, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
    handleScale: {
      mouseWheel: false, pinch: true,  // 휠 줌을 커스텀 핸들러로 처리
      axisPressedMouseMove: { time: true, price: true },
      axisDoubleClickReset: { time: true, price: true },
    },
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

  // 커스텀 휠 줌: 마우스 위치로 X/Y 자동 판단
  // lightweight-charts 기본 휠 줌은 꺼놨으므로 여기서 직접 처리
  mainEl.addEventListener('wheel', (e) => {
    e.preventDefault();
    const rect = mainEl.getBoundingClientRect();
    const relX = (e.clientX - rect.left) / rect.width;

    if (relX > 0.8) {
      // 우측 20% → Y축 줌
      const ps = lwMainChart.priceScale('right');
      const opts = ps.options();
      if (opts.autoScale) ps.applyOptions({ autoScale: false });
      const curTop = opts.scaleMargins?.top || 0.1;
      const curBot = opts.scaleMargins?.bottom || 0.1;
      const d = e.deltaY > 0 ? 0.03 : -0.03;
      ps.applyOptions({
        scaleMargins: {
          top: Math.max(0.01, Math.min(0.45, curTop + d)),
          bottom: Math.max(0.01, Math.min(0.45, curBot + d)),
        },
      });
    } else {
      // 나머지 → X축 줌
      const range = lwMainChart.timeScale().getVisibleLogicalRange();
      if (!range) return;
      const barCount = range.to - range.from;
      const zoomFactor = e.deltaY > 0 ? 0.1 : -0.1;
      const delta = barCount * zoomFactor;
      const newFrom = range.from + delta / 2;
      const newTo = range.to - delta / 2;
      if (newTo - newFrom > 5) {
        _isSyncingTimeScale = true;
        lwMainChart.timeScale().setVisibleLogicalRange({ from: newFrom, to: newTo });
        lwRsiChart.timeScale().setVisibleLogicalRange({ from: newFrom, to: newTo });
        lwMacdChart.timeScale().setVisibleLogicalRange({ from: newFrom, to: newTo });
        _isSyncingTimeScale = false;
      }
    }
  }, { passive: false });

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

  // Y축 리셋 버튼
  document.getElementById('btn-y-reset')?.addEventListener('click', () => {
    lwMainChart.priceScale('right').applyOptions({ autoScale: true });
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

  // visible range 변경 시 VPVR + 미래 이벤트 업데이트 (debounce)
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

  // 미래 이벤트 토글
  lwMainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
    if (document.getElementById('show-future-events')?.checked && futureEvents && futureEvents.length > 0) {
      renderFutureEventLines(futureEvents);
    }
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

  // 미래 이벤트 토글
  const showFutureEventsCheckbox = document.getElementById('show-future-events');
  if (showFutureEventsCheckbox) {
    showFutureEventsCheckbox.addEventListener('change', (e) => {
      if (e.target.checked && futureEvents.length > 0) {
        renderFutureEventLines(futureEvents);
      } else {
        const canvas = document.getElementById('future-event-canvas');
        if (canvas) canvas.remove();
      }
    });
  }

  document.getElementById('importance-level')?.addEventListener('change', () => {
    loadChartData(currentChartPeriod);
  });

  // 리사이즈 대응
  const ro = new ResizeObserver(() => {
    lwMainChart.applyOptions({ width: mainEl.clientWidth });
    lwRsiChart.applyOptions({ width: rsiEl.clientWidth });
    lwMacdChart.applyOptions({ width: macdEl.clientWidth });

    // 미래 이벤트 캔버스 크기 동기화
    const futureCanvas = document.getElementById('future-event-canvas');
    if (futureCanvas) {
      futureCanvas.width = mainEl.clientWidth;
      futureCanvas.height = mainEl.clientHeight;
      if (document.getElementById('show-future-events')?.checked && futureEvents.length > 0) {
        renderFutureEventLines(futureEvents);
      }
    }
  });
  ro.observe(mainEl);

  // 초기 데이터 로드
  loadChartData('6mo');
}

async function loadChartData(period) {
  // 이벤트 가중 레벨: core(핵심5) / important(중요15) / all(전체50)
  const showAll = document.getElementById('show-all-events')?.checked;
  const importanceLevel = document.getElementById('importance-level')?.value
    || (showAll ? 'all' : 'important');

  try {
    const [ohlcvResp, eventsResp, signalsResp, trendResp, strategyResp, futureEventsResp] = await Promise.all([
      fetch(`/api/chart/ohlcv?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
      fetch(`/api/chart/events?symbol=TSLA&period=${period}&importance_level=${importanceLevel}`),
      fetch(`/api/chart/signals?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
      fetch(`/api/chart/trendlines?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
      fetch(`/api/chart/strategy?symbol=TSLA&period=${period}&interval=${currentChartInterval}`),
      fetch('/api/chart/future-events'),
    ]);
    const ohlcvData = await ohlcvResp.json();
    const eventsData = await eventsResp.json();
    const signalsData = await signalsResp.json();
    const trendData = await trendResp.json();
    const strategyData = await strategyResp.json();
    const futureEventsData = await futureEventsResp.json();

    // 미래 이벤트 저장
    futureEvents = futureEventsData.events || [];

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
    const channelList = trendData.channels || (trendData.channel ? [trendData.channel] : []);
    channelList.forEach(ch => {
      const isPrimSupport = ch.primary.type === 'support';
      const pattern = ch.primary.pattern || '';

      // 핵심 빗각 (굵은 실선)
      const primaryS = lwMainChart.addLineSeries({
        color: isPrimSupport ? '#26a69a' : '#ef5350',
        lineWidth: 2, lineStyle: 0,
        lastValueVisible: true, priceLineVisible: false, crosshairMarkerVisible: false,
        title: pattern === '저저고' ? '저저고 빗각' : '고고저 빗각',
      });
      primaryS.setData(ch.primary.line);
      lwTrendlineSeries.push(primaryS);

      // 채널 반대편 (굵은 실선, 같은 기울기)
      const oppositeS = lwMainChart.addLineSeries({
        color: isPrimSupport ? '#ef5350' : '#26a69a',
        lineWidth: 2, lineStyle: 0,
        lastValueVisible: true, priceLineVisible: false, crosshairMarkerVisible: false,
        title: pattern === '저저고' ? '채널 상단' : '채널 하단',
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
    });

    // 시그널 마커 통합: VWMA 시그널 + 정배열/눌림목 시그널 + 이벤트
    const vwmaMarkers = (signalsData.signals || []).map(s => ({
      time: s.time,
      position: s.type.includes('BUY') ? 'belowBar' : 'aboveBar',
      color: s.type.includes('BUY') ? '#26a69a' : '#ef5350',
      shape: s.type === 'STRONG_BUY' ? 'arrowUp' : s.type.includes('BUY') ? 'arrowUp' : 'arrowDown',
      text: s.type === 'STRONG_BUY' ? 'B+' : s.type === 'BUY' ? 'B' : 'S',
      size: s.type === 'STRONG_BUY' ? 3 : 2,
    }));
    const strategyMarkers = (strategyData.signals || []).map(s => {
      const isBuy = s.type.includes('BUY') || s.type === 'PERFECT_ORDER_START';
      return {
        time: s.time,
        position: isBuy ? 'belowBar' : 'aboveBar',
        color: s.color || (isBuy ? '#3fb950' : '#ef5350'),
        shape: isBuy ? 'arrowUp' : 'arrowDown',
        text: s.text,
        size: ['STRONG_SELL', 'PULLBACK_BUY'].includes(s.type) ? 3 : 2,
      };
    });
    const signalMarkers = [...vwmaMarkers, ...strategyMarkers];
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

    // 추세 상태 표시 업데이트 (정배열/역배열 우선)
    const trendEl = document.getElementById('chart-indicator-summary');
    if (trendEl) {
      const stateColors = { PERFECT_ORDER: 'var(--green)', REVERSE_ORDER: 'var(--red)', TRANSITION: 'var(--yellow)' };
      const stateLabels = { PERFECT_ORDER: '정배열 ▲', REVERSE_ORDER: '역배열 ▼', TRANSITION: '과도기' };
      const state = strategyData.current_state;
      if (state && stateLabels[state]) {
        const stateHtml = `<span style="color:${stateColors[state]};font-weight:700">${stateLabels[state]}</span>`;
        trendEl.innerHTML = trendEl.innerHTML.replace(/· ST [▲▼]/, `· ${stateHtml}`);
      }
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
        // 미래 이벤트 수직 점선 렌더링
        if (document.getElementById('show-future-events')?.checked && futureEvents.length > 0) {
          renderFutureEventLines(futureEvents);
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
    size: m.severity === 'critical' ? 2 : m.is_tesla_direct ? 2 : 1,
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

  list.innerHTML = sorted.map(m => {
    const teslaTag = m.is_tesla_direct ? ' · <span style="color:#26a69a;font-weight:600">TSLA</span>' : '';
    const relTag = m.relevance_label ? ` · ${m.relevance_label}` : '';
    const impTag = m.importance ? `<span style="color:#f59e0b;font-weight:600;float:right">★${m.importance.toFixed(0)}</span>` : '';
    return `
    <div class="chart-event-item">
      <div class="ev-date">
        <span class="ev-severity" style="background:${m.color}"></span>
        ${m.time} · ${m.severity}${relTag}${teslaTag}
        ${impTag}
      </div>
      <div class="ev-title">
        <span class="ev-badge" style="background:${m.color}22;color:${m.color}">${m.category_label}</span>
        ${m.title.length > 50 ? m.title.slice(0, 50) + '...' : m.title}
      </div>
    </div>`;
  }).join('');
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
// 미래 이벤트 수직 점선 + 라벨 렌더링
// ============================================================

function renderFutureEventLines(events) {
  const mainEl = document.getElementById('lw-main-chart');
  if (!mainEl || !lwMainChart) return;

  // 기존 캔버스 제거
  let canvas = document.getElementById('future-event-canvas');
  if (canvas) canvas.remove();

  // 새 캔버스 생성
  canvas = document.createElement('canvas');
  canvas.id = 'future-event-canvas';
  canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:3;';
  mainEl.style.position = 'relative';
  mainEl.appendChild(canvas);

  // 캔버스 크기 동기화
  canvas.width = mainEl.clientWidth;
  canvas.height = mainEl.clientHeight;

  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const timeScale = lwMainChart.timeScale();

  events.forEach(evt => {
    // 날짜를 lightweight-charts 시간으로 변환
    const ts = new Date(evt.date).getTime() / 1000;
    const x = timeScale.timeToCoordinate(ts);
    if (x === null || x < 0 || x > canvas.width) return;

    // 수직 점선
    ctx.setLineDash([5, 5]);
    ctx.strokeStyle = evt.color;
    ctx.globalAlpha = evt.is_past ? 0.4 : 0.8;
    ctx.lineWidth = evt.importance === 'critical' ? 2 : 1;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();

    // 라벨
    ctx.setLineDash([]);
    ctx.globalAlpha = evt.is_past ? 0.5 : 1.0;
    ctx.font = '11px sans-serif';
    ctx.fillStyle = evt.color;
    ctx.save();
    ctx.translate(x + 4, 20);
    ctx.rotate(-Math.PI / 6);  // 30도 기울임
    const label = evt.title.length > 15 ? evt.title.slice(0, 15) + '…' : evt.title;
    ctx.fillText(label, 0, 0);
    ctx.restore();
  });

  ctx.globalAlpha = 1.0;
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
    // 브리핑과 속성 3단 분류를 병렬로 fetch
    const [briefingRes, propsRes] = await Promise.all([
      fetch(`/api/entities/${entityId}/briefing`),
      fetch(`/api/entities/${entityId}/properties`).catch(() => null), // 실패 시 null 처리
    ]);
    if (!briefingRes.ok) return;
    const briefingData = await briefingRes.json();
    const classifiedProps = propsRes?.ok ? await propsRes.json() : null;
    renderBriefing(briefingData, classifiedProps);
  } catch (e) { console.error('브리핑 로딩 실패:', e); }
}

function renderBriefing(data, classifiedProps = null) {
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

  // 3단 분류 속성이 있으면 우선 표시
  if (classifiedProps && (classifiedProps.essential || classifiedProps.propria || classifiedProps.accidental)) {
    html += renderClassifiedProperties(classifiedProps);
  }

  // Structured properties (기존 로직 - 폴백)
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
// 3단 분류 속성 렌더링 헬퍼 함수
// ============================================================

/**
 * 3단 분류 속성을 HTML로 렌더링
 * @param {Object} classifiedProps - { essential: [], propria: [], accidental: [] }
 * @returns {string} HTML 문자열
 */
function renderClassifiedProperties(classifiedProps) {
  let html = '';

  // 본질 (Essential) - 파란 좌측 보더
  if (classifiedProps.essential && classifiedProps.essential.length > 0) {
    html += `<div class="briefing-section">
      <h3 style="color:var(--blue);border-left:3px solid var(--blue);padding-left:8px;">본질 (Essential)</h3>
      <div class="props-container">`;
    for (const prop of classifiedProps.essential) {
      html += renderPropertyItem(prop, 'essential');
    }
    html += `</div></div>`;
  }

  // 고유 (Propria) - 초록 좌측 보더
  if (classifiedProps.propria && classifiedProps.propria.length > 0) {
    html += `<div class="briefing-section">
      <h3 style="color:var(--green);border-left:3px solid var(--green);padding-left:8px;">고유 (Propria)</h3>
      <div class="props-container">`;
    for (const prop of classifiedProps.propria) {
      html += renderPropertyItem(prop, 'propria');
    }
    html += `</div></div>`;
  }

  // 기타 (Accidental) - 회색 좌측 보더, 디폴트 숨김 (토글 가능)
  if (classifiedProps.accidental && classifiedProps.accidental.length > 0) {
    const accidentalId = 'accidental-' + Date.now();
    html += `<div class="briefing-section">
      <h3 style="color:var(--dim);border-left:3px solid var(--dim);padding-left:8px;cursor:pointer;" onclick="togglePropsSection('${accidentalId}')">
        <span class="props-toggle">▶</span> 기타 (Accidental) <span style="font-size:10px;color:var(--dim);">(${classifiedProps.accidental.length})</span>
      </h3>
      <div class="props-container" id="${accidentalId}" style="display:none;">`;
    for (const prop of classifiedProps.accidental) {
      html += renderPropertyItem(prop, 'accidental');
    }
    html += `</div></div>`;
  }

  return html;
}

/**
 * 개별 속성 항목 렌더링
 * @param {Object} prop - { label: string, value: string|string[] }
 * @param {string} category - 'essential'|'propria'|'accidental'
 * @returns {string} HTML 문자열
 */
function renderPropertyItem(prop, category) {
  const valueHtml = Array.isArray(prop.value)
    ? `<ul style="margin:4px 0;padding-left:16px;">${prop.value.map(v => `<li style="font-size:11px;color:var(--white);margin-bottom:2px;">${v}</li>`).join('')}</ul>`
    : `<span style="font-size:11px;color:var(--white);">${prop.value}</span>`;

  const labelWeight = category === 'essential' ? 'font-weight:600;' : '';
  const labelColor = category === 'accidental' ? 'color:var(--dim);' : 'color:var(--dim);';

  return `<div class="props-item" style="margin-bottom:8px;">
    <div class="props-label" style="${labelWeight}${labelColor}">${prop.label}</div>
    <div class="props-value">${valueHtml}</div>
  </div>`;
}

/**
 * 속성 섹션 토글 (기타 접기/펼치기)
 * @param {string} sectionId - 토글할 섹션의 ID
 */
function togglePropsSection(sectionId) {
  const section = document.getElementById(sectionId);
  const toggle = section.previousElementSibling.querySelector('.props-toggle');
  if (section.style.display === 'none') {
    section.style.display = 'block';
    toggle.textContent = '▼';
  } else {
    section.style.display = 'none';
    toggle.textContent = '▶';
  }
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
// Essence Dashboard
// ============================================================

/**
 * Essence 대시보드 로드
 * 7개 API 병렬 호출 후 렌더링 (실패 시 null 처리)
 */
async function loadEssenceDashboard() {
  const container = document.getElementById('essence-content');
  if (!container) return;

  // 로딩 표시
  container.innerHTML = '<div class="empty-state">Essence 데이터 로딩 중...</div>';

  try {
    const [thesisRes, timelineRes, topicsRes, essenceRes, moatRes, planRes, issuesRes] = await Promise.all([
      fetch('/api/tesla/thesis').catch(() => null),
      fetch('/api/tesla/timeline').catch(() => null),
      fetch('/api/tesla/topics').catch(() => null),
      fetch('/api/tesla/essence').catch(() => null),
      fetch('/api/tesla/moat').catch(() => null),
      fetch('/api/tesla/master-plan').catch(() => null),
      fetch('/api/tesla/issues/tagged?limit=10').catch(() => null),
    ]);

    const thesisData = thesisRes?.ok ? await thesisRes.json() : null;
    const timelineData = timelineRes?.ok ? await timelineRes.json() : null;
    const topicsData = topicsRes?.ok ? await topicsRes.json() : null;
    const essenceData = essenceRes?.ok ? await essenceRes.json() : null;
    const moatData = moatRes?.ok ? await moatRes.json() : null;
    const planData = planRes?.ok ? await planRes.json() : null;
    const issuesData = issuesRes?.ok ? await issuesRes.json() : null;

    renderEssenceDashboard(thesisData, timelineData, topicsData, essenceData, moatData, planData, issuesData);
  } catch (e) {
    console.error('Essence 데이터 로딩 실패:', e);
    container.innerHTML = '<div class="empty-state">데이터 로딩 실패</div>';
  }
}

/**
 * Essence 대시보드 렌더링
 * @param {Object} thesisData - Thesis 데이터
 * @param {Object} timelineData - Timeline 데이터
 * @param {Object} topicsData - Topics 데이터
 * @param {Object} essenceData - Essence 4축 데이터
 * @param {Object} moatData - MOAT 데이터
 * @param {Object} planData - Master Plan 데이터
 * @param {Object} issuesData - 최신 이슈 데이터
 */
function renderEssenceDashboard(thesisData, timelineData, topicsData, essenceData, moatData, planData, issuesData) {
  const container = document.getElementById('essence-content');
  if (!container) return;

  let html = '';

  // 상단: Thesis, Essence Timeline, Topics Overview
  html += renderThesis(thesisData);
  html += renderEssenceTimeline(timelineData);
  html += renderTopicsOverview(topicsData);

  // 중단: Essence 4축
  html += renderEssenceAxes(essenceData);

  // 하단: MOAT + Master Plan (2열)
  html += renderMoatAndPlan(moatData, planData);

  // 최하단: 오늘의 이슈
  html += renderTodayIssues(issuesData);

  container.innerHTML = html;
}

/**
 * Essence 4축 카드 렌더링
 * @param {Object} data - { axes: [{ label_ko, score, delta_7d, last_event_title, color }] }
 * @returns {string} HTML
 */
function renderEssenceAxes(data) {
  const axes = data?.components || [];
  if (axes.length === 0) return '<div class="empty-state">Essence 데이터 없음</div>';

  const cards = axes.map(axis => {
    const score = axis.score || 0;
    const delta = axis.delta_7d || 0;
    const deltaColor = delta > 0 ? 'var(--green)' : delta < 0 ? 'var(--red)' : 'var(--dim)';
    const deltaSign = delta > 0 ? '+' : '';
    const scoreColor = score >= 70 ? 'var(--green)' : score >= 50 ? 'var(--yellow)' : 'var(--red)';

    return `<div class="essence-card" style="border-top:4px solid ${axis.color || 'var(--dim)'};">
      <div class="essence-label">${axis.label_ko || 'Unknown'}</div>
      <div class="essence-score" style="color:${scoreColor}">${score}</div>
      <div class="essence-delta" style="color:${deltaColor}">7일 ${deltaSign}${delta}</div>
      ${axis.last_event_title ? `<div class="essence-event">${axis.last_event_title}</div>` : ''}
    </div>`;
  }).join('');

  return `<div class="essence-grid">${cards}</div>`;
}

/**
 * MOAT + Master Plan 2열 렌더링
 * @param {Object} moatData - { moats: [{ moat_type, strength }] }
 * @param {Object} planData - { initiatives: [{ name, progress_pct }] }
 * @returns {string} HTML
 */
function renderMoatAndPlan(moatData, planData) {
  let html = '<div class="moat-plan-grid">';

  // 왼쪽: MOAT
  html += '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;">';
  html += '<div class="panel-title" style="margin-bottom:12px;">MOAT 현재 상태</div>';
  const moats = moatData?.moats || [];
  if (moats.length > 0) {
    moats.forEach(moat => {
      const strength = moat.strength || 0;
      const color = strength >= 70 ? 'var(--green)' : strength >= 50 ? 'var(--yellow)' : 'var(--red)';
      html += `
        <div style="font-size:11px;color:var(--white);margin-bottom:2px;">${moat.moat_type}</div>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${strength}%;background:${color};"></div>
        </div>
      `;
    });
  } else {
    html += '<div style="color:var(--dim);font-size:11px;">MOAT 데이터 없음</div>';
  }
  html += '</div>';

  // 오른쪽: Master Plan
  html += '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;">';
  html += '<div class="panel-title" style="margin-bottom:12px;">Master Plan 진행도</div>';
  const initiatives = planData?.initiatives || [];
  if (initiatives.length > 0) {
    initiatives.forEach(init => {
      const progress = init.progress_pct || 0;
      const color = progress >= 70 ? 'var(--green)' : progress >= 50 ? 'var(--yellow)' : 'var(--red)';
      html += `
        <div style="font-size:11px;color:var(--white);margin-bottom:2px;">${init.label_ko || init.initiative}</div>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${progress}%;background:${color};"></div>
        </div>
      `;
    });
  } else {
    html += '<div style="color:var(--dim);font-size:11px;">Master Plan 데이터 없음</div>';
  }
  html += '</div>';

  html += '</div>';
  return html;
}

/**
 * 오늘의 이슈 렌더링
 * @param {Object} issuesData - { issues: [{ title, essence_component, severity, sentiment }] }
 * @returns {string} HTML
 */
function renderTodayIssues(issuesData) {
  let html = '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;">';
  html += '<div class="panel-title" style="margin-bottom:12px;">오늘의 이슈</div>';

  const issues = issuesData?.issues || [];
  if (issues.length > 0) {
    issues.forEach(issue => {
      const component = issue.essence_component || 'noise';
      const badgeColor = component === 'noise' ? 'var(--dim)' : getComponentColor(component);
      const severity = issue.severity || 'moderate';
      const sentiment = issue.sentiment || 'neutral';
      const sentimentColor = sentiment === 'positive' ? 'var(--green)' : sentiment === 'negative' ? 'var(--red)' : 'var(--dim)';

      html += `
        <div class="issue-row" style="border-left:3px solid ${sentimentColor};">
          <span class="essence-badge" style="background:${badgeColor}22;color:${badgeColor};">${component}</span>
          <span style="flex:1;font-size:12px;color:var(--white);">${issue.title}</span>
          <span class="essence-badge" style="background:var(--border);color:var(--dim);">${severity}</span>
        </div>
      `;
    });
  } else {
    html += '<div style="color:var(--dim);font-size:11px;">이슈 없음</div>';
  }

  html += '</div>';
  return html;
}

/**
 * Essence 컴포넌트별 색상 반환
 * @param {string} component - essence_component 값
 * @returns {string} CSS 색상 값
 */
function getComponentColor(component) {
  const colors = {
    'innovation': 'var(--blue)',
    'manufacturing': 'var(--cyan)',
    'energy': 'var(--yellow)',
    'software': 'var(--purple)',
    'market': 'var(--green)',
  };
  return colors[component] || 'var(--dim)';
}

// ============================================================
// Essence Dashboard - 신규 렌더링 함수
// ============================================================

/**
 * Thesis 섹션 렌더링
 * @param {Object} data - { date, overall_label, bull: [], bear: [] }
 * @returns {string} HTML
 */
function renderThesis(data) {
  if (!data || !data.bull || !data.bear) {
    return '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;"><div style="color:var(--dim);font-size:11px;">Thesis 데이터 없음</div></div>';
  }

  const date = data.date || new Date().toLocaleDateString('ko-KR');
  const overall = data.overall_label || 'Neutral';
  const overallColor = overall === 'Bullish' ? 'var(--green)' : overall === 'Bearish' ? 'var(--red)' : 'var(--dim)';
  const bullCount = data.bull.length;
  const bearCount = data.bear.length;
  const delta = bullCount - bearCount;
  const deltaSign = delta > 0 ? '+' : '';
  const deltaColor = delta > 0 ? 'var(--green)' : delta < 0 ? 'var(--red)' : 'var(--dim)';

  let html = `<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
      <div style="font-size:14px;font-weight:700;color:var(--white);">TESLA THESIS — ${date}</div>
      <div style="display:flex;align-items:center;gap:8px;">
        <span class="essence-badge" style="background:${overallColor}22;color:${overallColor};">${overall}</span>
        <span style="font-size:11px;color:var(--white);">Bull ${bullCount} | Bear ${bearCount} | Net <span style="color:${deltaColor};">${deltaSign}${delta}</span></span>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
      <!-- Bull Column -->
      <div class="bull-column" style="border-top:3px solid var(--green);padding-top:8px;">
        <div style="font-size:11px;font-weight:600;color:var(--green);margin-bottom:8px;">BULL CASE</div>
        ${data.bull.map(theme => renderThesisItem(theme, 'bull')).join('')}
      </div>
      <!-- Bear Column -->
      <div class="bear-column" style="border-top:3px solid var(--red);padding-top:8px;">
        <div style="font-size:11px;font-weight:600;color:var(--red);margin-bottom:8px;">BEAR CASE</div>
        ${data.bear.map(theme => renderThesisItem(theme, 'bear')).join('')}
      </div>
    </div>
  </div>`;

  return html;
}

/**
 * Thesis 항목 렌더링 헬퍼
 * @param {Object} theme - { title, detail, impact_label_ko, delta, period, date, occurred_at }
 * @param {string} type - 'bull' 또는 'bear'
 * @returns {string} HTML
 */
function renderThesisItem(theme, type) {
  const delta = theme.delta || 0;
  const deltaSign = delta > 0 ? '+' : '';
  const deltaColor = delta > 0 ? 'var(--green)' : delta < 0 ? 'var(--red)' : 'var(--dim)';
  const impactColor = type === 'bull' ? 'var(--green)' : 'var(--red)';
  // occurred_at 필드 우선 사용, 없으면 date 폴백
  const themeDate = theme.occurred_at || theme.date;

  return `<div style="margin-bottom:10px;padding:8px;background:var(--bg);border-radius:4px;">
    <div style="font-size:12px;font-weight:600;color:var(--white);margin-bottom:2px;">${theme.title || '-'}</div>
    <div style="font-size:11px;color:var(--dim);margin-bottom:4px;">${theme.detail || ''}</div>
    <div style="display:flex;align-items:center;justify-content:space-between;">
      <span class="essence-badge" style="background:${impactColor}22;color:${impactColor};font-size:9px;padding:2px 6px;">${theme.impact_label_ko || '-'}</span>
      <div style="text-align:right;">
        <div style="font-size:11px;font-weight:600;color:${deltaColor};">${deltaSign}${delta}${theme.period ? ` (${theme.period})` : ''}</div>
        <div style="font-size:10px;color:var(--dim);">${themeDate || '-'}</div>
      </div>
    </div>
  </div>`;
}

/**
 * Essence Timeline 렌더링 (SVG 기반)
 * @param {Object} data - { events: [{ date, title, impact, impact_label_ko, topic, thesis_side, detail }], days_back, days_forward }
 * @returns {string} HTML
 */
function renderEssenceTimeline(data) {
  if (!data || !data.events || data.events.length === 0) {
    return '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;"><div style="color:var(--dim);font-size:11px;">Timeline 데이터 없음</div></div>';
  }

  const events = data.events || [];
  const topics = data.topics || [];
  const daysBack = data.days_back || 28;
  const daysForward = data.days_forward || 56;
  const totalDays = daysBack + daysForward;

  // SVG 기본 설정 (반응형 viewBox)
  const svgWidth = 1000;
  const leftMargin = 120; // 왼쪽 topic 라벨 영역
  const headerH = 40; // 상단 눈금 영역
  const laneH = 50; // 각 topic 레인 높이
  const svgHeight = headerH + topics.length * laneH + 20;

  // 오늘 날짜 계산
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 이벤트 전처리: 날짜 계산 및 topic 인덱스 매핑
  const topicIdxMap = {};
  topics.forEach((t, i) => {
    topicIdxMap[t.id] = i;
  });

  const processedEvents = events.map(ev => {
    const eventDate = ev.occurred_at || ev.date;
    const evDate = new Date(eventDate);
    evDate.setHours(0, 0, 0, 0);
    const diffDays = Math.floor((evDate - today) / (1000 * 60 * 60 * 24));
    const isPast = diffDays < 0;

    // topic별 인덱스 매핑 (null이면 'other' 레인)
    let topicIdx = topicIdxMap[ev.topic];
    if (topicIdx === undefined) {
      const otherTopic = topics.find(t => t.id === 'other');
      topicIdx = otherTopic ? topicIdxMap['other'] : topics.length - 1;
    }

    // X 좌표 계산
    const x = leftMargin + (diffDays + daysBack) / totalDays * (svgWidth - leftMargin);

    // Y 좌표 (레인 중앙)
    const y = headerH + topicIdx * laneH + laneH / 2;

    // 점 반지름 (impact_level 기준)
    const impactLevel = ev.impact_level || 'minor';
    let radius = 4;
    if (impactLevel === 'critical') radius = 8;
    else if (impactLevel === 'major') radius = 6;
    else if (impactLevel === 'moderate') radius = 5;

    // 색상 (thesis_side 기준)
    const thesisSide = ev.thesis_side || 'neutral';
    let color = '#8b949e';
    if (thesisSide === 'bull') color = '#3fb950';
    else if (thesisSide === 'bear') color = '#f85149';

    // 라벨 (8자 제한)
    const label = ev.title.length > 8 ? ev.title.slice(0, 8) + '…' : ev.title;

    return { ...ev, diffDays, x, y, isPast, topicIdx, radius, color, label, eventDate };
  });

  // topic별로 이벤트 정렬 (x축 기준)
  const eventsByTopic = {};
  topics.forEach((t, i) => {
    eventsByTopic[i] = processedEvents
      .filter(ev => ev.topicIdx === i)
      .sort((a, b) => a.x - b.x);
  });

  // SVG 요소 생성
  let bgLayers = '';
  let topicLabels = '';
  let eventCircles = '';
  let eventLabels = '';

  // 1. 배경 레이어 (zebra stripe)
  topics.forEach((t, i) => {
    const y = headerH + i * laneH;
    const isEven = i % 2 === 0;
    const bgClass = isEven ? 'swimlane-row-even' : 'swimlane-row-odd';
    bgLayers += `<rect x="0" y="${y}" width="${svgWidth}" height="${laneH}" class="${bgClass}" />`;
  });

  // 2. 왼쪽 topic 라벨
  topics.forEach((t, i) => {
    const y = headerH + i * laneH + laneH / 2;

    // essence_component별 색상
    let dotColor = '#8b949e';
    const comp = t.essence_component;
    if (comp === 'autonomy_robotics') dotColor = '#d29922';
    else if (comp === 'vertical_integration') dotColor = '#3fb950';
    else if (comp === 'clean_energy_mission') dotColor = '#58a6ff';
    else if (comp === 'first_principle_engineering') dotColor = '#bc8cff';

    topicLabels += `
      <circle cx="15" cy="${y}" r="3" fill="${dotColor}" />
      <text x="24" y="${y + 4}" font-size="11" font-weight="600" fill="var(--fg)" text-anchor="start">${t.name_ko || t.id}</text>
    `;
  });

  // 3. 이벤트 및 라벨 (레인별 충돌 감지)
  const laneLastEndX = {}; // 각 레인의 마지막 라벨 끝 위치

  Object.keys(eventsByTopic).forEach(topicIdx => {
    const laneEvents = eventsByTopic[topicIdx];
    laneLastEndX[topicIdx] = leftMargin - 4; // 초기화

    laneEvents.forEach(ev => {
      // 점 스타일
      const fillStyle = ev.isPast ? `fill="${ev.color}"` : `fill="none" stroke="${ev.color}" stroke-width="2"`;

      eventCircles += `<circle cx="${ev.x}" cy="${ev.y}" r="${ev.radius}" ${fillStyle} class="swimlane-event-circle"
        data-title="${ev.title}" data-date="${ev.eventDate}" data-days="${ev.diffDays}"
        data-impact="${ev.impact_label_ko || ''}" data-side="${ev.thesis_side}"
        data-source="${ev.source || ''}" data-topic="${ev.topic || ''}" style="cursor:pointer;" />`;

      // 라벨 충돌 감지
      const labelWidth = ev.label.length * 6 + 4; // 대략적인 폭
      const labelStartX = ev.x + ev.radius + 4;
      const labelEndX = labelStartX + labelWidth;

      // 이전 라벨과 4px 이상 간격이 필요
      if (labelStartX > laneLastEndX[topicIdx] + 4) {
        eventLabels += `<text x="${labelStartX}" y="${ev.y + 3}" font-size="10"
          fill="${ev.color}" text-anchor="start" class="swimlane-label">${ev.label}</text>`;
        laneLastEndX[topicIdx] = labelEndX;
      }
      // 충돌 시 라벨 생략 (호버로만 확인)
    });
  });

  // 4. 과거/미래 배경
  const todayX = leftMargin + (daysBack / totalDays) * (svgWidth - leftMargin);
  const pastBg = `<rect x="${leftMargin}" y="${headerH}" width="${todayX - leftMargin}" height="${topics.length * laneH}" fill="rgba(139,148,158,0.04)" />`;
  const futureBg = `<rect x="${todayX}" y="${headerH}" width="${svgWidth - todayX}" height="${topics.length * laneH}" fill="rgba(64,149,255,0.04)" />`;

  // 5. 오늘 수직선
  const todayLine = `<line x1="${todayX}" y1="0" x2="${todayX}" y2="${svgHeight}" stroke="#e5c07b" stroke-width="2" />`;
  const todayLabel = `
    <rect x="${todayX - 22}" y="2" width="44" height="16" rx="3" fill="#e5c07b" />
    <text x="${todayX}" y="13" text-anchor="middle" font-size="9" font-weight="700" fill="#1a1a1a">TODAY</text>
  `;

  // 6. X축 눈금 (상단)
  const tickDays = [-28, -21, -14, -7, 0, 14, 28, 42, 56];
  let xAxisTicks = '';
  tickDays.forEach(days => {
    const x = leftMargin + (days + daysBack) / totalDays * (svgWidth - leftMargin);
    const tickDate = new Date(today);
    tickDate.setDate(tickDate.getDate() + days);
    const mm = String(tickDate.getMonth() + 1).padStart(2, '0');
    const dd = String(tickDate.getDate()).padStart(2, '0');
    const dateLabel = `${mm}/${dd}`;

    xAxisTicks += `
      <line x1="${x}" y1="25" x2="${x}" y2="${svgHeight}" stroke="var(--dim)" stroke-width="1" opacity="0.1" />
      <text x="${x}" y="20" text-anchor="middle" font-size="9" fill="var(--dim)">${dateLabel}</text>
    `;
  });

  const svg = `
    <svg width="100%" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg" class="swimlane-timeline-svg">
      <style>
        .swimlane-row-even { fill: var(--bg); }
        .swimlane-row-odd { fill: var(--bg); opacity: 0.7; }
        .swimlane-event-circle { transition: r 0.15s ease; }
        .swimlane-event-circle:hover { r: 10 !important; stroke-width: 3 !important; }
        .swimlane-tooltip {
          position: fixed;
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 10px 12px;
          font-size: 11px;
          color: var(--white);
          z-index: 1000;
          pointer-events: none;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          max-width: 280px;
        }
        .swimlane-tooltip .tt-title { font-weight: 600; margin-bottom: 4px; color: var(--white); }
        .swimlane-tooltip .tt-date { font-size: 10px; color: var(--dim); margin-bottom: 4px; }
        .swimlane-tooltip .tt-impact { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 9px; margin-bottom: 4px; }
        .swimlane-tooltip .tt-detail { font-size: 10px; color: var(--fg); line-height: 1.4; }
        .tt-impact.bull { background: rgba(63, 185, 80, 0.2); color: #3fb950; }
        .tt-impact.bear { background: rgba(248, 81, 73, 0.2); color: #f85149; }
        .tt-impact.neutral { background: rgba(139, 148, 158, 0.2); color: #8b949e; }
      </style>

      <!-- 배경 -->
      ${bgLayers}
      ${pastBg}
      ${futureBg}

      <!-- X축 눈금 -->
      ${xAxisTicks}

      <!-- 오늘 선 -->
      ${todayLine}
      ${todayLabel}

      <!-- Topic 라벨 -->
      ${topicLabels}

      <!-- 이벤트 점 -->
      ${eventCircles}

      <!-- 이벤트 라벨 -->
      ${eventLabels}
    </svg>
    <script>
      (function() {
        // 호버 툴팁
        const svg = document.querySelector('.swimlane-timeline-svg');
        if (!svg) return;

        svg.addEventListener('mouseenter', '.swimlane-event-circle', function(e) {
          const circle = e.target;
          const title = circle.getAttribute('data-title');
          const date = circle.getAttribute('data-date');
          const days = circle.getAttribute('data-days');
          const impact = circle.getAttribute('data-impact');
          const side = circle.getAttribute('data-side');
          const source = circle.getAttribute('data-source');

          const daysLabel = days >= 0 ? 'D+' + days : 'D' + days;

          const tooltip = document.createElement('div');
          tooltip.className = 'swimlane-tooltip';
          tooltip.innerHTML = \`
            <div class="tt-title">\${title}</div>
            <div class="tt-date">발생일: \${date} (\${daysLabel})</div>
            <div class="tt-impact \${side}">\${impact || side}</div>
            \${source ? \`<div class="tt-detail">출처: \${source}</div>\` : ''}
          \`;

          document.body.appendChild(tooltip);

          const updateTooltipPos = (e) => {
            const x = e.pageX + 12;
            const y = e.pageY - 12;
            tooltip.style.left = x + 'px';
            tooltip.style.top = y + 'px';
          };

          updateTooltipPos(e);
          circle.addEventListener('mousemove', updateTooltipPos);

          circle.addEventListener('mouseleave', () => {
            tooltip.remove();
          }, { once: true });
        }, true);

        // 클릭: topic 스크롤
        svg.addEventListener('click', '.swimlane-event-circle', function(e) {
          const topicId = e.target.getAttribute('data-topic');
          if (topicId) {
            const topicEl = document.getElementById('topic-' + topicId);
            if (topicEl) {
              topicEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
              topicEl.style.borderColor = 'var(--blue)';
              setTimeout(() => {
                topicEl.style.borderColor = 'var(--border)';
              }, 2000);
            }
          }
        }, true);
      })();
    </script>
  `;

  return `<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;">
    <div class="panel-title" style="margin-bottom:12px;">Essence Timeline (Topics Swimlane)</div>
    ${svg}
  </div>`;
}

/**
 * Topics Overview 렌더링
 * @param {Object} data - { topics: [{ id, name_ko, status, progress_pct, essence_component }] }
 * @returns {string} HTML
 */
function renderTopicsOverview(data) {
  if (!data || !data.topics || data.topics.length === 0) {
    return '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;"><div style="color:var(--dim);font-size:11px;">Topics 데이터 없음</div></div>';
  }

  const topics = data.topics || [];

  let html = '<div class="panel-section" style="background:var(--card);border-radius:8px;padding:16px;margin-bottom:16px;">';
  html += '<div class="panel-title" style="margin-bottom:12px;">Essence Topics</div>';

  topics.forEach(topic => {
    const statusColor = topic.status === 'on_track' ? 'var(--green)' : topic.status === 'delayed' ? 'var(--red)' : topic.status === 'accelerating' ? 'var(--blue)' : 'var(--dim)';
    const statusLabel = topic.status === 'on_track' ? '정상' : topic.status === 'delayed' ? '지연' : topic.status === 'accelerating' ? '가속' : topic.status || '-';
    const progress = topic.progress_pct || 0;
    const componentColor = getComponentColor(topic.essence_component);

    html += `<div id="topic-${topic.id}" class="topic-card" style="background:var(--bg);border-radius:6px;padding:12px;margin-bottom:8px;cursor:pointer;border:1px solid var(--border);" onclick="toggleTopicCard(this, '${topic.id}')">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="font-size:12px;font-weight:600;color:var(--white);">${topic.name_ko || '-'}</span>
          <span class="essence-badge" style="background:${statusColor}22;color:${statusColor};font-size:9px;">${statusLabel}</span>
        </div>
        <span class="topic-toggle-icon" style="font-size:10px;color:var(--dim);">▶</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <div class="progress-bar" style="flex:1;height:4px;border-radius:2px;background:var(--border);">
          <div class="progress-fill" style="width:${progress}%;background:${statusColor};height:100%;border-radius:2px;"></div>
        </div>
        <span style="font-size:10px;color:var(--dim);">${progress}%</span>
      </div>
      <div style="display:flex;align-items:center;gap:4px;">
        <span class="essence-badge" style="background:${componentColor}22;color:${componentColor};font-size:9px;">${topic.essence_component || '-'}</span>
      </div>
      <div class="topic-detail" style="display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--border);">
        <div style="color:var(--dim);font-size:10px;text-align:center;">로딩 중...</div>
      </div>
    </div>`;
  });

  html += '</div>';
  return html;
}

/**
 * Topic 카드 토글 및 Lazy Load
 * @param {HTMLElement} cardEl - 클릭된 카드 엘리먼트
 * @param {string} topicId - Topic ID
 */
async function toggleTopicCard(cardEl, topicId) {
  const detailEl = cardEl.querySelector('.topic-detail');
  const toggleIcon = cardEl.querySelector('.topic-toggle-icon');

  if (detailEl.style.display === 'none') {
    // 펼치기
    detailEl.style.display = 'block';
    toggleIcon.textContent = '▼';

    // Lazy load: 이미 로드되지 않았으면 데이터 fetch
    if (!detailEl.dataset.loaded) {
      try {
        const res = await fetch(`/api/tesla/topics/${topicId}/quarterly`);
        if (res.ok) {
          const data = await res.json();
          renderQuarterlyDetail(detailEl, data);
          detailEl.dataset.loaded = 'true';
        } else {
          detailEl.innerHTML = '<div style="color:var(--red);font-size:10px;text-align:center;">로딩 실패</div>';
        }
      } catch (e) {
        console.error('Topic 상세 로딩 실패:', e);
        detailEl.innerHTML = '<div style="color:var(--red);font-size:10px;text-align:center;">로딩 실패</div>';
      }
    }
  } else {
    // 접기
    detailEl.style.display = 'none';
    toggleIcon.textContent = '▶';
  }
}

/**
 * Quarterly Detail 렌더링
 * @param {HTMLElement} container - 렌더링할 컨테이너
 * @param {Object} data - { quarters: [{ quarter, title, outcome, impact_label, confidence, preconditions, is_past }] }
 */
function renderQuarterlyDetail(container, data) {
  if (!data || !data.quarters || data.quarters.length === 0) {
    container.innerHTML = '<div style="color:var(--dim);font-size:10px;text-align:center;">데이터 없음</div>';
    return;
  }

  const quarters = data.quarters || [];
  const pastQuarters = quarters.filter(q => q.is_past);
  const futureQuarters = quarters.filter(q => !q.is_past);

  let html = '';

  // 과거 분기
  if (pastQuarters.length > 0) {
    html += '<div style="margin-bottom:12px;"><div style="font-size:11px;font-weight:600;color:var(--white);margin-bottom:6px;">과거 실적</div>';
    pastQuarters.forEach(q => {
      // 과거 이벤트: occurred_at 표시
      const displayDate = q.occurred_at ? new Date(q.occurred_at).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' }) : '';
      html += `<div style="padding:6px;background:var(--bg);border-radius:4px;margin-bottom:4px;border-left:2px solid var(--border);">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2px;">
          <span style="font-size:11px;font-weight:600;color:var(--white);">${q.quarter || '-'}</span>
          <span class="essence-badge" style="background:var(--border);color:var(--white);font-size:9px;">${q.impact_label || '-'}</span>
        </div>
        <div style="font-size:10px;color:var(--white);margin-bottom:2px;">${q.title || '-'}</div>
        ${q.outcome ? `<div style="font-size:10px;color:var(--dim);">결과: ${q.outcome}</div>` : ''}
        ${displayDate ? `<div style="font-size:10px;color:var(--dim);">발생일: ${displayDate}</div>` : ''}
      </div>`;
    });
    html += '</div>';
  }

  // 예상 분기
  if (futureQuarters.length > 0) {
    html += '<div><div style="font-size:11px;font-weight:600;color:var(--dim);margin-bottom:6px;">예상 일정</div>';
    futureQuarters.forEach(q => {
      const confidence = q.confidence || 0;
      const confColor = confidence >= 70 ? 'var(--green)' : confidence >= 50 ? 'var(--yellow)' : 'var(--red)';
      const preconditions = q.preconditions || [];
      // 미래 이벤트: expected_start 표시
      const displayDate = q.expected_start ? new Date(q.expected_start).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' }) : '';

      html += `<div style="padding:6px;background:var(--bg);border-radius:4px;margin-bottom:4px;border-left:2px solid var(--dim);">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:11px;font-weight:600;color:var(--dim);">${q.quarter || '-'}</span>
          <span style="font-size:10px;color:${confColor};">확신도 ${confidence}%</span>
        </div>
        <div style="font-size:10px;color:var(--dim);margin-bottom:4px;">${q.title || '-'}</div>
        <div class="progress-bar" style="height:3px;border-radius:2px;background:var(--border);margin-bottom:4px;">
          <div class="progress-fill" style="width:${confidence}%;background:${confColor};height:100%;border-radius:2px;"></div>
        </div>
        ${displayDate ? `<div style="font-size:10px;color:var(--dim);">예정일: ${displayDate}</div>` : ''}
        ${preconditions.length > 0 ? `
          <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px;">
            ${preconditions.map(p => `<span class="essence-badge" style="background:var(--border);color:var(--dim);font-size:8px;padding:2px 4px;">${p}</span>`).join('')}
          </div>
        ` : ''}
      </div>`;
    });
    html += '</div>';
  }

  container.innerHTML = html || '<div style="color:var(--dim);font-size:10px;text-align:center;">데이터 없음</div>';
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
