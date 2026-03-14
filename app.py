import importlib

import streamlit as st
import streamlit_shadcn_ui as ui
from pages import data_analysis, globe_3d, compare_datasets


st.set_page_config(page_title="PyClimaExplorer", layout="wide")

SIDEBAR_CSS = """
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
[data-testid="stSidebar"] > div:first-child {
    height: 100%;
    display: flex;
    flex-direction: column;
}
.pce-sidebar-top {
    flex: 1 1 auto;
}
.pce-sidebar-title {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 1.25rem;
}
.pce-sidebar-bottom {
    margin-top: auto;
}
</style>
"""


def nav_button(label: str, page_key: str, icon: str, active_page: str) -> None:
    is_active = page_key == active_page
    classes = "w-full justify-start rounded-xl px-4 py-2 text-sm font-medium"
    if is_active:
        classes += " bg-zinc-100 text-zinc-900"
    else:
        classes += " text-zinc-600 hover:bg-zinc-50"

    clicked = ui.button(
        text=f"{icon}  {label}",
        key=f"nav_{page_key}",
        variant="ghost",
        class_name=classes,
    )
    if clicked:
        st.session_state["active_page"] = page_key


def shadcn_sidebar() -> str:
    """Render a ShadCN-styled sidebar and return the selected page key."""

    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="pce-sidebar-top">', unsafe_allow_html=True)
        st.markdown('<div class="pce-sidebar-title">PyClimaExplorer</div>', unsafe_allow_html=True)

        active_page = st.session_state.get("active_page", "analyse_data")

        nav_button("Analyse Data", "analyse_data", "", active_page)
        nav_button("3D Globe", "globe_3d", "", active_page)
        nav_button("Compare Datasets", "compare_datasets", "", active_page)
        nav_button("Climate Time Machine", "climate_time_machine", "", active_page)
        nav_button("Chatbot", "chatbot", "", active_page)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="pce-sidebar-bottom">', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        return st.session_state.get("active_page", "analyse_data")


def main():
    page_key = shadcn_sidebar()

    if page_key == "analyse_data":
        data_analysis.app()
    elif page_key == "globe_3d":
        # Standalone script page – reload to rerun top-level code each time.
        importlib.reload(globe_3d)
    elif page_key == "compare_datasets":
        compare_datasets.app()
    elif page_key == "climate_time_machine":
        # Standalone script page – import then reload so it executes on each selection.
        import sys
        if "pages.climate_time_machine" not in sys.modules:
            ctm_module = importlib.import_module("pages.climate_time_machine")
        else:
            ctm_module = sys.modules["pages.climate_time_machine"]
            importlib.reload(ctm_module)
    elif page_key == "chatbot":
        chatbot_module = importlib.import_module("pages.chatbot")
        chatbot_module.app()

if __name__ == "__main__":
    main()
