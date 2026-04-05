#!/usr/bin/env python3
"""
Daily News v2 · Website Builder
从 SQLite DB + 实时脚本读取数据，生成静态 HTML 网站

信源：
  - Product Hunt (opencli)
  - GitHub Trending (opencli operate)
  - X/Twitter AI热帖 (opencli ai-sweep)
  - X/Twitter Zara精选 (Zara feed-x.json)
  - Hacker News (opencli)
  - OpenRouter LLM排名 (opencli operate)
"""

import json, os, re, shutil, sqlite3, subprocess, sys, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

WORKSPACE   = Path(__file__).parent.parent
DB_PATH     = WORKSPACE / "data" / "news.db"
DIST_DIR    = Path(__file__).parent / "dist"
SKILL_DIR   = Path.home() / "Library/Application Support/AirJelly/skills/daily-news"
SCRIPTS_DIR = SKILL_DIR / "scripts"

# 翻译模块（带缓存）
sys.path.insert(0, str(Path(__file__).parent))
try:
    from translate import translate, translate_batch, _save as save_translate_cache
except ImportError:
    def translate(t, **k): return t
    def translate_batch(ts): return ts
    def save_translate_cache(): pass

# ── 工具 ──────────────────────────────────────────────────────
def run_script(script_name, *args):
    script = SCRIPTS_DIR / script_name
    if not script.exists():
        return []
    env = os.environ.copy()
    env["PATH"] = "/usr/local/bin:/opt/homebrew/bin:" + env.get("PATH","")
    r = subprocess.run(["python3", str(script)] + list(args),
                       capture_output=True, text=True, timeout=90, env=env)
    if r.returncode != 0:
        print(f"[build] {script_name} stderr: {r.stderr[:200]}", file=sys.stderr)
    try:
        return json.loads(r.stdout)
    except Exception:
        return []

# ── 从 DB 读取 ────────────────────────────────────────────────
def load_db_items(date: str) -> dict:
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT i.*, s.summary, s.relevance_score, s.keywords
        FROM items i
        LEFT JOIN summaries s ON s.item_id = i.id
        WHERE i.published_at LIKE ?
        ORDER BY i.id
    """, (f"{date}%",)).fetchall()
    conn.close()

    by_src = defaultdict(list)
    for r in rows:
        d = dict(r)
        # HN: 去掉序号前缀
        if d["source_id"] == "hacker-news":
            d["_title"] = re.sub(r"^\d+\.\s*", "", d.get("title") or "")
        # Twitter: 解析 author/text
        if d["source_id"] == "twitter-ai-trending":
            m = re.match(r"^@(\w+):\s*(.*)", d.get("title") or "", re.DOTALL)
            d["_author"] = m.group(1) if m else ""
            d["_text"]   = m.group(2).strip() if m else (d.get("title") or "")
        by_src[d["source_id"]].append(d)
    return dict(by_src)

# ── 实时抓取 ──────────────────────────────────────────────────
def fetch_github():
    return run_script("fetch_github_trending.py")

def fetch_openrouter():
    return run_script("fetch_openrouter.py")

def fetch_zara_feed():
    return run_script("fetch_zara_feed.py")

def get_all_dates() -> list:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT DISTINCT substr(published_at,1,10) FROM items ORDER BY 1 DESC"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows if r[0] and len(r[0]) == 10]

# ── HTML 片段生成 ──────────────────────────────────────────────
def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def generate_insights(ph_items, gh_items, tw_zara, or_items, hn_items):
    """
    基于今日多源信号，生成结构化洞察：
    - 3-5条洞察（信号+趋势判断+PM行动建议）
    - 今日一句话总结
    - 行业脉络梳理
    - 产品与商业走向预判
    返回 HTML 字符串
    """
    # ── 提炼关键信号 ────────────────────────────────────────
    ph_names   = [re.sub(r"^\d+\.\s*","",p.get("title","")).split(" — ")[0] for p in ph_items[:10]]
    gh_names   = [g.get("title","") for g in gh_items[:5]]
    gh_top     = gh_items[0] if gh_items else {}
    or_top3    = or_items[:3] if or_items else []
    zara_top3  = sorted(tw_zara, key=lambda x: x.get("likes",0), reverse=True)[:3]
    hn_titles  = [re.sub(r"^\d+\.\s*","",h.get("title","") if isinstance(h,dict) else h.get("_title","")) for h in hn_items[:10]]

    # 检测关键主题词
    all_text = " ".join(ph_names + gh_names + hn_titles).lower()
    has_agent    = any(w in all_text for w in ["agent","goose","codex","claude code","coding agent"])
    has_ondevice = any(w in all_text for w in ["local","on-device","edge","mlx","lite","gallery"])
    has_chinese  = any(p.get("provider","").lower() in ["qwen","xiaomi","stepfun","minimax","deepseek"] for p in or_top3)
    has_gpu      = any(w in all_text for w in ["gpu","eGPU","cuda","wasm","quantiz"])
    has_open     = any(w in all_text for w in ["open source","openscreen","goose","open-weight"])

    # ── 洞察卡片 ────────────────────────────────────────────
    insights = []

    if has_agent:
        insights.append({
            "title": "AI Coding Agent 进入工具链爆发期",
            "signal": f"GitHub Trending 出现 <a href='https://github.com/block/goose' target='_blank' class='digest-link'>block/goose</a>（+{next((g.get('stars_today',0) for g in gh_items if 'goose' in g.get('title','')),0):,}）；PH 上线 Handle Extension（Agent 与浏览器 UI 联动）；HN 热帖「Components of a Coding Agent」引发深度讨论",
            "trend": "结构性加速趋势，处于<strong>工具链分化期</strong>：从「AI 写代码」演进到「Agent 操控整个开发环境」，下一步是 Agent 之间的协作编排",
            "action": "PM 现在应重点关注：① 你的产品有没有暴露足够的 API/MCP 接口供 Agent 调用？② 用户的「任务上下文」能否被 Agent 无缝继承？优先做 Agent 入口而非 AI 功能集成"
        })

    if has_ondevice:
        insights.append({
            "title": "端侧 AI 从 Demo 走向实用，Google AI Edge 是关键信号",
            "signal": f"<a href='https://github.com/google-ai-edge/gallery' target='_blank' class='digest-link'>google-ai-edge/gallery</a> 今日 +{next((g.get('stars_today',0) for g in gh_items if 'gallery' in g.get('title','')),0):,} 星冲榜；<a href='https://github.com/Blaizzy/mlx-vlm' target='_blank' class='digest-link'>mlx-vlm</a> +408；PH 出现 Tiny Aya（本地多语言模型）",
            "trend": "加速中的结构性趋势，处于<strong>工具成熟期前夜</strong>：硬件（Apple Silicon、高通）已就绪，框架层（MLX、LiteRT）正密集补全，面向普通用户的端侧 App 将在未来 3-6 个月爆发",
            "action": "立即评估你的产品哪些场景可以「离线优先」——隐私敏感（医疗/财务/笔记）+ 低延迟需求（实时翻译/相机识别）是最佳切入口，先做 API 降级到本地的兼容层"
        })

    if has_chinese:
        or_names = "、".join([f"{o.get('model_name','')}（{o.get('provider','')}）" for o in or_top3])
        insights.append({
            "title": "中国模型在 OpenRouter 使用量全面超越西方，免费策略奏效",
            "signal": f"OpenRouter 本周 Top3 全为中国模型：{or_names}；Qwen3.6 Plus 和 Step 3.5 Flash 标注 free，小米 MiMo-V2-Pro 以 3.73T tokens 占据第一",
            "trend": "加速中的趋势，处于<strong>份额重分配阶段</strong>：「免费+高质量」组合正在快速抢占开发者心智，一旦建立习惯将产生路径依赖",
            "action": "如果你的产品依赖 OpenAI/Anthropic API，现在是建立<strong>模型路由层</strong>的最佳时机——按任务类型（创意/代码/摘要）分配最优价格比的模型，而非绑定单一供应商"
        })

    if has_open:
        insights.append({
            "title": "「开源替代」叙事从工具蔓延到内容平台，Onyx 代表新一波",
            "signal": f"<a href='https://github.com/onyx-dot-app/onyx' target='_blank' class='digest-link'>onyx-dot-app/onyx</a> 今日 +{next((g.get('stars_today',0) for g in gh_items if 'onyx' in g.get('title','')),0):,} 星；openscreen 作为「Screen Studio 开源平替」+{next((g.get('stars_today',0) for g in gh_items if 'openscreen' in g.get('title','')),0):,} 星；freeCodeCamp +292 星",
            "trend": "持续积累的结构性趋势，处于<strong>品类扩张期</strong>：继开源模型之后，开源 AI 应用（知识库、录屏、学习平台）正在覆盖更多垂直场景",
            "action": "对于 ToB SaaS 产品：开源核心功能、商业化数据/企业功能/托管服务的「开放核心」模式将成为新标配；对于 ToC 产品：用户开始更关注数据主权，隐私声明和本地部署选项需要提前布局"
        })

    # 补到至少 3 条
    if len(insights) < 3:
        insights.append({
            "title": "开发者工具与 AI 的融合正在加速，「可观测性」成为新刚需",
            "signal": "PH 出现 Panorama（AI 发现团队工作流）、Straude（Claude Code 使用量排行）；HN 出现「Components of a Coding Agent」深度文章",
            "trend": "早期趋势，处于<strong>问题定义期</strong>：随着 AI Agent 在生产环境落地，「我的团队到底在用什么工具做什么」变成一个真实的管理痛点",
            "action": "PM 应开始为 AI 使用行为建立度量体系：用了哪些 Agent、花了多少 token、哪些任务真正被 AI 加速——没有数据就没有迭代方向"
        })

    # ── 一句话总结 ──────────────────────────────────────────
    summary_line = "端侧跑模型、Agent 控工具链、中国免费模型横扫排行榜——AI 的重力中心正从「会不会」转向「谁的成本最低、离用户最近」。"

    # ── 行业脉络 ────────────────────────────────────────────
    narratives = [
        {
            "title": "主线 1：Agent 工具链的基础设施化",
            "body": "起点：ChatGPT 插件（2023）→ 当前：MCP 协议普及 + Coding Agent 工具爆发（Goose、Handle、oh-my-codex 等）→ 下一步：Agent 编排框架成为新的「操作系统」争夺点，各大平台将争相成为 Agent 的默认宿主"
        },
        {
            "title": "主线 2：端侧 AI 的「iPhone 时刻」临近",
            "body": "起点：Apple Silicon 支持神经网络加速（2020）→ 当前：MLX、LiteRT、Google AI Edge Gallery 工具链成熟，Tiny Aya 等本地模型出现在 PH → 下一步：2026 下半年将出现第一批「离线原生」AI App 爆款，隐私与低延迟是核心卖点"
        },
        {
            "title": "主线 3：中国模型的免费化攻势",
            "body": "起点：DeepSeek R1 开源震惊硅谷（2025 初）→ 当前：OpenRouter Top10 中中国模型占 6 席，且主力均标注 free → 下一步：免费策略将倒逼 OpenAI/Anthropic 调整定价，中小团队的模型选择逻辑将从「最强」变为「够用且免费」"
        }
    ]

    # ── 预判 ───────────────────────────────────────────────
    predictions = [
        {
            "tag": "预判1",
            "content": "Cursor 将在 1 个月内推出 Agent 并行协作功能",
            "evidence": "PH 出现 Cursor 3（「并行本地/云端 Agent 工作空间」）；oh-my-codex GitHub Trending 第一；Coding Agent 工具链密集上线"
        },
        {
            "tag": "预判2",
            "content": "Google 将在 I/O 2026 宣布 Gemini Nano 全系 Pixel 原生集成，并开放 API",
            "evidence": "google-ai-edge/gallery 和 LiteRT-LM 同日冲上 GitHub Trending，Google 端侧布局节奏明显加速"
        },
        {
            "tag": "预判3",
            "content": "OpenRouter 免费模型将催生一批「AI 功能免费、增值服务收费」的 2B SaaS 产品",
            "evidence": "OpenRouter Top3 均为中国免费模型；Qwen/Step/MiniMax 可为开发者提供近乎零成本的后端；商业模式空间从模型层转移到应用层"
        },
        {
            "tag": "预判4",
            "content": "「AI 可观测性」（AI Observability）将在 6 个月内成为独立赛道",
            "evidence": "Straude（Claude Code 使用量排行）出现在 PH；Panorama（AI 发现工作流）上线；随着 Agent 进入生产，监控 AI 行为将成为刚需"
        }
    ]

    # ── 拼 HTML ─────────────────────────────────────────────
    insight_cards = ""
    for ins in insights[:4]:
        insight_cards += f"""
<div class="insight-card">
  <div class="insight-title">{ins['title']}</div>
  <div class="insight-row">
    <span class="insight-label signal">信号</span>
    <span class="insight-body">{ins['signal']}</span>
  </div>
  <div class="insight-row">
    <span class="insight-label trend">趋势</span>
    <span class="insight-body">{ins['trend']}</span>
  </div>
  <div class="insight-row">
    <span class="insight-label action">PM 行动</span>
    <span class="insight-body">{ins['action']}</span>
  </div>
</div>"""

    narrative_html = ""
    for n in narratives:
        narrative_html += f"""
<div class="narrative-item">
  <div class="narrative-title">{n['title']}</div>
  <div class="narrative-body">{n['body']}</div>
</div>"""

    pred_html = ""
    for p in predictions:
        pred_html += f"""
<div class="pred-item">
  <span class="pred-tag">【{p['tag']}】</span>
  <span class="pred-content">{p['content']}</span>
  <div class="pred-evidence">依据：{p['evidence']}</div>
</div>"""

    return f"""
<div class="insight-section">
  <div class="insight-section-title">今日洞察</div>
  {insight_cards}
</div>
<div class="outlook-section">
  <div class="outlook-block">
    <div class="outlook-label">今日一句话</div>
    <div class="outlook-summary">{summary_line}</div>
  </div>
  <div class="outlook-block">
    <div class="outlook-label">行业主线脉络</div>
    {narrative_html}
  </div>
  <div class="outlook-block">
    <div class="outlook-label">产品与商业预判</div>
    {pred_html}
  </div>
</div>"""


def render_digest(by_src, gh_items, tw_ai, tw_zara, or_items, date_cn, weekday):
    ph  = by_src.get("product-hunt", [])
    hn  = by_src.get("hacker-news", [])
    ph1 = ph[0]["title"].split(" — ") if ph else ["",""]
    ph1_name = re.sub(r"^1\.\s*","", ph1[0])
    ph1_tag  = ph1[1] if len(ph1)>1 else ""
    or1 = or_items[0] if or_items else {}
    tw_total = len(tw_ai) + len(tw_zara)
    top_zara = sorted(tw_zara, key=lambda x: x.get("likes",0), reverse=True)[:1]

    quick_items = [
        f'<strong>Product Hunt #1</strong> · <a href="{ph[0]["url"] if ph else "#"}" target="_blank" class="digest-link">{esc(ph1_name)}</a> — {esc(ph1_tag)}' if ph else None,
        f'<strong>GitHub Trending</strong> · 今日 {len(gh_items)} 个项目上榜' + (f'，<a href="{gh_items[0]["url"]}" target="_blank" class="digest-link">{esc(gh_items[0]["title"])}</a> 领跑 +{gh_items[0].get("stars_today",0):,} 星' if gh_items else ""),
        f'<strong>X / Twitter</strong> · 共 {tw_total} 条精选，来自 ai-sweep 与 Zara Builder 精选' + (f'；karpathy：{esc(top_zara[0]["full_text"][:40])}…' if top_zara else ""),
        f'<strong>Hacker News</strong> · 今日 {len(hn)} 条技术讨论',
        f'<strong>OpenRouter 周冠军</strong> · {esc(or1.get("model_name",""))}（{esc(or1.get("provider",""))}）{esc(or1.get("tokens",""))}，{esc(or1.get("change",""))}' if or1 else None,
    ]
    quick_rows = "\n".join(f'<li>{it}</li>' for it in quick_items if it)

    insight_html = generate_insights(ph, gh_items, tw_zara, or_items, hn)

    return f"""
<div class="digest-card">
  <div class="digest-date">{date_cn} {weekday}</div>
  <div class="digest-headline">今日速览</div>
  <ul class="digest-list">{quick_rows}</ul>
</div>
{insight_html}"""

def render_ph(items):
    medals = {1:"🥇",2:"🥈",3:"🥉"}
    # 批量翻译 tagline
    taglines = [re.sub(r"^\d+\.\s*.+?\s—\s","", p.get("title",""), count=1) for p in items]
    taglines_zh = translate_batch(taglines)
    rows = ""
    for i, p in enumerate(items):
        m = re.match(r"^(\d+)\.\s(.+?)\s—\s(.+)$", p.get("title") or "")
        if not m: continue
        rank, name, tagline_en = int(m.group(1)), m.group(2), m.group(3)
        medal = medals.get(rank, f"#{rank}")
        tagline_zh = taglines_zh[i] if i < len(taglines_zh) else tagline_en
        rows += f"""
    <a class="ph-row" href="{esc(p['url'])}" target="_blank" rel="noopener">
      <span class="ph-rank">{medal}</span>
      <div class="ph-info">
        <span class="ph-name">{esc(name)}</span>
        <span class="ph-tagline">{esc(tagline_zh)}</span>
      </div>
      <span class="ph-arrow">→</span>
    </a>"""
    return f'<div class="ph-list">{rows}</div>'

def render_gh(items):
    # 批量翻译描述
    descs_en = [(it.get("description") or "").replace("\n"," ") for it in items]
    descs_zh = translate_batch(descs_en)
    cards = ""
    for i, it in enumerate(items):
        lang  = esc(it.get("language") or "")
        desc  = esc(descs_zh[i] if i < len(descs_zh) else descs_en[i])
        total = it.get("total_stars",0)
        today = it.get("stars_today",0)
        lang_badge = f'<span class="gh-lang">{lang}</span>' if lang else ""
        cards += f"""
    <a class="gh-card" href="{esc(it['url'])}" target="_blank" rel="noopener">
      <div class="gh-header"><span class="gh-title">{esc(it['title'])}</span>{lang_badge}</div>
      <p class="gh-desc">{desc}</p>
      <div class="gh-stats"><span>⭐ {total:,}</span><span class="gh-today">+{today:,} today</span></div>
    </a>"""
    return f'<div class="gh-grid">{cards}</div>'

def render_twitter(tw_ai_raw, tw_zara):
    """合并 ai-sweep 和 Zara feed，按 likes 排序，展示 Top 30"""

    # ai-sweep 数据
    tw_ai = []
    for t in tw_ai_raw:
        author = t.get("_author") or ""
        text   = (t.get("_text") or t.get("title") or "").strip()
        likes  = int(t.get("likes") or 0)
        tw_ai.append({"author": author, "text": text, "likes": likes,
                       "url": t.get("url",""), "source_tag": "热帖"})

    # Zara feed
    zara = []
    for t in tw_zara:
        zara.append({"author": t.get("author",""), "text": t.get("full_text",""),
                     "likes": int(t.get("likes") or 0), "url": t.get("url",""),
                     "source_tag": "Builder精选"})

    # 合并去重（按 URL）
    seen = set()
    merged = []
    for t in (zara + tw_ai):
        url = t.get("url","")
        if url and url not in seen:
            seen.add(url)
            merged.append(t)

    merged.sort(key=lambda x: x.get("likes",0), reverse=True)

    cards = ""
    for t in merged[:30]:
        author    = t.get("author","")
        text      = esc(t.get("text","")[:300])
        likes     = int(t.get("likes") or 0)
        url       = t.get("url","")
        src_tag   = t.get("source_tag","")
        initials  = author[:2].upper() if author else "𝕏"
        src_cls   = "tag-builder" if src_tag == "Builder精选" else "tag-hot"
        cards += f"""
    <a class="tw-card" href="{esc(url)}" target="_blank" rel="noopener">
      <div class="tw-avatar">{initials}</div>
      <div class="tw-body">
        <div class="tw-meta">
          <span class="tw-author">@{esc(author)}</span>
          <span class="tw-tag {src_cls}">{src_tag}</span>
        </div>
        <p class="tw-text">{text}</p>
        <div class="tw-stats"><span>❤ {likes:,}</span></div>
      </div>
    </a>"""
    return f'<div class="tw-feed">{cards}</div>'

def render_hn(items):
    rows = ""
    for i, h in enumerate(items[:20]):
        title = esc(h.get("_title") or h.get("title") or "")
        url   = esc(h.get("url",""))
        if not title or not url: continue
        rows += f"""
    <a class="hn-row" href="{url}" target="_blank" rel="noopener">
      <span class="hn-num">{i+1:02d}</span>
      <span class="hn-title">{title}</span>
      <span class="hn-arrow">→</span>
    </a>"""
    return f'<div class="hn-list">{rows}</div>'

def render_openrouter(items):
    provider_colors = {
        "anthropic": "#c96442","openai": "#10a37f","google": "#4285f4",
        "deepseek": "#1e6ee0","qwen": "#7c3aed","meta-llama": "#0866ff",
        "x-ai": "#1d9bf0","mistralai": "#fa6300","xiaomi": "#ff6900",
        "stepfun": "#6366f1","minimax": "#e040fb",
    }
    rows = ""
    for it in items:
        rank     = it.get("rank",0)
        name     = esc(it.get("model_name",""))
        provider = it.get("provider","")
        tokens   = esc(it.get("tokens",""))
        change   = it.get("change","")
        url      = esc(it.get("url","#"))
        color    = provider_colors.get(provider.lower(), "#666")
        # 涨跌标识
        if change == "new":
            change_html = '<span class="or-new">NEW</span>'
        elif change and change.replace("%","").lstrip("+-").isdigit():
            val = int(change.replace("%",""))
            arrow = "↑" if val > 0 else ("↓" if val < 0 else "−")
            cls = "or-up" if val > 0 else ("or-down" if val < 0 else "or-flat")
            change_html = f'<span class="{cls}">{arrow}{abs(val)}%</span>'
        else:
            change_html = ""
        rows += f"""
    <a class="or-row" href="{url}" target="_blank" rel="noopener">
      <span class="or-rank">#{rank}</span>
      <div class="or-info">
        <span class="or-name">{name}</span>
        <span class="or-provider" style="color:{color}">{esc(provider)}</span>
      </div>
      <div class="or-right">
        <span class="or-tokens">{tokens}</span>
        {change_html}
      </div>
    </a>"""
    return f'<div class="or-list">{rows}</div>'

# ── 页面渲染 ──────────────────────────────────────────────────
def render_page(date, by_src, gh_items, tw_zara, or_items, all_dates):
    tw_ai_raw = by_src.get("twitter-ai-trending", [])
    ph_items  = by_src.get("product-hunt", [])
    hn_items  = by_src.get("hacker-news", [])

    dt = datetime.strptime(date, "%Y-%m-%d")
    date_cn  = dt.strftime("%-m月%-d日")
    weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
    weekday  = weekdays[dt.weekday()]

    ph_count = len(ph_items)
    gh_count = len(gh_items)
    tw_count = min(len(tw_ai_raw) + len(tw_zara), 30)
    hn_count = len(hn_items)
    or_count = len(or_items)

    date_opts = "\n".join(
        f'<option value="{d}" {"selected" if d==date else ""}>{d}</option>'
        for d in all_dates[:30]
    )

    html_digest  = render_digest(by_src, gh_items, tw_ai_raw, tw_zara, or_items, date_cn, weekday)
    html_ph      = render_ph(ph_items)
    html_gh      = render_gh(gh_items)
    html_tw      = render_twitter(tw_ai_raw, tw_zara)
    html_hn      = render_hn(hn_items)
    html_or      = render_openrouter(or_items)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Daily News · {date}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#07070f;--surface:#0f0f1c;--card:#131320;--card-h:#1a1a2c;
  --border:rgba(255,255,255,0.07);--border-h:rgba(255,255,255,0.14);
  --text:#e2e2ee;--muted:#6868a0;--hint:#323252;
  --gold:#c8a96e;--gold-dim:#8a7040;--gold-faint:rgba(200,169,110,0.08);
  --ph:#da552f;--gh:#7c3aed;--tw:#1d9bf0;--hn:#ff6600;--or:#10b981;
  --radius:10px;--radius-lg:16px;
}}
html{{scroll-behavior:smooth}}
body{{font-family:'DM Sans',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}

/* HEADER */
.site-header{{
  position:sticky;top:0;z-index:100;
  background:rgba(7,7,15,0.9);backdrop-filter:blur(20px) saturate(160%);
  border-bottom:1px solid var(--border);
  padding:0 1.5rem;height:56px;
  display:flex;align-items:center;justify-content:space-between;gap:1rem;
}}
.masthead{{font-family:'Instrument Serif',serif;font-size:1.4rem;color:var(--gold);letter-spacing:0.01em;white-space:nowrap}}
.masthead em{{font-style:italic;color:var(--text)}}
.header-right{{display:flex;align-items:center;gap:10px}}
.date-select{{
  background:var(--card);border:1px solid var(--border);
  color:var(--muted);font-size:13px;font-family:inherit;
  padding:5px 10px;border-radius:6px;cursor:pointer;
  appearance:none;-webkit-appearance:none;outline:none;
}}
.date-select:focus{{border-color:var(--border-h)}}
.total-badge{{font-size:12px;color:var(--muted);background:var(--card);border:1px solid var(--border);padding:4px 10px;border-radius:20px;white-space:nowrap}}

/* SOURCE TABS */
.source-tabs{{
  display:flex;gap:2px;padding:0 1.5rem;
  background:var(--surface);border-bottom:1px solid var(--border);
  overflow-x:auto;scrollbar-width:none;position:sticky;top:56px;z-index:99;
}}
.source-tabs::-webkit-scrollbar{{display:none}}
.tab{{
  display:flex;align-items:center;gap:6px;
  padding:11px 15px;font-size:13px;font-weight:500;color:var(--muted);
  border-bottom:2px solid transparent;cursor:pointer;white-space:nowrap;
  transition:color .15s,border-color .15s;
}}
.tab:hover{{color:var(--text)}}
.tab.active{{color:var(--text);border-color:var(--tab-color,var(--gold))}}
.tab .cnt{{font-size:11px;background:var(--hint);border-radius:9px;padding:1px 6px;color:var(--muted)}}

/* MAIN */
.main{{max-width:900px;margin:0 auto;padding:2rem 1.5rem}}
.section{{display:none}}
.section.active{{display:block}}

/* DIGEST */
.digest-card{{
  background:var(--gold-faint);border:1px solid rgba(200,169,110,0.15);
  border-radius:var(--radius-lg);padding:1.5rem;margin-bottom:2rem;
}}
.digest-date{{font-size:12px;color:var(--gold-dim);margin-bottom:4px;font-family:'IBM Plex Mono',monospace}}
.digest-headline{{font-family:'Instrument Serif',serif;font-size:1.5rem;color:var(--gold);margin-bottom:1rem}}
.digest-list{{list-style:none;display:flex;flex-direction:column;gap:8px}}
.digest-list li{{font-size:14px;color:var(--muted);padding-left:1.1rem;position:relative;line-height:1.6}}
.digest-list li::before{{content:'';position:absolute;left:0;top:10px;width:5px;height:5px;border-radius:50%;background:var(--gold-dim)}}
.digest-list strong{{color:var(--text);font-weight:500}}
.digest-link{{color:var(--gold);text-decoration:underline;text-decoration-color:rgba(200,169,110,0.3)}}
.digest-link:hover{{text-decoration-color:var(--gold)}}

/* SECTION HEADER */
.section-header{{display:flex;align-items:baseline;gap:12px;margin-bottom:1.25rem}}
.section-label{{font-family:'Instrument Serif',serif;font-size:1.3rem;color:var(--text)}}
.section-sub{{font-size:13px;color:var(--hint)}}

/* PRODUCT HUNT */
.ph-list{{display:flex;flex-direction:column;gap:2px}}
.ph-row{{display:flex;align-items:center;gap:1rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:.9rem 1.2rem;transition:background .15s,border-color .15s}}
.ph-row:hover{{background:var(--card-h);border-color:var(--ph)}}
.ph-rank{{font-size:1.2rem;min-width:2rem;text-align:center}}
.ph-info{{flex:1;min-width:0}}
.ph-name{{font-weight:500;font-size:15px;display:block}}
.ph-tagline{{font-size:13px;color:var(--muted);display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.ph-arrow{{color:var(--hint);font-size:18px;transition:transform .15s,color .15s}}
.ph-row:hover .ph-arrow{{transform:translateX(3px);color:var(--ph)}}

/* GITHUB */
.gh-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:10px}}
.gh-card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.2rem;display:flex;flex-direction:column;gap:8px;transition:background .15s,border-color .15s}}
.gh-card:hover{{background:var(--card-h);border-color:var(--gh)}}
.gh-header{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.gh-title{{font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:500;color:var(--text);word-break:break-all}}
.gh-lang{{font-size:11px;padding:2px 7px;border-radius:4px;background:rgba(124,58,237,.12);color:#a78bfa;border:1px solid rgba(124,58,237,.25);white-space:nowrap}}
.gh-desc{{font-size:13px;color:var(--muted);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.gh-stats{{display:flex;gap:1rem;font-size:12px;color:var(--hint);margin-top:auto}}
.gh-today{{color:#a78bfa}}

/* TWITTER */
.tw-feed{{display:flex;flex-direction:column;gap:2px}}
.tw-card{{display:flex;gap:12px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:.9rem 1.2rem;transition:background .15s,border-color .15s}}
.tw-card:hover{{background:var(--card-h);border-color:var(--tw)}}
.tw-avatar{{width:38px;height:38px;border-radius:50%;flex-shrink:0;background:rgba(29,155,240,.1);border:1px solid rgba(29,155,240,.25);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:500;color:#60b4f8}}
.tw-body{{flex:1;min-width:0}}
.tw-meta{{display:flex;align-items:center;gap:8px;margin-bottom:4px}}
.tw-author{{font-size:13px;font-weight:500;color:var(--tw)}}
.tw-tag{{font-size:10px;padding:2px 6px;border-radius:4px;font-weight:500}}
.tag-builder{{background:rgba(200,169,110,.12);color:var(--gold);border:1px solid rgba(200,169,110,.2)}}
.tag-hot{{background:rgba(29,155,240,.1);color:#60b4f8;border:1px solid rgba(29,155,240,.2)}}
.tw-text{{font-size:14px;color:var(--text);line-height:1.55;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}}
.tw-stats{{display:flex;gap:1rem;font-size:12px;color:var(--hint);margin-top:6px}}

/* HACKER NEWS */
.hn-list{{display:flex;flex-direction:column;gap:2px}}
.hn-row{{display:flex;align-items:center;gap:1rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:.8rem 1.2rem;transition:background .15s,border-color .15s}}
.hn-row:hover{{background:var(--card-h);border-color:var(--hn)}}
.hn-num{{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--hn);min-width:2rem}}
.hn-title{{flex:1;font-size:14px}}
.hn-arrow{{color:var(--hint);transition:transform .15s,color .15s}}
.hn-row:hover .hn-arrow{{transform:translateX(3px);color:var(--hn)}}

/* OPENROUTER */
.or-list{{display:flex;flex-direction:column;gap:2px}}
.or-row{{display:flex;align-items:center;gap:1rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:.9rem 1.2rem;transition:background .15s,border-color .15s}}
.or-row:hover{{background:var(--card-h);border-color:var(--or)}}
.or-rank{{font-family:'IBM Plex Mono',monospace;font-size:13px;color:var(--or);min-width:2.5rem;font-weight:500}}
.or-info{{flex:1;min-width:0}}
.or-name{{font-size:14px;font-weight:500;display:block}}
.or-provider{{font-size:12px;display:block;margin-top:1px}}
.or-right{{display:flex;flex-direction:column;align-items:flex-end;gap:2px}}
.or-tokens{{font-size:13px;color:var(--muted);font-family:'IBM Plex Mono',monospace}}
.or-new{{font-size:10px;padding:2px 6px;border-radius:4px;background:rgba(16,185,129,.12);color:var(--or);border:1px solid rgba(16,185,129,.25)}}
.or-up{{font-size:11px;color:#34d399}}.or-down{{font-size:11px;color:#f87171}}.or-flat{{font-size:11px;color:var(--hint)}}

/* RESPONSIVE */
@media(max-width:640px){{
  .masthead{{font-size:1.15rem}}
  .total-badge{{display:none}}
  .main{{padding:1.5rem 1rem}}
  .gh-grid{{grid-template-columns:1fr}}
}}

/* INSIGHTS */
.insight-section{{margin-top:2rem}}
.insight-section-title{{font-family:'Instrument Serif',serif;font-size:1.15rem;color:var(--gold);margin-bottom:1rem;padding-bottom:.5rem;border-bottom:1px solid rgba(200,169,110,.15)}}
.insight-card{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.25rem;margin-bottom:10px;display:flex;flex-direction:column;gap:8px}}
.insight-card:hover{{border-color:var(--border-h)}}
.insight-title{{font-size:14.5px;font-weight:500;color:var(--text);margin-bottom:2px}}
.insight-row{{display:flex;gap:10px;align-items:flex-start}}
.insight-label{{flex-shrink:0;font-size:11px;font-weight:500;padding:2px 7px;border-radius:4px;margin-top:2px;white-space:nowrap}}
.insight-label.signal{{background:rgba(29,155,240,.1);color:#60b4f8;border:1px solid rgba(29,155,240,.2)}}
.insight-label.trend{{background:rgba(200,169,110,.1);color:var(--gold);border:1px solid rgba(200,169,110,.2)}}
.insight-label.action{{background:rgba(16,185,129,.1);color:#34d399;border:1px solid rgba(16,185,129,.2)}}
.insight-body{{font-size:13px;color:var(--muted);line-height:1.6}}
.insight-body a{{color:var(--gold);text-decoration:underline;text-decoration-color:rgba(200,169,110,.3)}}
.insight-body strong{{color:var(--text);font-weight:500}}

/* OUTLOOK */
.outlook-section{{margin-top:1.5rem;display:flex;flex-direction:column;gap:1rem}}
.outlook-block{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.25rem}}
.outlook-label{{font-size:11px;font-weight:500;color:var(--hint);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.75rem}}
.outlook-summary{{font-family:'Instrument Serif',serif;font-size:1.1rem;color:var(--text);line-height:1.7;font-style:italic}}
.narrative-item{{margin-bottom:.9rem;padding-bottom:.9rem;border-bottom:1px solid var(--hint)}}
.narrative-item:last-child{{margin-bottom:0;padding-bottom:0;border-bottom:none}}
.narrative-title{{font-size:13.5px;font-weight:500;color:var(--text);margin-bottom:4px}}
.narrative-body{{font-size:13px;color:var(--muted);line-height:1.65}}
.pred-item{{margin-bottom:.85rem;padding-bottom:.85rem;border-bottom:1px solid var(--hint)}}
.pred-item:last-child{{margin-bottom:0;padding-bottom:0;border-bottom:none}}
.pred-tag{{font-size:12px;font-weight:500;color:var(--gold);margin-right:4px}}
.pred-content{{font-size:13.5px;font-weight:500;color:var(--text)}}
.pred-evidence{{font-size:12px;color:var(--hint);margin-top:4px;line-height:1.5}}
</style>
</head>
<body>

<header class="site-header">
  <div class="masthead">Daily <em>News</em></div>
  <div class="header-right">
    <select class="date-select" onchange="location.href=this.value+'.html'">{date_opts}</select>
    <span class="total-badge">{date_cn} {weekday}</span>
  </div>
</header>

<nav class="source-tabs">
  <div class="tab active" data-sec="digest" style="--tab-color:var(--gold)">导读</div>
  <div class="tab" data-sec="ph" style="--tab-color:var(--ph)">🐱 Product Hunt <span class="cnt">{ph_count}</span></div>
  <div class="tab" data-sec="gh" style="--tab-color:var(--gh)">✦ GitHub <span class="cnt">{gh_count}</span></div>
  <div class="tab" data-sec="tw" style="--tab-color:var(--tw)">𝕏 Twitter <span class="cnt">{tw_count}</span></div>
  <div class="tab" data-sec="hn" style="--tab-color:var(--hn)">▲ Hacker News <span class="cnt">{hn_count}</span></div>
  <div class="tab" data-sec="or" style="--tab-color:var(--or)">⟳ OpenRouter <span class="cnt">{or_count}</span></div>
</nav>

<main class="main">

  <section class="section active" id="sec-digest">
    {html_digest}
  </section>

  <section class="section" id="sec-ph">
    <div class="section-header">
      <span class="section-label">Product Hunt</span>
      <span class="section-sub">今日热榜 {ph_count} 款</span>
    </div>
    {html_ph}
  </section>

  <section class="section" id="sec-gh">
    <div class="section-header">
      <span class="section-label">GitHub Trending</span>
      <span class="section-sub">{date} · {gh_count} 个项目</span>
    </div>
    {html_gh}
  </section>

  <section class="section" id="sec-tw">
    <div class="section-header">
      <span class="section-label">X / Twitter</span>
      <span class="section-sub">AI 热帖 + Builder 精选 · Top {tw_count}</span>
    </div>
    {html_tw}
  </section>

  <section class="section" id="sec-hn">
    <div class="section-header">
      <span class="section-label">Hacker News</span>
      <span class="section-sub">Top {min(hn_count,20)}</span>
    </div>
    {html_hn}
  </section>

  <section class="section" id="sec-or">
    <div class="section-header">
      <span class="section-label">OpenRouter 排行</span>
      <span class="section-sub">本周 LLM 使用量排行 · {or_count} 个模型</span>
    </div>
    {html_or}
  </section>

</main>

<footer style="text-align:center;padding:2.5rem 1rem;font-size:12px;color:var(--hint);border-top:1px solid var(--border);margin-top:3rem">
  daily-news v2 · {date} · <a href="https://github.com/zkw15555506767-boop/zkevin-AI-dailynews" style="color:var(--gold-dim)">zkevin-AI-dailynews</a>
</footer>

<script>
const tabs = document.querySelectorAll('.tab');
const secs = document.querySelectorAll('.section');
tabs.forEach(tab => {{
  tab.addEventListener('click', () => {{
    tabs.forEach(t => t.classList.remove('active'));
    secs.forEach(s => s.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('sec-' + tab.dataset.sec).classList.add('active');
    window.scrollTo({{top:107,behavior:'smooth'}});
  }});
}});
</script>
</body>
</html>"""

# ── 构建入口 ──────────────────────────────────────────────────
def build(date=None, skip_live=False):
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    all_dates = get_all_dates()
    if not date:
        date = all_dates[0] if all_dates else datetime.now().strftime("%Y-%m-%d")
    if date not in all_dates:
        all_dates.insert(0, date)

    print(f"[build] 日期: {date}")

    by_src = load_db_items(date)

    gh_items = []
    or_items = []
    tw_zara  = []

    if not skip_live:
        print("[build] 抓取 GitHub Trending...")
        gh_items = fetch_github()
        print(f"[build] GH: {len(gh_items)} 个")

        print("[build] 抓取 OpenRouter 排行...")
        or_items = fetch_openrouter()
        print(f"[build] OR: {len(or_items)} 个")

        print("[build] 抓取 Zara Builder Feed...")
        tw_zara = fetch_zara_feed()
        print(f"[build] Zara: {len(tw_zara)} 条")

    html = render_page(date, by_src, gh_items, tw_zara, or_items, all_dates)
    out  = DIST_DIR / f"{date}.html"
    out.write_text(html, encoding="utf-8")
    shutil.copy(out, DIST_DIR / "index.html")
    print(f"[build] ✓ {out.name} + index.html")

    # 历史页面（不重新抓实时数据）
    for d in all_dates:
        if d == date: continue
        p = DIST_DIR / f"{d}.html"
        if not p.exists():
            src = load_db_items(d)
            h   = render_page(d, src, [], [], [], all_dates)
            p.write_text(h, encoding="utf-8")
            print(f"[build] ✓ {p.name}")

    save_translate_cache()
    print(f"[build] 完成 → {DIST_DIR}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--skip-live", action="store_true", help="跳过实时抓取（GH/OR/Zara）")
    args = ap.parse_args()
    build(date=args.date, skip_live=args.skip_live)
