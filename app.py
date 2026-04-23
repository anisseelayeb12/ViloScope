import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.general    import charger_communes, get_infos_ville
from modules.meteo      import get_previsions, get_climat_annuel, code_vers_description
from modules.emploi     import get_offres
from modules.logement   import get_logement
from modules.vie_locale import get_vie_locale

st.set_page_config(page_title="ViloScope", layout="wide", initial_sidebar_state="expanded")

C1 = "#C0392B"
C2 = "#1A5276"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; color: #111111; background-color: #FFFFFF; }
.main .block-container { padding: 2rem 3rem; max-width: 1400px; }
[data-testid="stSidebar"] { background-color: #111111; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] div,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #EEEEEE !important; }
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] input { color: #111111 !important; background-color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
.titre { font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 900; letter-spacing: -1px; }
.sous-titre { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.2em; color: #999; margin-bottom: 1.5rem; }
.h1 { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 700; border-left: 4px solid #C0392B; padding-left: 0.7rem; margin-bottom: 1rem; }
.h2 { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 700; border-left: 4px solid #1A5276; padding-left: 0.7rem; margin-bottom: 1rem; }
.carte { background: #F7F6F3; border: 1px solid #E0E0E0; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; }
.gchiffre { font-family: 'Playfair Display', serif; font-size: 2.1rem; font-weight: 700; line-height: 1; }
.clabel { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.15em; color: #888; margin-top: 0.3rem; }
.dtable { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.dtable td { padding: 0.4rem 0; }
.dtable tr + tr td { border-top: 1px solid #EEEEEE; }
.dlabel { color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; }
.dval { text-align: right; font-weight: 600; }
.remarque { background: #F0F4F8; border-left: 3px solid #1A5276; padding: 1rem 1.2rem; margin: 1rem 0; font-size: 0.92rem; line-height: 1.6; color: #333; }
.remarque strong { color: #111; }
.sep { border: none; border-top: 1px solid #E0E0E0; margin: 1.5rem 0; }
.sepfort { border: none; border-top: 2px solid #111; margin: 0.3rem 0 1.5rem 0; }
.slabel { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.18em; color: #888; margin-bottom: 1rem; }
[data-baseweb="tab"] { font-size: 0.73rem !important; text-transform: uppercase !important; letter-spacing: 0.12em !important; font-weight: 600 !important; }
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_communes():
    return charger_communes()

df_communes = load_communes()
liste = df_communes["nom_standard"].tolist()

with st.sidebar:
    st.markdown("<div style='padding:1rem 0 0.4rem;font-family:Playfair Display,serif;font-size:1.5rem;font-weight:900;color:#FFF;letter-spacing:-1px;'>ViloScope</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.65rem;text-transform:uppercase;letter-spacing:0.2em;color:#666;'>Comparateur de villes</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#333;margin:0.8rem 0;'>", unsafe_allow_html=True)
    # Recherche et sélection ville 1
    st.markdown("<div style='font-size:0.65rem;text-transform:uppercase;letter-spacing:0.15em;color:#888;margin-bottom:0.3rem;'>Ville 1</div>", unsafe_allow_html=True)
    recherche1 = st.text_input("r1", value="", placeholder="Taper pour rechercher...", label_visibility="collapsed", key="r1")
    liste1 = [v for v in liste if recherche1.strip().lower() in v.lower()] if recherche1.strip() else liste
    if not liste1:
        liste1 = liste
    ville1 = st.selectbox("v1", liste1, index=0, label_visibility="collapsed", key="s1")

    # Recherche et sélection ville 2
    st.markdown("<div style='font-size:0.65rem;text-transform:uppercase;letter-spacing:0.15em;color:#888;margin:0.7rem 0 0.3rem;'>Ville 2</div>", unsafe_allow_html=True)
    recherche2 = st.text_input("r2", value="", placeholder="Taper pour rechercher...", label_visibility="collapsed", key="r2")
    liste2 = [v for v in liste if recherche2.strip().lower() in v.lower()] if recherche2.strip() else liste
    if not liste2:
        liste2 = liste
    ville2 = st.selectbox("v2", liste2, index=min(1, len(liste2)-1), label_visibility="collapsed", key="s2")

    if ville1 == ville2:
        st.error("Choisissez deux villes différentes.")
        st.stop()
    st.markdown("<hr style='border-color:#333;margin:1rem 0 0.7rem;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.63rem;color:#555;line-height:1.7;'>{len(liste)} villes disponibles<br><br>Sources : INSEE · DVF · Open-Meteo<br>France Travail · OpenStreetMap</div>", unsafe_allow_html=True)

v1 = get_infos_ville(df_communes, ville1)
v2 = get_infos_ville(df_communes, ville2)

def fpop(n):
    return f"{int(n):,}".replace(",", "\u202f")

st.markdown(f"""
<div class="titre"><span style="color:#C0392B;">{ville1}</span><span style="color:#CCC;"> vs </span><span style="color:#1A5276;">{ville2}</span></div>
<div class="sous-titre">Analyse comparative — Villes françaises</div>
<hr class="sepfort">
""", unsafe_allow_html=True)

tab_gen, tab_emp, tab_log, tab_met, tab_vie = st.tabs(["General", "Emploi", "Logement", "Meteo", "Vie locale"])


def graphe_barres(titre, labels, vals, cols):
    fig = go.Figure(go.Bar(
        x=labels, y=vals, marker_color=cols,
        text=[fpop(v) for v in vals], textposition="outside",
        textfont=dict(size=12, color="#111111"),
    ))
    fig.update_layout(
        title=dict(text=titre, font=dict(size=9, color="#888"), x=0),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                   tickfont=dict(size=10, color="#555"), tickformat=",d"),
        xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#111")),
        margin=dict(t=35, b=10, l=70, r=10), height=280, showlegend=False,
    )
    return fig


def graphe_groupe(titre, cats, vals1, vals2, nom1, nom2):
    fig = go.Figure([
        go.Bar(name=nom1, x=cats, y=vals1, marker_color=C1,
               text=[fpop(v) for v in vals1], textposition="outside",
               textfont=dict(size=10, color="#111")),
        go.Bar(name=nom2, x=cats, y=vals2, marker_color=C2,
               text=[fpop(v) for v in vals2], textposition="outside",
               textfont=dict(size=10, color="#111")),
    ])
    fig.update_layout(
        barmode="group",
        title=dict(text=titre, font=dict(size=9, color="#888"), x=0),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                   tickfont=dict(size=10, color="#555"), tickformat=",d"),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#111")),
        legend=dict(font=dict(size=11, color="#111"), bgcolor="white",
                    bordercolor="#E0E0E0", borderwidth=1),
        margin=dict(t=35, b=10, l=70, r=10), height=320,
    )
    return fig


def remarque(texte):
    st.markdown(f"<div class='remarque'>{texte}</div>", unsafe_allow_html=True)


# ── GENERAL ───────────────────────────────────────────────────────────────────
with tab_gen:
    c1, c2 = st.columns(2, gap="large")
    for col, v, couleur, hc in [(c1, v1, C1, "h1"), (c2, v2, C2, "h2")]:
        with col:
            st.markdown(f"<div class='{hc}'>{v['nom']}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="carte">
                <div class="gchiffre" style="color:{couleur};">{fpop(v['population'])}</div>
                <div class="clabel">Habitants</div>
            </div>
            <div class="carte">
                <table class="dtable">
                    <tr><td class="dlabel">Superficie</td><td class="dval">{v['superficie']:.1f} km²</td></tr>
                    <tr><td class="dlabel">Densite</td><td class="dval">{v['densite']:.0f} hab/km²</td></tr>
                    <tr><td class="dlabel">Departement</td><td class="dval">{v['departement']}</td></tr>
                    <tr><td class="dlabel">Region</td><td class="dval">{v['region']}</td></tr>
                    <tr><td class="dlabel">Code INSEE</td><td class="dval">{v['code_insee']}</td></tr>
                </table>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)
    cg1, cg2 = st.columns(2)
    with cg1:
        st.plotly_chart(graphe_barres("POPULATION", [ville1, ville2],
            [v1["population"], v2["population"]], [C1, C2]), use_container_width=True)
    with cg2:
        st.plotly_chart(graphe_barres("DENSITE (hab/km²)", [ville1, ville2],
            [v1["densite"], v2["densite"]], [C1, C2]), use_container_width=True)

    ratio = v1["population"] / v2["population"] if v2["population"] else 1
    plus_grande = ville1 if ratio > 1 else ville2
    moins_grande = ville2 if ratio > 1 else ville1
    ratio_aff = max(ratio, 1 / ratio)
    plus_dense = ville1 if v1["densite"] > v2["densite"] else ville2
    diff_densite = abs(v1["densite"] - v2["densite"])

    remarque(
        f"<strong>{plus_grande}</strong> est {ratio_aff:.1f} fois plus peuplee que "
        f"<strong>{moins_grande}</strong>. "
        f"En matiere de densite, <strong>{plus_dense}</strong> est nettement plus dense "
        f"avec un ecart de {diff_densite:.0f} habitants par km² entre les deux villes."
    )


# ── EMPLOI ────────────────────────────────────────────────────────────────────
with tab_emp:
    st.markdown("<div class='slabel'>Emploi et chômage — INSEE (Recensement 2020)</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    res_emp = {}

    for col, v, couleur, hc in [(c1, v1, C1, "h1"), (c2, v2, C2, "h2")]:
        with col:
            st.markdown(f"<div class='{hc}'>{v['nom']}</div>", unsafe_allow_html=True)
            with st.spinner("Chargement..."):
                data, erreur = get_offres(v["code_insee"])
            res_emp[v["nom"]] = data

            if data and data.get("emplois", 0) > 0:
                st.markdown(f"""
                <div class="carte">
                    <div class="gchiffre" style="color:{couleur};">{fpop(data['emplois'])}</div>
                    <div class="clabel">Emplois sur le territoire</div>
                </div>
                <div class="carte">
                    <table class="dtable">
                        <tr><td class="dlabel">Taux de chômage</td><td class="dval">{data['taux_chom']} %</td></tr>
                        <tr><td class="dlabel">Chômeurs</td><td class="dval">{fpop(data['chomeurs'])}</td></tr>
                    </table>
                </div>""", unsafe_allow_html=True)

                if data["secteurs"]:
                    fig = go.Figure(go.Bar(
                        x=list(data["secteurs"].keys()),
                        y=list(data["secteurs"].values()),
                        marker_color=couleur,
                        text=list(data["secteurs"].values()),
                        textposition="outside",
                        textfont=dict(size=11, color="#111"),
                    ))
                    fig.update_layout(
                        title=dict(text="EMPLOIS PAR SECTEUR", font=dict(size=9, color="#888"), x=0),
                        plot_bgcolor="white", paper_bgcolor="white",
                        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                                   tickfont=dict(size=10, color="#555")),
                        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#111")),
                        margin=dict(t=30, b=10, l=50, r=10), height=250, showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                if len(data["evolution"]) > 1:
                    ev = data["evolution"]
                    annees = sorted(ev.keys())
                    fig2 = go.Figure(go.Scatter(
                        x=annees, y=[ev[a] for a in annees],
                        mode="lines+markers",
                        line=dict(color=couleur, width=2.5),
                        marker=dict(size=8, color=couleur),
                    ))
                    fig2.update_layout(
                        title=dict(text="EVOLUTION DU NOMBRE D'EMPLOIS", font=dict(size=9, color="#888"), x=0),
                        plot_bgcolor="white", paper_bgcolor="white",
                        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                                   tickfont=dict(size=10, color="#555")),
                        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#111"), type="category"),
                        margin=dict(t=30, b=10, l=70, r=10), height=220, showlegend=False,
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.markdown(f"""
                <div class="carte">
                    <div style="color:#888;font-size:0.88rem;">
                        Aucune donnee disponible.<br>
                        <span style="font-size:0.75rem;color:#aaa;">{erreur or 'Verifiez les fichiers dossier_complet dans data/'}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    d1 = res_emp.get(v1["nom"])
    d2 = res_emp.get(v2["nom"])
    if d1 and d2 and d1.get("emplois") and d2.get("emplois"):
        st.markdown("<hr class='sep'>", unsafe_allow_html=True)
        st.plotly_chart(graphe_barres("NOMBRE D'EMPLOIS",
            [ville1, ville2], [d1["emplois"], d2["emplois"]], [C1, C2]),
            use_container_width=True)
        st.plotly_chart(graphe_barres("TAUX DE CHÔMAGE (%)",
            [ville1, ville2], [d1["taux_chom"], d2["taux_chom"]], [C1, C2]),
            use_container_width=True)
        plus = ville1 if d1["emplois"] > d2["emplois"] else ville2
        diff = abs(d1["emplois"] - d2["emplois"])
        chom1, chom2 = d1["taux_chom"], d2["taux_chom"]
        moins_chom = ville1 if chom1 < chom2 else ville2
        remarque(
            f"<strong>{plus}</strong> concentre davantage d'emplois avec {fpop(diff)} emplois de plus. "
            f"Le taux de chômage est plus faible à <strong>{moins_chom}</strong> "
            f"avec {min(chom1, chom2)} % contre {max(chom1, chom2)} %."
        )


# ── LOGEMENT ──────────────────────────────────────────────────────────────────
with tab_log:
    st.markdown("<div class='slabel'>Prix de l'immobilier — DVF 2023 a 2025</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    res_log = {}

    for col, v, couleur, hc in [(c1, v1, C1, "h1"), (c2, v2, C2, "h2")]:
        with col:
            st.markdown(f"<div class='{hc}'>{v['nom']}</div>", unsafe_allow_html=True)
            with st.spinner("Analyse..."):
                data = get_logement(v["nom"])
            res_log[v["nom"]] = data

            if data:
                dern = max(data.keys())
                d = data[dern]
                pg = f"{int(d['prix_global'])} €/m²"
                pa = f"{int(d['prix_appart'])} €/m²" if d["prix_appart"] else "N/A"
                pm = f"{int(d['prix_maison'])} €/m²" if d["prix_maison"] else "N/A"
                st.markdown(f"""
                <div class="carte">
                    <div class="gchiffre" style="color:{couleur};">{pg}</div>
                    <div class="clabel">Prix median — {dern}</div>
                </div>
                <div class="carte">
                    <table class="dtable">
                        <tr><td class="dlabel">Appartement</td><td class="dval">{pa}</td></tr>
                        <tr><td class="dlabel">Maison</td><td class="dval">{pm}</td></tr>
                        <tr><td class="dlabel">Transactions analysees</td><td class="dval">{fpop(d['nb_transactions'])}</td></tr>
                    </table>
                </div>""", unsafe_allow_html=True)

                if len(data) > 1:
                    at = sorted(data.keys())
                    fig = go.Figure(go.Scatter(
                        x=[str(a) for a in at],
                        y=[data[a]["prix_global"] for a in at],
                        mode="lines+markers",
                        line=dict(color=couleur, width=2.5),
                        marker=dict(size=8, color=couleur),
                    ))
                    fig.update_layout(
                        title=dict(text="EVOLUTION DU PRIX AU M²", font=dict(size=9, color="#888"), x=0),
                        plot_bgcolor="white", paper_bgcolor="white",
                        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                                   ticksuffix=" €", tickfont=dict(size=10, color="#555")),
                        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#111"),
                                   type="category"),
                        margin=dict(t=30, b=10, l=70, r=10), height=220, showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("""
                <div class="carte"><div style="color:#888;font-size:0.88rem;">
                    Aucune donnee.<br>
                    <span style="font-size:0.75rem;">Lancez d'abord : python preparer_donnees.py</span>
                </div></div>""", unsafe_allow_html=True)

    dl1 = res_log.get(v1["nom"])
    dl2 = res_log.get(v2["nom"])
    if dl1 and dl2:
        st.markdown("<hr class='sep'>", unsafe_allow_html=True)
        a1 = dl1[max(dl1.keys())]
        a2 = dl2[max(dl2.keys())]
        cats = ["Prix global", "Appartement", "Maison"]
        vals1 = [a1["prix_global"], a1["prix_appart"] or 0, a1["prix_maison"] or 0]
        vals2 = [a2["prix_global"], a2["prix_appart"] or 0, a2["prix_maison"] or 0]
        st.plotly_chart(graphe_groupe("COMPARAISON DES PRIX AU M²",
            cats, vals1, vals2, ville1, ville2), use_container_width=True)

        plus_cher = ville1 if a1["prix_global"] > a2["prix_global"] else ville2
        diff_prix = abs(a1["prix_global"] - a2["prix_global"])
        pct = (diff_prix / min(a1["prix_global"], a2["prix_global"])) * 100
        remarque(
            f"L'immobilier est plus cher a <strong>{plus_cher}</strong>, "
            f"avec un ecart de <strong>{int(diff_prix)} €/m²</strong> sur le prix median global, "
            f"soit environ <strong>{pct:.0f}%</strong> de difference entre les deux villes."
        )


# ── METEO ─────────────────────────────────────────────────────────────────────
with tab_met:
    st.markdown("<div class='slabel'>Previsions et climat — Open-Meteo</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    currents = {}
    for col, v, couleur, hc in [(c1, v1, C1, "h1"), (c2, v2, C2, "h2")]:
        with col:
            st.markdown(f"<div class='{hc}'>{v['nom']}</div>", unsafe_allow_html=True)
            with st.spinner("Chargement..."):
                current, previsions = get_previsions(v["lat"], v["lon"])
            currents[v["nom"]] = current
            if current:
                temp = current.get("temperature", "?")
                desc = code_vers_description(current.get("weathercode", 0))
                vent = current.get("windspeed", "?")
                st.markdown(f"""
                <div class="carte">
                    <div class="gchiffre" style="color:{couleur};">{temp} °C</div>
                    <div class="clabel">{desc} — Vent {vent} km/h</div>
                </div>""", unsafe_allow_html=True)
            if previsions is not None:
                st.markdown("<div style='font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888;margin-bottom:0.3rem;'>Previsions 7 jours</div>", unsafe_allow_html=True)
                st.dataframe(previsions, use_container_width=True, hide_index=True)

    cur1 = currents.get(v1["nom"])
    cur2 = currents.get(v2["nom"])
    if cur1 and cur2:
        t1 = cur1.get("temperature", 0)
        t2 = cur2.get("temperature", 0)
        if abs(t1 - t2) >= 0.5:
            plus_chaud = ville1 if t1 > t2 else ville2
            remarque(f"En ce moment, <strong>{plus_chaud}</strong> est plus chaud de <strong>{abs(t1 - t2):.1f} °C</strong>.")

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)
    st.markdown("<div class='slabel'>Temperatures moyennes sur 12 mois</div>", unsafe_allow_html=True)

    cc1, cc2 = st.columns(2)
    climats = {}
    for col, v, couleur in [(cc1, v1, C1), (cc2, v2, C2)]:
        with col:
            with st.spinner(f"Chargement {v['nom']}..."):
                climat = get_climat_annuel(v["lat"], v["lon"])
            climats[v["nom"]] = climat
            if climat is not None:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=climat["Mois"], y=climat["Temp max moy (C)"],
                    mode="lines", name="Max", line=dict(color=couleur, width=2.5)))
                fig.add_trace(go.Scatter(x=climat["Mois"], y=climat["Temp min moy (C)"],
                    mode="lines", name="Min", line=dict(color=couleur, width=1.5, dash="dot")))
                fig.update_layout(
                    title=dict(text=f"TEMPERATURES — {v['nom'].upper()}", font=dict(size=9, color="#888"), x=0),
                    plot_bgcolor="white", paper_bgcolor="white",
                    yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                               ticksuffix=" °C", tickfont=dict(size=10, color="#555")),
                    xaxis=dict(showgrid=False, tickangle=45, tickfont=dict(size=9, color="#111")),
                    legend=dict(font=dict(size=10, color="#111"), bgcolor="white",
                                bordercolor="#E0E0E0", borderwidth=1),
                    margin=dict(t=30, b=60, l=55, r=10), height=270,
                )
                st.plotly_chart(fig, use_container_width=True)

                fig2 = go.Figure(go.Bar(
                    x=climat["Mois"], y=climat["Precipitations totales (mm)"],
                    marker_color=couleur, opacity=0.75,
                    text=[f"{p:.0f}" for p in climat["Precipitations totales (mm)"]],
                    textposition="outside", textfont=dict(size=9, color="#555"),
                ))
                fig2.update_layout(
                    title=dict(text="PRECIPITATIONS MENSUELLES (mm)", font=dict(size=9, color="#888"), x=0),
                    plot_bgcolor="white", paper_bgcolor="white",
                    yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                               ticksuffix=" mm", tickfont=dict(size=10, color="#555")),
                    xaxis=dict(showgrid=False, tickangle=45, tickfont=dict(size=9, color="#111")),
                    margin=dict(t=30, b=60, l=55, r=10), height=240, showlegend=False,
                )
                st.plotly_chart(fig2, use_container_width=True)

    # Remarque climatique comparée
    cl1 = climats.get(v1["nom"])
    cl2 = climats.get(v2["nom"])
    if cl1 is not None and cl2 is not None:
        st.markdown("<hr class='sep'>", unsafe_allow_html=True)
        st.markdown("<div class='slabel'>Remarque climatique</div>", unsafe_allow_html=True)

        moy_max1 = cl1["Temp max moy (C)"].mean()
        moy_max2 = cl2["Temp max moy (C)"].mean()
        moy_min1 = cl1["Temp min moy (C)"].mean()
        moy_min2 = cl2["Temp min moy (C)"].mean()
        precip1  = cl1["Precipitations totales (mm)"].sum()
        precip2  = cl2["Precipitations totales (mm)"].sum()

        plus_chaud    = ville1 if moy_max1 > moy_max2 else ville2
        diff_tmax     = abs(moy_max1 - moy_max2)
        plus_doux     = ville1 if moy_min1 > moy_min2 else ville2
        plus_pluvieux = ville1 if precip1 > precip2 else ville2
        diff_precip   = abs(precip1 - precip2)

        if diff_tmax < 1:
            ligne1 = "Les deux villes affichent des temperatures maximales tres proches sur l'annee, avec moins de 1 °C d'ecart."
        else:
            ligne1 = f"Sur les 12 derniers mois, <strong>{plus_chaud}</strong> est la ville la plus chaude avec {diff_tmax:.1f} °C d'ecart en moyenne."

        ligne2 = f"Les nuits sont plus douces a <strong>{plus_doux}</strong>, ce qui indique un hiver globalement plus clement."
        ligne3 = f"<strong>{plus_pluvieux}</strong> est la plus pluvieuse, avec {diff_precip:.0f} mm de pluie cumulee de plus sur l'annee."

        remarque(f"{ligne1}<br>{ligne2}<br>{ligne3}")


# ── VIE LOCALE ────────────────────────────────────────────────────────────────
with tab_vie:
    st.markdown("<div class='slabel'>Equipements dans un rayon de 5 km — OpenStreetMap</div>", unsafe_allow_html=True)
    st.info("Le chargement peut prendre 20 a 40 secondes. Les resultats sont ensuite mis en cache.")

    with st.spinner(f"Interrogation OpenStreetMap pour {ville1}..."):
        vie1 = get_vie_locale(v1["lat"], v1["lon"])
    with st.spinner(f"Interrogation OpenStreetMap pour {ville2}..."):
        vie2 = get_vie_locale(v2["lat"], v2["lon"])

    c1, c2 = st.columns(2, gap="large")
    for col, v, vie, couleur, hc in [(c1, v1, vie1, C1, "h1"), (c2, v2, vie2, C2, "h2")]:
        with col:
            st.markdown(f"<div class='{hc}'>{v['nom']}</div>", unsafe_allow_html=True)
            if vie:
                lignes = ""
                for i, (cat, val) in enumerate(vie.items()):
                    bord = "" if i == 0 else "border-top:1px solid #EEE;"
                    lignes += f"<tr style='{bord}'><td class='dlabel' style='padding:0.4rem 0;'>{cat}</td><td class='dval' style='color:{couleur};padding:0.4rem 0;'>{val}</td></tr>"
                st.markdown(f"<div class='carte'><table class='dtable'>{lignes}</table></div>", unsafe_allow_html=True)

    if vie1 and vie2:
        st.markdown("<hr class='sep'>", unsafe_allow_html=True)
        cats  = list(vie1.keys())
        vals1 = [vie1.get(k, 0) or 0 for k in cats]
        vals2 = [vie2.get(k, 0) or 0 for k in cats]

        fig = go.Figure([
            go.Bar(name=ville1, x=cats, y=vals1, marker_color=C1,
                   text=vals1, textposition="outside", textfont=dict(size=10, color="#111")),
            go.Bar(name=ville2, x=cats, y=vals2, marker_color=C2,
                   text=vals2, textposition="outside", textfont=dict(size=10, color="#111")),
        ])
        fig.update_layout(
            barmode="group",
            title=dict(text="COMPARAISON DES EQUIPEMENTS", font=dict(size=9, color="#888"), x=0),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="#F0F0F0", zeroline=False,
                       tickfont=dict(size=10, color="#555")),
            xaxis=dict(showgrid=False, tickangle=25, tickfont=dict(size=10, color="#111")),
            legend=dict(font=dict(size=11, color="#111"), bgcolor="white",
                        bordercolor="#E0E0E0", borderwidth=1),
            margin=dict(t=30, b=80, l=50, r=10), height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

        total1 = sum(vals1)
        total2 = sum(vals2)
        plus_equip = ville1 if total1 > total2 else ville2
        ecarts = [(cats[i], abs(vals1[i] - vals2[i]), ville1 if vals1[i] > vals2[i] else ville2)
                  for i in range(len(cats)) if vals1[i] + vals2[i] > 0]
        if ecarts:
            cat_max, ecart_max, ville_max = max(ecarts, key=lambda x: x[1])
            remarque(
                f"<strong>{plus_equip}</strong> concentre davantage d'equipements au total dans un rayon de 5 km. "
                f"L'ecart le plus marque concerne les <strong>{cat_max.lower()}</strong> : "
                f"<strong>{ville_max}</strong> en compte {ecart_max} de plus que l'autre ville."
            )
