"""Воронка открытия карты: сколько заявок дошло до каждого шага и где они теряются.

Каждая заявка — словарь с полями:
  last_step      самый дальний шаг, до которого дошёл клиент (одно из STAGES)
  reject_reason  причина отказа/обрыва, если есть
  + поля для сегментов (SEGMENT_FIELDS)
"""

from collections import Counter, defaultdict

# TODO: заменить на реальные статусы заявки из админки, в порядке прохождения
STAGES = [
    "started",        # начал заявку
    "personal_data",  # заполнил анкету
    "kyc_passed",     # прошёл идентификацию
    "approved",       # одобрен скорингом
    "issued",         # карта выпущена
    "activated",      # карта активирована
]

SEGMENT_FIELDS = ["channel", "platform", "card_type"]


def stage_counts(apps):
    """Число заявок, дошедших хотя бы до каждого шага."""
    reached = [0] * len(STAGES)
    for app in apps:
        step = app.get("last_step")
        if step not in STAGES:
            continue
        for i in range(STAGES.index(step) + 1):
            reached[i] += 1
    return reached


def funnel_table(apps):
    reached = stage_counts(apps)
    top = reached[0] or 1
    rows = []
    for i, stage in enumerate(STAGES):
        prev = reached[i - 1] if i else reached[0]
        rows.append({
            "stage": stage,
            "reached": reached[i],
            "from_start": reached[i] / top,
            "from_prev": reached[i] / prev if prev else 0.0,
        })
    return rows


def reasons_by_stage(apps):
    """Причины обрыва, сгруппированные по шагу, на котором клиент остановился."""
    out = defaultdict(Counter)
    for app in apps:
        if app.get("last_step") != STAGES[-1]:
            out[app.get("last_step")][app.get("reject_reason") or "не указана"] += 1
    return out


def by_segment(apps, field):
    groups = defaultdict(list)
    for app in apps:
        groups[app.get(field) or "неизвестно"].append(app)
    return {name: stage_counts(group) for name, group in groups.items()}


def render_markdown(apps):
    lines = [f"# Воронка открытия карт\n\nЗаявок: **{len(apps)}**\n"]

    lines += ["## Воронка\n", "| Шаг | Дошли | % от старта | % от прошлого шага |", "|---|---:|---:|---:|"]
    rows = funnel_table(apps)
    for r in rows:
        lines.append(f"| {r['stage']} | {r['reached']} | {r['from_start']:.1%} | {r['from_prev']:.1%} |")

    worst = min(rows[1:], key=lambda r: r["from_prev"], default=None)
    if worst:
        lines.append(f"\n**Самый большой провал:** переход на шаг `{worst['stage']}` — проходит {worst['from_prev']:.1%}.\n")

    lines.append("## Где и почему останавливаются\n")
    for stage, reasons in reasons_by_stage(apps).items():
        lines.append(f"**{stage}**: " + ", ".join(f"{k} — {v}" for k, v in reasons.most_common(5)))
    lines.append("")

    for field in SEGMENT_FIELDS:
        seg = by_segment(apps, field)
        if len(seg) < 2:
            continue
        lines += [f"## Конверсия по `{field}`\n", "| Сегмент | Старт | Активировали | Конверсия |", "|---|---:|---:|---:|"]
        for name, reached in sorted(seg.items(), key=lambda kv: -kv[1][0]):
            conv = reached[-1] / reached[0] if reached[0] else 0
            lines.append(f"| {name} | {reached[0]} | {reached[-1]} | {conv:.1%} |")
        lines.append("")

    return "\n".join(lines)
