import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="IDP Store", layout="wide")

CONFIG_PATH = Path(__file__).parent / "apps_config.json"


def load_config():
    if not CONFIG_PATH.exists():
        return {"apps": []}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_chip_color(label: str) -> str:
    label = (label or "").lower()
    if label in ["latest", "production", "stable"]:
        return "#0f9d58"
    if label in ["experimental", "beta", "preview"]:
        return "#f9ab00"
    if label in ["legacy", "manual"]:
        return "#5f6368"
    if label in ["sprint 2", "sprint 3", "sprint 4", "sprint 5"]:
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


def render_app_card(app: dict):
    name = app.get("name", "Unknown App")
    description = app.get("description", "No description provided.")
    repo = app.get("repo", "-")
    branch = app.get("branch", "-")
    entry_file = app.get("entry_file", "-")
    streamlit_url = app.get("streamlit_url", "")
    logo = app.get("logo", "")
    tags = app.get("tags", [])

    github_url = f"https://github.com/{repo}" if repo and repo != "-" else ""

    with st.container(border=True):
        top1, top2 = st.columns([1, 5], gap="small")

        with top1:
            if logo:
                st.image(logo, width=64)
            else:
                st.markdown(
                    """
                    <div style="
                        width:64px;
                        height:64px;
                        border-radius:16px;
                        background:#111827;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:28px;
                    ">📄</div>
                    """,
                    unsafe_allow_html=True,
                )

        with top2:
            st.markdown(f"### {name}")
            if tags:
                for tag in tags:
                    render_chip(tag)

            st.write(description)
            st.caption(f"Repo: {repo}")
            st.caption(f"Branch: {branch} | Entry: {entry_file}")

        b1, b2 = st.columns(2)
        with b1:
            if streamlit_url:
                st.link_button("Open App", streamlit_url, use_container_width=True)
            else:
                st.button("Open App", disabled=True, use_container_width=True, key=f"open_{name}")

        with b2:
            if github_url:
                st.link_button("Open GitHub Repo", github_url, use_container_width=True)
            else:
                st.button("Open GitHub Repo", disabled=True, use_container_width=True, key=f"repo_{name}")


def app_matches(app: dict, q: str) -> bool:
    q = q.strip().lower()
    if not q:
        return True

    blob = " ".join([
        app.get("name", ""),
        app.get("description", ""),
        app.get("repo", ""),
        app.get("branch", ""),
        app.get("entry_file", ""),
        " ".join(app.get("tags", [])),
    ]).lower()

    return q in blob


def main():
    config = load_config()
    apps = config.get("apps", [])

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("IDP Store")
    st.caption("Browse and launch all versions of Intelligent Document Processor")

    t1, t2, t3 = st.columns([2, 1, 1])
    with t1:
        search = st.text_input("Search apps", placeholder="Search by version, sprint, repo, or feature")
    with t2:
        st.metric("Total Apps", len(apps))
    with t3:
        latest_count = sum(1 for a in apps if "Latest" in a.get("tags", []))
        st.metric("Latest Builds", latest_count)

    if not apps:
        st.warning("No apps configured. Please update apps_config.json.")
        return

    filtered = [app for app in apps if app_matches(app, search)]

    if not filtered:
        st.info("No matching apps found.")
        return

    cols = st.columns(2, gap="large")
    for i, app in enumerate(filtered):
        with cols[i % 2]:
            render_app_card(app)


if __name__ == "__main__":
    main()
