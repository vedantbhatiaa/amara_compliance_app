"""Plotly figures styled after the dss+ result decks. All visible text goes through L() (interface language)."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core import (BUSINESS_ORDER, COUNTRY_CODE, COUNTRY_ORDER, CRIT_ORDER, GRID, INK_2, MUTED, NAVY, STATUS_COLORS,
                  STATUS_ORDER, L, flag_uri)

FONT = "Montserrat, 'Segoe UI', Helvetica, Arial, sans-serif"
CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
          "toImageButtonOptions": {"format": "png", "scale": 2}}
COUNTRY_TONES = {"Spain": "#1B1F3B", "Portugal": "#3E4A7A", "Mexico": "#1FA276", "Colombia": "#6BBF8F",
                 "France": "#2F6DB5", "Greece": "#5A93CF", "Italy": "#8A8FA3"}
TYPE_COLORS = {"Office": "#2F6DB5", "EPC": "#8A8FA3", "Factory": "#1B1F3B", "Warehouse": "#1FA276",
               "Services": "#C4A11A"}


def _base(fig, height, legend=True, margin=None):
    fig.update_layout(
        height=height, margin=margin or dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=NAVY, size=12),
        barmode="stack", bargap=0.28, showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12), title_text="",
                    traceorder="normal"),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, color=NAVY, size=12)),
    )
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=11))
    fig.update_xaxes(showgrid=False, linecolor="#C9CCD6", tickfont=dict(color=INK_2, size=12))
    return fig


def _bar(status, x, y, **kw):
    """Stacked bar segment for one compliance status (colour keyed by the English status name)."""
    return go.Bar(
        name=L(status), x=x, y=y, marker=dict(color=STATUS_COLORS[status], line=dict(color="white", width=1.5)),
        text=[v if v else "" for v in y], textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=12), textangle=0, cliponaxis=False, **kw)


def _crit():
    return [L(c) for c in CRIT_ORDER]


def criticality_stack(fig_data, height=360):
    """Single site/segment: stacked compliance status per criticality level (deck site slides)."""
    fig = go.Figure()
    xs = _crit()
    for i, s in enumerate(STATUS_ORDER):
        y = [fig_data.get(c, [0, 0, 0])[i] for c in CRIT_ORDER]
        fig.add_trace(_bar(s, xs, y, hovertemplate="%{x}<br>" + L(s) + ": <b>%{y}</b><extra></extra>"))
    for x, c in zip(xs, CRIT_ORDER):
        t = sum(fig_data.get(c, [0, 0, 0]))
        fig.add_annotation(x=x, y=t, text=f"<b>{t}</b>", showarrow=False, yshift=10, font=dict(color=INK_2, size=11))
    fig.update_layout(uniformtext=dict(minsize=9, mode="hide"))
    _base(fig, height)
    return fig


def cluster_business_stack(cluster_fig, height=460):
    """Deck 'Compliance status per criticality of business in the <cluster>': business × criticality."""
    types = [b for b in BUSINESS_ORDER if b in cluster_fig]
    x0, x1, keys = [], [], []
    for b in types:
        for c in CRIT_ORDER:
            x0.append(L(b)); x1.append(L(c)); keys.append((b, c))
    fig = go.Figure()
    for i, s in enumerate(STATUS_ORDER):
        y = [cluster_fig[b][c][i] for b, c in keys]
        fig.add_trace(_bar(s, [x0, x1], y, customdata=list(zip(x0, x1)),
                           hovertemplate="%{customdata[0]} · %{customdata[1]}<br>" + L(s) + ": <b>%{y}</b><extra></extra>"))
    fig.update_layout(uniformtext=dict(minsize=9, mode="hide"), bargap=0.18)
    _base(fig, height)
    fig.update_xaxes(tickfont=dict(size=11))
    return fig


def global_high_chart(rows, height=500):
    """Deck 'Compliance status by High Criticality per type of business in the different clusters'."""
    pos, xs, ticks, groups = 0.0, [], [], {}
    for b in BUSINESS_ORDER:
        rs = [r for r in rows if r["business_type"] == b]
        if not rs:
            continue
        start = pos
        for r in rs:
            xs.append(pos); ticks.append(r)
            pos += 1
        groups[b] = (start + pos - 1) / 2
        pos += 0.9
    fig = go.Figure()
    for i, s in enumerate(STATUS_ORDER):
        y = [r["values"][i] for r in ticks]
        cd = [(L(r["business_type"]), L(r["cluster"])) for r in ticks]
        fig.add_trace(_bar(s, xs, y, width=0.78, customdata=cd,
                           hovertemplate="%{customdata[0]} · %{customdata[1]}<br>" + L(s) + ": <b>%{y}</b><extra></extra>"))
    ymax = max(sum(r["values"]) for r in ticks)
    fsz = ymax * 0.055
    for x, r in zip(xs, ticks):
        tot = sum(r["values"])
        n = len(r["flags"])
        for k, code in enumerate(r["flags"]):
            fig.add_layout_image(dict(source=flag_uri(code), xref="x", yref="y", x=x + (k - (n - 1) / 2) * 0.36,
                                      y=tot + ymax * 0.02, sizex=0.34, sizey=fsz, xanchor="center", yanchor="bottom",
                                      sizing="contain", layer="above"))
    for b, cx in groups.items():
        fig.add_annotation(x=cx, y=0, yref="paper", yshift=-44, text=f"<b>{L(b)}</b>", showarrow=False,
                           font=dict(size=13, color=NAVY))
    fig.update_layout(uniformtext=dict(minsize=9, mode="hide"))
    _base(fig, height, margin=dict(l=10, r=10, t=40, b=60))
    fig.update_xaxes(tickmode="array", tickvals=xs, ticktext=["·".join(r["flags"]) for r in ticks],
                     tickfont=dict(size=10, color=MUTED))
    fig.update_yaxes(range=[0, ymax * 1.14])
    return fig


def small_multiples(items, cols=4, height_per_row=250):
    """items: list of (title, {crit: [c,p,nc]}) → grid of criticality stacks. Titles are passed already translated."""
    n = len(items)
    rows = (n + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[t for t, _ in items],
                        horizontal_spacing=0.05, vertical_spacing=0.16 if rows > 1 else 0.1)
    xs = _crit()
    for k, (title, data) in enumerate(items):
        r, c = k // cols + 1, k % cols + 1
        for i, s in enumerate(STATUS_ORDER):
            y = [data.get(cr, [0, 0, 0])[i] for cr in CRIT_ORDER]
            fig.add_trace(_bar(s, xs, y, showlegend=(k == 0), legendgroup=s,
                               hovertemplate=title + "<br>%{x} · " + L(s) + ": <b>%{y}</b><extra></extra>"), row=r, col=c)
    fig.update_layout(uniformtext=dict(minsize=8, mode="hide"))
    _base(fig, height_per_row * rows + 40, margin=dict(l=10, r=10, t=40, b=10))
    fig.update_layout(legend=dict(orientation="h", y=1.0 + 0.1 / rows, yanchor="bottom", x=0))
    fig.update_annotations(font=dict(size=12, color=NAVY, family=FONT))
    fig.update_xaxes(tickfont=dict(size=10))
    return fig


def business_high_multiples(cluster_figs, clusters):
    """High-criticality stacks by type of business, one panel per cluster."""
    fig = make_subplots(rows=1, cols=len(clusters), subplot_titles=[L(c) for c in clusters], horizontal_spacing=0.06)
    for k, cl in enumerate(clusters):
        types = [b for b in BUSINESS_ORDER if b in cluster_figs[cl]]
        for i, s in enumerate(STATUS_ORDER):
            y = [cluster_figs[cl][b]["High"][i] for b in types]
            fig.add_trace(_bar(s, [L(b) for b in types], y, showlegend=(k == 0), legendgroup=s,
                               hovertemplate=L(cl) + " · %{x}<br>" + L("High") + " · " + L(s) + ": <b>%{y}</b><extra></extra>"),
                          row=1, col=k + 1)
    fig.update_layout(uniformtext=dict(minsize=8, mode="hide"))
    _base(fig, 350, margin=dict(l=10, r=10, t=60, b=10))
    fig.update_layout(legend=dict(y=1.12))
    fig.update_annotations(font=dict(size=12, color=NAVY, family=FONT))
    return fig


def share_bars(labels, data, height=None):
    """100% horizontal stacked bars. labels already translated; data: list of [c,p,nc]."""
    fig = go.Figure()
    tots = [max(1, sum(d)) for d in data]
    for i, s in enumerate(STATUS_ORDER):
        pct = [d[i] / t * 100 for d, t in zip(data, tots)]
        fig.add_trace(go.Bar(
            name=L(s), y=labels, x=pct, orientation="h",
            marker=dict(color=STATUS_COLORS[s], line=dict(color="white", width=1.5)),
            text=[f"{p:.0f}%" if p >= 7 else "" for p in pct], textposition="inside",
            textfont=dict(color="white", size=11), textangle=0, customdata=[d[i] for d in data],
            hovertemplate="%{y}<br>" + L(s) + ": <b>%{x:.0f}%</b> (%{customdata})<extra></extra>"))
    _base(fig, height or 60 + 34 * len(labels))
    fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=NAVY, size=12))
    return fig


def activity_bars(df_counts, height=None):
    """Horizontal stacked counts by key activity (checklist). Index = activity label as displayed."""
    fig = go.Figure()
    for s in STATUS_ORDER:
        fig.add_trace(go.Bar(
            name=L(s), y=df_counts.index, x=df_counts[s], orientation="h",
            marker=dict(color=STATUS_COLORS[s], line=dict(color="white", width=1.5)),
            text=[v if v else "" for v in df_counts[s]], textposition="inside", textfont=dict(color="white", size=11),
            textangle=0, insidetextanchor="middle",
            hovertemplate="%{y}<br>" + L(s) + ": <b>%{x}</b><extra></extra>"))
    _base(fig, height or max(260, 60 + 26 * len(df_counts)), margin=dict(l=10, r=10, t=10, b=10))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=NAVY, size=11))
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title_text=L("Requirements"), title_font=dict(size=11, color=MUTED))
    fig.update_layout(legend=dict(orientation="h", y=1.0, yanchor="bottom", x=0))
    return fig


def status_donut(counts, height=300):
    keys = [k for k in ["Compliant", "Partially compliant", "Non-compliant", "Not applicable", "Not assessed"] if counts.get(k)]
    vals = [counts[k] for k in keys]
    fig = go.Figure(go.Pie(labels=[L(k) for k in keys], values=vals, hole=0.62, sort=False, direction="clockwise",
                           marker=dict(colors=[STATUS_COLORS[k] for k in keys], line=dict(color="white", width=2)),
                           textinfo="value", textfont=dict(color="white", size=12),
                           hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"<b style='font-size:22px'>{sum(vals)}</b><br><span style='font-size:11px;color:{MUTED}'>"
                            f"{L('requirements')}</span>", showarrow=False, x=0.5, y=0.5)
    _base(fig, height, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_layout(legend=dict(orientation="v", y=0.5, yanchor="middle", x=1.02))
    return fig


def heat_rate(rows, z, text, height=None):
    """% compliant heatmap: rows (translated site names) × High/Medium/Low."""
    fig = go.Figure(go.Heatmap(
        z=z, x=_crit(), y=rows, text=text, texttemplate="%{text}", textfont=dict(size=11),
        colorscale=[[0, "#E24B47"], [0.5, "#F6D48A"], [1, "#1FA276"]], zmin=0, zmax=100,
        xgap=3, ygap=3, colorbar=dict(title=L("% compliant"), ticksuffix="%", thickness=10, len=0.8),
        hovertemplate="%{y} · %{x}<br>" + L("Compliant") + ": <b>%{z:.0f}%</b><extra></extra>"))
    _base(fig, height or 80 + 30 * len(rows), legend=False, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=NAVY))
    fig.update_xaxes(side="top", tickfont=dict(color=NAVY))
    return fig


def unique_counts(df):
    """Unique legal requirements (see data_prep/build_unique_requirements.py).
    Returns (per country × type: n unique, per country: n unique, overall: n unique). A requirement that applies to
    several types of business in a country counts once in that country's total."""
    by_type = df.groupby(["country", "business_type"]).req_uid_type.nunique()
    by_country = df.groupby("country").req_uid.nunique()
    return by_type, by_country, int(df.req_uid.nunique())


def treemap(df, height=470):
    """All countries → country → type of business; every tile shows its number of UNIQUE legal requirements.
    Tile areas follow the type-of-business counts; a country's label shows its own unique total. A single root node
    lets the user click back out after zooming into a country."""
    by_type, by_country, total = unique_counts(df)
    countries = [c for c in by_country.sort_values(ascending=False).index]
    ids, labels, parents, values, shown, colors = (["ALL"], [f"{L('All countries')} · {total}"], [""], [0], [total],
                                                   ["#F2F3F5"])
    for c in countries:
        ids.append(c); labels.append(f"{L(c)} · {int(by_country[c])}"); parents.append("ALL"); values.append(0)
        shown.append(int(by_country[c])); colors.append(COUNTRY_TONES.get(c, "#8A8FA3"))
    for (c, b), n in by_type.items():
        ids.append(f"{c}|{b}"); labels.append(L(b)); parents.append(c); values.append(int(n))
        shown.append(int(n)); colors.append(COUNTRY_TONES.get(c, "#8A8FA3"))
    fig = go.Figure(go.Treemap(
        ids=ids, labels=labels, parents=parents, values=values, customdata=shown, branchvalues="remainder",
        maxdepth=3, marker=dict(colors=colors, line=dict(color="white", width=2)),
        texttemplate="<b>%{label}</b><br><span style='font-size:18px'>%{customdata}</span>",
        textposition="middle center", insidetextfont=dict(family=FONT, color="white", size=14),
        outsidetextfont=dict(family=FONT, color=NAVY, size=13),
        tiling=dict(pad=3), pathbar=dict(visible=True, thickness=24, textfont=dict(family=FONT, size=13)),
        root=dict(color="#F2F3F5"),
        hovertemplate="<b>%{label}</b><br>%{customdata} " + L("unique legal requirements") + "<extra></extra>"))
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT, color=NAVY))
    return fig


def site_table(df):
    """Unique legal requirements and checklist rows per site (English keys), ordered by country then size."""
    g = (df.groupby(["country", "site_id", "site", "business_type"])
           .agg(n=("req_uid", "nunique"), rows=("req_uid", "size")).reset_index())
    g["ci"] = g.country.map({c: i for i, c in enumerate(COUNTRY_ORDER)})
    return g.sort_values(["ci", "n"], ascending=[True, False]).drop(columns="ci")


def site_bars(df, height=460):
    """Number of unique legal requirements per site, grouped by country, coloured by type of business."""
    g = site_table(df)
    g["label"] = g.site.map(L) + "  ·  " + g.country.map(COUNTRY_CODE)
    fig = go.Figure()
    for b in BUSINESS_ORDER:
        s = g[g.business_type == b]
        if s.empty:
            continue
        fig.add_trace(go.Bar(y=s.label, x=s.n, name=L(b), orientation="h", marker=dict(color=TYPE_COLORS[b]),
                             text=s.n, textposition="outside", textfont=dict(color=INK_2, size=11), cliponaxis=False,
                             hovertemplate="%{y}<br>" + L(b) + ": <b>%{x}</b> " + L("unique legal requirements")
                                           + "<extra></extra>"))
    _base(fig, height, margin=dict(l=10, r=30, t=30, b=10))
    fig.update_layout(barmode="overlay", bargap=0.25)
    fig.update_yaxes(categoryorder="array", categoryarray=list(g.label), autorange="reversed", showgrid=False,
                     tickfont=dict(color=NAVY, size=11))
    fig.update_xaxes(showgrid=True, gridcolor=GRID)
    return fig