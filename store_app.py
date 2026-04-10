import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="IDP Store", layout="wide")

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "apps_config.json"
LOGO_PATH = BASE_DIR / "assets" / "idp-logo.png"

UI_SIZES = {
    "header_logo_width": 280,
    "card_logo_width": 250,
    "card_logo_column_ratio": [1.35, 2.25],
}

def get_logo_path(app: dict):
    logo = app.get("logo", "")
    if not logo:
        return None

    path = BASE_DIR / logo
    return path if path.exists() else None
    
def load_config():
    if not CONFIG_PATH.exists():
        st.error(f"Missing config file: {CONFIG_PATH}")
        return {"apps": []}

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"apps_config.json is invalid JSON. Line {e.lineno}, column {e.colno}: {e.msg}")
        st.code(CONFIG_PATH.read_text(encoding="utf-8"))
        return {"apps": []}
    except Exception as e:
        st.error(f"Failed to load config: {str(e)}")
        return {"apps": []}


def get_chip_color(label: str) -> str:
    label = (label or "").lower()
    if label in ["latest", "production", "stable"]:
        return "#0f9d58"
    if label in ["experimental", "beta", "preview"]:
        return "#f9ab00"
    if label in ["legacy", "manual"]:
        return "#5f6368"
    if label.startswith("sprint"):
        return "#1a73e8"
    return "#6c757d"


def render_chip(text: str):
    color = get_chip_color(text)
    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background:{color};
            color:white;
            font-size:12px;
            font-weight:600;
            margin-right:6px;
            margin-bottom:6px;
        ">{text}</span>
        """,
        unsafe_allow_html=True,
    )


def get_app_tags(app: dict):
    tags = app.get("tags", [])
    if not tags and app.get("tag"):
        tags = [app.get("tag")]
    return tags


def has_tag(app: dict, tag_name: str) -> bool:
    tags = [t.lower() for t in get_app_tags(app)]
    return tag_name.lower() in tags


def app_matches_search(app: dict, q: str) -> bool:
    q = q.strip().lower()
    if not q:
        return True

    blob = " ".join([
        app.get("name", ""),
        app.get("description", ""),
        app.get("repo", ""),
        app.get("branch", ""),
        app.get("entry_file", ""),
        " ".join(get_app_tags(app)),
    ]).lower()

    return q in blob


def app_matches_filter(app: dict, active_filter: str) -> bool:
    if active_filter == "All":
        return True

    tags = [t.lower() for t in get_app_tags(app)]

    if active_filter == "Stable":
        return "stable" in tags

    if active_filter == "Latest":
        return "latest" in tags

    if active_filter == "Manual":
        return "manual" in tags

    if active_filter == "Sprint":
        return any(t.startswith("sprint") for t in tags)

    return True


def render_header():
    c1, c2 = st.columns([1, 5], gap="medium")

    with c1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=UI_SIZES["header_logo_width"])

    with c2:
        st.title("IDP Store")
        st.caption("Browse and launch all versions of Intelligent Document Processor")


def render_app_card(app: dict):
    name = app.get("name", "Unknown App")
    description = app.get("description", "No description provided.")
    repo = app.get("repo", "-")
    branch = app.get("branch", "-")
    entry_file = app.get("entry_file", "-")
    streamlit_url = app.get("streamlit_url", "")
    tags = get_app_tags(app)
    github_url = f"https://github.com/{repo}" if repo and repo != "-" else ""
    app_logo = get_logo_path(app)

    with st.container(border=True):
        c1, c2 = st.columns(UI_SIZES["card_logo_column_ratio"], gap="medium")

        with c1:
            if app_logo:
                st.image(str(app_logo), width=UI_SIZES["card_logo_width"])
            elif LOGO_PATH.exists():
                st.image(str(LOGO_PATH), width=UI_SIZES["card_logo_width"])

        with c2:
            st.markdown(f"### {name}")

            if tags:
                for tag in tags:
                    render_chip(tag)

            st.write(description)
            st.caption(f"Repo: {repo}")
            st.caption(f"Branch: {branch} | Entry: {entry_file}")

        st.markdown("")

        b1, b2 = st.columns(2)
        with b1:
            if streamlit_url:
                st.link_button("Open App", streamlit_url, use_container_width=True)
            else:
                st.button("Open App", disabled=True, use_container_width=True, key=f"open_{name}")

        with b2:
            if github_url:
                st.link_button("GitHub", github_url, use_container_width=True)
            else:
                st.button("GitHub", disabled=True, use_container_width=True, key=f"repo_{name}")


def main():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1300px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    config = load_config()
    apps = config.get("apps", [])

    render_header()

    if not apps:
        st.warning("No apps configured. Please update apps_config.json.")
        return

    t1, t2, t3 = st.columns([2.2, 1, 1], gap="medium")
    with t1:
        search = st.text_input("Search apps", placeholder="Search by version, sprint, repo, or feature")
    with t2:
        st.metric("Total Apps", len(apps))
    with t3:
        stable_count = sum(1 for a in apps if has_tag(a, "Stable"))
        st.metric("Stable Builds", stable_count)

    st.markdown("### Filter")

    filter_labels = ["All", "Stable", "Latest", "Manual", "Sprint"]
    filter_cols = st.columns(len(filter_labels))
    active_filter = st.session_state.get("store_filter", "All")

    for i, label in enumerate(filter_labels):
        with filter_cols[i]:
            if st.button(label, use_container_width=True, key=f"filter_{label}"):
                st.session_state["store_filter"] = label
                active_filter = label

    st.caption(f"Active Filter: {active_filter}")

    filtered = [
        app for app in apps
        if app_matches_search(app, search) and app_matches_filter(app, active_filter)
    ]

    if not filtered:
        st.info("No matching apps found.")
        return

    st.markdown("### Available Versions")

    cols = st.columns(3, gap="large")
    for i, app in enumerate(filtered):
        with cols[i % 3]:
            render_app_card(app)


if __name__ == "__main__":
    main()
