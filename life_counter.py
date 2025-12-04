
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="MTG Life Counter", layout="wide")

# ----------------- ANIMATED UI CSS -----------------
st.markdown("""
<style>

@keyframes pulseLife {
    0%   { transform: scale(1); }
    50%  { transform: scale(1.12); }
    100% { transform: scale(1); }
}

@keyframes glowBorder {
    0%   { box-shadow: 0px 0px 5px rgba(255,255,255,0.2); }
    50%  { box-shadow: 0px 0px 20px rgba(255,255,255,0.8); }
    100% { box-shadow: 0px 0px 5px rgba(255,255,255,0.2); }
}

@keyframes fadeInCard {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0px); }
}

.animated-card {
    animation: fadeInCard 0.7s ease-out;
}

.life-animate {
    animation: pulseLife 0.45s ease-in-out;
}

.card-glow {
    animation: glowBorder 1.8s infinite ease-in-out;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ----------------- DARK MODE -----------------
if "dark" not in st.session_state:
    st.session_state.dark = False

if st.toggle("🌙 Dark Mode", value=st.session_state.dark):
    st.session_state.dark = True
    st.markdown("<style> body { background-color: #111; color:#eee; } </style>", unsafe_allow_html=True)
else:
    st.session_state.dark = False
    st.markdown("<style> body { background-color: #fff; color:#000; } </style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🪄 MTG Life Counter — Complete Edition</h1><hr>", unsafe_allow_html=True)

# ----------------- INITIAL STATE -----------------
players = ["P1", "P2", "P3", "P4"]

if "life" not in st.session_state:
    st.session_state.life = {p: 40 for p in players}

if "cmd" not in st.session_state:
    st.session_state.cmd = {p: {o: 0 for o in players if o != p} for p in players}

if "poison" not in st.session_state:
    st.session_state.poison = {p: 0 for p in players}

if "color" not in st.session_state:
    st.session_state.color = {p: "White" for p in players}

if "monarch" not in st.session_state:
    st.session_state.monarch = None

if "initiative" not in st.session_state:
    st.session_state.initiative = None

if "life_log" not in st.session_state:
    st.session_state.life_log = []

COLOR_MAP = {
    "White": "#f2f2f2",
    "Blue": "#b3d1ff",
    "Black": "#333333",
    "Red": "#ffb3b3",
    "Green": "#b3ffb3",
}

# ----------------- PLAYER CARD FUNCTION -----------------
def player_card(p):
    bg = COLOR_MAP[st.session_state.color[p]]
    text_color = "#000" if st.session_state.color[p] != "Black" else "#fff"

    with st.container(border=True):
        st.markdown("<div class='animated-card card-glow'>", unsafe_allow_html=True)

        st.markdown(
            f"<h2 style='text-align:center;color:{text_color}'>{p}</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h1 class='life-animate' style='text-align:center;color:{text_color}'>{st.session_state.life[p]} life</h1>",
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)
        if c1.button(f"{p} +1"):
            st.session_state.life[p] += 1
            st.session_state.life_log.append((datetime.now(), p, st.session_state.life[p]))
        if c2.button(f"{p} -1"):
            st.session_state.life[p] -= 1
            st.session_state.life_log.append((datetime.now(), p, st.session_state.life[p]))

        st.markdown("### Commander Damage")
        for o in players:
            if o == p: 
                continue
            colA, colB, colC = st.columns([3, 1, 1])
            cd = st.session_state.cmd[p][o]
            colA.write(f"From {o}: **{cd}**")
            if colB.button(f"+1 ({o}→{p})"):
                st.session_state.cmd[p][o] += 1
            if colC.button(f"-1 ({o}→{p})"):
                st.session_state.cmd[p][o] = max(0, st.session_state.cmd[p][o])

        st.markdown("### Poison")
        colP1, colP2, colP3 = st.columns([3,1,1])
        colP1.write(f"Poison: **{st.session_state.poison[p]}**")
        if colP2.button(f"{p} +P"):
            st.session_state.poison[p] += 1
        if colP3.button(f"{p} -P"):
            st.session_state.poison[p] = max(0, st.session_state.poison[p])

        st.markdown("### Player Color")
        st.session_state.color[p] = st.selectbox(
            f"Color ({p})", ["White", "Blue", "Black", "Red", "Green"],
            index=["White","Blue","Black","Red","Green"].index(st.session_state.color[p])
        )

        if st.session_state.monarch == p:
            st.markdown("👑 **You are the Monarch**")
        if st.session_state.initiative == p:
            st.markdown("⚔️ **You have the Initiative**")

        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- LAYOUT -----------------
c1, c2 = st.columns(2)
with c1: player_card("P1")
with c2: player_card("P2")

c3, c4 = st.columns(2)
with c3: player_card("P3")
with c4: player_card("P4")

# ----------------- SPECIAL ROLES -----------------
st.markdown("---")
st.subheader("Special Roles")

colM, colI = st.columns(2)

with colM:
    new_m = st.selectbox("Set Monarch", ["None"] + players)
    st.session_state.monarch = None if new_m == "None" else new_m

with colI:
    new_i = st.selectbox("Set Initiative", ["None"] + players)
    st.session_state.initiative = None if new_i == "None" else new_i

# ----------------- LIFE GRAPH -----------------
st.markdown("---")
st.subheader("📊 Life Total Graph")

if st.session_state.life_log:
    fig, ax = plt.subplots()
    for p in players:
        times = [t for t, pl, _ in st.session_state.life_log if pl == p]
        vals = [v for _, pl, v in st.session_state.life_log if pl == p]
        if times:
            ax.plot(times, vals, label=p)
    ax.legend()
    ax.set_ylabel("Life")
    ax.set_xlabel("Time")
    st.pyplot(fig)
else:
    st.write("No data yet.")

# ----------------- RESET -----------------
st.markdown("---")
if st.button("🔁 Reset Everything"):
    for p in players:
        st.session_state.life[p] = 40
        st.session_state.poison[p] = 0
        st.session_state.color[p] = "White"
        for o in players:
            if o != p:
                st.session_state.cmd[p][o] = 0
    st.session_state.monarch = None
    st.session_state.initiative = None
    st.session_state.life_log = []
    st.success("Reset complete!")
