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


def render_app_card(app):
    with st.container(border=True):
        st.markdown(f"### {app['name']}")
        st.caption(app.get("tag", ""))
        st.write(app.get("description", "No description"))
        st.caption(f"Repo: {app.get('repo', '-')}")
        st.caption(f"Branch: {app.get('branch', '-')}")
        st.caption(f"Entry: {app.get('entry_file', '-')}")
        st.link_button("Open App", app["streamlit_url"], use_container_width=True)
        repo_url = f"https://github.com/{app['repo']}"
        st.link_button("Open GitHub Repo", repo_url, use_container_width=True)


def main():
    st.title("IDP Store")
    st.caption("Launch and browse all Intelligent Document Processor versions")

    config = load_config()
    apps = config.get("apps", [])

    if not apps:
        st.warning("No apps configured. Please update apps_config.json.")
        return

    search = st.text_input("Search versions", "")
    filtered = []

    for app in apps:
        blob = " ".join([
            app.get("name", ""),
            app.get("description", ""),
            app.get("tag", ""),
            app.get("repo", "")
        ]).lower()

        if search.strip().lower() in blob:
            filtered.append(app)

    if not filtered:
        st.info("No matching apps found.")
        return

    cols = st.columns(2)
    for i, app in enumerate(filtered):
        with cols[i % 2]:
            render_app_card(app)


if __name__ == "__main__":
    main()
